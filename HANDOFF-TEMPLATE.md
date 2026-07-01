# HANDOFF TEMPLATE · Margaux → GiGi / Vlog-Video Employee

When Margaux finishes triage and a cluster of clips wants to become ONE video (a vlog, a process piece, a story arc) rather than separate posts, she outputs a handoff in THIS shape. The assembler (GiGi or a dedicated vlog-video employee) executes it. This is the spec that employee's skill is built from.

Margaux triages and hands off. She does not edit video. The assembler builds. Kailin records only what the Record List asks for.

## When to produce a handoff (vs standalone posts)
- Produce a **handoff** when 3+ approved clips share a through-line (a build, a day, a make-of, an arc). One story = one video.
- Produce **standalone post specs** (the normal routing sheet) for one-off clips.
- A cluster can do BOTH: the handoff is the vlog, the routing sheet lists the same clips as spinoff posts for other days.

## The handoff format (fill every section)

### 1 · Concept + arc
One line: what the video IS and the through-line. Name the format (vertical vlog Reel + TikTok / horizontal YouTube / carousel). State the page (personal-first) and that it's firewall-safe.

### 1b · Runtime budget (REQUIRED, this is what breaks briefs)
State an HONEST target runtime and publish a **timecode table whose beat durations literally sum to it** (e.g. 0:00-0:03, 0:03-0:06...). A tight 30-40s usually beats a padded 70. Rule of thumb: **VO length ≈ visual length** (a 30s VO needs ~30s of holds). If the beats don't sum to target, the brief is wrong, add real beats (talking-head, a wide "all 200" reveal, a time-lapse) or lower the target. Do not ship a runtime number the cut can't hit.

### 1c · Hook + event context (REQUIRED)
- **Hook in the first 1-2 seconds:** lead with the strongest beat (the stakes, a number), never a throat-clear like "okay so this is my week." Put the real hook FIRST, add a **re-hook around second 7** so the middle montage doesn't sag. Output **2 hook variants (A/B)** to test.
- **Event context:** a personal-page vlog reaches cold viewers, so at least one burned line must tell them what to act on (date + city + what-it-is), e.g. `july 30 · atlanta`. Firewall still holds (never name the accelerator), but "pretty BTS with no event info" drives admiration, not attendance.

### 2 · Director's shot list (director-to-editor detail, one block per shot)
Per shot give: **SOURCE** clip (real filename) · **IN-POINT** (where to start, skip dead air, "mid-action, blade already moving") · **FRAMING + ACTION** (what's in frame, what happens) · **CUT** (hold time + transition) · **ON-SCREEN TEXT** · **VOICE** line over it. Cold-open on the strongest reveal, craft/middle beats, payoff, CTA. This must read like a director handing an editor a cut list, not a summary.

**CRITICAL video-vs-photo rule (mark each shot VIDEO or PHOTO):**
- **VIDEO** = HOLD, let it breathe, 3-4s.
- **PHOTO** = FLASH in and out fast, under ~1.5s, ALWAYS with a tiny push-in (Ken Burns) so it's never static. Never hold a still photo like it's video, that reads as a slideshow and kills vlog momentum.

Call out b-roll/cutaway clips and an explicit DO-NOT-USE list (receipts, dupes, unusable).

### 3 · Voiceover script (PERSONAL VLOG voice, NOT ad copy)
Write it the way she actually TALKS in a vlog: casual, conversational, first-person, warm, with natural fillers ("okay so," "honestly," "oh and"). It should sound like she picked up her phone and showed you, not like polished marketing copy. One-loose-take energy. Numbered lines mapped to shots ("(over 3-4)"). This is what Kailin records. No em-dashes in captioned text. If a line depends on footage/audio Margaux couldn't confirm, mark it a suggestion, never invent dialogue.

### 4 · Record list (the ONLY things Kailin shoots)
Bullet exactly what she must capture: the VO lines, any missing hero/payoff shot, and the highest-value gap Margaux found (usually a 15-sec talking-to-camera confessional). Keep it to the minimum.

### 5 · Look / music / pacing
Grade (warm highlights, lifted shadows, slight desaturation, brass/cream/walnut, never clinical). Text style (brass/cream, 2 lines max, burned in frame 1). Music (quiet warm cinematic, let craft sounds breathe). Pacing (hold each beat 3-4s, one quiet moment beats five busy ones).

### 6 · Standalone spinoffs
The same clips as separate posts for days without the full vlog, pulled from the routing sheet.

### 7 · Assembler notes (for GiGi)
- **Format-decision layer:** GiGi confirms carousel vs Reel vs vlog. Margaux recommends, GiGi decides.
- **Firewall:** tease the SHOW, never the Collective/cohort/accelerator. Only "a guest-voted winner crowned live" is public.
- **Voice rules:** no em-dashes, strip hard-block words (curated, elevate, unforgettable, seamless, culinary journey), anchor verbatim where it lands, ONE CTA (keyword system).
- **Anchor:** "Six countries. Six cultures. One night Atlanta plates the world."

### 8 · Production layer (REQUIRED so an editor/skill can execute deterministically)
The creative brief alone can't be cut without guessing. Every handoff also specifies:
- **Transitions:** name the cut between every beat (hard cut / match cut / whip / J-L cut so VO overlaps picture). "Hard cut" once is not enough.
- **Aspect + safe zones:** 1080×1920 vertical, captions between ~15% and ~78% of height (clear of the platform buttons + bottom bar), center-weighted.
- **Audio bed:** VO is the spine; music ~-18dB ducking to ~-24dB under VO; name WHICH 1-2 clips let nat sound poke through and mute the rest.
- **Captions:** lowercase (reads more personal than title-case), bold sans, brass/cream with a soft dark stroke, appear frame 1 of their beat and hold the whole beat (state in AND out), inside the safe zone.
- **Music source:** actionable, TikTok Commercial Library / Epidemic / Artlist, a BPM range (~80-95 for warm), cut to end on the CTA. Not "quiet warm instrumental."
- **Export:** 1080×1920, 30fps, H.264, loudness ~-14 LUFS.
- **Cover/thumbnail frame** + cover text.
- **Payoff fallback:** if a to-be-shot hero doesn't get filmed, name an existing-clip substitute so the video still ships.
- **Platform variants:** note TikTok vs Reel vs Shorts caption-safe differences if they matter.

### 9 · Structured ingest (for the vlog-video employee skill)
A skill shouldn't re-parse prose. Margaux hands the picks as structured data per clip: `{clip_id, VIDEO|PHOTO, in_point, suggested_seconds, on_screen_text, vo_line, role}`, plus the runtime target and event-context line. The assembler renders the cut from that; the human-readable handoff is generated from the same data.

## Worked example (the passport vlog)
The first real handoff Margaux produced, "Making the Passports," is the reference implementation of every section above (the full readable version was delivered to Kailin as `Margaux-Vlog-Handoff-Passports.html`). Arc: rush-order arrives → Gigi hand-finishes → payoff. Cold-open on the unboxing, craft montage (foil cut, wrap, hand-sew, assembly, favor tins, material test), payoff on a finished passport, CTA "Comment STORY." 7 VO lines for Kailin to record + one finished-passport hero shot + an optional talking-to-camera intro.

## Next build
A dedicated **vlog-video employee skill** takes this handoff as input and outputs the assembled edit (cut list for CapCut/InVideo, burned captions, the grade, the music). Until it exists, GiGi or a human editor executes the handoff by hand. Margaux's job ends at this document.
