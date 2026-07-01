# Voice · one source of truth (shared with GiGi)

This is content-director's voice file. It does NOT restate the Plated voice, it POINTS at the same source GiGi should read, so the two never drift. Seeded 2026-06-30 from Kailin's real posts, not invented.

---

## A. PLATED voice → load the shared authority (do not duplicate)
The canonical Plated voice rules are **vendored into this repo at `deploy/voice/plated-defaults-CONTEXT.md`** (machine-independent, no Mac path). In production they live in the Supabase `voice_profile` table, GiGi and Margaux read the same source. The Mac skill `~/.claude/skills/plated-defaults/CONTEXT.md` is the upstream to sync FROM, not a runtime dependency. Load sections 1 to 4 before writing any Plated caption:
- **§1 Anchor (verbatim, never paraphrase):** "Six countries. Six cultures. One night Atlanta plates the world."
- **§2 Habitat rule:** one mention per surface, never adjacent to the anchor, never the lead.
- **§3 Voice v2.1 HARD BLOCK (strip before output):** world-class, best-in-class, industry-leading, premier, elevate, redefine, reimagine, delight, exceptional, carefully crafted, unparalleled, seamless, meticulously, above 5 stars, curate(d), bespoke, culinary journey, sensory experience, unforgettable.
- **§4 Tiers:** pick ONE per piece (1A Black women 30-55 anchor · 1B cross-cultural decision-makers · 1C Gen Z founder-creators).

> STALE-FACT WARNING: `plated-defaults/CONTEXT.md` §7 still says July 16 / Japan / 200 cap / $175-275. Those are OUT OF DATE. Use the CURRENT facts below. (Flagged for Kailin to refresh at the source so GiGi stops broadcasting dead facts.)

### Current Plated Vol I facts (use these)
- **Date:** Thursday, July 30, 2026 · **Venue:** Ventanas Rooftop, Atlanta
- **Stations (Japan CUT):** France → Morocco → Mexico → India → Italy → USA (rooftop/helipad finale)
- **The mechanic:** guests carry a passport, vote at every station, one chef crowned live under the skyline. Every cocktail has a zero-proof version.
- **Habitat:** 10% of every ticket to Habitat for Humanity Atlanta.

## B. KAILIN personal voice (the founder-in-public brand)
Locked self-description from her own posts: **"restrained, cinematic, a little secret. Luxury by withholding."** Personal page uses **"I"** (founder voice); Plated page uses **"we."**

### Positioning
A staffing-company founder who spent years as the invisible hand at other people's events, now building one night that pulls Atlanta's unseen kitchen hands into the middle of the room. Building Plated Circuit in public.

### Audience
Atlanta culture-forward women 25-45, aspiring founders, food and event lovers, future Plated guests. Drives follows to @platedcircuit.

### Content pillars (tag every personal clip to one)
1. **Founder-in-public** · the real build of Plated, wins and mess, "the thing I've been quietly making."
2. **Behind-the-scenes hands** · the people and craft most events hide.
3. **Atlanta lifestyle** · the city, networking, events, Fan Fest, the scene.
4. **The come-up / mindset** · the personal arc, what nobody tells you about building this.

### Voice do / don't
- **Sounds like:** restrained, cinematic, intimate, a little secret. Plain strong sentences. Lets scarcity and craft speak. Real, not hype.
- **Never:** em-dashes or en-dashes (hard rule), the Voice v2.1 banned words above, hype/influencer filler ("so excited to share"), hashtag soup, anything that reads like a brand account instead of a person. No "cheap / discount / buy now."
- **Signature moves:** open with a quiet confession or reframe ("You don't eat six countries. You travel to them."), withhold rather than oversell, one clean CTA.

### Real caption samples (her actual voice, the corpus)
```
I'm spending my whole summer on a dinner party most people will never get into.

Here's why. I run a staffing company. I've spent years as the person behind the
scenes at other people's events, and the whole time one thing kept sitting with me:
Atlanta feeds the world every single day, in kitchens nobody sees.

So I'm building one night that pulls those hands into the middle of the room.
Six countries. Six cultures. One night Atlanta plates the world. Cooked by the
people who actually carry it, on one rooftop.

It's called Plated Circuit. This is the thing I've been quietly making.
Follow along → @platedcircuit
```
```
You don't eat six countries. You travel to them.

Plated Circuit isn't a tasting menu and it isn't a dinner, it's an immersive
passage. The rooftop transforms around you, country by country.
```
Point `social-content` / `event-promo-content` at THESE, never generic best-practice.

## C. The conversion bridge (personal → Plated)
Personal grows the audience, Plated converts it. Every personal post in the 30-day window carries a funnel role (FORMATS.md 70 build / 20 soft / 10 hard). Link-in-bio: the giveaway entry / ticket page. CTA phrasings she actually uses: "follow along → @platedcircuit", "link in bio", giveaway "tag two people you'd bring."

## D. Sync architecture (why this stays in lockstep with GiGi)
- **Plated voice** = single source `plated-defaults/CONTEXT.md` §1-4. Both GiGi and content-director read it. GiGi currently carries its own copies (`08-GIGI-PLATED-BRAIN.md`, deployed `content-data.js` brand_voice, n8n webhook), those should be repointed at the shared file so they cannot drift (flagged for Kailin).
- **Personal voice** = this file's section B, the home for Kailin's own voice. Keep it seeded from her real posts as the corpus grows.
