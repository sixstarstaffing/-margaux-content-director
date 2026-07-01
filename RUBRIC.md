# Scoring Rubric · three axes + authenticity premium + reject gates

Score every asset on three independent axes. They do not collapse into one number before routing. A clip can be 40 Technical / 95 Content and be gold (that is a TikTok, not a feed post).

## Pre-filter reject gates (Stage 1, before scoring)
Auto-flagged by `triage-media.py`, treated as REJECT, not rank. Held with a reason, rescuable if the moment is irreplaceable:
- **Blur** · OpenCV Laplacian variance below threshold (≈100, tune per camera).
- **Exposure** · luma histogram crushed (blacks) or blown (whites) beyond a fraction of pixels.
- **Shake** · optical-flow jitter variance too high for a usable take.

## Axis 1 · Technical (decides feed vs raw, never the kill switch alone)
- **90 to 100** · sharp, clean light, framed well, clear audio. Feed-ready.
- **70 to 89** · solid, minor issues. Feed with light polish or native as-is.
- **50 to 69** · watchable but rough. Raw platforms only (TikTok, Story).
- **Below 50** · unusable on craft. Held unless the moment is irreplaceable.

## Axis 2 · Content value (most important)
Is there a reason to stop scrolling. Where Fan Fest / mic-buying / networking / errands live or die.
- **90 to 100** · strong hook, real story, genuine emotion, or B-roll that elevates another post. Lead content.
- **70 to 89** · clear value, a moment. Good supporting post.
- **50 to 69** · filler, needs a strong hook/edit to earn a slot.
- **Below 50** · nothing happening. Kill with a reason.

## Axis 3 · Brand fit (which page, as a lean)
- **Plated-specific** · about the event/food/Plated world, on brand. Earns Plated.
- **Either** · fits both. Personal-first sends it to personal unless Stage 7 Board 2 finds a real Plated reason.
- **Personal-specific** · Kailin as creator, lifestyle, behind-the-scenes, journey.
- **Off-brand for both** · note and hold, do not force-fit.

## Authenticity premium (the v1 fix)
Polish is a ROUTING signal, not a status rank. Over-produced personal content underperforms.
- Raw, confessional, founder-life footage (mic-buying, errands, talking-to-camera, Fan Fest) **can score 95 on the personal and TikTok tiers**. Do not mark it down for being unpolished, that IS the aesthetic.
- **Mark DOWN** personal/TikTok content that is too polished, ad-like, or brand-stiff. Board 1 can fail it for this.
- The premium does NOT apply to the Plated FEED, which stays curated. It applies to personal feed, TikTok, Reels, Stories.

## Handoff to routing
- High Technical + High Content → feed (page by Brand fit, personal-first on a tie).
- Low Technical + High Content → TikTok/Reels (raw is native, do not waste it).
- High Technical + Low Content → Story or B-roll for a future edit, not a standalone feed post.
- Low + Low → Kill with a reason.
