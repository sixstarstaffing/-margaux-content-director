# Margaux · BrandForge / Plated Handoff (save to memory + process)

**Date:** 2026-07-01 · **Status:** LIVE and validated (tested end-to-end from Discord).
**For:** the BrandForge / Plated-Command terminal. Read this, save the key facts to
memory, and sync your org chart + flow. This closes the loop everyone's been waiting on.

---

## What Margaux is (one sentence)
Margaux is the **Content Director**: she watches ALL of a day's raw footage/photos and
decides **what to post, where, and in what order** (personal-first), so good real content
never sits ignored again (the origin failure: the 6/23 lifestyle batch that got uploaded
and forgotten).

## Her ONE job (keep it this clean, she's a contractor with a single lane)
Triage the day's **real** content from a Drive folder → route each asset to the right home
(Personal IG / Personal TikTok / Story / Plated feed / POLISH-then-post / kill/dupe) →
deliver a short digest to Kailin + a full routing sheet for the editor. **That's it.**

She does **NOT**:
- create/edit the posts (that's **Studio**)
- publish/schedule (that's **Amplifier / Blotato**, always approval-gated)
- plan the shoot (that's **GiGi**)

She's the guardrail on two sides: nothing good gets ignored, and nothing sloppy gets
routed forward. Real content is king; AI is polish only.

---

## Where she falls on the org chart
```
GiGi  (Planning engine · department head)
  └── Margaux  (Content Director · contractor/worker, reports to GiGi)   ← ONE job
        │  triage + route the day's real footage
        ▼
Studio (Create)  →  QA gate / portal  →  Amplifier + Blotato (Distribute, gated)
```
Margaux is a **contractor under GiGi**. GiGi plans the shoot; Margaux triages what actually
got filmed and hands the approved picks forward. She is the **front door** the 6/30
BrandForge board flagged as the missing piece between "shoot planned/filmed" and "Studio
creates." Her internal roles were renamed (Scout→Sweeper, Producer→Desk) so they don't
clash with BrandForge's own Scout/Producer contractors.

## The end-to-end flow (how she plugs in)
```
GiGi plans shoot → film it → drop clips + one-line notes in the Margaux Daily folder
   → MARGAUX triages + routes (personal-first)
   → digest to Kailin in Discord (full sheet saved for the editor)
   → Kailin approves
   → Studio makes the posts → QA gate → Amplifier / Blotato publishes (gated, never auto)
```

---

## How she runs today (no terminal needed, fully hosted)
Hosted on the **Hermes VPS** (hermes-agent container, repo at `/root/margaux-test`), same
stack pattern as Iris. Two live triggers, both deliver the digest to Discord:

1. **Drop-and-forget (Option A):** Kailin drops clips + notes in the "Margaux Daily
   Content" Drive folder. Host cron runs her at **7 AM + 10 PM ET**, reads the folder via
   the Drive API, processes, digests. Empty folder = stays quiet.
2. **On-demand Discord bot (Option B):** Kailin posts a Drive folder link + the words
   **"content delivery"** in Discord (`Margaux#6944`, in Kailin's server). The bot runs
   that folder and replies with the digest. A host watchdog keeps the bot alive.

## BrandForge integration (what's wired vs pending)
- **Wired now:** delivery via Discord digest + full routing sheet in `sheets/` on the VPS.
- **Pending (WS6):** her routing decisions writing into the shared **Supabase** DB so the
  Studio/QA/portal read them directly (the export step: Supabase → `content-data.js` /
  `qa-items.json`, portal reads the JS, not Supabase live). Not built yet. Until then,
  the handoff to Studio is the routing sheet + Kailin's approval. **This is the next
  integration task if BrandForge wants Margaux's output in the portal.**

## Save these to memory
- Margaux = Content Director, LIVE, hosted on Hermes VPS, contractor under **GiGi**, one
  job = triage + route the day's real footage (personal-first).
- Two triggers: cron 7am/10pm on the Margaux Daily folder + Discord bot ("content
  delivery" + link). Digest → Discord.
- She does not create, publish, or plan. Studio creates, Amplifier/Blotato publishes
  (gated), GiGi plans.
- Repo: https://github.com/sixstarstaffing/-margaux-content-director (brain-spec = the
  skill files). Skill also lives at `~/.claude/skills/content-director/`.
- Next BrandForge task = WS6 Supabase export so her picks land in the portal.

## Standards she already enforces (don't re-litigate)
Personal-first routing · real content is king / AI is polish only · NO em-dashes anywhere ·
brand-guard on any Plated asset · 3-board ship gate · the **firewall** (never publicly
reveal the Collective / chef-accelerator; the only public framing is "guest-voted winner
crowned live").

We did it. She's real, she's live, she has one clean lane.
