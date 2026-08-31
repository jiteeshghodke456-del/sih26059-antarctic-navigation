# Diagram Prompts for the ISIH Deck

Two copy-paste prompts. Both depict the **full SIH product** (the December
vision), because that is the ambition being pitched — pitched at a depth
appropriate for the ISIH round.

Shared design system, so the two diagrams read as one family:

| Role | Colour | Why this colour |
|---|---|---|
| Deep ocean / background | `#0A1F2E` | Near-black navy reads as "polar night", high contrast, projector-safe |
| Ice / data | `#62C6DA` → `#DAEDEF` | Cyan-to-pale-ice gradient; the literal subject |
| Safe route / success | `#117A3D` | Maritime green = "go"; the payoff colour |
| Caution / hazard | `#E5A55F` | Amber, matching real nautical chart convention |
| Danger / blocked | `#B03A2E` | Chart red = danger; used sparingly so it always means one thing |
| Text on dark | `#F5FAFB` | Off-white, softer than pure white under projector glare |

Typography: **Poppins SemiBold** or **Montserrat Bold** for headings (geometric,
friendly, not corporate); **Inter** or **Source Sans Pro** for labels.

---

## PROMPT 1 — The story diagram (right half of a slide)

> Create a high-resolution vertical infographic, aspect ratio **8:9** (portrait),
> rendered at **3000 × 3375 pixels**, designed to occupy the right half of a
> 16:9 presentation slide. Leave a 6% margin of empty space on all sides.
>
> **Subject:** how an AI system guides a research ship safely through Antarctic
> sea ice. The audience is a bright, curious 15-year-old — the diagram must be
> instantly understandable with zero prior knowledge, and should feel like an
> adventure, not a technical manual.
>
> **Background:** deep polar-night navy `#0A1F2E`, with a very subtle darker
> radial vignette so the centre content lifts forward.
>
> **Layout:** a single vertical journey with **five numbered stages**, flowing
> top to bottom, connected by a glowing cyan `#62C6DA` line that visibly
> *thickens and brightens* as it descends — so the eye is pulled downward and
> the sequence feels like momentum building toward an answer.
>
> Each stage is a rounded card (16 px corner radius) in a slightly lighter navy
> `#12293A`, with a soft cyan outer glow, containing a large simple flat-vector
> icon on the left and two lines of text on the right.
>
> **The five stages, in this exact order and wording:**
>
> 1. **"Satellites watch the ice"** — icon: a satellite beaming a cone of light
>    down onto a white-and-cyan ice sheet. Subtext: *"Every single day, even
>    through darkness and cloud."*
> 2. **"AI predicts where the ice will move"** — icon: a stylised neural network
>    of glowing cyan nodes morphing into an ice map. Subtext: *"Up to 7 days
>    ahead."*
> 3. **"Physics predicts where icebergs drift"** — icon: a large iceberg with
>    ~90% shown submerged below a waterline, with curved arrows for wind and
>    ocean current. Subtext: *"Real equations, not guesswork."*
> 4. **"The computer finds the safest route"** — icon: a small map with a green
>    `#117A3D` route curving around an amber `#E5A55F` hazard zone. Subtext:
>    *"Balancing safety, speed and fuel."*
> 5. **"The ship gets it — with no internet"** — icon: a research vessel with a
>    small offline/no-signal symbol glowing green beside it. Subtext: *"Works
>    on a laptop on the bridge, in the middle of nowhere."*
>
> **Stage numbers:** large circular badges (1–5), cyan outline with the numeral
> in `#F5FAFB`, sitting on the connecting line at each card's left edge.
>
> **Header** at the top, above stage 1, in Poppins SemiBold `#F5FAFB`:
> **"From satellite to ship's bridge"** — with a smaller cyan subtitle beneath:
> *"How we guide a ship through moving ice."*
>
> **Emotional payoff:** stage 5's card is the visual climax — give it the
> strongest green `#117A3D` glow, slightly larger scale than the others, so the
> viewer's eye lands on the ship arriving safely and feels resolution.
>
> **Style:** modern flat vector illustration with subtle glows. Clean, confident,
> a little cinematic. No photorealism, no clip-art, no 3D bevels, no drop
> shadows, no stock-photo people. Absolutely no lorem ipsum — use exactly the
> text specified above and no other text.

---

## PROMPT 2 — The system architecture diagram (full slide)

> Create a high-resolution technical system-architecture diagram, aspect ratio
> **16:9**, rendered at **3840 × 2160 pixels**, designed to fill a presentation
> slide. Leave a 4% margin on all sides.
>
> **Subject:** the architecture of an AI decision-support platform for Antarctic
> ship navigation. The audience is a technically literate judge: it must look
> rigorous and considered, while still being readable from across a room.
>
> **Background:** deep navy `#0A1F2E`. Section bands in slightly lighter navy
> `#12293A` with 1 px cyan `#62C6DA` borders at 30% opacity.
>
> **Overall structure: three horizontal bands, stacked top to bottom.** The
> single most important visual idea is that the top band and the bottom band are
> *separated by a narrow bottleneck* — this separation is the architecture's core
> insight and must be immediately obvious.
>
> ### BAND 1 (top, ~45% of height) — labelled **"ASHORE — needs bandwidth and a GPU"**
>
> A left-to-right pipeline of five stages, connected by cyan arrows:
>
> 1. **Data sources** — a vertical stack of five small pill-shaped labels:
>    `NSIDC satellite ice`, `CMEMS ocean forecast`, `ERA5 / GFS weather`,
>    `GEBCO seafloor depth`, `USNIC iceberg positions`
> 2. **Quality control & regridding** — box, subtitle *"artifact masking · one
>    common grid"*
> 3. **AI ice forecast** — the visual hero of this band. Show **five small
>    stacked neural-network cards** (an ensemble) feeding into one output,
>    labelled **"5× U-Net ensemble"**, subtitle *"corrects the operational
>    forecast"*. Beside it, a small bell-curve/spread icon labelled
>    **"calibrated uncertainty"** in amber `#E5A55F`.
> 4. **Hazard assembly** — box containing three stacked mini-layers labelled
>    `predicted ice + safety margin`, `iceberg drift zones (physics)`,
>    `source disagreement`
> 5. **Route optimisation** — box labelled **"PolarRoute"**, subtitle
>    *"Dijkstra over an adaptive mesh · 12 runs → best trade-offs"*
>
> ### BAND 2 (middle, ~10% of height) — the bottleneck
>
> A visually *narrow* horizontal channel, deliberately constrained, containing a
> single glowing green `#117A3D` capsule labelled **"VOYAGE PACK"**, subtitle
> *"signed · versioned · under 1 MB"*.
>
> Passing through it, a thin green arrow descending from Band 1 to Band 3,
> annotated on the left in small amber text: **"Iridium satellite link — slow,
> expensive, sometimes just text-message sized"** and on the right:
> **"or a USB stick carried aboard in port"**.
>
> Make this band feel like a *pinch point* — narrow, tight, the visual waist of
> an hourglass. This is the whole point: only a tiny compressed file crosses it.
>
> ### BAND 3 (bottom, ~45% of height) — labelled **"ABOARD — no internet required"**
>
> A left-to-right pipeline of four stages:
>
> 1. **Pack store** — box, subtitle *"current + previous versions, can roll back"*
> 2. **Local re-planning** — box, subtitle *"full route recomputed in ~9 seconds,
>    ordinary laptop CPU"*
> 3. **Local API** — small box labelled `FastAPI`
> 4. **Bridge display** — the largest box in this band, drawn as a simplified
>    map screen showing a green route curving around amber ice, with three small
>    UI callouts beside it: `data age banner`, `risk tolerance slider`,
>    `sources-disagree overlay`
>
> ### Annotations
>
> - A callout arrow pointing at the **5× U-Net ensemble**, in amber:
>   *"Five models. When they disagree, the route becomes more cautious
>   automatically."*
> - A callout arrow pointing at the **bottleneck**, in green:
>   *"Everything heavy stays ashore. Only a small file goes to sea."*
>
> ### Title
>
> Top-left, Poppins SemiBold `#F5FAFB`, large: **"System Architecture"**, with a
> cyan subtitle: *"Heavy computing ashore. Real decisions aboard, offline."*
>
> **Style:** clean modern technical diagram — think a well-designed engineering
> whitepaper, not a corporate slide. Crisp 2 px lines, generous spacing,
> consistent 12 px corner radii, strict left-to-right reading order within each
> band. Every arrow must be labelled or clearly directional. No photorealism, no
> 3D, no drop shadows, no clip-art icons, no decorative filler. Use only the text
> specified above.

---

## Notes on why these are built this way

**Prompt 1 uses a vertical journey**, not a flowchart, because a narrative
sequence with numbered stages carries a non-expert far better than a network of
boxes. The thickening line and the brighter final card give it a sense of
arrival — the viewer feels the problem being solved, which is what makes a
diagram memorable rather than merely informative.

**Prompt 2's hourglass shape does the persuasive work.** A judge who sees a wide
top, a pinched middle, and a wide bottom immediately understands the constraint
the whole system was designed around — before reading a single label. That
constraint (a ship with almost no internet) is the project's strongest
differentiator, so the diagram is built to make it the first thing understood.

**Colour discipline:** green appears only for "safe / working", amber only for
"caution / uncertainty", red not at all in these two diagrams — it is reserved
for the route figure where something is genuinely blocked. Consistent meaning
across every slide means the audience learns the code once and reads the rest
fluently.
