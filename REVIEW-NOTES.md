# Review notes · what the rebuild fixes (do not regress)

v1 was scored by a no-mercy 3-board review on 2026-06-30: adversarial board 58, Sevyn/Kim creator lens 58, plus a tooling research pass. This file records the confirmed findings and where each is fixed so a future edit does not undo them.

## Technical (adversarial board)
1. **Drive MCP cannot bridge a video binary to ffmpeg / would blow context.** → Preconditions + SETUP.md: local sync required, MCP for census only, model reads small JPG frames not the binary.
2. **`sample-frames.sh` took a local path the pipeline never produced.** → `triage-media.py` operates on the synced local folder; sample-frames.sh is the documented ffmpeg-only fallback.
3. **whisper "if installed" silently dropped talking-head quality.** → whisper.cpp in SETUP, run only on detected speech, and "scored on visuals only" printed when unavailable.
4. **Naive `select='gt(scene,0.3)'` is brittle, misses held moments, over-fires on shake, no frame cap, 3s interval misses "the good 2s".** → PySceneDetect AdaptiveDetector + aesthetic best-frame pick + frame cap; interval tightened in fallback.
5. **"Independent checks / 3 boards / blind re-score" were one model in different hats.** → Renamed SELF-checks. Real independence = fresh sub-agent re-score (no prior scores in context) + Kailin's eyes. Stated in hard rules and Stage 7.
6. **Dedupe contradicted the coverage audit.** → `assessed + deduped + auto-rejected == uploaded`, deduped/rejected get visible verdicts, best-take picked after frame review.
7. **No personal-brand pillars or voice corpus.** → `PERSONAL-BRAND.md` is a precondition, built from real posts.
8. **No trend/audio awareness.** → Stage 6 Trend Desk with WebSearch.
9. **No series/franchise thinking.** → Stage 5 series tag + `FORMATS.md` registry + campaign tracker.
10. **Tiered floors arbitrary, 95 starves Plated feed pre-launch.** → BOARDS.md floors tuned for the sprint, justified.
11. **"Drop a tier" downgraded event content out of the Plated feed.** → event-critical routes to Polish, not auto-drop.
12. **brand-lint run on raw footage (no palette).** → scoped to designed overlays/covers only; footage gets vibe/context check.
13. **HEIC unhandled.** → normalized in Stage 0 / the script.
14. **One sheet becomes scroll-hunting at 30 assets.** → Ready list capped, rest to backlog, single "do this first".
15. **Script `set -e` aborts on one bad clip; wrong whisper output path.** → per-clip try/except in the Python script.

## Strategy (Sevyn / Kim K)
16. **Grades hooks instead of building them.** → Stage 4 Hook Engineering, 3 layers per post.
17. **No franchise/series arc.** → FORMATS.md series registry + cross-day tracker.
18. **Over-indexes polish vs authentic.** → authenticity premium in RUBRIC; Board 1 can fail too-polished personal content.
19. **No trend/timing/audio.** → Trend Desk; Fan Fest flagged time-sensitive to front of order.
20. **No personal-to-tickets conversion bridge.** → conversion role per post + funnel ratio in FORMATS.md.
21. **Does not feed shoot-day planning.** → Stage 8 coverage-to-shotlist brief.
22. **Daily-only, no campaign view.** → 30-day campaign tracker in OUTPUT-TEMPLATE.
23. **Post order "easiest first" instead of momentum.** → sequence by timeliness, then series cadence, then conversion.
24. **Caption did too many jobs.** → split Hook / Caption / CTA / Audio in the template.
25. **No first-hour engagement play.** → one-line first-hour action per ready post.

## Round 2 · independent re-grade (80/100) fixes
A fresh reviewer caught that the rebuild overclaimed in the script. Fixed:
- **Aesthetic best-frame pick was vaporware.** → Now real: `triage-media.py` samples N candidates per scene and keeps the highest-scoring via a wired OpenCV proxy (sharpness+exposure+colorfulness), unit-tested (sharp 0.89 kept, blurry 0.32 / black 0.0 rejected). CLIP is optional, not required, and docs no longer push multi-GB deps for it.
- **whisper never executed.** → Now wired: extracts 16k wav, runs whisper-cli, returns transcript, only when speech_ratio > 0.15.
- **silencedetect logic inverted.** → Replaced with `speech_ratio()` that sums `silence_duration` vs clip duration (parse unit-tested = 3.0).
- **Unreadable frames slipped through as kept.** → `reject_reason` is None-safe and returns "unreadable"; guard fixed.
- **Docs-vs-code contradiction + heavy installs that bought nothing.** → SETUP split into CORE (wired, afternoon install) vs OPTIONAL (whisper) vs EXPERIMENTAL (CLIP, skip for v1).
- **Daily run too heavy for a solo founder.** → Default run is now LITE: hooks/trend-desk/sub-agent re-score run only on what will actually post that day; sub-agent re-score narrowed to Plated-feed only; full pass is opt-in "deep run". Protects the overwhelm rule.
- **Trend desk could fabricate track names.** → TRENDS.md now asks for CANDIDATES to verify in-app, forbids inventing a song title.

## Residual honest limitations (not "fixed", acknowledged)
- True independence still ultimately rests on Kailin's eyes and the one sub-agent re-score. A skill cannot fully self-certify taste.
- Trend reads are candidates to confirm in-app, not live-chart truth.
- The OpenCV aesthetic proxy ranks craft (sharp/exposed/colorful), not "is this interesting", the model still has to look at the frames for content value. It is a pre-sorter, not the judge.
- ffmpeg + the core pip installs are a real (if small) setup step; nothing runs on video until they are in.
