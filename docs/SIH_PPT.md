# SIH 2026 — Slide Deck, Copy-Paste Ready
### Problem Statement 26059 · AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory and Navigation Decision Support System

**How to use this file.** Each slide has three blocks:
- **TEXT TO PASTE** — final copy. Paste it in, change the team name/ID, done.
- **LAYOUT** — where every element sits, matched to the reference deck.
- **DIAGRAM PROMPT** — copy-paste into your image/diagram tool.

Every number in here traces to a file in this repo, and nothing is estimated or
rounded up. Where a line describes something designed but not yet built, it
says so in the same breath — "designed," "next," "on the roadmap" — those are
the only aspirational words in this deck, and they are labelled, never hidden
inside a present-tense verb. `docs/TRUE_CLAIMS.md` holds the evidence trail for
each claim, and the "what a judge may ask" answers.

---

## ⚠️ Read this before you generate any diagram

**Text-to-image models garble text inside diagrams.** The reference deck's
flowcharts and architecture panels were clearly built in a diagram tool, not
generated — every label is crisp and correctly spelled, which no image model
does reliably.

So for each slide below there are two prompts:

- **`DIAGRAM PROMPT (structured tool)`** — for **Napkin AI, Whimsical, Excalidraw,
  Mermaid, draw.io, or PowerPoint SmartArt**. Use this for anything with labels.
  This is the one that will actually look like the reference deck.
- **`IMAGE PROMPT (generative)`** — only for decorative panels and icon sets,
  where garbled text does not matter.

If you only have an image generator, generate the *icons* and lay the *boxes and
text* over them in PowerPoint. That is how the reference deck looks the way it does.

---

## GLOBAL DESIGN SYSTEM — apply to every slide

Match the reference exactly:

| Element | Spec |
|---|---|
| Slide size | 16:9 widescreen (1440 × 810 pt) |
| Background | Pure white, light mode throughout |
| Title font | Bold serif (Bookman Old Style / Cambria / Georgia), centred, ~40 pt, black |
| Slide-1 title | Same serif, **deep navy `#1F4E79`**, left-aligned, ~54 pt |
| Body font | Serif, black, **justified**, ~16–18 pt |
| Section headings inside boxes | Bold, **navy `#1F4E79`**, ~22 pt |
| Bullet style | Bold lead-in phrase, then colon, then normal-weight explanation |
| Banner headings | White bold serif on a **blue `#1F6FB5`** rounded bar |
| Footer | Solid blue `#1F6FB5` bar, full width, white bold centred "SMART INDIA HACKATHON 2026", page number at right |
| Logos | Team logo top-**left**, SIH 2026 logo top-**right**, on every slide except slide 1 (SIH logo only, top-right) |
| Accents | Orange `#E87722` · Teal `#12A0A0` · Risk red `#C0392B` · Solution green `#1E8449` |
| Boxes | White fill, thin dark outline, generous rounded corners |
| Icons | Flat line icons, single colour, no photographs |

**One deviation from the reference, on purpose:** we use **teal + orange** as the
data/route colour pair instead of red/green. Red-green is the commonest colour
blindness and our route figures are read left-to-right by an examiner at
distance. Teal and orange stay distinguishable for every viewer.

---

# SLIDE 1 — TITLE

### TEXT TO PASTE

> **SMART INDIA HACKATHON 2026**
>
> - **Problem Statement ID –** 26059
> - **Problem Statement Title –** AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory, and Navigation Decision Support System
> - **Theme –** Space Technology / Earth Observation
> - **PS Category –** Software
> - **Team ID –** `<your team ID>`
> - **Team Name –** `<your team name>`

### LAYOUT
Exactly the reference: title top-left in navy serif, SIH 2026 logo top-right,
six bullets filling the left 60%, large faint hexagon/graphic watermark on the
right 40%. **No footer bar on this slide.**

### IMAGE PROMPT (generative) — right-side watermark
```
Flat vector illustration, light mode, pure white background, no text.
A large pale grey hexagon outline. Inside it, a stylised ship's compass rose
merged with a snowflake, rendered half in warm orange circuit-board lines and
half in teal contour lines resembling sea-ice edges. Minimal, corporate, clean,
lots of white space. Subtle, low contrast, suitable as a background watermark
behind bullet text. No lettering anywhere.
```

---

# SLIDE 2 — PROPOSED SOLUTION / APPROACH

**Header:** centred bold serif title, italic subtitle beneath.

> # SETU
> *Knowing the ice before the ship gets there*

*(Setu = "bridge" — the bridge between shore science and the ship's bridge.
Swap for your own name; keep the tagline structure: short name, one italic line.)*

### TEXT TO PASTE — left column, under a blue "Proposed Solution / Approach" banner

> - **Correct the forecast, don't reinvent it:** We do not predict sea ice from scratch. We take the operational physics forecast and learn its *error*, then add the correction back. An untrained model reproduces the forecast exactly, so the system can never be worse than the physics it starts from.
>
> - **Trust the data only where it deserves trust:** The satellite record silently reports suppressed coastal pixels as *open water*. We detect and mask them. In the 200 km approach to Bharati this affects **43.2% of days**.
>
> - **Track the ice that can sink you, separately:** Icebergs follow different physics from sea ice. We run a published closed-form drift model over the US National Ice Center catalogue — **33 bergs as of 27 Aug 2026 (weekly product), 15 of them inside our corridor**.
>
> - **Route with the ship's real limits:** We reuse PolarRoute, the open-source router from the British Antarctic Survey, and feed it our corrected ice and the vessel's true dimensions, routing today on a working 80% ice-concentration limit. Replacing that with the regulator's own IMO POLARIS risk index is designed, not built yet — it needs a thickness channel we don't have.
>
> - **Answer the question a captain actually asks:** Not "what is the shortest line", but **"when should I arrive, will the last 100 km be open, and what do I do if it isn't."**

### DIAGRAM PROMPT (structured tool) — top right: end-to-end workflow
```
Create a left-to-right flowchart, light mode, white background, thin black
arrows, titled "SETU end-to-end workflow".

Shapes and colours, matching this legend:
- Stadium/pill shape, PINK fill: "Start" and "End"
- Rectangle, YELLOW fill: process steps
- Diamond, BLUE fill with white text: decisions
- Small rectangle, PURPLE fill: data-source labels attached to steps

Flow:
Start (pink)
-> "Satellite ice observed" (yellow), with purple tag "NSIDC daily"
-> "Quality check: mask suppressed coastal pixels" (yellow), purple tag "QA flag"
-> "Physics forecast fetched" (yellow), purple tag "CMEMS"
-> "AI corrects the forecast" (yellow)
-> "Iceberg drift computed" (yellow), purple tag "US Ice Center"
-> Decision diamond (blue): "Is the destination open?"
     - branch "YES" -> "Route and sail" (yellow)
     - branch "NO"  -> "Hold, or switch to helicopter and barge" (yellow)
-> Decision diamond (blue): "Forecast still verifying?"
     - branch "YES" -> "Hold course" (yellow)
     - branch "NO"  -> "Widen corridor, fall back to physics forecast" (yellow)
-> "Daily voyage pack to the ship, under 1 MB" (yellow)
-> End (pink)

Keep every label under 8 words. Clean, evenly spaced, easy to follow start to
finish. No shadows, no gradients.
```

### DIAGRAM PROMPT (structured tool) — bottom right: Innovation and Uniqueness
```
Create a fan-out diagram, light mode, white background.

At the top centre, a rounded green label reading "Innovation and Uniqueness".
From it, five curved brown arrows fan downward to five equal rounded cards in a
row. Each card has a bold title, two lines of small description, and a simple
flat line icon at the bottom. Use five distinct muted fills, left to right:
teal, deep blue, olive, orange, brown. White text.

Card 1 — "Next: Uncertainty Reaches The Route"
   Designed and gated (stratified conformal calibration); wiring model disagreement into the routing cost is the next build step, not done yet.

Card 2 — "We Audit The Satellite Data"
   We found the record reports suppressed coastal pixels as open water.

Card 3 — "Knows What It Cannot See"
   States its blind spots out loud instead of hiding them.

Card 4 — "Grounded In A Real Besetting"
   The abort-and-hold logic is modelled on a real incident from the Indian Antarctic programme (MV Magdalena Oldendorff, 20th ISEA) — there is no automated incident-learning system yet.

Card 5 — "Router Needs No Signal"
   PolarRoute's own mesh-to-route pipeline runs offline in about 9 seconds on a laptop CPU. A live re-plan control the master can trigger at sea is designed, not built.

Flat, corporate, minimal. No shadows.
```

---

# SLIDE 3 — TECHNICAL APPROACH

### DIAGRAM PROMPT (structured tool) — main four-zone architecture
```
Create a horizontal four-zone architecture diagram (swimlanes), light mode,
white background. Four tall columns, each with a pastel tinted fill and a
dashed border, each with a bold centred header. Labelled arrows between zones.

ZONE 1 (pale blue) header "Zone 1 — Data Sources"
  A cloud shape containing four pills:
    "NSIDC sea-ice (no login)"
    "CMEMS forecast"
    "US Ice Center bergs"
    "ERA5 wind and wave"
  Below the cloud, a small ship icon labelled "Vessel: MV Vasiliy Golovnin".

ZONE 2 (pale green) header "Zone 2 — Quality and Preparation"
  A box titled "Ingest and QC" containing four rows, each with a small icon:
    "Mask suppressed coastal pixels"
    "Regrid to a common 25 km grid"
    "Build the 12 input channels"
    "Flag missing days"

ZONE 3 (pale purple) header "Zone 3 — Intelligence Layer"
  A box titled "Models" containing three stacked sub-boxes:
    "Sea-ice correction U-Net (1.93 M parameters)"
    "Conformal calibration (turns spread into a safety margin)"
    "Iceberg drift, Wagner closed form"
  A small database cylinder beside it labelled "Forecast archive".

ZONE 4 (teal) header "Zone 4 — Decision Support"
  A box titled "Router and Advisor" containing:
    "PolarRoute engine (British Antarctic Survey)"
    "80% ice limit today (POLARIS: on roadmap)"
    "Iceberg exclusion zones"
    "Corridor, not a single line"
  Below it a laptop icon labelled "Ship's laptop, works offline".

Arrows, labelled:
  Zone 1 -> Zone 2 : "raw files"
  Zone 2 -> Zone 3 : "clean channels"
  Zone 3 -> Zone 4 : "forecast + uncertainty"
  Zone 4 -> Zone 1 : "voyage pack under 1 MB" (curved return arrow along the bottom)

Beneath all four zones, a full-width strip labelled "Components / Technology
stack" containing evenly spaced logos: Python, PyTorch, NumPy, xarray, FastAPI,
PostgreSQL, Leaflet, GitHub Actions.

Flat, clean, corporate. Every label under 9 words. No shadows or gradients.
```

### DIAGRAM PROMPT (structured tool) — right panel: Implementation Process
```
Create a vertical S-curve timeline, light mode, white background, six stages.
Circular icon badges alternate left and right along a smooth curved ribbon that
changes colour gradually from deep teal at the top to orange at the bottom.
Each badge has a bold title and two lines of description beside it.

Header at the top: "Implementation Process" in bold with a small gear icon.

1. "Data Foundation" — Fetch and quality-check the full satellite record. Mask
   the pixels the product itself flags as unreliable.
2. "Train The Corrector" — Learn the physics model's error, split strictly by
   time so no future day leaks into training.
3. "Measure Honestly" — Score once against persistence, the baseline that
   actually matters in sea-ice forecasting.
4. "Add Uncertainty" (next) — Five-model disagreement becoming a calibrated
   safety margin is designed and gated; today's prototype routes on one model.
5. "Route And Advise" — Feed corrected ice and iceberg zones into PolarRoute
   under a working ice limit; POLARIS compliance follows once thickness ships.
6. "Ship It To Sea" — Compress to a sub-1 MB voyage pack; the routing pipeline
   itself runs offline in ~9 s. A live re-plan control is designed, not built.

Flat vector, single-weight line icons, no photographs.
```

### TEXT TO PASTE — small caption strip under the architecture
> **Reused, not rebuilt:** PolarRoute and meshiphi (British Antarctic Survey, MIT licence) provide the routing engine. We extend them; we do not fork them. Our contribution is the corrected ice, the uncertainty, the iceberg layer, and the decision logic.

---

# SLIDE 4 — FEASIBILITY AND VIABILITY

### TEXT TO PASTE — three boxes across the top

> **Feasibility**
> - Every data source is **live and free today** — sea ice, icebergs and bathymetry need **no login at all**.
> - The routing engine already exists and is **MIT-licensed** from the British Antarctic Survey.
> - The sea-ice model is **trained and measured**, not proposed: it beats persistence at every horizon from 1 to 7 days.

> **Viability**
> - Runs on **one laptop at sea**. Heavy computation stays ashore; the ship receives a **sub-1 MB pack**.
> - Aligned with MoES direction — GRSE signed an MoU with Kongsberg in **June 2025** to build India's first indigenous Polar Research Vessel.
> - Calibrated first for **MV Vasiliy Golovnin**, the vessel India actually charters, then extended to more hulls.

> **Practical Implementation**
> - **Audited on three full years** of real satellite data, 1,096 files, zero failures; the model itself is **trained on two of those years** (2019–2020).
> - **Degradation in defined grades is designed, not running yet:** ADR-022 specifies forecast-grade → CMEMS-direct → climatology-grade, so the router never refuses past the forecast horizon. The demo does not yet announce which grade it is on.
> - Designed for the **Dec–April** Indian resupply season and the Maitri and Bharati approaches specifically.

### DIAGRAM PROMPT (structured tool) — bottom mirrored challenges/strategies
```
Create a wide panel split into two halves by a dashed vertical centre line,
light mode, white background.

LEFT HALF — header inside a grey circle with a gear-and-warning icon:
"Potential Challenges and Risks". Five numbered RED circles (01-05) arranged in
a vertical zigzag, joined by curved black arrows flowing downward. Each has a
bold label and one line of description:

01 Data lies at the coast — The satellite record reports suppressed coastal
   pixels as open water.
02 No drift data in our season — The observational ice-drift product is not
   produced in the southern summer.
03 The router sees frozen ice — The open-source engine assumes ice does not
   move during the voyage.
04 Forecast skill runs out — Useful skill ends near seven days; a voyage takes
   over two weeks.
05 Small ice is invisible — Growlers that hole hulls are far below satellite
   resolution.

RIGHT HALF — mirror image. Header inside a grey circle with a person-climbing
icon: "Strategies For Overcoming Challenges". Five numbered GREEN circles
(01-05), curved black arrows flowing upward, text right-aligned:

01 Read the quality flag the file already ships and treat those cells as
   unknown, never as open water.
02 Use modelled currents from the operational ocean forecast, and state that it
   is modelled.
03 Build a time-expanded route graph: one ice layer per forecast day.
04 Commit only the first two days; beyond that give a corridor, and past seven
   days show a fan, not a line.
05 Never claim growler warning. Say so on the slide, and leave it to radar and
   the lookout.

Flat, clean, evenly spaced, easy to follow. No shadows.
```

---

# SLIDE 5 — IMPACT AND BENEFITS

### DIAGRAM PROMPT (structured tool) — left: hub and spokes
```
Create a hub-and-spoke diagram, light mode, white background.

CENTRE: a donut/ring chart in teal and orange segments. Inside the ring, a
small silhouette of an Antarctic research station with an Indian flag. Ring
label, three lines, centred: "Potential Impact on Targeted Audience".

Five grey rounded boxes radiate outward, joined to the ring by black elbow
connectors ending in small open circles. Each box has a flat line icon, a bold
navy heading, and two or three lines of text.

TOP — "Ship's Master and Crew"
  Fewer days stuck in ice. Knows in advance whether the station approach will be
  open, and what to do if it is not.

LEFT — "NCPOR and MoES"
  Expedition planning on measured evidence instead of judgement alone. Same
  corridor India already sails.

RIGHT — "Expedition Scientists"
  More usable days on station because cargo windows are planned around real ice,
  not guessed.

BOTTOM-LEFT — "The Nation"
  Reduces dependence on chartered foreign hulls and foreign ice advisories.
  Directly supports the indigenous Polar Research Vessel programme.

BOTTOM-RIGHT — "Future Crews"
  Every voyage archived. The system gets better each season instead of starting
  over.

Flat, corporate, generous white space.
```

### TEXT TO PASTE — right column, under a blue "Benefits of the solution" banner
Three quote-style cards, orange left-and-bottom accent border, large quotation
marks, each paired with a black arrow pointing to a category label and line icon.

> **Safety** — *"A support ship on the 20th Indian Antarctic Expedition sat beset in the ice for roughly five and a half months. Our system is built around the conditions that cause exactly that."*

> **Operational** — *"The station approach was shut on 23 of 31 December days. Knowing which days those are is the difference between waiting at sea and planning around it."*

> **Scientific** — *"We publish what the system cannot see as carefully as what it can. A decision-support tool that hides its blind spots is not decision support."*

### TEXT TO PASTE — full-width banner across the bottom
> **"It does not just draw a line on the ice. It tells you when to go, when to wait, and when it no longer trusts itself."**

---

# SLIDE 6 — RESEARCH AND REFERENCES

Single large rounded box. Two navy headings. Every entry states **what we
adopted from it** — that is what the reference deck does and it is what an
examiner rewards.

### TEXT TO PASTE

> **Applied and Field Research**
> - Audited the full NOAA/NSIDC satellite record, **1,096 daily files, 2018–2020**, and measured how often the product's own quality flag marks coastal cells unreliable. **Adopted:** our quality-control layer, and the 43.2% figure for the Bharati approach.
> - Read the installed source of the PolarRoute routing engine rather than its documentation. **Adopted:** confirmation that wave resistance is defined but never called, and that the router has no time dimension — both now design requirements, not surprises.
> - Reconstructed real besetting incidents, including **MV Magdalena Oldendorff on the 20th Indian Antarctic Expedition**. **Adopted:** the decision architecture's abort-and-hold logic.

> **Academic and Government Sources**
>
> - **IMO MSC.1/Circ.1519 — POLARIS.** The mandated framework for ice-class operating limits. **Adopted:** replaces our invented 80% ice threshold with the regulator's own risk index; also forces a thickness output, since POLARIS is indexed by ice *type*.
>   https://www.nautinst.org/static/uploaded/2f01665c-04f7-4488-802552e5b5db62d9.pdf
>
> - **Wagner, Dell & Eisenman (2017), *An Analytical Model of Iceberg Drift*, J. Phys. Oceanogr. 47(7).** **Adopted:** implemented directly as our iceberg drift model. We also caught a drag-coefficient inconsistency between the preprint text and the authors' reference code, and pinned the correct values in a test.
>   https://arxiv.org/abs/1610.06403
>
> - **Ivanova et al. (2015), *The Cryosphere* 9, 1797 — 30-algorithm sea-ice round robin.** **Adopted:** the honest error bar. Published algorithms disagree by roughly **ten times more at the ice edge** than in thick pack, which is why we ship uncertainty rather than a single number.
>   https://tc.copernicus.org/articles/9/1797/2015/
>
> - **Lavergne et al. (2019), *The Cryosphere* 13, 49 — sea-ice concentration climate records.** **Adopted:** the producers state their shipped uncertainty **excludes** melt-pond, thin-ice and weather-filter effects. We therefore calibrate our own instead of trusting theirs.
>   https://tc.copernicus.org/articles/13/49/2019/
>
> - **Massonnet et al. (2023), *Front. Mar. Sci.* 10:1148899 — SIPN South.** **Adopted:** the benchmark bar. Across 22 groups and over 3,000 forecasts, only **51% beat plain climatology**, and persistence was not tested at all. Our results are measured against persistence.
>   https://doi.org/10.3389/fmars.2023.1148899
>
> - **Hibler (1979) ice strength, as implemented in CICE.** **Adopted:** the reason we refuse to publish an ice-compression number without an error bar — strength is exponential in concentration, so a 5-point concentration error becomes a **2.7× strength error**.
>
> - **PolarRoute / meshiphi, British Antarctic Survey (MIT licence).** **Adopted:** the routing engine itself. We extend it rather than rebuild it.
>   https://github.com/antarctica/PolarRoute
>
> - **US National Ice Center, Antarctic Icebergs.** **Adopted:** live iceberg positions, free and without an account, updated weekly.
>   https://usicecenter.gov/Products/AntarcIcebergs

---

## APPENDIX — numbers you may be asked for

Keep this off the slides; keep it in your head.

| Claim | Number | Where it lives |
|---|---|---|
| Sea-ice model vs persistence | +18.5% (1 d) → **+30.6% (7 d)** | `docs/ISIH_RESULTS.md` |
| Model size | 1,929,601 parameters, 12 channels | `docs/ISIH_RESULTS.md` |
| Satellite files used | 1,096, zero failures | `docs/ISIH_RESULTS.md` |
| Coastal data artifact | **43.2%** of days, Bharati 200 km box | `isih/figures/ice_quality_audit.json` |
| Destination closed | **23 of 31** December days | `isih/figures/destination_window.json` |
| Approach 100 km north open | **31 of 31** days | same |
| Icebergs tracked / in corridor | **33 / 15** | `models/iceberg/regime_report.json` |
| Iceberg regime flip | 20/33 current-driven at 10 m/s → **28/33 wind-driven at 30 m/s** | same |
| Transit, Cape Town → Bharati | **8.6 days steaming** (not total voyage) | `docs/ISIH_RESULTS.md` |
| Drift model tests passing | **23/23**, reproducing the paper's own table | `models/iceberg/test_drift.py` |

**Three things to say before you are asked** — they convert doubt into credit:
1. "Our route-regret experiment came out against us on the date we tested. We are reporting it."
2. "We withdrew our own 17.4-day transit figure after finding the vessel specification was wrong."
3. "This can never warn you about growlers. Nothing in orbit sees them."
