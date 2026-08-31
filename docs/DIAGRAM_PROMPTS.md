# Diagram Prompts for the ISIH Deck (v2 — light mode, editorial register)

Two copy-paste prompts. Both depict the **full SIH product** (the December
vision), pitched at ISIH depth.

## Design register — read this before generating

The target style is a **broadsheet editorial infographic** — the kind printed in
*The Economist* or the *Financial Times*: clean, factual, confident, quietly
beautiful. It is *not* a children's illustration and *not* a corporate slide.

Concretely this means: thin precise lines, flat restrained colour, real map
geometry, generous white space, technical annotation. **No glows, no rounded
bubbly shapes, no cartoon icons, no gradients on text, no drop shadows, no 3D.**

Simplicity comes from *ruthless removal of words*, not from childish visuals.

### Shared palette (light mode)

| Role | Hex | Use |
|---|---|---|
| Page | `#F7FAFB` | Background |
| Ocean | `#DCE9F2` | Open water |
| Sea ice | `#FFFFFF` → `#9FC7DB` | White = dense ice, pale blue = thin |
| Land | `#E8EDF0` w/ `#C0CFD7` outline | Antarctic continent |
| Route (safe) | `#0E7A4A` | The recommended path |
| Blocked | `#C0392B` | Impassable, used sparingly |
| Caution | `#C97B1E` | Uncertainty, hazard |
| Structure | `#1B6478` | Arrows, rules, frames |
| Text primary | `#12303D` | Headings, labels |
| Text secondary | `#5A7280` | Captions |

### Typography

Headings **Inter Tight SemiBold** (or Söhne / Suisse Int'l). Labels **Inter
Medium**. Captions **Inter Regular**. Numerals tabular. Never a rounded
geometric display face — those read juvenile at this size.

### Verified facts (do not alter these)

All coordinates verified against Wikipedia / NCPOR, 2026-08-31. Every station
below lies in the 0°E–90°E sector the map covers.

| Station | Country | Lat | Lon |
|---|---|---|---|
| Troll | Norway | 72.01°S | 2.54°E |
| **Maitri** | **India** | **70.77°S** | **11.73°E** |
| Novolazarevskaya | Russia | 70.78°S | 11.82°E |
| **Dakshin Gangotri** | **India** (buried 1990) | **70.08°S** | **12.00°E** |
| Princess Elisabeth | Belgium | 71.95°S | 23.35°E |
| Syowa | Japan | 69.00°S | 39.58°E |
| Mawson | Australia | 67.60°S | 62.87°E |
| **Bharati** | **India** | **69.40°S** | **76.19°E** |
| Zhongshan | China | 69.37°S | 76.37°E |
| Progress | Russia | 69.38°S | 76.39°E |
| Davis | Australia | 68.58°S | 77.97°E |

**Cape Town** (departure port): 33.9°S, 18.4°E.

**Two facts that carry the pitch:**

1. **Maitri and Novolazarevskaya are ~4 km apart** in the Schirmacher Oasis.
2. **Larsemann Hills is an international cluster** — Bharati, Zhongshan (China)
   and Progress (Russia) sit within ~20 km of each other.

India's bases are not isolated. The same sea ice closes the approach for every
nation in these clusters, so a system that solves this serves the region, not
only India. Say that in the pitch; the map should make it self-evident.

**Maitri to Bharati is ~64° of longitude — roughly 2,450 km** — and both must be
served in one austral summer. That distance is why routing is hard.

## PROMPT 1 — The mission map (right half of a slide)

> Create a high-resolution editorial infographic map, aspect ratio **8:9**
> (portrait), rendered at **3000 × 3375 pixels**, to occupy the right half of a
> 16:9 presentation slide. Light mode. Style reference: a data-driven map graphic
> from The Economist — precise, restrained, elegant. Not an illustration.
>
> **Background:** `#F7FAFB`. Ocean `#DCE9F2`. Antarctic continent `#E8EDF0` with
> a thin `#C0CFD7` coastline.
>
> **Projection and framing:** a polar-stereographic view centred on the Indian
> Ocean sector of Antarctica, spanning roughly 0°E to 90°E and 30°S to 72°S.
> Southern Africa appears at the top-left with Cape Town on its coast; the
> Antarctic coastline curves across the bottom of the frame.
>
> **Sea ice:** a broad band hugging the Antarctic coast, drawn as a soft gradient
> from white `#FFFFFF` (dense ice near the coast) to pale blue `#9FC7DB` (thin
> ice at the outer edge), fading into open ocean. Give it a natural, irregular,
> satellite-derived edge — never a smooth arc.
>
> **Mark every research station listed below.** Two visual tiers, so India's are
> unmistakable while the international context is still visible:
>
> **TIER 1 — India's stations.** Large solid `#0E7A4A` dots, 22 px, each with a
> thin leader to a label in Inter SemiBold `#12303D`, all-caps, plus a caption
> in `#5A7280`:
> - **MAITRI** (70.77°S, 11.73°E) — caption: *"India · 1989"*
> - **BHARATI** (69.40°S, 76.19°E) — caption: *"India · 2012"*
> - **DAKSHIN GANGOTRI** (70.08°S, 12.00°E) — drawn as a hollow `#5A7280` ring,
>   not filled. Caption: *"India's first base · buried in ice 1990"*
>
> **TIER 2 — other nations' stations.** Small hollow `#5A7280` dots, 9 px, with
> labels in Inter Regular 60% the size of Tier 1, in `#5A7280`. Name only, with
> the country in parentheses. No captions:
> - Troll (Norway) — 72.01°S, 2.54°E
> - Novolazarevskaya (Russia) — 70.78°S, 11.82°E
> - Princess Elisabeth (Belgium) — 71.95°S, 23.35°E
> - Syowa (Japan) — 69.00°S, 39.58°E
> - Mawson (Australia) — 67.60°S, 62.87°E
> - Zhongshan (China) — 69.37°S, 76.37°E
> - Progress (Russia) — 69.38°S, 76.39°E
> - Davis (Australia) — 68.58°S, 77.97°E
>
> **Cape Town** (33.9°S, 18.4°E) — solid `#12303D` square marker, label
> `CAPE TOWN`, caption *"Departure port"*.
>
> **Two station clusters must read as clusters, not as overlapping clutter.**
> Where stations sit within a few kilometres of each other, draw the individual
> dots at true position but run their leader lines to a single small grouped
> label block set slightly away from the coast:
>
> - **Schirmacher Oasis** — Maitri, Novolazarevskaya and Dakshin Gangotri sit
>   within a few km near 11.7–12.0°E. Group-label these three together.
> - **Larsemann Hills** — Bharati, Zhongshan and Progress sit within ~20 km near
>   76.2–76.4°E. Group-label these three together.
>
> Inside each grouped block, India's station name is `#12303D` SemiBold and the
> others are `#5A7280` Regular, so the eye finds India first.
>
> **Two voyage paths**, both starting at Cape Town, drawn as solid `#0E7A4A`
> lines 5 px wide, curving realistically around the densest ice rather than
> cutting through it:
> - a shorter path running almost due south to **Maitri**
> - a much longer path sweeping south-east to **Bharati**
>
> **Reading order — this is critical.** The viewer's eye must start at Cape Town
> and travel outward with no ambiguity. Achieve this with:
> - a filled `#0E7A4A` circle numbered **1** placed directly on Cape Town
> - a numbered **2** on Maitri, a numbered **3** on Bharati
> - directional chevrons spaced along each route line, pointing away from Cape
>   Town
> - the two route lines being the highest-contrast elements on the page, so they
>   are seen before any text
>
> **One measurement annotation**, a thin `#1B6478` double-headed arrow spanning
> between the two Indian coastal clusters, labelled in small caps:
> `2,450 km APART · BOTH SERVED IN ONE SUMMER`
>
> **One hazard annotation**, a short `#C97B1E` leader pointing into the densest
> white ice near the coast: *"Sea ice closes the approach — and moves every day"*
>
> **Title block**, top-left, over the ocean, generous margin:
> Heading in Inter Tight SemiBold `#12303D`, 2 lines: **"One ship. One summer.
> Two stations 2,450 km apart."**
> Subtitle in `#5A7280`: *"India's bases share this coast — and this ice — with
> six other nations."*
>
> **Total word count on the entire image must not exceed 95 words**, station
> names included. Every label earns its place or is removed.
>
> **Do not include:** a compass rose, a decorative border, latitude/longitude
> gridlines, ships drawn as illustrations, national flags, icons, glows, or any
> 3D effect. Flat, precise, cartographic.

---

## PROMPT 2 — System architecture (full slide)

> Create a high-resolution technical system-architecture diagram, aspect ratio
> **16:9**, rendered at **3840 × 2160 pixels**, filling a presentation slide.
> Light mode. Style reference: an architecture figure from a well-designed
> engineering whitepaper — crisp, factual, generously spaced. Not a corporate
> slide, not an illustration.
>
> **Background:** `#F7FAFB`. All boxes are white `#FFFFFF` with a 1.5 px
> `#C0CFD7` border and a 4 px corner radius — square-ish, not bubbly. All arrows
> `#1B6478`, 2 px, with small solid triangular heads.
>
> **Structure: three horizontal bands.** The essential visual idea is that the
> top band is wide, the middle band is a *narrow pinch*, and the bottom band is
> wide again — an hourglass. A viewer must grasp that separation before reading
> any label.
>
> ### BAND 1 — top, ~42% of height
>
> Band label, small caps, left-aligned above the band, `#5A7280`:
> `ASHORE — HEAVY COMPUTING, FULL BANDWIDTH`
>
> Five boxes, left to right, joined by arrows:
>
> 1. **`DATA`** — inside, a compact vertical list in `#5A7280`, one per line:
>    `Satellite ice` / `Ocean forecast` / `Weather` / `Seafloor depth` /
>    `Iceberg positions`
> 2. **`QUALITY CONTROL`** — caption: *"Remove sensor errors"*
> 3. **`AI ICE FORECAST`** — the visual anchor of this band, drawn slightly
>    larger. Inside: five thin horizontal bars stacked in `#1B6478`, representing
>    five models, converging into one bar. Caption: *"5 models · forecasts 7 days
>    ahead"*. Immediately to its right, a small `#C97B1E` box labelled
>    `UNCERTAINTY` with caption *"How sure are we?"*
> 4. **`HAZARD MAP`** — inside, three thin stacked layers labelled `Ice`,
>    `Icebergs`, `Depth`
> 5. **`ROUTE SEARCH`** — caption: *"Finds the safest fast route"*
>
> ### BAND 2 — middle, ~12% of height — the pinch
>
> Draw this band visually narrow and centred, clearly constricted relative to the
> bands above and below.
>
> One capsule, `#0E7A4A` fill, white text, centred: **`VOYAGE PACK`**, with
> caption directly beneath in `#12303D`: *"Under 1 MB"*
>
> A single `#0E7A4A` arrow passes downward through it. To its left, small
> `#C97B1E` text: *"Satellite link at sea is slow and expensive"*. To its right,
> small `#5A7280` text: *"or carried aboard on a USB stick"*.
>
> ### BAND 3 — bottom, ~42% of height
>
> Band label, small caps, left-aligned, `#5A7280`:
> `ABOARD — WORKS WITH NO INTERNET`
>
> Four boxes, left to right, joined by arrows:
>
> 1. **`STORED ON BOARD`** — caption: *"Keeps older versions"*
> 2. **`RE-PLAN`** — caption: *"New route in ~9 seconds, on a laptop"*
> 3. **`LOCAL SERVER`**
> 4. **`BRIDGE SCREEN`** — largest box in the band, drawn as a simplified map
>    panel: pale `#DCE9F2` ocean, a white ice band, and a `#0E7A4A` route curving
>    around it. Three short labels beside it, each with a thin leader line:
>    `Data age`, `Risk setting`, `Where sources disagree`
>
> ### Two annotations only
>
> - Thin `#C97B1E` leader to the five-model box: *"When the models disagree, the
>   route becomes more cautious"*
> - Thin `#0E7A4A` leader to the pinch: *"Everything heavy stays ashore"*
>
> ### Title
>
> Top-left, above Band 1, Inter Tight SemiBold `#12303D`:
> **"How the system works"**
> Subtitle `#5A7280`: *"Built for a ship that has almost no internet."*
>
> **Reading order must be unmistakable:** strictly left-to-right within each
> band, strictly top-to-bottom between bands. Number the three bands **1**, **2**,
> **3** in small `#1B6478` circles at the far left of each band.
>
> **Total word count on the entire image must not exceed 110 words.**
>
> **Do not include:** photorealism, 3D, drop shadows, glows, gradients on boxes,
> clip-art icons, stock imagery, decorative filler, or any text beyond what is
> specified.

---

## Why these choices

**Light mode with an editorial register** removes the "kiddy" problem at its
root. Childishness came from glows, rounded bubbles and cartoon icons — not from
simplicity. Simplicity is preserved here by capping the word count (60 and 110
words) and forcing every label to justify itself.

**The first diagram is now a real map**, because the geography *is* the argument.
Two Indian stations 2,450 km apart, one short season, ice closing the approach —
a judge who sees that understands the problem before a word is spoken. Including
Dakshin Gangotri as a hollow marker adds a quiet, true detail: India has been
doing this since 1983, and lost its first base to the ice.

**Numbered entry points** (1 on Cape Town; 1-2-3 on the architecture bands) fix
the "where do I start reading" problem directly, rather than hoping the layout
implies it.

**Colour carries fixed meaning across every slide**: green is the safe route,
amber is uncertainty, red is genuinely blocked. Learn it once on slide one, read
every later slide fluently.
