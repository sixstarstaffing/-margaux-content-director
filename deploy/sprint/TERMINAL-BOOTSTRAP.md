# Terminal Bootstrap · run this FIRST in every contractor terminal

Do this before touching any work. It is the guard against the POZD Sprint 3 failure (terminals reaching for Mac-local files).

## 1. Clone the repo (never work from a Mac path)
```
git clone <repo-url> margaux-content-director
cd margaux-content-director
```
Everything you need is IN this clone: the brain spec (SKILL.md + reference md), the pipeline (`scripts/`), the schema (`deploy/schema/`), the API contract (`deploy/API-CONTRACTS.md`), the vendored voice (`deploy/voice/`), the playbook (`deploy/playbook/`). If a task seems to need a file on Kailin's Mac, STOP and report it, that is the exact bug this sprint exists to avoid.

## 2. Read your brief
- `BUILD-SPRINT.md` (the command center + your workstream row)
- `MARGAUX-DEPLOY.md` (the architecture)
- `deploy/API-CONTRACTS.md` if you build WS2/WS3/WS4

## 3. Load secrets from the shared store (never hardcode, never a Mac file)
Copy `deploy/.env.template` to `.env` and fill from the shared secret store (n8n credentials / Supabase Vault / the WS0 handoff). `.env` is git-ignored, never commit it.

## 4. Report in
```
python deploy/sprint/report.py --ws WS<n> --status started --pct 0 --msg "on it" --push
```
This posts to Kailin's #build-updates channel, relays to Command Center, logs to `logs/TERMINAL-WS<n>-LOG.md`, and pushes it so Command Center can roll it up.

## 5. Work the acceptance criteria in your BUILD-SPRINT row
Report a `milestone` at each real checkpoint, `blocked` the moment you are stuck (Kailin sees blockers immediately), and `done` only when your acceptance test passes on a fresh clone with real (test) services, no Mac file touched.

## Critical-path gate
If you are WS2/WS3/WS4/WS5/WS6/WS7: do NOT start until WS1 (the Supabase schema) is merged. The schema is a frozen contract, building against a moving one is how terminals collide. Command Center announces when WS1 is frozen.
