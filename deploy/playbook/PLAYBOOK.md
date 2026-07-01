# AI Employee Setup Playbook — Claude + Hermes + Discord
**Proven by building Iris (cross-business EA), 2026-06-23. Reuse this for every new AI employee.**

This is the exact stack and sequence that got Iris live in Discord, running on Claude, with a scoped live task database. Every gotcha below cost real time the first time — follow the order and you skip them.

---

## The architecture (what each piece is)
| Layer | What | Notes |
|---|---|---|
| **Runtime** | **Hermes Agent** (Nous Research) on a **Hostinger VPS**, one-click install → Docker container `hvps-hermes-agent` | always-on, auto-restart, persistent disk. This is the "body." |
| **Brain** | **Claude** = the default/orchestrator intelligence (Anthropic key) | the reasoning core; Hostinger image ships NO model key by default |
| **Legs (per-task models)** | **the best model for each task**, not one model for everything | wire **OpenRouter** to unlock the full catalog; route cheap/fast models for routine work, a frontier model for hard reasoning, specialized models for code/vision. Hermes supports a default + **fallback chain** + per-task `-m/--provider` override. Claude stays the brain; the legs flex to whatever's best. |
| **Channel** | **Discord** (bot + private server + #brief/#chat) | how you talk to the employee, anywhere |
| **Identity** | `data/SOUL.md` | who they are, their voice, their job |
| **Skills** | `data/skills/<emp>/*/SKILL.md` | markdown + frontmatter, agentskills.io standard (same as Claude skills) |
| **State** | **Supabase** (scoped role + REST token) | tasks/memory; one project, per-employee scoped role |

One VPS can run multiple Hermes agents (separate containers). Each employee = its own SOUL + skills + Discord bot + scoped DB role.

---

## What you need before starting (per employee)
1. **Hostinger VPS** with the Hermes one-click agent running (or reuse the existing box, add another agent container).
2. **Discord developer app** → bot token, **Message Content Intent = ON**, a **private server** (just you) with **#brief** + **#chat** channels, Developer Mode ON to copy channel IDs.
3. **Anthropic API key** (the brain).
4. *(if the employee manages data)* a **Supabase project** + its **JWT Secret** (Settings → API).

---

## The proven sequence

### 0. Get clean SSH to the box
Reset the VPS root password in **hpanel.hostinger.com → VPS → Settings → SSH access** if you don't have it. Then install a key so file transfers don't fight password prompts:
```bash
ssh-keygen -t ed25519 -f ./emp_key -N "" -q
# one password login to install it:
ssh root@<VPS_IP> "mkdir -p /root/.ssh && echo '$(cat emp_key.pub)' >> /root/.ssh/authorized_keys"
# from now on: ssh -i emp_key root@<VPS_IP>
```
Container name: `docker ps --format '{{.Names}}' | grep hermes` → call it `$C`.

### 1. Author identity + skills, copy onto the box
- Write `SOUL.md` (see `SOUL-template.md` in this folder — businesses in priority order, the rubric, weekly rhythm, voice, first-contact behavior).
- Build skill packs as `SKILL.md` files (Iris's 7 live at `~/Desktop/iris-hermes/skills/` — good templates: morning-brief, schedule-day, manage-tasks, draft-comms, anticipate-needs, core-context).
```bash
scp -i emp_key SOUL.md root@<VPS_IP>:/docker/<C>/data/SOUL.md
scp -r -i emp_key skills/. root@<VPS_IP>:/docker/<C>/data/skills/<emp>/
ssh -i emp_key root@<VPS_IP> "chown -R 10000:10000 /docker/<C>/data/SOUL.md /docker/<C>/data/skills/<emp>"
```
(Back up the stock SOUL.md first: `cp data/SOUL.md data/SOUL.md.bak`.)

### 2. Wire the model — REQUIRED, image ships none
**Brain = Claude (default). Legs = best model per task.** Simplest start = Claude default:
```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> /docker/<C>/data/.env
docker exec -u hermes -e HOME=/opt/data <C> hermes config set model.provider anthropic
docker exec -u hermes -e HOME=/opt/data <C> hermes config set model.default claude-sonnet-4-6
```
**To get "best model per task" (the real goal):** add **OpenRouter** as a provider (`OPENROUTER_API_KEY` in `data/.env`) — one key unlocks Claude + GPT + Gemini + DeepSeek + 15 others. Then:
- keep Claude as `model.default` (the orchestrator brain),
- set a **fallback chain** with `hermes fallback ...` (e.g. frontier → cheaper → local) for resilience + cost,
- override per task at call time with `-m <model> --provider <p>`, or per-skill, so heavy reasoning → frontier model, routine/cheap → a fast small model, code/vision → a specialist.

Validate any key against its provider first (e.g. `api.anthropic.com/v1/messages`) so you don't wire a dead key. (`config set` also creates `config.yaml` → enables gateway auto-start on reboot.)

### 3. Connect Discord — DO THIS IN THE HOSTINGER BROWSER TERMINAL
The `hermes gateway setup` wizard is an interactive TUI that **fights SSH automation** (redraw races). Run it in **hpanel → VPS → Browser terminal** (a real TTY):
```
docker exec -it <C> hermes gateway setup
```
- Pick **Discord** → paste the **FULL bot token** → set **home channel = #brief** → accept restart.
- ⚠️ **Token truncation gotcha:** the getpass field silently drops characters on long pastes (we got 52 of 72 chars). Afterward, verify: `awk -F= '/DISCORD_BOT_TOKEN/{print length($2)}' /docker/<C>/data/.env` — a real Discord bot token is **72 chars**. If short, fix it via SSH: `sed -i 's|^DISCORD_BOT_TOKEN=.*|DISCORD_BOT_TOKEN=<full>|' data/.env`.

### 4. Make it actually respond (two settings the wizard doesn't set)
Append to `/docker/<C>/data/.env`:
```
DISCORD_FREE_RESPONSE_CHANNELS=<#chat id>,<#brief id>   # else bot ONLY replies when @mentioned
GATEWAY_ALLOW_ALL_USERS=true                            # else ALL users denied (fine: solo private server)
```

### 5. Start the gateway (persistent)
```bash
docker exec <C> sh -lc 'pkill -f "gateway run"'
docker exec -d -u hermes -e HOME=/opt/data <C> sh -lc 'hermes gateway run >> /opt/data/logs/gateway.log 2>&1'
# verify:
docker exec <C> sh -lc 'tail -20 /opt/data/logs/gateway.log' | grep -iE 'connected as|discord connected|improper|error'
docker exec -u hermes -e HOME=/opt/data <C> hermes gateway list   # should show PID, "running"
```
Because step 2 created `config.yaml`, the container entrypoint auto-starts the gateway on every reboot. (No config.yaml → it won't.)

### 6. Test in Discord
Message **#chat**: "what's my top 3 today?" — should answer in voice. If silent, see Troubleshooting.

### 7. (If the employee manages data) scoped Supabase access
Tasks/state in Supabase, but **the container has no IPv6** so it can't reach the direct PG host, and **the pooler returns tenant-not-found** → the employee MUST use the **REST API with a scoped JWT** (never the service-role key on the VPS).
1. Apply your schema migrations from a machine that CAN reach the DB (Mac, via `pg8000` direct to `db.<ref>.supabase.co` — IPv6, user `postgres`, pw = `SUPABASE_DB_PASSWORD`). Create a scoped role, e.g. `emp_app`, with grants on its schema only + RLS.
2. `grant emp_app to authenticator;` (lets PostgREST run as it).
3. Mint a long-lived JWT `{role:"emp_app", iss:"supabase", ref:"<ref>", iat, exp}` signed HS256 with the **JWT Secret** (Settings → API). **Secret is used as a raw UTF-8 string, NOT base64-decoded.** See `mint-scoped-supabase-token.py`.
4. Put in `data/.env`: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (apikey header), `EMP_DB_TOKEN` (Authorization: Bearer). REST calls to a non-public schema need `Accept-Profile: <schema>` (read) / `Content-Profile: <schema>` (write).
5. Prove scoping: the token should 200 on its own table and **403 on every other schema**.
6. Give the employee a `manage-tasks`-style skill with the exact recipe (load creds from `$HOME/.env`).

### 8. (Optional) any-terminal write helper
The `iris-add` pattern (`~/.local/bin/iris-add`) lets any Mac terminal drop a row into the live table. Clone it per employee/table.

---

## Gotchas that cost us time (the whole reason this doc exists)
1. **Bot token truncates on paste** into the getpass field (52 vs 72 chars) → always verify length.
2. **Bot only replies on @mention** until `DISCORD_FREE_RESPONSE_CHANNELS` is set.
3. **No model key** in the Hostinger image → "No inference provider configured" until you set one.
4. **`GATEWAY_ALLOW_ALL_USERS` defaults to deny-all** → you (the owner) get silently blocked.
5. **Container has no IPv6** → can't reach Supabase direct PG (IPv6-only); **pooler = tenant-not-found** in every region → REST API is the only path from the container.
6. **Scoped REST access** = mint an HS256 JWT with `role:<scoped_role>` (secret raw UTF-8, not base64) + `grant <role> to authenticator`.
7. **`gateway status` false-positive**: stray `gateway setup` processes look like a running gateway. Trust `gateway list` + the `gateway run` PID.
8. **The setup TUI fights SSH** → use the Hostinger browser terminal for `hermes gateway setup`.
9. **Secret redaction is on** — the agent scrubs secrets from output/logs; that's fine, it doesn't block tool env.

## Key paths on the box
```
/docker/<C>/data/SOUL.md            identity
/docker/<C>/data/skills/<emp>/      skills
/docker/<C>/data/.env               secrets + config (model key, discord, supabase)
/docker/<C>/data/config.yaml        model config; its EXISTENCE = gateway auto-starts on reboot
/docker/<C>/data/logs/gateway.log   gateway/Discord logs
```

## Troubleshooting "she's silent in Discord"
1. Gateway connected? `gateway.log` → "✓ discord connected" (not "Improper token" = token wrong/truncated).
2. Bot in the server + can see channels? Hit Discord API `/users/@me/guilds` and `/channels/<id>` with the bot token.
3. Message received but no reply? → channel not in `DISCORD_FREE_RESPONSE_CHANNELS` (needs @mention), or `GATEWAY_ALLOW_ALL_USERS` not set (denied).
4. Replies with "No inference provider configured" → model not wired (step 2).
5. Replies with a provider auth error → bad/expired model key.
