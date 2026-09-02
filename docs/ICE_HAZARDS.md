# ICE_HAZARDS.md — Physical Ice Hazards for Antarctic Navigation

**Scope**: safety-critical physical hazards for the Cape Town → Bharati / Maitri resupply voyage
(austral summer, Dec–Apr, MV *Vasiliy Golovnin*). This document exists to feed the **risk field of the
routing cost function** directly. It answers one concrete engineering question repeatedly: *given that
this project forecasts sea-ice concentration on a 25 km grid, which hazards can that field see, which
can it only hint at, and which are structurally invisible?*

**Status of claims.** Every non-trivial claim is tagged:

| Tag | Meaning |
|---|---|
| **VERIFIED** | Read directly from a primary source this session; source URL given. |
| **INFERRED** | Derived by reasoning/arithmetic from a VERIFIED fact. The reasoning is shown so it can be checked. |
| **UNVERIFIED** | Believed true but **not** confirmed from a primary source this session. **Do not put an UNVERIFIED number on a judged slide.** |

**Sources that could not be reached this session** are listed in §6. They are named rather than
silently dropped.

**Primary source used throughout §1**: WMO **Sea-Ice Nomenclature, WMO No. 259** (Volume I —
Terminology and Codes; Volume III — International System of Sea-Ice Symbols), snapshot as of the
5th Session of the JCOMM Expert Team on Sea Ice (March 2014), PDF hosted by NSIDC:
<https://nsidc.org/sites/default/files/wmo-259-2015_multilingual.pdf> (fetched and text-extracted
this session; landing page <https://nsidc.org/data/documentation/sea-ice-nomenclature-wmo-259>).
Quoted definitions below are transcribed from that PDF. **VERIFIED.**

---

## Table of contents

- [(a) Taxonomy of Antarctic sea-ice structures per WMO nomenclature](#a-taxonomy-of-antarctic-sea-ice-structures-per-wmo-nomenclature)
- [(b) Ice convergence / compression — the besetting hazard](#b-ice-convergence--compression--the-besetting-hazard)
- [(c) Blizzards and katabatic winds in the austral summer](#c-blizzards-and-katabatic-winds-in-the-austral-summer-decapr)
- [(d) What a 25 km sea-ice concentration product CANNOT see](#d-what-a-25-km-sea-ice-concentration-product-cannot-see)
- [§5 Direct implications for the routing cost function](#5-direct-implications-for-the-routing-cost-function)
- [§6 Unreachable / unverified](#6-unreachable-paywalled-or-dead-sources)
- [§7 Backlog lines to append](#7-backlog-lines-to-append-to-docsbacklogmd)

---

## (a) Taxonomy of Antarctic sea-ice structures per WMO nomenclature

### a.0 The arithmetic that governs everything below

A 25 km NSIDC polar-stereographic cell covers **25 × 25 = 625 km²**. Every "is it visible?" verdict in
this section is, at bottom, this one comparison. **INFERRED** (arithmetic on the stated grid spacing;
grid spacing is **VERIFIED** — "All data are on a 25 km x 25 km grid", NSIDC G02202 v5,
<https://nsidc.org/data/g02202/versions/5>).

Second governing fact, and it is worth more than the arithmetic: the NCAR Climate Data Guide's expert
assessment of this exact product family says plainly —

> "The low spatial resolution limits the precision of the ice edge location and **makes the products of
> limited use for operational support (e.g., navigation)**."
> …
> "The concentration fields are **least reliable for small-scale studies (e.g., <100 km)**."
> …
> "Concentration estimates are most reliable within the consolidated ice pack during cold, winter
> conditions (errors ~5-10%). The estimates are **least reliable close to the ice edge and during melt
> conditions, where biases may be 20-30%**."

— NCAR Climate Data Guide, *Sea Ice Concentration: NOAA/NSIDC Climate Data Record*,
<https://climatedataguide.ucar.edu/climate-data/sea-ice-concentration-noaansidc-climate-data-record>.
**VERIFIED.**

Read those three sentences together and the honest position for the demo is: **the effective decision
scale of a 25 km passive-microwave SIC field is ~100 km, not 25 km, and it is at its *worst* precisely
in the two regimes this voyage lives in — the ice edge, and summer melt.** This is not a reason to
abandon the product; it is the reason the routing layer must be uncertainty-aware and must tier down
(which `ARCHITECTURE.md` §2.4a already does). It is also the single most defensible thing the team can
say to a judge who asks "what are the limits of your system?"

### a.1 Master table

"Visible at 25 km SIC?" is judged against a **25 km passive-microwave sea-ice-concentration** field
only (no thickness, no stage of development, no SAR).

| # | Structure | WMO def. (No. 259) | Typical scale | Visible in 25 km SIC? | Danger to a ship | Modellable from ERA5 wind + CMEMS ocean + NSIDC 25 km SIC? |
|---|---|---|---|---|---|---|
| 1 | **Drift ice / pack ice** | 1.1.2 — "any area of sea ice other than fast ice… When concentrations are high, i.e. **7/10 or more**, drift ice may be replaced by the term pack ice" | 10²–10⁶ km² | **Yes** — this is the one thing the product is *for* | Transit resistance, speed loss, besetting at high conc. | **Yes.** This is the project's core forecast target. |
| 2 | **Fast ice** | 1.1.1 / 3.1 — "sea ice which forms and remains fast along the coast, attached to the shore, to an ice wall, to an ice front, between shoals or **grounded icebergs**… may extend a few metres or **several hundred kilometres from the coast**" | m → 100s km | **Partly, and dangerously ambiguously.** A wide fast-ice sheet occupies pixels, but it reports as ~100 % SIC — **indistinguishable from 100 % drifting pack** | Hard barrier. A ship can push through drifting pack at 100 %; it cannot push through 100 km of consolidated fast ice. Also the *anchor* for besetting traps (see §b) | **No, not from SIC alone.** Requires a dedicated fast-ice detection product (Nihashi & Ohshima 2015 algorithm, or Fraser et al. circum-Antarctic landfast product). **Named gap.** |
| 3 | **Marginal ice zone (MIZ)** | 4.4.11 — "The region of an ice cover which is **affected by waves and swell penetrating into the ice from the open ocean**" | 10–200 km wide band | **Yes as a band; no as a boundary.** Note the WMO definition is *wave-physical*, not a concentration threshold — the project's 15–80 % SIC operational definition (`ML_ARCHITECTURE.md` §1.6.5) is a **proxy for**, not the same thing as, the WMO MIZ | Floe impact loads under swell; worst ice-edge forecast error; where the ship physically enters the ice | **Partly.** Concentration yes; the wave-penetration definition needs a wave field (ERA5 / GFS provides `swh`) that the pipeline does not currently combine with SIC. **Named gap — and a cheap one to close.** |
| 4 | **Pressure ridge** | 8.2.2 — "A line or wall of broken ice **forced up by pressure**… the submerged volume of broken ice under a ridge, forced downwards by pressure, is termed an **ice keel**". Sub-classes 8.2.2.1–: new (sharp peaks, side slope ~40°), weathered, very weathered, aged, consolidated. Charted with mean/max sail height **in decimetres** and areal concentration in tenths or frequency per nautical mile (WMO Vol. III §6) | Sail 1–5 m; keel 3–5× sail; **width tens of m; length km** | **No.** Width is ~10⁻³ of a pixel | **The primary ice-transit stopper.** A consolidated ridge is thick multi-year-equivalent ice concentrated in a line; ridge density and keel depth, not mean concentration, set icebreaker progress | **No.** Requires SAR (Sentinel-1 EW) or a model with a ridging/thickness-distribution scheme. `DATASET.md` §2 already sources Sentinel-1 EW; **ridging is the strongest use case for it.** |
| 5 | **Rafting / finger rafting** | 6.4 — "Pressure processes whereby one piece of ice overrides another. Most common in new and young ice". 6.4.1 finger rafting — interlocking thrusts like "fingers"; WMO explicitly notes **"finger rafting in grey ice is common in Antarctica"** | Floe-scale, m–100s m | **No** | Doubles local thickness of young ice with no change in concentration — a 100 % nilas field that has rafted is not the trivial obstacle its SIC suggests | **No.** Not resolvable and not represented in a concentration-only field. |
| 6 | **Lead** | 7.3 — "Any fracture or passage-way through sea ice which is **navigable by surface vessels**". Related fracture width classes 7.1.2–7.1.5: very small 1–50 m, small 50–200 m, medium 200–500 m, large >500 m. Sub-types: **shore lead** (7.3.1, between drift ice and shore/ice front), **flaw lead** (7.3.2, between drift ice and fast ice, navigable) | m → km wide, 10s–100s km long | **Not as a locatable feature.** A lead is essentially always sub-pixel in width. **But** it *depresses* pixel-mean SIC: a 2.5 km-wide lead crossing a 25 km cell lowers that cell's concentration by ~10 % (**INFERRED**, area arithmetic) | Leads are the **opportunity**, not the hazard — they are the route. Danger is indirect: a lead can close (see §b) | **Statistically, yes; geometrically, no.** Low SIC inside a high-SIC region is a real statistical signal that leads exist there — it is *not* a located, followable lead. **Say this exactly this way in the demo.** |
| 7 | **Polynya** | 7.4 — "Any **non-linear** shaped opening enclosed in ice. Polynyas may contain brash ice and/or be covered with new ice, nilas or young ice". 7.4.1 **shore polynya** (drift ice ↔ coast/ice front), 7.4.2 **flaw polynya** (drift ice ↔ fast ice), 7.4.3 **recurring polynya** (recurs same position every year) | 10² – >10⁴ km² | **Large ones yes, small ones no** — and see the warning in §c.4: the coastal band is exactly where the land-spillover filter degrades the field | Note the WMO caveat: a polynya **may be covered with new ice or nilas** — "open water" on a SIC map may be a refreezing surface, not navigable water | **Detection partly; prediction genuinely.** Coastal polynyas are wind-driven and **recurring** (7.4.3) — an ERA5/GFS offshore-wind-forced expectation is physically justified. See §c.4. |
| 8 | **Brash ice** | 4.3.6 — "Accumulations of floating ice made up of **fragments not more than 2 m across**, the wreckage of other forms of ice" | Fragments ≤2 m | **No** | Propeller/rudder damage; hull abrasion; slows a vessel badly in an ice-choked channel | **No.** |
| 8b | **Jammed brash barrier** | 4.4.8.1.1 — "A strip or narrow belt of new, young or brash ice (**usually 100–5000 m wide**) formed at the edge of either drift or fast ice or at the shore. It is **heavily compacted mostly due to wind action** and may **extend 2 to 20 m below the surface**… can also consolidate to form a strip of unusually thick ice" | 0.1–5 km wide | **No** (max 5 km vs 25 km pixel) | **Severe and under-appreciated.** A wind-compacted barrier up to **20 m deep** sitting exactly at the fast-ice edge — i.e. exactly where the ship must cross to reach Bharati/Maitri. Not a concentration anomaly; a *depth* anomaly | **No.** But note WMO's own attribution: **"heavily compacted mostly due to wind action"** — its *formation condition* (persistent wind onto an ice edge) is exactly the §b convergence proxy. Flag the zone, don't claim to see the barrier. |
| 9 | **Floe size classes** | 4.3.2 — giant **>10 km**; vast **2–10 km**; big **500–2000 m**; medium **100–500 m**; small **20–100 m**; ice cake **<20 m**; small ice cake **<2 m**. Antarctic-specific: 4.3.3 **cake ice** — "commonly used in Antarctica to refer to a collection of ice cakes… older and thicker than pancake ice" | <2 m → >10 km | **Only "giant" approaches pixel scale.** A vast floe at its 10 km maximum is 100 km² = **16 % of one pixel** (**INFERRED**) | Floe size sets impact loads and manoeuvrability far more than concentration does: 80 % SIC in small floes is navigable, 80 % in vast floes may not be | **No.** Floe-size distribution needs SAR/optical. |
| 10 | **Nilas** (incl. dark/light) | 2.2 — thin elastic crust, matt surface, rafts in "fingers", **up to 10 cm**. 2.2.1 **dark nilas** <5 cm; 2.2.2 **light nilas** >5 cm | <10 cm thick | **No — and worse than "no": actively mis-measured.** Passive microwave "surface melt and **thin ice**, often leads to **large underestimation of concentration**" (Climate Data Guide, **VERIFIED**) | Navigationally trivial for a strengthened ship — but it makes the SIC field *wrong low*, so the router may believe a route is clearer than it is, or vice versa | **No stage-of-development at all** from 25 km SIC. A thermodynamic thin-ice model or AMSR polarisation-ratio thin-ice retrieval would be needed. |
| 11 | **Young ice: grey / grey-white** | 2.4 — young ice **10–30 cm**, transition between nilas and first-year. 2.4.1 **grey ice 10–15 cm** — "Less elastic than nilas and breaks on swell. **Usually rafts under pressure**". 2.4.2 **grey-white ice 15–30 cm** — under pressure more likely to ridge than to raft | 10–30 cm | **No** | Grey-white is the threshold where deformation switches from **rafting to ridging** (WMO 2.4.1 vs 2.4.2) — i.e. where wind-driven compression starts building the thing that actually stops ships | **No.** |
| 12 | **First-year ice thickness classes** | 2.5 — FY ice **30 cm – 2 m**. 2.5.1 **thin FY / white ice 30–70 cm** (1st stage 30–50, 2nd stage 50–70); 2.5.2 **medium FY 70–120 cm**; 2.5.3 **thick FY >120 cm** | 0.3–2 m | **No — this is the single biggest information gap.** | A 25 km cell reporting **90 % SIC** may be 90 % nilas (trivial) or 90 % thick FY ice at >1.2 m (impassable for a non-icebreaker). **The routing cost function cannot distinguish these from SIC alone.** | **No.** Antarctic sea-ice *thickness* has no operational satellite product at navigation quality. **This is a real, permanent limitation — state it, do not paper over it.** |
| 13 | **Bergy bit** | 10.4.4 — "A large piece of floating glacier ice, generally showing **less than 5 m above sea-level but more than 1 m** and normally about **100–300 m² in area**" | 100–300 m² | **No.** 300 m² ÷ 625 km² ≈ **5 × 10⁻⁷ of a pixel** (**INFERRED**) | Hull penetration. Glacier ice is far harder and denser than sea ice | **No.** Not seen by USNIC/BYU either (≥~10 nm axis) — already flagged in `ML_ARCHITECTURE.md` §507 and `VIVA_PREP.md`. |
| 14 | **Growler** | 10.4.5 — "Piece of ice smaller than a bergy bit and floating **less than 1 m above the sea surface**… normally occupying an area of about **20 m²**… **difficult to distinguish when surrounded by sea ice or in high sea state**" | ~20 m² | **No.** 20 m² ÷ 625 km² ≈ **3 × 10⁻⁸ of a pixel** (**INFERRED**) | **The classic hull-holing hazard.** WMO itself states they are hard to see even *visually* from the bridge in high sea state or among sea ice | **No.** No satellite, no model. Mitigation is procedural (speed reduction, ice watch, radar) — say so honestly. |
| 15 | **Tide crack** | 3.4 (forms of fast ice) — the crack at the line of junction between an immovable icefoot/ice wall and fast ice, worked by tidal rise and fall | m wide | **No** | Not a hazard to the *ship*, but a serious hazard to **over-ice cargo movement** — and Bharati's cargo goes ashore over the fast ice (see §c.5) | **No.** Local tidal/observational problem, not a satellite one. |
| 16 | **Ridging / hummocking / fracturing** (processes) | 6.1 **Fracturing** — "Pressure process whereby ice is permanently deformed, and rupture occurs". 6.2 **Hummocking** — "The pressure process by which sea ice is forced into hummocks. When the floes rotate in the process it is termed **screwing**". 6.3 **Ridging** — "The pressure process by which sea ice is forced into ridges" | Process, all scales | **No** | These are the *mechanisms* of §b. Screwing in particular is what damages a hull that is already beset | **Indirectly, yes** — see §b. Their *driver* (convergence) is estimable even though their *product* is invisible. |

### a.2 The WMO concentration classes the router should speak in

From WMO No. 259 Vol. III §14 (hatching for total concentration) — **VERIFIED**:

| Concentration | WMO term |
|---|---|
| 10/10 | Consolidated pack ice / compact |
| 9–10/10 | Very close pack ice |
| 7–9/10 | Close pack ice |
| 4–6/10 | Open pack ice |
| 1–3/10 | Very open pack ice |
| <1/10 | Open water |
| 0 | Ice free |
| — | Bergy water |

**Recommendation**: the UI and the route legend should use these exact WMO terms, not invented bands.
An MoES/NCPOR audience reads ice charts in this vocabulary; inventing "medium ice" instead of "close
pack ice" is a free, unforced credibility loss. Note this maps cleanly onto the project's existing
open-water / MIZ / pack strata (<15 % / 15–80 % / >80 %, `ML_ARCHITECTURE.md` §325) — **but the
boundaries do not coincide** (80 % sits inside WMO "close pack ice", 7–9/10). Keep the internal strata
for calibration; display WMO terms to the user. **INFERRED** (comparison of the two schemes).

---

## (b) Ice convergence / compression — the besetting hazard

### b.1 What compression is, in WMO's own words

WMO No. 259 separates the *kinematics* from the *stress*, and the distinction is the whole problem:

- **5.1 Diverging** — "Ice fields or floes in an area are subjected to diverging or dispersive motion,
  thus **reducing ice concentration and/or relieving stresses in the ice**."
- **5.2 Compacting** — "Pieces of floating ice are said to be compacting when they are subjected to a
  **converging motion**, which **increases ice concentration and/or produces stresses which may result
  in ice deformation**."
- **5.3 Shearing** — "An area of drift ice is subject to shear when the ice motion varies significantly
  in the direction normal to the motion, subjecting the ice to **rotational forces**."

**VERIFIED** (WMO No. 259 §5). Note the "and/or": compacting can raise concentration, *or* raise stress,
*or* both. A field that is already at 10/10 has nowhere to go in concentration — it can only take up
stress. **That is why compression is invisible in a concentration product exactly when it is most
dangerous.** **INFERRED**, but it follows directly from the WMO wording.

### b.2 The accepted operational representation — and it is qualitative

**This is the direct answer to the brief's key question, part 1.**

The internationally standardised operational representation of compression is a **three-class
qualitative symbol drawn by a human ice analyst**, not a number. WMO No. 259 Volume III, §4 "Symbols
for dynamic processes", lists the dynamic-process symbols as *Compacting, Diverging, Shearing, Drift*,
with the following **supplementary (optional)** subdivision for compacting — quoted verbatim:

> "**- Compacting:**
>   Slight compacting
>   Considerable compacting
>   Strong compacting"

**VERIFIED** (WMO No. 259 Vol. III §4, from the NSIDC-hosted PDF).

That is the whole of the international standard. There is **no WMO-defined threshold, unit, or formula**
separating "slight" from "considerable" from "strong". Compare this with how precisely WMO codifies
ridges (mean and maximum sail height in decimetres, areal concentration in tenths *or* frequency per
nautical mile, five weathering classes) — the contrast is deliberate and it tells you that compression
resisted quantification even in a standard written by ice services.

**Therefore: if the project produces a compression output, the honest and standards-compliant thing to
produce is a three-class categorical flag (slight / considerable / strong), not a continuous
"compression index" with invented units.** A judge who knows ice charts will recognise the WMO scale
and credit it. A made-up 0–100 "compression score" invites the question "where did that number come
from?", which has no good answer.

### b.3 Why there is no formula — the physics

Two independent operational statements, both about the Baltic (the world's most intensively
compression-forecast sea):

1. > "**Compression is a manifestation of ice cover stresses and a phenomenon physically different from
   > convergence.**"
2. > "Compression **cannot be predicted well in a deterministic forecast** since it can be a local and
   > quickly changing phenomenon, and is **very sensitive to small changes in wind speed and direction,
   > prevailing ice conditions, and model parameters**. A **probabilistic ensemble simulation** is
   > needed to produce a meaningful compression forecast."
3. > "In current numerical models the ice thickness distribution and drift are captured well, but
   > **compressive situations are often missing from forecast products**, though their inclusion is
   > requested by the shipping community… As compressing ice is capable of **stopping ships for days and
   > even damaging them**, its inclusion in ice forecasts is vital."

**Attribution**: these sentences are from the abstract of *Improving Ice Pressure Forecasting for
Operational Purposes*, OTC Arctic Technology Conference paper **OTC-25595-MS**, landing page
<https://onepetro.org/OTCARCTIC/proceedings-abstract/15OARC/15OARC/OTC-25595-MS/77472>.
**PARTIALLY VERIFIED — read this session only via search-engine renderings of the abstract; the
OnePetro page itself returned HTTP 403 and the full paper was not accessible.** The wording above is
reproduced as returned by search. **Before quoting any of this on a slide, obtain the paper and confirm
the exact sentences and the author list.** (A parallel ResearchGate record exists at
<https://www.researchgate.net/publication/313881026_Improving_Ice_Pressure_Forecasting_for_Operational_Purposes>,
also not fetched.)

Statement (1) is the crux and is worth restating in the team's own words: **convergence is a
kinematic quantity (∇·u < 0) that you can compute; compression is a stress state that depends on the
ice's rheology, thickness distribution, and its boundary conditions.** The same convergence applied to
thin new ice produces rafting and harmlessly thickened young ice; applied to close pack against a rigid
barrier it produces the force that stops a ship.

Corroboration from an independent primary source: the Finnish Ice Service's own operational description
lists **ice pressure** as a field reported by *icebreakers* (i.e. human observation from the ice), and
describes its 10-day forecast as containing "anticipated ice pressure zones… **to the extent it can be
evaluated** based on both icebreaker observations and sea-ice models", with the underlying model being
**NEMO-SI³** for the early forecast days. **No formula, scale, or index for compression is given.**
Source: Eriksson, P. B., et al. (2025), *The Finnish Ice Service, its sea-ice monitoring of the Baltic
Sea and operational concept*, **Frontiers in Marine Science 12: 1561461**,
<https://doi.org/10.3389/fmars.2025.1561461>. **VERIFIED** (fetched this session).

That is the strongest possible evidence for the honest answer: **the world's most compression-aware ice
service, in a 2025 peer-reviewed description of its own operations, hedges its compression product with
"to the extent it can be evaluated" and leans on human icebreaker reports.**

### b.4 AARI compression charts — status: NOT CONFIRMED

The brief asked specifically about AARI (Arctic and Antarctic Research Institute, St Petersburg)
compression charts. **UNVERIFIED.** What was confirmed this session: AARI produces operational sea-ice
charts for navigation safety in *both* polar regions, compiled every 10 days during the navigation
season and monthly otherwise, encoded in the **SIGRID** grid format for exchange, and archived at NSIDC
(<https://nsidc.org/data/nsidc-0050/versions/1>, <https://nsidc.org/data/G02176>). What was **not**
confirmed: that AARI publishes a distinct *compression* chart product, or the point-scale (commonly
described as a 1–3 балла scale) sometimes attributed to Russian ice charts. The SIGRID-3 specification
PDF (<https://globalcryospherewatch.org/wordpress/wp-content/themes/global-cryosphere-watch/files/resources/JCOMM_TR23_SIGRID3.pdf>)
was downloaded but its text layer could not be extracted, so its code tables were not read directly.

**Do not assert an AARI compression scale in the deck.** The WMO three-class scale in §b.2 is verified
and is sufficient; cite that instead.

### b.5 Documented Antarctic besetting incidents

#### Akademik Shokalskiy + Xue Long, Commonwealth Bay, Dec 2013 – Jan 2014

Peer-reviewed analysis: **Wang, Z., Turner, J., Sun, B., Li, B., & Liu, C. (2014), "Cyclone-induced
rapid creation of extreme Antarctic sea ice conditions", *Scientific Reports* 4, 5317**,
<https://doi.org/10.1038/srep05317> (open access, PMC4060491). **VERIFIED** — fetched this session.

Facts, all VERIFIED from that paper unless marked:

| Element | Detail |
|---|---|
| Mechanism | **Cyclone-enhanced katabatic winds.** A low approaching from the west first *suppresses* katabatic flow (northerlies on its eastern flank); "once a low has moved to the east of a site the **katabatic flow is enhanced** because of the strong southerly flow on the storm's western side." The resulting violent south-easterlies are downslope flow "turned from the downslope direction by the Coriolis force." |
| Peak winds | **17.9 m/s on 24 Dec 00 UT; 16.8 m/s on 26 Dec** |
| **Were the winds exceptional?** | **NO.** The paper states these were "not exceptional (but in the highest 29 %)" against Decembers 1979–2012. Between events winds dropped to **1.5 and 0.8 m/s**, allowing consolidation. |
| Timescale | MODIS shows **large open water on 3 Dec** → floes drifted westward by **7 Dec** → "packed" by **15 Dec** → rescue requested **24 Dec**. So: **~2 weeks from open water to beset**, with decisive consolidation over days. |
| Ice thickness reached | **~2.5 m** |
| Rescue limit | *Xue Long* can break **<1.2 m** — i.e. the icebreaker sent to help was itself outclassed by a factor of two, and became beset |
| **The trap geometry** | Iceberg **B09B grounded in Commonwealth Bay in March 2011**. This "provided favorable conditions for **fast ice to grow around it, forming a northward protruding barrier**", which "**blocked the westward ice drift and hence aided sea ice consolidation on its eastern side**." |

**Why this case is the single most important input to our risk-field design.** The wind was in the top
29 % of Decembers — unremarkable. Any system that flags besetting risk on a **wind-speed threshold alone
would not have flagged this event.** What made it lethal was **geometry**: a grounded iceberg plus its
accreted fast-ice barrier, sitting downwind of mobile pack. The risk was in the *boundary condition*,
not the *forcing*. **INFERRED**, but directly from the paper's own causal chain.

Corollary, and it is uncomfortable: **the grounded-iceberg + fast-ice barrier that caused this is
exactly the pair of features our 25 km SIC field cannot distinguish** (see §a table rows 2 and 13, and
§d). A grounded berg is far sub-pixel; the fast ice around it reports as 100 % SIC identical to the
mobile pack pressing against it.

#### MV Magdalena Oldendorff, Muskegbukta Bay, June–November 2002

**Geographically the most relevant incident to this project** — it happened in the **Lazarev Sea /
Queen Maud Land sector**, serving **Novolazarevskaya**, which is ~3.5 km from India's **Maitri**.

- 21,000 tdw chartered vessel, returning from **Novolazarevskaya** carrying 79 Russian scientists from
  Novolazarevskaya and Mirny toward Cape Town when **~80 km of thick ice** blocked its path.
- **Beset from 11 June 2002.**
- *S. A. Agulhas* closed to ~370 km and airlifted **79 scientists + 11 crew** out by two Oryx
  helicopters (22 Squadron, SAAF) around 27 June.
- Argentine icebreaker **Almirante Irízar** attempted to lead her out from 19 July; on **30 July**, in
  **−32 °C and "rapidly closing ice"**, the attempt was **abandoned**.
- The icebreaker moved her to a safe position in **Muskegbukta Bay** and transferred **overwintering
  supplies for a skeleton crew of 17**.
- She **freed herself in late November 2002** and reached Cape Town before Christmas.
- **ESA tasked Envisat ASAR** (SAR, night-capable) to support the rescue.

Sources: ESA, *Envisat's night eye supports icebound ship rescue in Antarctica*,
<https://www.esa.int/Applications/Observing_the_Earth/Envisat_s_night_eye_supports_icebound_ship_rescue_in_Antarctica>;
Scott Polar Research Institute / WDC for Glaciology, <https://wdcgc.spri.cam.ac.uk/news/ship>;
*Science*, <https://www.science.org/content/article/scientists-rescued-from-stranded-ship>.
**VERIFIED via these sources as returned by search; the ESA and SPRI pages were not individually
re-fetched.** Treat the specific dates as **HIGH-CONFIDENCE but re-check before slide use.**

**Two honest caveats the team must state, not hide:**

1. **This was an austral WINTER besetting (11 June).** It is *not* a Dec–Apr voyage-window event and
   must not be presented as one. Its relevance is **(i)** the sector (Lazarev Sea, Queen Maud Land,
   Maitri's own approach), **(ii)** the demonstration that a besetting in this sector can last **five
   months** and defeat a purpose-built icebreaker, and **(iii)** that the operational response was to
   task **SAR imagery**, which is exactly the capability `DATASET.md` §2 already sources.
2. Precise besetting coordinates were not confirmed this session. **UNVERIFIED.**

#### What the two cases have in common

| | Shokalskiy 2013 | Magdalena Oldendorff 2002 |
|---|---|---|
| Season | Austral summer (Dec) | Austral winter (Jun) |
| Sector | Commonwealth Bay, ~67°S 143°E | Lazarev Sea, ~70°S 12°E (**our sector**) |
| Forcing | Cyclone-enhanced katabatic, peak 17.9 m/s — **unexceptional** | Not established this session |
| Barrier | Grounded iceberg B09B + accreted fast ice | Coastal / fast-ice constriction (~80 km of ice) |
| Vessel state | Stationary (science ops) at time of packing | Slow, transiting out |
| Rescue icebreaker outcome | **Also beset** | **Abandoned the attempt** |
| Duration | ~2 weeks | ~5 months |

**The common structure — and this is what the risk field should encode: high concentration + a rigid
downwind barrier + persistent onshore/along-barrier wind + a slow or stationary vessel.** Not wind
speed. Not concentration. The *conjunction*. **INFERRED** from the two case records.

### b.6 KEY QUESTION, answered directly

> **Can compression risk be estimated from sea-ice concentration + wind fields alone (the inputs this
> project has), and what is the accepted operational proxy/formula for that, if one exists?**

**Answer, in three parts.**

**1. No — compression itself cannot be estimated from SIC + wind alone, and no accepted formula
exists.** Compression is a **stress** state; SIC and wind give you **kinematics**. The primary sources
say so explicitly: compression is "physically different from convergence" and "cannot be predicted well
in a deterministic forecast" (§b.3), and the international standard represents it as a hand-drawn
three-class symbol with no defined thresholds (§b.2). Any product claiming a computed compression value
from SIC + wind is over-claiming. **Do not build one.**

**2. What *does* exist operationally is a full dynamic–thermodynamic sea-ice model with a rheology,
run as an ensemble.** FMI uses NEMO-SI³ plus icebreaker reports; the OTC work argues explicitly for
**probabilistic ensembles** because compression is hyper-sensitive to small wind perturbations. This is
outside this project's scope and schedule, and saying so is a strength, not a weakness.

**3. What this project *can* legitimately build is a kinematic CONVERGENCE proxy plus a geometric
BARRIER term, presented as a hazard flag on the WMO three-class scale.** Concretely:

**Term 1 — kinematic convergence.** Compute the horizontal divergence of the sea-ice velocity field:

```
div(u) = ∂u/∂x + ∂v/∂y          [units: s⁻¹, or day⁻¹ at daily sampling]

convergence = −div(u),   flagged where convergence > 0
```

This is textbook ice kinematics and is not an invented index. Two real, free sources of **u** exist:

- **NSIDC-0116 v4, *Polar Pathfinder Daily 25 km EASE-Grid Sea Ice Motion Vectors*** — **25 km, daily,
  Southern Hemisphere included (−37° to −90°), 1 Nov 1978 – 31 Dec 2024, free via HTTPS/wget**, inputs
  AVHRR/AMSR-E/SMMR/SSMI/SSMIS + buoys + NCEP/NCAR reanalysis.
  <https://nsidc.org/data/nsidc-0116>. **VERIFIED.** **This is on precisely the project's 25 km grid —
  it drops straight into the existing pipeline.** It is not currently in `DATASET.md`. **Add it.**
- **OSI SAF OSI-455 sea-ice drift CDR** — Lavergne, T. & Down, E. (2023), *ESSD* 15, 5807–5834,
  <https://doi.org/10.5194/essd-15-5807-2023>. **75 km spacing** on EASE2, daily 24 h displacement
  (12:00–12:00 UTC), both hemispheres, 1991–2020. Validation RMSE vs buoys: Arctic winter 2.1 km,
  Arctic summer 2.6 km, **Antarctic 3–4 km**. **VERIFIED.**
  **Two limitations that matter enormously here, both stated by the authors:** (i) summer tracking from
  microwave imagery is "much less reliable" due to surface melt — so summer vectors come from a
  **free-drift parametric model forced with ERA5 wind**, i.e. in the project's own Dec–Apr window the
  "observed" drift is substantially a wind extrapolation; (ii) **"no vectors distributed near
  coastlines"** and validation excludes MIZ and coastal regions — i.e. **the product is blank exactly
  where besetting happens.**

  Point (i) is not fatal — it is a *verified precedent* that wind-forced free drift is an acceptable
  operational way to obtain Antarctic summer ice motion. Cite Lavergne & Down for that legitimacy.
  Point (ii) means OSI-455 alone cannot support a coastal-besetting proxy. **Prefer NSIDC-0116.**

  *(The classical free-drift closure — ice speed ≈ ~2 % of the 10 m wind, deflected some tens of degrees
  — is **UNVERIFIED this session**. Do not put specific coefficients on a slide without a citation.)*

**Term 2 — the barrier / boundary condition.** From §b.5, convergence only becomes dangerous when the
ice has nowhere to go. Encode a **downwind-obstruction** term: for each cell, look downwind along the
wind (or ice-drift) vector for, within some distance, any of — the coast, a fast-ice edge, a grounded
iceberg, or a sharp SIC gradient into ≥95 % ice. This is a geometric computation over fields the
project already has (GEBCO coastline, SIC gradient) plus one it must add (fast ice — see §a table row
2, named gap).

**Term 3 — vessel state.** Both case studies involved a **slow or stationary** vessel. Besetting risk is
not a property of the ice alone. A route that has the ship *lingering* in a converging, barrier-backed
cell is qualitatively different from one that transits it. This is naturally expressible as a cost
that scales with **dwell time in the cell**, which the mesh/Dijkstra formulation (`GAP_ANALYSIS.md`,
PolarRoute 3D-DSP) already carries as a time dimension.

**Proposed composite, presented as a categorical flag — not a physical quantity:**

```
besetting_flag(cell, t) = f( SIC ≥ close-pack threshold,
                             convergence = −div(u) > 0,
                             downwind_barrier_within(D),
                             dwell_time(cell) )
   → mapped onto WMO {none, slight, considerable, strong} compacting classes
```

**Label this in the UI and the deck as an "ice-convergence hazard flag", explicitly NOT an "ice
compression forecast".** State that no validated Antarctic compression forecast exists, that the
international standard for compression is itself a three-class qualitative human judgement, and that
this flag is a screening proxy for the *preconditions* documented in the Shokalskiy and Oldendorff
cases. **That framing is both true and stronger in front of a judge than a fake number would be** — it
demonstrates that the team read the standard and found the honest boundary of what is computable.

**Unresolved and worth stating as such:** the thresholds (what convergence rate, what barrier distance
D, what dwell time) are **not derivable from any source found this session**. They must either be tuned
against real Antarctic besetting cases (a tiny sample — arguably too tiny to fit) or set conservatively
by hand and declared as expert-set, not learned. **UNVERIFIED — do not claim these are calibrated.**

---

## (c) Blizzards and katabatic winds in the austral summer (Dec–Apr)

### c.1 Mechanism

Katabatic wind is gravity-driven drainage of cold, dense air down the Antarctic ice-sheet slope, with
direction largely set by topography and deflected by the Coriolis force. **VERIFIED** (Wang et al. 2014,
§b.5, which describes the Commonwealth Bay south-easterlies as downslope flow "turned from the downslope
direction by the Coriolis force").

The operationally important point, made independently by two primary sources, is that **pure katabatic
drainage is not what produces the dangerous events — the dangerous events are synoptic cyclones
reinforcing katabatic drainage:**

- Wang et al. 2014: a low west of the site suppresses katabatic flow; once it moves **east** of the
  site, "the katabatic flow is **enhanced** because of the strong southerly flow on the storm's western
  side." **VERIFIED.**
- Lal & Ram 2009 (IMD, on Maitri): "Winds in the coastal region of East Antarctica are driven by
  **mesoscale katabatic winds and synoptic-scale cyclonic systems**… that superimpose gradient winds
  over the low-level mesoscale flow. The strongest winds are generally forced by **offshore cyclonic
  vortices** that move primarily 'around the coast'… When in the appropriate location, these depressions
  can **reinforce the drainage flow at the coast**." It further notes that this is "in contrast to pure
  drainage flow, which **does not persist for extended periods** due to exhaustion of the upstream
  supply of air." **VERIFIED** (see §c.2 for the citation).

**Design consequence.** The predictable, forecastable part of this hazard is the **synoptic cyclone
track**, which ERA5/GFS resolve well at 0.25°, superimposed on a **topographically fixed** katabatic
climatology. This is a genuinely favourable structure for a forecast system: the persistent part is
static and the variable part is well-forecast. **INFERRED.**

### c.2 Frequency and intensity at the Indian Antarctic stations — real station data

**Primary source, and it is the best possible one for this project**: Lal, R. P. & Ram, S. (2009),
*Climatology of blizzards over Schirmacher Oasis, east Antarctica*, **MAUSAM 60(1), 39–50**, India
Meteorological Department. PDF:
<https://mausamjournal.imd.gov.in/index.php/MAUSAM/article/download/960/803/3457>. **VERIFIED** —
downloaded and text-extracted this session. This is **IMD's own analysis of 16 years of observations
recorded by Indian expeditions at Maitri**, plus 6 years at **Dakshin Gangotri**.

**Blizzard definition used** (station practice at Maitri): surface wind **> 23 kt** with moderate-to-heavy
drifting or blowing snow reducing visibility to **< 1000 m**. **VERIFIED.**

**Table 2 — Maitri (70°45′57″S, 11°44′09″E; Schirmacher Oasis, ~100 km inland, 117 m elevation),
1990–2005, n = 339 blizzards. VERIFIED, transcribed from the paper.**

| Month | Total blizzards (16 yr) | % of annual | Avg blizzards/yr | **Avg blizzard-days/yr** |
|---|---|---|---|---|
| Jan | 2 | 0 | 0.1 | **0.3** |
| Feb | 5 | 1 | 0.3 | **0.5** |
| Mar | 27 | 8 | 1.7 | **3.0** |
| **Apr** | 39 | 12 | 2.4 | **5.3** |
| May | 50 | 15 | 3.1 | 6.3 |
| Jun | 36 | 11 | 2.3 | 4.8 |
| Jul | 48 | 14 | 3.0 | 6.1 |
| Aug | 44 | 13 | 2.8 | 6.6 |
| Sep | 38 | 11 | 2.4 | 5.1 |
| Oct | 30 | 9 | 1.9 | 4.0 |
| Nov | 13 | 4 | 0.8 | 2.1 |
| **Dec** | 7 | 2 | 0.4 | **0.9** |
| **Total** | **339** | 100 | **21.2** | **45.0** |

The paper states: **"85 % of total blizzard occurred during April to October and only 15 % during
January, February, March, December and November."** **VERIFIED.**

**Table 3 — Dakshin Gangotri (69°59′23″S, 11°56′26″E; "in Lazarev Sea area of Queen's Maud Land",
i.e. on the ice shelf ~85 km north of Maitri, at the COAST), 1984–1989, n = 303. VERIFIED,
transcribed from the paper.**

| Month | Total blizzards (6 yr) | Avg blizzards/yr | % of annual | **Avg blizzard-days/yr** |
|---|---|---|---|---|
| Jan | 9 | 1.8 | 3.5 | **5.2** |
| Feb | 21 | 4.2 | 8.2 | **9.6** |
| Mar | 27 | 4.5 | 8.7 | **11.5** |
| **Apr** | 30 | 5.0 | 9.7 | **10.7** |
| May | 28 | 4.7 | 9.1 | 12.0 |
| Jun | 27 | 4.5 | 8.7 | 12.8 |
| Jul | 33 | 5.5 | 10.7 | 10.2 |
| Aug | 26 | 4.3 | 8.3 | 8.0 |
| Sep | 22 | 3.7 | 7.2 | 9.3 |
| Oct | 31 | 5.2 | 10.1 | 10.5 |
| Nov | 31 | 5.2 | 10.1 | 9.5 |
| **Dec** | 18 | 3.0 | 5.8 | **5.3** |
| **Total** | **303** | **51.5** | 100 | **114.6** |

### c.3 The finding that matters most in (c) — and it is easy to get wrong

**The coastal site experiences roughly 5–20× more summer blizzard-days than the inland oasis site.**

| Month (voyage window) | Maitri (inland) blizzard-days/yr | Dakshin Gangotri (**coastal**) blizzard-days/yr | Ratio |
|---|---|---|---|
| Dec | 0.9 | **5.3** | ~6× |
| Jan | 0.3 | **5.2** | ~17× |
| Feb | 0.5 | **9.6** | ~19× |
| Mar | 3.0 | **11.5** | ~4× |
| Apr | 5.3 | **10.7** | ~2× |
| **Dec–Apr total** | **10.0** | **42.3** | **~4×** |

**INFERRED** (arithmetic on the two VERIFIED tables).

**Why this is load-bearing.** The ship, the anchorage, the barge runs and the over-ice cargo traverse
all happen **at the coast**, not at Schirmacher Oasis. Maitri's blizzard climatology — which is the
number anyone would find first, because Maitri is the famous station — **understates the hazard at the
place the ship actually operates by roughly a factor of four over the voyage window, and by a factor of
~17–19 in January and February.** A team that quotes "Maitri sees almost no summer blizzards" is
quoting a real number about the wrong location.

**Caveats, stated plainly:**
- Different periods (1984–89 vs 1990–2005) and different instruments/observers. Some of the gap is
  epoch and practice, not geography. **However**, the ratio is far too large to be explained by
  inter-decadal variability alone, and the coastal-vs-inland physics (drainage flow accelerating down
  the escarpment and the coastal cyclone track) predicts exactly this sign and rough magnitude.
  **INFERRED, moderate confidence.**
- Dakshin Gangotri's 6-year record is short; the monthly numbers have wide error bars that the paper
  does not quote. **UNVERIFIED** (no confidence intervals published).
- **Recommendation**: present both rows side by side and let the contrast be the point. Do not average
  them, and do not quote only Maitri.

### c.4 Intensity

From the same IMD paper, **VERIFIED**:

- **Average maximum wind speed during a blizzard: ~52 kt (~27 m/s).**
- **Exceeded 100 kt (~51 m/s) on several occasions.**
- Distribution of blizzard maximum winds at Maitri: **27 % in 41–50 kt; 19 % in 31–40 kt; 18 % in
  51–60 kt; 85 % of all blizzards had max wind up to 70 kt.**
- **Average duration 25 hours.** Longest **168 hours (7 days), June 1997**. **12 occasions exceeded
  72 hours.**
- **No significant correlation** between blizzard duration and maximum wind speed; none between max wind
  and temperature rise; none between wind speed and pressure departure.
- MSL pressure: average max 987.2 hPa, average min 976.3 hPa during blizzards; lowest recorded 944 hPa
  (July 2005).

**The "no correlation between duration and intensity" result is operationally significant**: a
25-hour-mean event that can run 7 days, with duration unpredictable from the observed wind, means an
anchorage/cargo decision cannot be made on "how strong is it" alone. **INFERRED.**

Note also, for context on how quickly Antarctic near-surface wind climatologies vary along the coast:
katabatic winds **exceed 15 m/s southwest of Cape Darnley** while remaining **below 10 m/s over the flat
Amery Ice Shelf** — a first-order change over a short distance driven purely by slope. **VERIFIED**
(reported in the coastal-polynya literature, see §c.5 sources; note this is a *Prydz Bay* datum,
relevant to the **Bharati** leg).

### c.5 Effect on cargo and personnel transfer — Bharati specifically

**Primary source**: *Larsemann Hills, East Antarctica — Antarctic Specially Managed Area No. 6
Management Plan*, Measure 15 (2014), ATCM XXXVII Final Report. PDF:
<https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/asma/asma_pdf_en/ASMA06_en.pdf>.
**VERIFIED** — downloaded and text-extracted this session. This is an **Antarctic Treaty instrument**
covering the area containing India's **Bharati** station.

Quoted verbatim, **VERIFIED**:

- §4.2 Climate: **"A major feature of the climate of the Larsemann Hills is the existence of persistent
  and strong katabatic winds that blow from the north-east on most summer days."** Daytime Dec–Feb air
  temperatures frequently exceed 4 °C and can exceed 10 °C; mean monthly a little above 0 °C.
- §4.2, same paragraph: **"The pack ice is extensive inshore throughout summer, and the fjords and bays
  are rarely ice-free."**
- §4.5.2 Sea access: **"No anchorages or barge landings are designated for the Area due to the variable
  sea ice conditions. Vessels usually anchor approximately 5 nm offshore, depending on ice conditions,
  however vessels chartered by India have reached as close as 50 m away from the site of Bharati."**
- §4.5.2 continues: **"Access from ships to the eastern shore of Broknes by small boat is difficult and
  sometimes impossible"** due to ice conditions.
- Station operations: **"Resupply is generally undertaken once a year in summer. Until mid-December,
  cargo is transported ashore using Pisten Bullies and trailers over fast ice. Voyages after the melting
  of the fast ice use flat bottom barges for carrying cargo."**
- Neighbouring Progress IV (Russia) is described as a site "used for the staging of heavy cargo
  delivered **ship-shore across the fast ice**."
- **"Sea ice usually persists in the fjords and between the shore and numerous near-shore islands until
  late in the summer season."**

**What this means for the risk field — and it is a genuinely non-obvious operational structure:**

1. **There is a mid-December mode switch.** Before ~mid-December, cargo crosses **fast ice** on tracked
   vehicles; after fast-ice breakup, it goes by **barge**. These two modes have *opposite* preferences:
   the over-ice mode wants the fast ice **intact and thick**; the barge mode wants it **gone**. A
   routing/decision system that treats "less ice = better" unconditionally gets the early-season case
   exactly backwards. **INFERRED**, directly from the quoted text.
2. **The anchorage distance is itself ice-dependent and varies by two orders of magnitude** — "usually
   ~5 nm offshore" but Indian-chartered vessels "have reached as close as 50 m." That range (≈9 km down
   to 50 m) is far below the 25 km grid's ability to inform. **The final approach is not a
   25 km-forecastable decision** and the product should not pretend otherwise. **INFERRED.**
3. **Katabatic winds blow on "most summer days"** at Bharati — this is a persistent background
   condition, not an event. The event is the blizzard superimposed on it (§c.1).
4. The ASMA plan gives **no wind speed figures**. The Bharati-specific wind *intensity* climatology is
   **UNVERIFIED** and remains a gap — §c.2's numbers are for the **Maitri/Queen Maud Land** sector, not
   Prydz Bay.

### c.6 Katabatic winds OPEN coastal polynyas — this is a routing OPPORTUNITY

**This is the counter-intuitive point in the brief, and it is correct.**

**Mechanism, VERIFIED**: Antarctic coastal polynyas are formed and maintained by strong, persistent
**katabatic winds that push sea ice away from the coast** — a latent-heat (wind-driven) polynya. The
katabatic flow is a gravity-driven downslope cold flow whose direction is controlled largely by
topography, so the polynyas it opens are **fixed in location and recur annually** (which is exactly
WMO 7.4.3, *recurring polynya*).

**Primary reference**: Nihashi, S. & Ohshima, K. I. (2015), *Circumpolar Mapping of Antarctic Coastal
Polynyas and Landfast Sea Ice: Relationship and Variability*, **Journal of Climate 28(9), 3650–3670**,
<https://doi.org/10.1175/JCLI-D-14-00369.1>. Key structural finding, **VERIFIED via the journal listing
and abstract**: large polynyas — **Cape Darnley, Barrier, Shackleton, Vincennes Bay, Dalton, Dibble,
Amundsen** — form **on the western (lee) side of landfast ice**, while **Mertz and Terra Nova Bay**
polynyas form **adjacent to glacier tongues with fast ice**. Method: AMSR-E thin-ice-thickness and
fast-ice detection; thin ice **< ~0.2 m** estimated from the AMSR-E brightness-temperature polarisation
ratio.

**Cape Darnley and Mackenzie Bay are the two major coastal polynyas of the Prydz Bay region** — i.e. the
**Bharati** approach sector. **VERIFIED.** Katabatic winds there exceed **15 m/s** southwest of Cape
Darnley (§c.4).

**So the routing framing is:**

> The same katabatic wind that makes the coastal approach dangerous for cargo transfer is the wind that
> holds open a band of navigable water against the coast. Coastal polynyas are the **last leg's
> opportunity**, and they are **persistent and predictable in location** because their driver is fixed
> topography.

**Four caveats that must accompany that claim, or it becomes a liability:**

1. **A polynya is a sea-ice factory, not a warm lagoon.** It is open water losing heat to a −20 °C
   katabatic gale; it is the highest sea-ice-production environment on Earth (this is why Cape Darnley
   makes Antarctic Bottom Water). It refreezes continuously into frazil/grease/nilas. WMO 7.4 says it
   directly: a polynya **"may contain brash ice and/or be covered with new ice, nilas or young ice."**
   **VERIFIED.** "Open water on the map" is not the same as "navigable, ice-free water."
2. **The open water comes packaged with a 15–25 m/s offshore wind**, which is precisely the condition
   that makes small-boat and barge transfer impossible (§c.5). Opportunity for the *hull*, hazard for
   the *cargo operation*. These are two different decisions and the system should not conflate them.
3. **Direction decides everything.** The exact same katabatic forcing that opens a lee-side polynya
   will, if the barrier lies *downwind* instead of upwind, pack ice into a besetting trap — that is
   literally the Shokalskiy case (§b.5), where cyclone-enhanced katabatic winds drove ice **onto** a
   grounded-berg-plus-fast-ice barrier. **Wind and barrier geometry, evaluated together, is what
   separates the opportunity from the trap. Neither wind speed alone nor SIC alone can tell them
   apart.** This is the single most important synthesis in this document.
4. **The 25 km SIC field is compromised in exactly the coastal band where polynyas live** — see §d.

### c.7 Who actually forecasts this

| System | What it is | Verified specs | Use for this project |
|---|---|---|---|
| **ERA5** (ECMWF / Copernicus CDS) | Reanalysis, 0.25° hourly, 1940–present | Already in `DATASET.md` §5.1 | **Training / climatology.** Resolves the synoptic cyclones that drive blizzards. Does **not** resolve mesoscale katabatic jets at coastal-escarpment scale. **INFERRED** from 0.25° ≈ 28 km vs the Cape Darnley / Amery 15 vs 10 m/s contrast (§c.4). |
| **GFS** (NOAA) | Operational forecast to 384 h, free, no auth | Already in `DATASET.md` §5.2 | **Live routing wind.** Same mesoscale caveat as ERA5. |
| **AMPS — Antarctic Mesoscale Prediction System** | "An experimental, **real-time** numerical weather prediction capability that provides support for the United States Antarctic Program, Antarctic science, and **international Antarctic efforts**." Runs **WRF** and **MPAS**; **twice-daily forecasts covering Antarctica**; run by **NCAR** with NSF Office of Polar Programs support. Homepage <https://www2.mmm.ucar.edu/rt/amps/>; project page <https://www.mmm.ucar.edu/projects/amps>. **VERIFIED** (project page fetched this session). Resolutions reported (via the BAMS decadal review and secondary listings, **not** re-verified on the project page): improved from 45/15/5/1.67 km to **30/10/3.3/1.1 km**, with the whole continent at 10 km and 60 vertical levels to 10 hPa. **PARTIALLY VERIFIED — treat the specific grid numbers as needing confirmation.** | **This is the right tool for the katabatic/coastal-wind layer, and it is a named, credible, US-agency system that explicitly serves "international Antarctic efforts."** Its 10 km continental grid is 2.5× finer than ERA5 and is the only listed system that plausibly resolves the katabatic jets. **Not currently in `DATASET.md` — evaluate and add.** Whether AMPS output is bulk-downloadable for our corridor, its licence, and its Queen Maud Land / Prydz Bay coverage were **NOT confirmed this session — UNVERIFIED.** Reference paper: *A Decade of Antarctic Science Support Through AMPS*, **BAMS 93(11)**, <https://journals.ametsoc.org/view/journals/bams/93/11/bams-d-11-00186.1.xml>. |
| **ECMWF operational IFS** | Global operational NWP | Not investigated this session | Named in the brief; **UNVERIFIED** for access terms. ERA5 (its reanalysis sibling) is already sourced. |

---

## (d) What a 25 km sea-ice concentration product CANNOT see

This is the honest-limitations section. It should be a slide.

**The pixel is 625 km². The forecast is a concentration percentage. There is no thickness, no stage of
development, no floe size, no deformation state, and no distinction between ice that is drifting and ice
that is welded to the coast.**

### d.1 Structurally invisible — sub-pixel by orders of magnitude

| Hazard | Its size | Fraction of one 625 km² pixel |
|---|---|---|
| **Growler** (~20 m²) — the classic hull-holing hazard | 20 m² | **3 × 10⁻⁸** |
| **Bergy bit** (100–300 m²) | ≤300 m² | **5 × 10⁻⁷** |
| **Brash ice** fragments (≤2 m) | ≤4 m² | ~6 × 10⁻⁹ |
| **Pressure ridge** (width tens of m, length km) | ~10⁻² km² per km length | ~10⁻⁵ |
| **Tide crack** | metres wide | negligible |
| **Small / medium floes** (20–500 m) | ≤0.25 km² | ≤4 × 10⁻⁴ |
| **Jammed brash barrier** (0.1–5 km wide, **2–20 m deep**) | ≤5 km wide | never resolved in width |
| **Navigable lead** (typically ≤500 m; even "large fracture" is >500 m) | ≤~1 km wide | **the route itself is sub-pixel** |

**INFERRED** — arithmetic against the WMO size definitions in §a, all of which are VERIFIED.

### d.2 Present in the pixel but not distinguishable — the more dangerous category

These are worse than the invisible ones, because the field *reports something* and that something is
ambiguous:

1. **Ice thickness / stage of development.** A cell at 90 % SIC may be 90 % **nilas (<10 cm)** or 90 %
   **thick first-year ice (>120 cm)**. These differ by more than an order of magnitude in what they do
   to a hull, and **the 25 km SIC field assigns them the same number.** *Xue Long* — a real icebreaker —
   was stopped by 2.5 m ice against a 1.2 m capability (§b.5). **A concentration-only cost function
   cannot express that failure.**
2. **Fast ice vs. consolidated drifting pack.** Both report ~100 %. One is a 100 km-wide immovable
   barrier; the other is mobile ice a strengthened ship can work through. **This is the distinction that
   the Shokalskiy trap was built from.**
3. **Deformation state.** Level ice at 95 % and heavily ridged ice at 95 % are the same pixel. Ridge
   density and keel depth, not concentration, govern icebreaker progress.
4. **Floe size.** 80 % SIC in small floes vs. 80 % in vast floes are different voyages.
5. **Whether "open water" is actually open.** WMO 7.4 explicitly allows a polynya to be "covered with
   new ice, nilas or young ice" — and passive microwave under-detects thin ice, so a refreezing polynya
   may read as *more* open than it is. **VERIFIED** from both WMO 7.4 and the Climate Data Guide thin-ice
   statement.
6. **Ice compression.** By construction: at 10/10 concentration, compacting shows up only as **stress**,
   which a concentration field has no channel for (§b.1). **The most dangerous ice state is the one the
   product is definitionally blind to.**

### d.3 Measurement pathologies — where the number itself is wrong, not just coarse

All **VERIFIED** from the NCAR Climate Data Guide entry for this exact product family
(<https://climatedataguide.ucar.edu/climate-data/sea-ice-concentration-noaansidc-climate-data-record>)
and NSIDC G02202 documentation:

| Pathology | Statement | Why it bites *this* project specifically |
|---|---|---|
| **Melt-season underestimation** | "Surface melt and thin ice, often leads to **large underestimation of concentration**" | The voyage window **is** the melt season. The bias is toward reporting the route as *clearer than it is*. |
| **Ice-edge unreliability** | "least reliable close to the ice edge and during melt conditions, where **biases may be 20-30 %**" (vs ~5–10 % in the consolidated winter pack) | The MIZ crossing is the decisive routing choice, and it is where the input is worst. This compounds the already-documented CMEMS MIZ under-estimate (`COMPETITIVE_ANALYSIS.md` §2). |
| **Land spillover** | "This leads to **false ice along the coast**. Automated filters remove much of such ice, but some may remain." NSIDC further notes the spillover filter "may affect the area of some open water features within the ice pack near coasts such as polynyas." | **The correction and the artifact both live in the coastal band — which is exactly where the coastal polynyas of §c.6 are, and exactly where besetting happens.** The one place the product could offer the biggest routing prize is the one place its coastal handling is least trustworthy. |
| **Weather false-ice** | "Thick precipitating clouds, as well as wind roughening of the surface, can lead to **false ice returns over open ocean**" | Southern Ocean storms are exactly thick-precipitating and wind-roughening. The `qc_flags` layer (`ARCHITECTURE.md` §4.1) is the right mitigation; this is the citation justifying it. |
| **Effective scale** | "least reliable for **small-scale studies (e.g., <100 km)**" | **The effective decision scale is ~100 km, not 25 km.** A route drawn to 25 km precision implies a precision the input does not have. |
| **Fitness for purpose** | "The low spatial resolution limits the precision of the ice edge location and **makes the products of limited use for operational support (e.g., navigation)**" | The data providers' own expert community says this product is of limited use for navigation. **Quote it first, before a judge finds it.** |

### d.4 The one-slide version

> **A 25 km sea-ice concentration field tells you where the ice is, roughly, at ~100 km effective
> precision. It does not tell you how thick it is, whether it is moving or welded to the coast, whether
> it is ridged, how big the floes are, whether the leads are open, whether the ice is under compression,
> or whether there is a growler in it. Every ship that has been beset in the Antarctic was beset by
> something in that second list.**
>
> **What we do about it:** forecast the field we can forecast, attach honest calibrated uncertainty to
> it, derive a *convergence hazard flag* rather than a fake compression number, name SAR as the route to
> the deformation-scale hazards, and never let the route line imply a precision the input cannot carry.

That is a stronger position than claiming completeness, and it is the position the primary sources
support.

---

## §5 Direct implications for the routing cost function

Concrete, actionable, ordered by value:

1. **Add a fast-ice layer.** It is the highest-value missing field in the whole hazard stack: it is the
   difference between "100 % ice you can work through" and "100 % ice that is a wall", and it is the
   anchor of both documented besetting traps. Candidate: the Nihashi & Ohshima (2015) fast-ice detection,
   or a circum-Antarctic landfast product (an ESSD preprint on high-resolution circum-Antarctic landfast
   mapping exists: <https://essd.copernicus.org/preprints/essd-2020-99/essd-2020-99.pdf> — **not fetched,
   UNVERIFIED**).
2. **Add NSIDC-0116 v4 ice-motion vectors (25 km, daily, Antarctic, free)** to `DATASET.md` and compute
   `−div(u)` as the convergence term. It is already on the project's grid. **VERIFIED available.**
3. **Build the besetting flag as a conjunction, not a threshold** — high SIC **AND** convergence **AND**
   a downwind barrier **AND** dwell time. Justify it by the Shokalskiy case, where wind speed alone was
   in the top 29 % (i.e. unremarkable) and a wind-threshold rule would have failed.
4. **Report compression on the WMO three-class scale** (slight / considerable / strong) and label it an
   *ice-convergence hazard flag*, never an *ice compression forecast*.
5. **Use WMO concentration vocabulary in the UI** (very open / open / close / very close / consolidated
   pack ice) — free credibility with an MoES/NCPOR audience.
6. **Encode the mid-December cargo mode switch at Bharati** as an explicit constraint: before breakup,
   intact fast ice is an *asset* (vehicle traverse); after breakup, it is an *obstacle* (barge access).
   Monotone "less ice is better" is wrong for part of the season. **This is a differentiator — it comes
   from an Antarctic Treaty management plan, not from generic ice-routing literature.**
7. **Combine the ERA5/GFS wave field with SIC to give a physical MIZ**, matching WMO 4.4.11's
   wave-penetration definition rather than only a concentration band. Cheap; the wave data is already
   sourced.
8. **Do not attempt a growler/bergy-bit layer.** Say honestly that no satellite or model sees them, that
   even WMO notes they are hard to see visually among sea ice or in high sea state, and that mitigation
   is procedural. This is already the position in `VIVA_PREP.md` and `WEAKNESS_ANALYSIS.md` — §a rows 13
   and 14 now give it a WMO citation.
9. **Evaluate AMPS** for the coastal katabatic layer before committing to ERA5/GFS alone near the
   stations.

---

## §6 Unreachable, paywalled, or dead sources

Stated explicitly rather than silently worked around:

| Source | What was wanted | Outcome |
|---|---|---|
| OnePetro, **OTC-25595-MS** *Improving Ice Pressure Forecasting for Operational Purposes* | Full method, any compression formula, author list | **HTTP 403.** Abstract sentences obtained only via search-engine rendering. **Quotes in §b.3 need confirmation from the paper before slide use.** |
| MDPI **JMSE 13(7):1267**, *Vessel Safety Navigation Under the Influence of Antarctic Sea Ice* (doi 10.3390/jmse13071267) | Antarctic-specific RIO/RIO* risk-index formula and RIV table; besetting hotspots | **HTTP 403** on both `doi.org` redirect target and direct `curl` with browser UA. **Not read.** This is the most relevant single paper found for the routing risk index and **should be retrieved by another route** (institutional access, or the ResearchGate copy). |
| **SIGRID-3** spec, JCOMM TR-23 (PDF, 458 KB) | WMO SIGRID code tables for stage of development, floe size, ridging/compression codes | Downloaded (HTTP 200) but the **PDF text layer could not be extracted** (FlateDecode, no OCR run). Code tables **not read**. The equivalent information was obtained from WMO No. 259 Vol. III instead. |
| **Nordic Cryosphere Digital Twin**, TemaNord 2025:565, *Six use cases supporting specific sea ice phenomena* | An open-access modern statement of how compression is operationally handled and what resolution it needs | **HTTP 403.** Not read. Likely a good source; worth retrying. |
| **AARI** compression chart product / point scale | Confirm existence and definition of a Russian compression scale | **Not found.** AARI chart production and SIGRID encoding confirmed; a distinct compression product/scale **not confirmed**. See §b.4. |
| **AMPS** grid resolutions, output access, licence, corridor coverage | Confirm the 30/10/3.3/1.1 km figures and whether output is bulk-downloadable for the Cape Town–Bharati corridor | Project page fetched and confirms model/operator/cadence; **resolution figures came from secondary listings and are PARTIALLY VERIFIED. Access terms UNVERIFIED.** |
| Nihashi & Ohshima (2015), *J. Climate* 28, 3650 | Full text: polynya area statistics, detection thresholds | Abstract-level findings only (structure of lee-side polynyas, AMSR-E thin-ice <0.2 m method). Full text **not fetched**. |
| ESA / SPRI / *Science* pages on **Magdalena Oldendorff** | Confirm dates and coordinates independently | Content obtained via search rendering; individual pages **not re-fetched**. Dates are HIGH-CONFIDENCE; **besetting coordinates UNVERIFIED**. |
| Bharati / Larsemann Hills **wind-speed** climatology | Intensity numbers for the Prydz Bay coast equivalent to §c.2's Queen Maud Land numbers | **Not found.** The ASMA plan gives direction and persistence but **no speeds**. **Named gap.** |
| Free-drift wind-factor coefficients (ice speed ≈ % of wind, turning angle) | A citable value | **UNVERIFIED.** Wind-forced free drift as an *accepted operational method* is verified (Lavergne & Down 2023); the coefficients are not. |

---

## §7 Backlog lines

**Merged into `docs/backlog.md` during post-workflow reconciliation (2026-09-02)** — see its "Open —
research follow-ups" and "Open — demo honesty" sections. Not duplicated here.

---

## Source list

**Primary, fetched and read this session (VERIFIED):**

1. WMO, *Sea-Ice Nomenclature (WMO No. 259)*, snapshot to ETSI-V March 2014 — <https://nsidc.org/sites/default/files/wmo-259-2015_multilingual.pdf>
2. Wang, Z., Turner, J., Sun, B., Li, B. & Liu, C. (2014), *Cyclone-induced rapid creation of extreme Antarctic sea ice conditions*, **Sci. Rep. 4, 5317** — <https://doi.org/10.1038/srep05317>
3. Lal, R. P. & Ram, S. (2009), *Climatology of blizzards over Schirmacher Oasis, east Antarctica*, **MAUSAM 60(1), 39–50**, India Meteorological Department — <https://mausamjournal.imd.gov.in/index.php/MAUSAM/article/download/960/803/3457>
4. ATCM XXXVII Measure 15 (2014), *Larsemann Hills, East Antarctica — ASMA No. 6 Management Plan* — <https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/asma/asma_pdf_en/ASMA06_en.pdf>
5. Eriksson, P. B. et al. (2025), *The Finnish Ice Service…*, **Front. Mar. Sci. 12:1561461** — <https://doi.org/10.3389/fmars.2025.1561461>
6. Lavergne, T. & Down, E. (2023), *A climate data record of year-round global sea-ice drift from OSI SAF*, **ESSD 15, 5807–5834** — <https://doi.org/10.5194/essd-15-5807-2023>
7. NSIDC, *Polar Pathfinder Daily 25 km EASE-Grid Sea Ice Motion Vectors, Version 4* — <https://nsidc.org/data/nsidc-0116>
8. NSIDC, *NOAA/NSIDC CDR of Passive Microwave Sea Ice Concentration, Version 5* — <https://nsidc.org/data/g02202/versions/5>
9. NCAR Climate Data Guide, *Sea Ice Concentration: NOAA/NSIDC Climate Data Record* — <https://climatedataguide.ucar.edu/climate-data/sea-ice-concentration-noaansidc-climate-data-record>
10. NCAR/MMM, *Antarctic WRF Mesoscale Prediction System (AMPS)* — <https://www.mmm.ucar.edu/projects/amps>

**Secondary / abstract-level only (flagged in text):**

11. Nihashi, S. & Ohshima, K. I. (2015), **J. Climate 28(9), 3650** — <https://doi.org/10.1175/JCLI-D-14-00369.1>
12. *Improving Ice Pressure Forecasting for Operational Purposes*, **OTC-25595-MS** — <https://onepetro.org/OTCARCTIC/proceedings-abstract/15OARC/15OARC/OTC-25595-MS/77472> (403)
13. Powers, J. G. et al. (2012), *A Decade of Antarctic Science Support Through AMPS*, **BAMS 93(11)** — <https://journals.ametsoc.org/view/journals/bams/93/11/bams-d-11-00186.1.xml>
14. ESA, *Envisat's night eye supports icebound ship rescue in Antarctica* — <https://www.esa.int/Applications/Observing_the_Earth/Envisat_s_night_eye_supports_icebound_ship_rescue_in_Antarctica>
15. Scott Polar Research Institute / WDC Glaciology, *Magdalena Oldendorff* — <https://wdcgc.spri.cam.ac.uk/news/ship>
16. JCOMM TR-23, *SIGRID-3: A vector archive format for sea ice charts* — <https://globalcryospherewatch.org/wordpress/wp-content/themes/global-cryosphere-watch/files/resources/JCOMM_TR23_SIGRID3.pdf> (downloaded, text not extractable)

---

*Written 2026-09-02. Every table row tagged VERIFIED is transcribed from a source fetched during that
session; every INFERRED row shows its reasoning; every UNVERIFIED item is listed in §6. Nothing in this
document is a confident guess.*
