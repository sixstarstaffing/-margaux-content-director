---
name: plated-defaults
description: Pre-loaded Plated Circuit Vol I context. Load BEFORE invoking event-promo-content / viral-content-forge / coreyhaines social-content / openclaudia social-content. Namespaced — do NOT bleed into Sixstar / OTG / District / BrandForge contexts.
type: context
date: 2026-05-02
---

# Plated Circuit · Vol I · Default Context

Load this block at the top of any marketing/content skill prompt for Plated. If a skill cannot be parameterized, paste the relevant section verbatim into the prompt.

## 1. Locked anchor (verbatim · never paraphrase)

> **"Six countries. Six cultures. One night Atlanta plates the world."**

A 6-country immersive culinary tour. World Cup year. Atlanta hands. Substance is cultural authenticity through craft — six cultural co-creators sign off on their station. Stations rooted, not costumed.

DO NOT lead with "celebrating community" or "giving back." That over-pivot was rejected 2026-05-02.

## 2. Habitat 10% language rule (mandatory)

- Single mention per surface (1 IG caption · 1 LinkedIn post · 1 email · 1 press line)
- NEVER adjacent to anchor headline
- Phrasing: "10% of every ticket to Habitat for Humanity Atlanta."
- Factual line · not the pitch · not the lead
- Lyric (any agent-authored copy) NEVER anchors a DM/post/caption on the donation

## 3. Brand voice · Voice v2.1 banned phrases (HARD BLOCK)

Strip these before output. Zero tolerance:

`world-class` · `best-in-class` · `industry-leading` · `premier` · `elevate` · `redefine` · `reimagine` · `delight` · `exceptional` · `carefully crafted` · `unparalleled` · `seamless` · `meticulously` · `above 5 stars`

Also avoid: `curate(d)`, `bespoke`, `culinary journey`, `sensory experience`, `unforgettable`. These read AI-generated and trip viral-content-forge AI-tells detector.

## 4. Audience tiers (Marketing Plan §2)

- **Tier 1A** — Black women 30-55 · 50-60 seats · cultural decision-maker engine · the anchor
- **Tier 1B** — Cultural decision-makers across South Asian / Latine / East Asian / MENA / Italian-American · 25-30 seats · sourced via cultural-bridge community leads
- **Tier 1C** — Gen Z founder-creators 22-30 · $100K+ HHI · 10-15 seats · creator economy / tech / fashion / DTC

When writing copy, pick ONE tier per piece. Don't blend.

## 5. Toolstack (paste into image/video skill prompts)

- **Higgsfield** — AI video generation (cinematic Reels, B-roll loops)
- **Captions** — auto-captioning, talking-head Reels
- **CapCut** — multicam edit, trend audio overlay
- **Nanobanana** (Gemini Imagen 4) — moodboards, station hero stills, paste-ready 1:1 / 4:5 / 9:16
- **Daniel** (designer) — wordmark, brand graphics (NOT Nanobanana for these)

## 6. Phase calendar (5/3 → 6/12 → post-event)

| Week | Phase | Posting cadence | Content focus |
|---|---|---|---|
| Wk 1 (5/3-5/9) | Soft launch | 1 IG/day · 1 LI/wk | Founder bio · 9-grid post #1-3 · cultural co-creator intros |
| Wk 2 (5/10-5/16) | Mailer wave | 2 IG/day · Reels begin | Mailer unboxing · station teasers · Habitat single mention |
| Wk 3 (5/17-5/23) | Press push | 3 IG/day · 1 LI 2x/wk | Press kit drops · founder shoot V01-V07 · ticket reminder |
| Wk 4 (5/24-5/30) | Panic trigger window | 4 IG/day · daily LI | If <80 tix by 5/24 → drop to 150 cap publicly |
| Wk 5 (5/31-6/6) | Final push | 6 IG/day · daily Stories | Day-of teasers · station moodboards · sponsor thank-you |
| Wk 6 (6/7-6/12) | Event week | 8 IG/day · live Stories | T-5 to T-0 countdown · day-of capture |
| Post (6/13+) | Recap | 1 IG/day decay | Vol II teaser · sponsor recap deck · Habitat check delivery |

## 7. Vol I event facts (for press / captions / hooks)

- **Date:** July 16, 2026
- **Venue:** Ventanas Atlanta (75% locked · expect public confirm post-countersign)
- **Capacity:** 200 (panic trigger to 150 if <80 sold by 5/24)
- **Tiers:** $175 GA · $215 Passport · $275 VIP (rooftop access)
- **Stations:** Japan · Morocco · Mexico · India · Italy (rooftop) · USA (rooftop)
- **Food:** All 6 stations cooked by J.C. (District Catering)
- **Habitat:** 10% of every ticket to Habitat for Humanity Atlanta

## 8. Internal-only (NEVER public · NEVER in Lyric output)

These live in `INTERNAL-COMPASS.md` — DO NOT auto-load into public skill prompts:
- "Above 5 stars"
- "IYKYK"
- "Institutional trust"
- Sponsor revenue projections
- Pricing-defensibility internal math

If a skill is generating PUBLIC copy (caption, email, post), this section MUST be excluded.

## 8b. Brand mark system (LOCKED 2026-05-06)

**NEVER generate or set type for the lettermark. NEVER use Georgia/Times-italic "PC" placeholder.** Use canonical files only.

### The system
- **Tier 1 · House mark · Concept A · Pineider Slug v5** — italic Bodoni P + upright Centaur C + circular period. Forever. Every Vol. Every always-on surface.
- **Tier 2 · Vol I sub-mark · Concept C · Fili Florentine v5** — fat hand-letter P + swash + hairline copperplate C. **Vol I ONLY.** Retires after Vol I event cycle.
- **Tier 2 · Vol I monomark** — P + diamond, P-only mark for Vol I small-format (favicon, social avatar fallback, hot-foil interior stamp).
- **Wordmark primary** — "PLATED CIRCUIT" Bodoni Bold uppercase, wide letterspacing. Letterhead, sponsor brief, press kit, formal pitch.
- **Wordmark italic** — *Plated Circuit* Bodoni Book Italic, title case. Intimate surfaces, interior pages.

### Canonical file locations
- Logo folder: `~/Desktop/plated-circuit-logos/`
  - `01-house-mark-A-pineider-slug/` (Tier 1 forever)
  - `02-vol-I-sub-mark-C-fili-florentine/` (Tier 2 Vol I only)
  - `03-vol-I-monomark-C-fili-mono/` (Tier 2 Vol I small-format)
  - `04-wordmark-plated-circuit/01-primary-uppercase-roman/`
  - `04-wordmark-plated-circuit/02-alt-italic-titlecase/`
  - `05-passport-cover-lockup/` (production foil composite)
- Surface decision authority: `~/aios-mac/terminals/t17c-lettermark-A-v2/BRAND-MARK-SYSTEM.md`

### Per-mark folder structure
Each mark folder has: SVG (black/gold/cream), `transparent-black/` + `transparent-gold/` (256/512/1024/2400 PNG), `on-walnut/` + `on-cream/` + `on-black/` (PNG+JPG, 600/1200/2400), `README.md`.

### Sanctioned colors only
- Real black: `#0a0a0a`
- Champagne gold: `#D4AF37`
- Cream: `#f4ebd6`
- Dark walnut: `#341E16`

No other color recolorings. No CSS gradients on the mark itself.

### Surface decision quick-pick
- Always-on / forever / merch / favicon / sig / press kit / sponsor brief → **A house mark**
- Vol I passport interior / Vol I mailer / Vol I menu / Vol I event signage → **C Vol I sub-mark**
- Vol I small format (favicon during Vol I season, hot-foil interior stamp) → **Vol I monomark**
- Letterhead / formal print / signage / business card → **Wordmark primary** (paired with house mark)
- Passport cover production hot-foil → use `05-passport-cover-lockup/passport-cover-lockup-vol-I-gold.svg`

### When in doubt
Read `BRAND-MARK-SYSTEM.md` (full surface decision table). If surface isn't listed there, default to A house mark + flag for Kailin.

## 9. How to invoke

If the skill accepts a system prompt or context block, paste sections 1-7 above. If not, prepend to the user prompt:

```
[PLATED CONTEXT — load before responding]
Anchor: Six countries. Six cultures. One night Atlanta plates the world.
Voice: strip {world-class, best-in-class, premier, elevate, redefine, reimagine, delight, exceptional, carefully crafted, unparalleled, seamless, meticulously, above 5 stars, curated, bespoke, culinary journey}
Habitat rule: single mention per surface · "10% of every ticket to Habitat for Humanity Atlanta" · never adjacent to anchor
Tier focus: [pick 1A / 1B / 1C]
Phase: [pick week from calendar]
[/PLATED CONTEXT]

[user request here]
```
