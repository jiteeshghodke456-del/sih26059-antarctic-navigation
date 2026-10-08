# Operational Iceberg/Ice Charting Services — Do Any Forecast Trajectories?

Research brief for SIH26059. Question: does any operational service forecast iceberg
**trajectories** (future position), as opposed to charting **current** position, for
Antarctic/Southern Ocean shipping — and specifically for the Indian Ocean sector
(Queen Maud Land / Bharati–Maitri approach)?

Status marks: **VERIFIED (source)** / **INFERRED** / **UNVERIFIED**.

---

## A. International Ice Patrol (IIP) — North Atlantic

**What it is.** The International Ice Patrol is a US Coast Guard–led, internationally-funded
(19 SOLAS signatory nations) service established after the 1912 *Titanic* disaster. It has
operated continuously since 1913 (except during the two World Wars). **VERIFIED** —
[International Ice Patrol – Wikipedia](https://en.wikipedia.org/wiki/International_Ice_Patrol),
[IIP History – USCG Navcen](https://www.navcen.uscg.gov/international-ice-patrol-history).

**Geographic scope — explicitly NOT Antarctic.** IIP's operating area is the North Atlantic,
specifically the Grand Banks of Newfoundland and the transatlantic Great Circle shipping lanes
that cross iceberg-prone waters calved from **Greenland** (west Greenland outlet glaciers),
not Antarctic ice-shelf calving. This is a different hemisphere, different ocean basin
circulation regime (Labrador Current vs. Antarctic Circumpolar Current / coastal gyres), and a
different source population of icebergs (relatively small, glacier-calved "bergy bits" and
growlers common in North Atlantic shipping lanes vs. Antarctica's much larger tabular
ice-shelf-calved bergs, some hundreds of km long). **VERIFIED** —
[Wikipedia: International Ice Patrol](https://en.wikipedia.org/wiki/International_Ice_Patrol).

**Does IIP forecast trajectories, or only chart current position? — It does both, and the
distinction matters for this project.**

- IIP's core operational model is **BAPS — the iceBerg Analysis and Prediction System**,
  adopted from the Canadian Ice Service in 1998 and still run today at the IIP Operations
  Center (New London, CT) under the North American Ice Service (NAIS) collaborative
  arrangement with Canada. BAPS is a genuine **drift-and-deterioration forecast model**: it
  ingests winds, waves, sea surface temperature and ocean currents, and **predicts where each
  tracked iceberg will be roughly 24 hours ahead**, along with an estimate of size/deterioration
  (melt) over that window. **VERIFIED** — summarized consistently across
  [IIP Annual Report 2022](https://www.navcen.uscg.gov/sites/default/files/pdf/Annual_Report_2022_Season.pdf),
  [USCG contract award notice re: BAPS](https://orangeslices.ai/uscg-contract-award-iip-iceberg-analysis-and-prediction-system-baps/),
  and corroborated in general terms by
  [phys.org: "Iceberg patrol gains faster updates from orbit"](https://phys.org/news/2016-11-iceberg-patrol-gains-faster-orbit.amp).
  A separate academic description of an operational IIP-tested drift model (solving iceberg
  force balance — water drag, air drag, Coriolis, sea-surface-slope terms — initialized from
  Sentinel-1 SAR detections) describes a **48-hour** forecast horizon in some published work; the
  exact horizon (24 h per BAPS documentation vs. 48 h per some drift-model papers) is not fully
  reconciled across sources and should be treated as **UNVERIFIED at the single-number level**,
  though the *existence* of multi-hour-to-multi-day forward drift prediction is well corroborated.
  See [ResearchGate: "An Operational Model of Iceberg Drift"](https://www.researchgate.net/publication/44050768_An_Operational_Model_of_Iceberg_Drift).
  **Partial reconciliation (from the parallel iceberg-research brief, which read the 2024 IIP
  annual report directly — see docs/ICEBERG_RESEARCH.md §c.3):** BAPS actually runs on a
  **12-hourly** model cycle (0000Z and 1200Z), with each cycle's limits built to stay valid until
  the *next* 0000Z run — i.e. a rolling ≤24 h validity window, not a single fixed "24 h" or "48 h"
  forecast step. That is consistent with both numbers above without fully resolving which paper's
  "48 h" figure refers to a different, non-BAPS drift model. Do not present one single number
  without this caveat.
- However, the **public-facing daily products** IIP actually issues to mariners — the "Iceberg
  Chart," "Iceberg Bulletin," and the "Limit of All Known Ice" — are framed and consumed as
  **today's** ice/iceberg situation, not as a delivered per-iceberg future-track product. The
  forward-drift modeling inside BAPS is used internally to (a) extrapolate/decay-adjust
  detections between sparse aerial/satellite passes and (b) draw the conservative "Limit of All
  Known Ice" boundary outward to cover likely undetected drift — it is not published to mariners
  as an explicit "iceberg X will be at position Y at time T+24h" trajectory feed. **INFERRED**
  from the product descriptions on
  [Navcen: International Ice Patrol Home and Iceberg Products](https://navcen.uscg.gov/north-american-ice-service-products),
  which lists only "Today's Iceberg Chart" and "Today's Iceberg Bulletin" as mariner-facing
  outputs, with no separate forecast-track product exposed.

**Delivery mechanism (context for §C).** IIP disseminates via US Coast Guard radio broadcast
(COMMCOM, Chesapeake VA), **Inmarsat SafetyNET**, **radiofax**, plus web download and an email
subscription (GovDelivery) for daily products; GIS shapefile/KML exports are also offered for
ingestion into ECDIS/navigation software. **VERIFIED** —
[Wikipedia: International Ice Patrol](https://en.wikipedia.org/wiki/International_Ice_Patrol),
[Navcen product page](https://navcen.uscg.gov/north-american-ice-service-products).

**Bottom line for this project:** IIP is the closest real-world precedent for "iceberg drift
forecasting as an operational product," which is directly relevant to validating that this
project's own trajectory-forecast component is a legitimate, precedented capability — but IIP
(a) is North Atlantic only, (b) does not publish an explicit per-berg future-position feed to
end users even though its internal model computes one, and (c) has never been extended to the
Southern Ocean. None of this reduces the novelty of a Southern-Ocean-facing, mariner-delivered
trajectory forecast product — if anything it strengthens the case that IIP's internal-only
BAPS output is a known, validated technique this project can adapt/cite, while the
Antarctic/Indian-Ocean-sector public delivery gap is real (§B, §C).

---

## B. Southern Ocean / Antarctic equivalent of IIP — does one exist?

**Short answer: No body forecasts Southern Ocean iceberg trajectories today. Every
Antarctic-facing service found is current-position charting only.** This is a genuine,
verifiable gap.

### B.1 US National Ice Center (USNIC) — Antarctic iceberg tracking
USNIC has tracked large Antarctic icebergs since 1978. Its current tracking criterion, read
directly from the live product page (docs/ICEBERG_RESEARCH.md §A1, treated as authoritative), is
an **OR of two thresholds: ≥20 sq NM in area, OR ≥10 NM on the longest axis** — not a simple
historical-to-current size increase. It publishes **weekly**
updates of named/tracked iceberg positions and dimensions using SAR, visible, and infrared
imagery. **VERIFIED** —
[USNIC: Antarctic Iceberg Naming and Tracking](https://usicecenter.gov/Resources/AntarcticIcebergs),
[USNIC: Antarctic Iceberg Data](https://usicecenter.gov/Products/AntarcIcebergs).
Nothing in USNIC's Antarctic product documentation describes a forward drift/trajectory
forecast — the product is explicitly a weekly position/size snapshot. **INFERRED** (absence)
from the same USNIC product pages; no forecast product is advertised there.

### B.2 AARI (Russia) + USNIC joint Southern Ocean ice charts
AARI (Arctic and Antarctic Research Institute, Russia) collaborates with USNIC to produce
Southern Ocean sea-ice charts covering October–April (austral spring/summer/autumn), archived
at AARI. These are ice-edge/concentration charts, not iceberg trajectory products, and are not
described as forecasts. **VERIFIED (existence of collaboration)** —
search-corroborated via [AARI methodology page](https://en.russian-arctic.info/info/articles/oceanology/AARI/)
and cross-referenced in the Frontiers paper below; the specific joint-chart claim should be
treated as **INFERRED** pending a direct AARI primary-source page (not independently fetched in
this session due to search-budget constraints — flagged, not silently dropped).

### B.3 Argentine Naval Hydrographic Service (SHN) — NAVAREA VI
A peer-reviewed 2022 paper, "Southern Ocean ice charts at the Argentine Naval Hydrographic
Service and their impact on safety of navigation," is the most concrete primary-adjacent source
found. Key facts extracted directly from the paper:
- Southern Ocean ice-service-providing nations named: **Argentina, Australia, Chile, China,
  Denmark, Germany, Norway, Russia, and the USA.**
- SHN is the coordinator for **NAVAREA VI** (Antarctic Peninsula, Bellingshausen Sea, Weddell
  Sea, Southwestern Atlantic) — i.e., the **Atlantic-facing** sector of Antarctica, not the
  Indian Ocean sector where Bharati/Maitri sit.
- SHN publishes three chart types weekly on its website (concentration, ice-edge, iceberg
  location) — **all current-position analyses. The paper contains no mention of a
  forecast/predictive trajectory product** for icebergs or sea ice in this service.
- Delivery: charts are pushed via **SafetyNET and NAVTEX** ("for duplication of communications
  to ensure the location of sea-ice edge is acquired by all vessels in NAVAREA VI"), plus web
  publication and, since 2019, the **PolarView portal**.
**VERIFIED** —
[Frontiers in Marine Science (2022), Southern Ocean ice charts at SHN](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.971894/full).

### B.4 China — Fast Ice Prediction System (FIPS), Prydz Bay
The closest thing to an Antarctic "prediction" system found in this research is China's **FIPS
(Fast Ice Prediction System)**, run for CHINARE (Chinese National Antarctic Research Expedition)
to support RV *Xuelong*'s resupply of Zhongshan Station in **Prydz Bay** — which is in the
**Indian Ocean sector**, geographically the closest documented service to the Bharati/Maitri
approach corridor. Important distinction: FIPS predicts **land-fast ice thickness/extent**
(a thermodynamic ice-growth model, HIGHTSI, initialized from satellite-derived ice
concentration/extent/tide-crack data) for route planning through fast ice near the coast — it is
**not an iceberg drift/trajectory forecast**. It forecasts ice *state* (thickness, presence) at
a location, not the future *position* of a specific drifting iceberg. **VERIFIED (existence and
scope)** —
[Cambridge/Annals of Glaciology: "Fast Ice Prediction System (FIPS) for land-fast sea ice at
Prydz Bay, East Antarctica: an operational service for CHINARE"](https://www.cambridge.org/core/journals/annals-of-glaciology/article/fast-ice-prediction-system-fips-for-landfast-sea-ice-at-prydz-bay-east-antarctica-an-operational-service-for-chinare/61F057B3A102C191C52C1B650D7095F9),
[MDPI (2017): "Satellite-Based Sea Ice Navigation for Prydz Bay, East Antarctica"](https://www.mdpi.com/2072-4292/9/6/518)
(full text was 403-blocked to automated fetch in this session — title/abstract-level claims only
are used here; **flagged as not independently full-text-verified**, corroborated instead via
search snippets and the companion Cambridge paper, which is a stronger primary source for FIPS
itself).

### B.5 Research-stage iceberg drift forecasting (not operational)
Academic work on iceberg drift *forecasting* algorithms exists and is active, but is explicitly
research/prototype stage, not a fielded operational service for the Southern Ocean:
- **IDRIFTNET** (2025) — "Physics-Driven Spatiotemporal Deep Learning for Iceberg Drift
  Forecasting," arXiv preprint. **VERIFIED as existing (preprint, not peer-reviewed at time of
  writing)** — [arXiv:2507.00036](https://arxiv.org/abs/2507.00036). Not tied to an operational
  Southern Ocean delivery service.
- Older statistical/physical drift-model literature (e.g., "An iceberg forecast approach based
  on a statistical ocean current model," ScienceDirect 2018; "On predicting iceberg drift,"
  ScienceDirect 1980) is Arctic/sub-Arctic-focused research, feeding into IIP's BAPS lineage
  rather than a Southern Ocean product. **VERIFIED as existing**, scope confirmed
  Arctic/sub-Arctic via titles and abstracts —
  [ScienceDirect 2018](https://www.sciencedirect.com/science/article/abs/pii/S0165232X1830226X),
  [ScienceDirect 1980](https://www.sciencedirect.com/science/article/abs/pii/0165232X80900555).

### B.6 Conclusion on the gap
**No agency — USNIC, AARI, SHN, or any other Southern Ocean ice-service provider identified in
this research — publishes a *public* operational iceberg trajectory (future-position) forecast
product for the Southern Ocean.** Every agency service found is either (a) current-position
charting (weekly snapshots), or (b) a fast-ice *state* forecast (FIPS) rather than a
drifting-iceberg *position* forecast. IIP's BAPS is the only agency precedent for operational
iceberg-drift forecasting anywhere, and it is North Atlantic-only, uses a different iceberg
population, and does not even publish its internal per-berg predictions as a public trajectory
feed (§A).

**Correction (found by the parallel iceberg-research brief, docs/ICEBERG_RESEARCH.md §A7 — flagged
here so this claim is not overstated):** one *non-agency, commercial* precedent does exist. **CLS**
(Collecte Localisation Satellites, a CNES subsidiary) has run a bespoke, per-client operational
Antarctic iceberg detection-and-drift service for the Vendée Globe yacht race **since 2008**,
dynamically adjusting the race's Antarctic Exclusion Zone from per-berg trajectory forecasts —
VERIFIED via CLS/press sources, see docs/ICEBERG_RESEARCH.md §A7 for citations. It is not a public
product, has no downloadable feed, and is not built for merchant/research-vessel navigation, so it
does not contradict the operational finding below for *this* project's purposes — but the
absolute phrasing must be narrowed to be defensible in front of a judge who knows the Vendée
Globe.

**Revised conclusion:** **no public, agency-run Southern-Ocean iceberg trajectory forecast,
deliverable to a vessel underway, exists today.** The sole operational precedent (CLS) is
commercial, bespoke to one race, and not obtainable as a data product — it does not fill this
project's gap, it only proves the gap is technically solvable. This remains a legitimate, citable
differentiation point for an open, agency-style Southern-Ocean forecast: this project would be
filling a real void in *public* capability, not duplicating IIP, USNIC, AARI, SHN, or CLS.

---

## C. What ice information actually reaches vessels in the Indian Ocean sector (Queen Maud Land / Bharati–Maitri approach)

**Relevant agencies for this specific sector.** Based on the SHN paper's list of Southern Ocean
ice-service-providing nations (Argentina, Australia, Chile, China, Denmark, Germany, Norway,
Russia, USA — §B.3) and the geography, the Indian Ocean sector (≈20°E–90°E, which includes Queen
Maud Land, Prydz Bay, and the Bharati–Maitri corridor) is **not** SHN's NAVAREA VI. It falls
within the maritime-safety-information coordination of whichever nation(s) hold NAVAREA/METAREA
responsibility for that longitude band (South Africa for NAVAREA VII is the geographically
plausible coordinator for the western part of this sector, given South Africa's Antarctic
presence at Queen Maud Land — **UNVERIFIED**: this session could not confirm the NAVAREA VII
Antarctic ice-bulletin content directly; search results returned only general geography, not a
primary NAVAREA VII ice-service page. This should be verified against the IMO/IHO World-Wide
Navigational Warning Service (WWNWS) NAVAREA coordinator list before being stated as fact in any
submission deck).

**India's own vessel operations in this sector.** India's Antarctic supply/expedition voyages
(NCPOR-chartered vessel, Indian Scientific Expedition to Antarctica, ISEA) run the route
Cape Town → Bharati → Maitri (India Bay/Lazarev Sea) → Cape Town, arriving off Bharati in
January and typically exiting the Lazarev Sea in late March. **VERIFIED** —
[NCPOR ISEA advertisements, e.g. 45-ISEA](http://isea.ncpor.res.in/forms/45-ISEA%20Webpage%20Advertisment.pdf),
[Bharati (research station) – Wikipedia](https://en.wikipedia.org/wiki/Bharati_(research_station)),
[Maitri (research station) – Wikipedia](https://en.wikipedia.org/wiki/Maitri_(research_station)).

There is existing peer-reviewed Indian research on ship-routing between Bharati and Maitri using
Scatsat-1-derived sea-ice extent and NSIDC sea-ice concentration plus modeled wind velocity,
validated against the actual route sailed by the 33rd ISEA — i.e., this is a **research
route-optimization study**, not a description of an operational, continuously-updated
underway-delivery ice-information service. **VERIFIED (existence/scope of the study)** —
[ScienceDirect: "Investigating optimum ship route in the Antarctic in presence of sea ice and
wind resistances – A case study between Bharati and Maitri"](https://www.sciencedirect.com/science/article/pii/S1873965221000736)
(full text was paywalled/403-blocked to automated fetch in this session — **claims above are
from the indexed title/abstract only; the paper's own description of how ice data reached the
ship underway, if any, was NOT independently verified and should be re-checked by a team member
with institutional/publisher access before being cited as authoritative**).

**Delivery mechanism — concrete, not just chart existence.** No source found in this research
describes a satcom-broadcast (SafetyNET/NAVTEX-equivalent) ice-information feed specific to the
Indian Ocean Antarctic sector analogous to SHN's NAVAREA VI SafetyNET/NAVTEX broadcast (§B.3).
What is documented, generically, for polar vessel operations in this class:
- **Low-bandwidth satcom for underway data (Iridium Certus / VSAT).** Polar-class vessels
  generally rely on Iridium Certus (a "consistent polar coverage but typically lower bandwidth"
  service) or VSAT where available; navigation systems built for this environment cache ice
  chart tiles locally so the vessel retains offline ice charts when the link drops. This is a
  **general polar-shipping pattern**, not something confirmed specifically for NCPOR/ISEA
  voyages. **INFERRED / general industry pattern**, not sector-specific —
  [search-corroborated, no single primary source; drawn from general polar navigation software
  vendor material referencing Iridium Certus and offline chart caching].
- **China's FIPS (§B.4)** is delivered to CHINARE/*Xuelong* as an "operational service" — the
  Cambridge/Annals of Glaciology paper title itself states this — implying some form of
  routine data push to the ship or its shore-based routing team during the resupply season, but
  the paper's full text (not independently fetched here) would be needed to confirm the exact
  bandwidth/channel (this session did not verify whether FIPS output reaches the ship directly
  via satcom or is used shore-side by a routing team who then radios/emails a distilled
  recommendation to the bridge — **UNVERIFIED at this level of detail**).
- **No evidence found of a satcom-broadcast (SafetyNET/NAVTEX) ice product specifically for the
  Bharati–Maitri corridor**, in contrast to the explicitly-documented SafetyNET/NAVTEX delivery
  for NAVAREA VI (§B.3) and for IIP in the North Atlantic (§A). Absent a directly confirmed
  NAVAREA VII (or whichever NAVAREA governs this sector) ice-bulletin broadcast, the most
  defensible characterization, given what was actually found, is: **ice information for this
  route is most plausibly assembled pre-voyage / at port calls (Cape Town) from the multiple
  national services listed in §B.3's provider list, supplemented in-transit by whatever
  general-purpose satcom bandwidth the vessel carries for weather/routing data — not a
  dedicated, continuously-updated, sector-specific iceberg trajectory broadcast.** This
  characterization is **INFERRED** from the absence of any documented dedicated service, not
  from a source that states it directly — flagged clearly as an inference, not a verified fact,
  and worth a follow-up direct query to NCPOR's own voyage-planning team (who would know the
  actual in-house practice) before this claim appears in a judged deck.

---

## Summary — direct answers to the three sub-questions

**A.** IIP (North Atlantic only) does run an internal drift-forecast model (BAPS, ~24h ahead,
descended from a 1998 Canadian Ice Service model) but its public mariner-facing products are
framed as current-day charts/bulletins, not a published per-iceberg future-track feed. IIP has
no Antarctic mandate or equivalent.

**B.** No *public agency* (USNIC, AARI, SHN, or any other of the nine ice-service-providing
nations identified) forecasts iceberg trajectories — every agency service found is
current-position charting, or in China's case, fast-ice-state forecasting (not iceberg-position
forecasting). One non-agency exception exists: **CLS** has run a commercial, bespoke
iceberg-drift-forecast service for the Vendée Globe yacht race since 2008 (docs/ICEBERG_RESEARCH.md
§A7) — not a public product, not built for merchant/research shipping, and not obtainable as
a data feed. **This is a confirmed, real gap in *public* capability** and a legitimate
differentiation point for this project's trajectory-forecast component — it would not be
duplicating an existing public operational capability anywhere in the Southern Ocean (CLS proves
the problem is solvable, not that it is already solved for this use case).

**C.** For the Indian Ocean sector / Bharati–Maitri corridor specifically: the governing
NAVAREA/agency delivering broadcast ice bulletins there was **not confirmed** in this session
(UNVERIFIED — needs a direct WWNWS/NAVAREA coordinator lookup); no dedicated satcom-broadcast
iceberg-trajectory or even current-position service specific to this corridor was found; the
best-documented related work is a research-stage (not operational-service) Indian ship-routing
study using satellite-derived ice parameters, and China's operational-but-fast-ice-only FIPS in
the same general sector (Prydz Bay). Delivery in practice is most plausibly a mix of pre-voyage
briefing/planning plus whatever general-purpose low-bandwidth satcom (Iridium Certus-class) the
vessel carries — this last point is an inference from absence of evidence, not a verified fact,
and should be confirmed directly with NCPOR voyage planners.

---

## Follow-ups flagged for the team (not resolved in this session — search-budget constrained)

- Confirm the actual NAVAREA/METAREA coordinator for the Queen Maud Land longitude band
  (candidate: South Africa / NAVAREA VII) via the IMO/IHO WWNWS coordinator list.
- Get full-text access to the Bharati–Maitri ship-routing paper
  ([ScienceDirect S1873965221000736](https://www.sciencedirect.com/science/article/pii/S1873965221000736))
  and the Prydz Bay satellite-navigation paper
  ([MDPI 2072-4292/9/6/518](https://www.mdpi.com/2072-4292/9/6/518)) — both were 403-blocked to
  automated fetch in this session.
- Ask NCPOR's own ISEA voyage-planning team directly what ice-information source and delivery
  channel they actually use underway — this is the single fastest way to close the §C
  uncertainty and would also be a strong "we talked to the actual stakeholder" credibility point
  for the SIH submission.
