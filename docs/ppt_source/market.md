# Market, Startup Path and Money — SIH 26059

Draft for §39 / §40 of the master prompt. Written 2026-09-07.

**Rule for this document.** Every number is marked either **[SOURCED]** with a link,
or **[ASSUMPTION]** with the reasoning shown. Where a number is an assumption, the
arithmetic is written out so anyone can substitute their own figure and see what
changes. No market-size number is invented. Where none exists, the count of ships
and programmes is used instead, and the counting is shown.

---

## 0. The short version

This is a small market. It has roughly **fifty to seventy ships** in the world
that genuinely need Antarctic ice routing. It moves slowly, it buys through
government procurement, and the closest thing to a direct competitor is a
**seven-person company that has been at it since 2014**.

So the plan is not to sell a subscription to a large fleet. There is no large
fleet.

The plan is:

1. Be the decision layer for **one programme that has to solve this every year
   anyway** — India's. NCPOR charters a ship for one 100-day window per season
   and pays for it by the day.
2. Get paid by that programme as a service contract, not by mariners as a seat
   licence. India's own precedent for ocean forecasting is a free public
   service, so the money comes from the ministry, not the bridge.
3. Only then sell the same engine to the other twenty-three countries that run
   the same voyage, and to the ice-going tourism and fishing operators who
   already pay a European vendor for less.
4. The size is in the Arctic, not the Antarctic. India plans its first cargo
   vessel on the Northern Sea Route in 2027. The Antarctic is where the
   credibility is built. The Arctic is where the volume is.

Realistic ceiling: a **sustainable specialist company of eight to twelve
people**, not a venture outcome. That is what this market supports. Saying so is
part of the pitch, because the alternative is a hockey stick a judge can
disprove in one question.

---

## 1. Who actually buys polar ice intelligence today

Four models exist. Only one of them makes money, and it makes a modest amount.

### 1.1 The free public-good layer — this is our input, not our competitor

Ice charts and ice concentration are produced by national agencies and given
away. The US National Ice Center, Russia's AARI, the Canadian Ice Service and
the Norwegian Ice Service all publish routine charts; the Norwegian service
publishes shapefiles and an API on weekdays. **[SOURCED]**
([cryo.met.no](https://cryo.met.no/en/latest-ice-charts),
[NSIDC IICWG](https://nsidc.org/iicwg))

Polar View, the European polar EO service, exists explicitly "for public good
and in support of public policy," backed by ESA and the European Commission.
**[SOURCED]** ([polarview.org/about](https://polarview.org/about/),
[Copernicus](https://www.copernicus.eu/en/polar-view))

Copernicus Marine data is free. NSIDC data is free. **The raw ice field is not a
product anyone can sell.** Any plan that involves charging for satellite ice
concentration is dead on arrival, and a judge who knows the field will say so.

### 1.2 The one real polar-specialist vendor — Drift+Noise / IcySea

This is the closest company to what we would become, so it is worth being precise
about it.

| Fact | Value | Source |
|---|---|---|
| Founded | 2014, spin-off from the Alfred Wegener Institute, Bremen | **[SOURCED]** [ESA BIC](https://esa-bic.de/startup/drift-noise-gmbh/) |
| Team | **7 core staff** plus 2 advisers | **[SOURCED]** [driftnoise.com/about-us](https://driftnoise.com/about-us.html) |
| Product | IcySea — map-based near-real-time ice information, Arctic and Antarctic, "optimised for low-bandwidth connections" | **[SOURCED]** [driftnoise.com/icysea](https://driftnoise.com/icysea.html) |
| Named users | RV *Polarstern* (AWI, Germany), RSV *Nuyina* (Australian Antarctic Division), Ponant, Hapag-Lloyd Cruises, Lindblad, HSVA, BigLift | **[SOURCED]** [driftnoise.com/about-us](https://driftnoise.com/about-us.html) |
| Pricing | Free trial, then "access to new data requires an IcySea subscription"; quotations by email only. **No public price.** | **[SOURCED]** [driftnoise.com/icysea](https://driftnoise.com/icysea.html) |
| Business model | Stated as subscription SaaS, funding continuous development | **[SOURCED]** [driftnoise.com](https://driftnoise.com/icysea) |

Three things follow, and all three are useful to us.

**First, the market is real.** Two national Antarctic programmes — Germany's AWI
and the Australian Antarctic Division — pay a commercial vendor for ice
information rather than doing it in house. That answers the question "would a
national programme ever buy this?" with a name, not a hope.

**Second, the market is small.** Twelve years in, with the two best-known polar
research ships in the world as customers, it is a seven-person company. That is
the honest ceiling of the *pure ice-information* business.

**Third, our claim is adjacent, not superior.** IcySea's own description is an
ice-information app. Ours is a route decision that carries forecast uncertainty
into the route. We have never tested IcySea and will not claim it is worse. The
correct sentence is: *"They tell you what the ice is. We tell you whether your
destination will be open on the day you arrive, and what that costs you if you
are wrong."*

### 1.3 The large commercial routing vendors — structurally uninterested

StormGeo guides roughly **13,000 vessels, about a third of the global fleet, and
monitors 75,000 voyages a year.** **[SOURCED]**
([StormGeo](https://stormgeo.com/insights/unlocking-the-full-potential-of-stormgeo-s-voyage-optimization))
It absorbed Applied Weather Technology (AWT) in January 2014 and still runs the
AWT brand for route advisory. **[SOURCED]**
([PR Newswire](https://www.prnewswire.com/news-releases/applied-weather-technology-shares-acquired-by-stormgeo-242336441.html))

StormGeo treats "ice conditions" as one input parameter among many, and keeps
human route analysts on call 24/7. It is a mid-latitude fuel-and-weather
business.

**This is a structural fact in our favour, not a weakness we have to attack.** A
company serving 13,000 hulls will not build a tuned product for 55. The niche
persists for the same reason it has persisted for Drift+Noise since 2014.

### 1.4 How the money is actually charged, when it is charged

There is no published price for polar ice services. There is a published range
for conventional weather routing, from trade sources rather than audited data:

| Model | Price | Source quality |
|---|---|---|
| Software subscription, per vessel per year | USD 10,000 – 50,000 | **[SOURCED, trade press]** [ShipUniverse](https://www.shipuniverse.com/how-to-save-20-on-fuel-costs-with-weather-routing-software/) |
| Shore-based routing service, annual contract | USD 5,000 – 6,000 per year | **[SOURCED, trade press]** [metacad.io](https://metacad.io/en/knowledge/weather-routing/) |
| Per voyage | USD 300 – 1,500 | **[SOURCED, trade press]** [metacad.io](https://metacad.io/en/knowledge/weather-routing/) |

Treat these as order-of-magnitude anchors, not as quotes. They are trade-press
figures for the mid-latitude commercial market. A polar product sits at or above
the top of that range because the fleet is tiny and the consequence of being
wrong is a stranded ship rather than a slow one — but that is our judgment, not a
sourced fact.

---

## 2. The Indian entry point — and it is a good one

### 2.1 The recurring purchase that already exists

NCPOR runs a global tender, every few seasons, for one ice-class vessel. The
2021 tender for the 41st expedition is public and readable. It is the single most
useful commercial document in this whole analysis, because it describes the
customer's problem in the customer's own words and the customer's own money.
**[SOURCED]**
([NCPOR/14(102)/21, Tender for Time Chartering of Ice Class Vessel, XLI ISEA](https://ncpor.res.in/upload/tenders/41%20ISEA%20Tender-Ice%20Class%20Vessel-R.PDF))

What the tender says, verbatim or near-verbatim:

- **One vessel, time charter, `100 +/- 30 days`**, austral summer, December to
  April, with the option to extend at the same rate for **four subsequent
  seasons**.
- The financial bid is literally: mobilisation/demobilisation at Cape Town (50%
  weight) + mobilisation/demobilisation at Mormugao (50%) + **`Day rate x 100
  days`** + victualling (40 passengers × 100 days). **Day hire is the dominant
  term.**
- Required capability: independent navigation at a **continuous 1.5 knots through
  compact even ice 1.2 m thick with 0.2 m snow cover**, class equivalent to
  **1A-Super or better**, double-skinned hull, maximum age 35 years.
- Operating box: **66°S to 70°S, 80°E to 06°E** — "near Prydz Bay (Larsemann
  Hills area) and India Bay". That is Bharati and the Maitri approach. It is our
  corridor, written by the customer.
- Bid bond: **INR 50,00,000 / USD 75,000**. Performance guarantee: 5% of contract
  value.

Two clauses matter more than the rest.

**The ice-failure clause.** *"In the event that upon the vessel's arrival at
Prydz Bay the local ice conditions deem it not safe to discharge overboard on to
the fast ice the Charterer's cargo / equipment, then the Owners will discharge
the cargo for delivery to the shore using a boat, pontoon barges ... **provided
the conditions of the coast permit such discharge**."*

NCPOR's own contract anticipates that ice will stop the discharge. Its fallback
is conditional on the coast being workable. There is no clause for what happens
when it is not.

**The equipment clause.** Under *Communication and Navigational Facilities*, the
vessel must carry, among other things, **"ice-information receiving
equipment."** **[SOURCED, same tender, §11]**

Read that again. NCPOR already writes ice information into its procurement. It
buys the *receiver*. India owns nothing on the other end of it.

**That gap is the wedge.** It is not a hypothetical need we have invented for a
pitch. It is a line item in a live government tender with nothing Indian
attached to it.

### 2.2 The indigenous Polar Research Vessel — verified, and honestly early

The claim checks out, with an important caveat about maturity.

- Kongsberg Maritime signed an MoU with **Garden Reach Shipbuilders & Engineers
  (GRSE)** at Nor-Shipping 2025 in Oslo, June 2025, to **explore the design** of
  India's first indigenous Polar Research Vessel. **[SOURCED]**
  ([Kongsberg Maritime](https://www.kongsberg.com/maritime/news-and-events/news-archive/2025/kongsberg-maritime-signs-mou-with-india-to-explore-design-of-indigenous-polar-research-vessel/),
  [PIB PRID 2133528](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2133528),
  [Marine Log](https://www.marinelog.com/news/kongsberg-maritime-inks-mou-with-india-to-explore-design-of-indigenous-polar-research-vessel/))
- It will be built at GRSE Kolkata, and the design must account for **NCPOR's
  requirement**, since NCPOR will operate it. **[SOURCED]** (same)
- As of 2026, GRSE has **"initiated design preparatory activities."** It is an
  MoU and a design phase. **[SOURCED]**

**Be honest on the slide: there is no PRV contract, no announced cost, and no
delivery date.** Anyone claiming otherwise is guessing.

Do not confuse it with the other ship. The **₹839.55 crore, 89.5 m Ocean Research
Vessel** contracted to GRSE on 16 July 2024, 36-month build, is for the Deep
Ocean Mission — a different hull for a different job. **[SOURCED]**
([PIB PRID 2033981](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2033981),
[Business Standard](https://www.business-standard.com/companies/news/grse-to-build-ocean-research-vessel-in-collaboration-with-ncpor-124071700544_1.html))
Getting these two mixed up in a presentation would be an easy and expensive
mistake.

**Why the PRV still matters commercially even though it is early.** A ship being
designed now is a ship whose decision-support software can still be specified in.
Software written after a ship is delivered gets bolted on. Software specified
during design gets a place on the bridge. The window to be in that conversation
is open right now and will close.

### 2.3 The money is a ministry contract, not a subscription — and there is a precedent

The most important Indian fact for pricing is uncomfortable and should be faced
directly.

**INCOIS, an autonomous body under the same ministry, has run "Ocean State
Forecast along Ship Routes" since March 2013** — wave height and surface wind, 5
days ahead, 3-hourly, updated daily, provided to the Indian Navy, Indian Coast
Guard, merchant and passenger shipping, and fishermen. **[SOURCED]**
([INCOIS](https://incois.gov.in/site/services/osf.jsp),
[J. Atmos. Ocean. Technol. 2015](https://journals.ametsoc.org/view/journals/atot/32/11/jtech-d-15-0047_1.xml))

So MoES already runs a national ship-routing advisory, and it gives it away.

That cuts both ways, and both ways are useful:

- **Against us:** we cannot expect to charge Indian mariners for an advisory when
  the ministry's own equivalent is free. Any deck that shows Indian per-vessel
  subscription revenue is wrong.
- **For us:** it proves the institutional home exists, the delivery channel
  exists, and MoES already believes this kind of service is worth funding. An
  Antarctic ice extension to a national forecasting service is not a new idea to
  sell — it is an existing programme to extend. The customer is the ministry, and
  the product is a service contract.

### 2.4 The procurement mechanics actually favour a student team

A DPIIT-recognised startup on the Government e-Marketplace gets **exemption from
prior-turnover requirements, exemption from prior-experience requirements, and
exemption from Earnest Money Deposit**, under GFR Rule 173(i) and the public
procurement policy for startups and micro/small enterprises. **[SOURCED]**
([Startup India](https://www.startupindia.gov.in/content/sih/en/public_procurement.html),
[GeM](https://gem.gov.in/latest))

This is the single most practical fact in this document. The normal reason a
two-year-old company cannot bid for a government contract — no turnover, no track
record, no cash for a deposit — is waived by rule. The path from a working
prototype to an actual purchase order is short and written down.

---

## 3. Supply chain — this is a supply chain, and it is the hardest kind

The master prompt asks for supply-chain relevance. This is not a decoration. The
Indian Antarctic resupply is a textbook single-window supply chain, and the
tender describes it physically.

### 3.1 What the chain actually is

Every element below is from the NCPOR charter document. **[SOURCED]**

- **One hull.** Not a fleet. One time-chartered ice-class vessel.
- **One window.** 100 ± 30 days, December to April. There is no second sailing.
- **Paid by the day.** `Day rate × 100 days` is the dominant cost line. A day
  spent waiting for ice is a day bought and not used.
- **Cargo lands on ice, not on a quay.** Containers are craned overboard onto the
  **sea-ice or ice shelf** — 25 MT single-crane, 50 MT in tandem — and hauled
  inland. The tender's own justification: *"Due to unpredictable ice-shelf edge,
  uneven topography and unexpected breakages of the ice-shelf edge, this
  requirement is very critical to ensure safety of men and expedition material."*
- **Two fallbacks, both chartered separately and both weather-dependent.** A
  self-propelled 50 MT flat-bottom barge (17 × 6 m, two 40 ft containers), and
  **two Kamov Ka-32 heavy helicopters** carried in the hold.
- **Fuel goes by hose.** Pumped from ship's tanks to tanks standing on the ice
  shelf 500 m from the edge.
- **Comms are metered.** Clause 15.4: communication charges are **"payable as per
  actual"**, with per-day data usage controlled across 50 devices.
- **The delivery point is inside a managed area.** Bharati sits inside **ASMA 6,
  Larsemann Hills**, of which India is a co-proponent. Under Annex V of the
  Environmental Protocol an ASMA needs no entry permit, but its Management Plan
  governs the activity — which here means landing, small-boat and helicopter
  operations. **[SOURCED, our own analysis of the Antarctic Treaty Secretariat
  register]** (`isih/protected_areas.py`, `isih/figures/protected_areas.json`,
  source `apa_shape_2024.zip`)

### 3.2 What a closed window costs — measured, not asserted

Our own result, computed from real NOAA/NSIDC satellite ice for December 2019
against this vessel's actual capability:

| Location | Days observed | Days closed | Share |
|---|---|---|---|
| **Bharati** (the delivery point) | 31 | **23** | 74.2% |
| Bharati approach, 100 km north | 31 | 0 | 0% |
| **Maitri coast approach** | 31 | **31** | 100% |

**[SOURCED — our own, reproducible]** `isih/figures/destination_window.json`

The first closure at Bharati was on **2 December — the second day of the month.**

Read the middle row again. The ocean crossing was never the problem. **The
approach 100 km out was open every single day.** The last 100 km is what closes.
A router optimised for the transit is optimising the part that was never at risk.

### 3.3 What that costs, without inventing a day rate

We do not have NCPOR's awarded day rate, and the bid bond cannot be back-solved
into one. So use the ratio the tender itself hands us.

> The contract value formula is `day rate × 100 days` plus fixed terms.
> **One lost day is therefore about 1% of the season's hire.**

That statement needs no dollar figure and cannot be argued with. Eight days of
waiting is roughly 8% of the charter, spent on nothing. And waiting is the good
outcome.

The bad outcome is documented elsewhere, in a comparable programme:

- **Mawson station, 2021.** Thick sea ice prevented a full resupply. The closest
  the ship could get was reported as 30 km. Eighteen expeditioners went without
  full supplies for months. **[SOURCED]**
  ([ABC News](https://www.abc.net.au/news/2021-08-21/antarctic-resupply-mission-coordination-complex/100396612))
- In another Mawson season the fast ice did not break out at all, and the
  resupply became a **helicopter fly-off from the ice edge roughly 40 nautical
  miles out**. **[SOURCED]** ([Australian Antarctic
  Program](https://www.antarctica.gov.au/about-antarctica/history/exploration-and-expeditions/expeditioner-stories/the-a-factor-in-the-mawson-fly-off/))
- **Akademik Shokalskiy, 2013–14.** Beset in ice off Dumont d'Urville. Rescue cost
  reported at **AUD 2.4 million**, and diverting *Aurora Australis* away from the
  Casey resupply was expected to cost **over AUD 900,000** on its own. **[SOURCED]**
  ([phys.org](https://phys.org/news/2014-01-antarctic-scientists.html),
  [ABC](https://www.abc.net.au/news/2014-01-22/52-tourists-and-reserchers-rescued-from-antarctic-ice-return-to/5212072))
- Across the Southern Ocean, ASOC counted **more than 25 shipping incidents
  requiring emergency response between 2006 and 2019** — groundings, ice
  collisions, besetment, machinery failure, fire. **[SOURCED]**
  ([ASOC](https://www.asoc.org/wp-content/uploads/2022/02/Follow-up-to-Vessel-Incidents-in-Antarctic-Waters.pdf))

Note honestly what that last number means: **about two incidents a year across
the whole continent.** It is a serious problem and a small one. That is exactly
why the insurance-analytics buyer is weak — see §4.4.

### 3.4 The one live Indian project this maps onto

**Maitri II.** Approved by the Finance Ministry, **₹2,000 crore over seven
years**, to be built near Schirmacher Oasis and completed by **January 2029**,
executed by NCPOR under MoES. **[SOURCED]**
([Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/maitri-ii-research-station-in-antarctica),
[GKToday](https://www.gktoday.in/india-approves-maitri-ii-antarctic-research-station/) —
secondary sources summarising press reporting; the primary approval document was
not located)

A station build is not a resupply. It is **several consecutive seasons of heavy
cargo through the same window, to the same coast, on a fixed deadline.**

And that coast is the one our own measurement found closed **31 days out of 31**
in December 2019.

That is the sentence to say out loud to an NCPOR audience. Not "our model has
lower RMSE." This: *"You are about to move two thousand crore of station across
a coast that our data says was shut every day of the month we measured. Which
day would you like to arrive?"*

### 3.5 The supply-chain contribution, stated once

Most marine routing products optimise **transit** — get there faster, burn less.
That is the right objective when the destination is a port that is open every
day.

In a single-window chain the objective is different. **The thing worth predicting
is the probability that the delivery point is open on the day you arrive**, and
what your options are if it is not. Transit speed is almost irrelevant when the
approach is open 31 days out of 31 and the berth is shut 23.

Reframing the objective from *transit* to *window* is our actual supply-chain
contribution. It is also why our own measurement was worth doing: it is the
number that proved the reframing was right.

---

## 4. The other buyers, assessed honestly

Counted first, judged second.

### 4.1 The countable universe

| Segment | Hulls | Source |
|---|---|---|
| National Antarctic programme vessels, **in service** | **55**, across **24 countries** (plus 2 under construction) | **[SOURCED — counted directly from the COMNAP Antarctic Vessels register, Nov 2024 edition](https://github.com/PolarGeospatialCenter/comnap-antarctic-vessels)** |
| Peer-reviewed cross-check | "51 in-service vessels" in the COMNAP database | **[SOURCED]** [Polar Record, Cambridge](https://www.cambridge.org/core/journals/polar-record/article/icebreaking-polar-class-research-vessels-new-antarctic-fleet-capabilities/9177AFA1FDFAD8B9E5AE5DC68A5C8F80) |
| COMNAP member programmes | 31–34 | **[SOURCED]** [COMNAP](https://www.comnap.aq/our-members/), Polar Record |
| IAATO tourism vessels, 2024–25 | **58 ships + 14 yachts** (8 motor, 6 sailing) | **[SOURCED]** [IAATO papers to ATCM 47](https://iaato.org/antarctic-treaty/iaato-atcm-information-papers) |
| CCAMLR krill vessels notified, 2024 | **14**, from 6 member states | **[SOURCED]** [CCAMLR Fishery Report 2024, Area 48](https://fishdocs.ccamlr.org/FishRep_48_KRI_2024.html) |
| CCAMLR toothfish | 13 *licensed fisheries* — not a vessel count | **[SOURCED]** [CCAMLR](https://www.ccamlr.org/en/fisheries/toothfish-fisheries) |

One detail worth putting on a slide. India's single entry in the COMNAP register
is `Vasiliy Golovnin | In Service | Cargo | December–April`. **The register that
defines this entire market lists our exact target vessel, by name, with our exact
season.** We are not guessing at the customer.

### 4.2 Other national Antarctic programmes — the real second market

**Is the need real? Yes, demonstrably.** Germany's AWI and the Australian
Antarctic Division already pay a commercial vendor for ice information for
*Polarstern* and *Nuyina*. **[SOURCED]**
([driftnoise.com/about-us](https://driftnoise.com/about-us.html))

**What would they pay for?** Not raw ice — they have that. They would pay for a
routing and window-planning layer that consumes their own charter constraints,
and for it to run at Iridium bandwidth on their own ship.

**Honest difficulty:** 24 countries is a small number of buyers, each with a
different language, procurement system and incumbent relationship. Several
(United States, Russia, China) will never buy Indian software for a strategic
programme. Realistic reachable set is perhaps **six to ten programmes**, and each
sale takes years. **[ASSUMPTION, stated as judgment]**

### 4.3 Expedition cruise and Southern Ocean fishing

**Cruise.** 58 ships and 14 yachts, and Ponant, Hapag-Lloyd and Lindblad already
buy IcySea. So willingness to pay is proven. But most of that fleet works the
Antarctic Peninsula in open summer water, where ice routing matters far less. The
genuinely ice-constrained subset is the small number of ships that go to the Ross
Sea, the Weddell, or along East Antarctica. **[ASSUMPTION on the subset size —
no source gives it.]** Call it **10 to 15 hulls**.

**Fishing.** Fourteen krill vessels, six flag states, fishing Subareas 48.1–48.4.
The 2025 fishery **closed early for the first time ever** after the 620,000 t
quota was caught. **[SOURCED]**
([hookandnet](https://mag.hookandnet.com/2025/09/09/2025-09krill/content.html),
[CCAMLR](https://www.ccamlr.org/en/fisheries/krill-fisheries))
A race to a quota inside a shrinking season is a genuine, money-shaped ice
problem: fishing days lost to ice are quota not caught.

**Honest difficulty:** this is a commercial fleet with commercial procurement,
which we have never sold into, dominated by a small number of Norwegian, Chinese
and Korean operators. It is a real segment but it is not our beachhead.

### 4.4 Insurers and P&I clubs — the weakest of the four, and we should say so

The natural pitch is "insurers will pay for ice risk analytics." The evidence
does not support it.

What the sources actually show is that **hull and machinery underwriters manage
polar exposure through warranties and exclusions, treating Arctic and Antarctic
areas as permanently excluded zones with high ice and navigational risk**, rather
than by pricing it with data. **[SOURCED]**
([Gard](https://gard.no/en/insights/beast-from-east/),
[NorthStandard](https://north-standard.com/insights-and-resources/resources/publications/the-polar-code))

An exclusion needs no analytics. And the loss frequency — about two Southern
Ocean incidents a year — is too thin to build a pricing model on.

**Verdict: park it.** There may be a long-run product in evidencing compliance
and prudent passage planning to an underwriter, but it is not a stage-one or
stage-two revenue line, and claiming otherwise would be the exact "sparkly and
useless after deployment" failure the master prompt warns about.

### 4.5 The Arctic — where the scale actually is

Two sourced facts make this an expansion path rather than a daydream.

- **India's Arctic Policy (17 March 2022)** names maritime and economic
  cooperation as an explicit pillar, and NCPOR is the nodal agency. India has run
  the Himadri station at Ny-Ålesund since 2008. **[SOURCED]**
  ([Manorama Yearbook](https://www.manoramayearbook.in/india/special-articles/2022/03/18/india-arctic-policy.html),
  [The Arctic Institute](https://www.thearcticinstitute.org/india-arctic-legal-framework-sustainable-approach/))
- At the Arctic Regions Forum in Arkhangelsk on **13 August 2026**, a Joint
  Secretary of the **Ministry of Ports, Shipping and Waterways** said India plans
  its **first pilot cargo vessel on the Northern Sea Route in 2027**, to assess
  operational viability, icebreaker escort protocols and transit efficiency.
  **[SOURCED]**
  ([Marine Insight](https://www.marineinsight.com/india-first-cargo-ship-northern-sea-route/),
  [channeliam](https://en.channeliam.com/2026/08/18/india-northern-sea-route-first-cargo-vessel/))

The physics is the same. The ice field, the uncertainty, the routing under a
concentration constraint — all transfer. The fleet is orders of magnitude larger,
and the buyer is a shipping ministry rather than a research institute.

**But say the honest thing:** Antarctic sea ice and Arctic sea ice are different
regimes, our model is validated on Antarctic data only, and transfer would need
retraining and revalidation. This is a **credible adjacency, not a shipped
capability.** Marked ROADMAP.

---

## 5. The startup path — three stages, each with an exit condition

Each stage names what has to be true before the next one starts. If the
condition is not met, the stage repeats or the plan stops. That is the difference
between a roadmap and a wish.

### Stage 1 — Research tool (now → roughly March 2027)

**What it is.** What exists today: a trained sea-ice correction model that beats
persistence at every horizon from 1 to 7 days (+18.5% to +30.6%), a tested
Wagner–Dell–Eisenman iceberg drift implementation, a working demo on real
December 2019 satellite ice and real PolarRoute routes, a daily CMEMS harvest on
GitHub Actions, and the protected-areas legal layer.
**[SOURCED — ours]** `docs/ISIH_RESULTS.md`, `docs/TRUE_CLAIMS.md`

**Who it is for.** NCPOR scientists and the Indian polar research community. Not
mariners yet.

**Revenue.** None, and none expected. Possible non-dilutive support: DPIIT
startup recognition, an MoES-funded research project, an institutional
collaboration through NCPOR's existing sea-ice research group.

**Exit condition to Stage 2.** One named person inside NCPOR uses an output of
this system to answer a question they actually had. Not a demo. A use.

### Stage 2 — NCPOR operational pilot (roughly 2027 → 2029)

**What it is.** A shore-side planning desk for one expedition season, plus a
bandwidth-light package on the ship, plus a written post-season report comparing
what we predicted with what happened.

**The specific job.** Answer, before departure and again each day at sea:
*when will Bharati and the India Bay approach be workable, with what confidence,
and what does the ship do if the answer changes?*

**Revenue model.** A **season service contract** with NCPOR, procured through GeM
under the startup exemptions. It is a service, not a licence — because the
customer is a ministry institute and Indian precedent (INCOIS OAS) is that the
advisory itself is a public good.

**Exit condition to Stage 3.** A completed season with a written verification
report, and NCPOR renewing. One season of real operational use is the only asset
that opens the door to any other national programme.

### Stage 3 — Multi-programme product and Arctic transfer (2029 onwards)

**What it is.** The same engine, offered to other COMNAP programmes and to
ice-going commercial operators, with the corridor-specific tuning made
configurable rather than hard-coded.

**Two things gate it, and both are outside our control:**
- Whether the Indian PRV programme reaches a build contract, which as of 2026 is
  still at design-preparatory stage.
- Whether the Stage-2 season produced a verification report good enough to show
  a foreign programme.

**Revenue model.** Per-programme annual licence plus operations support; per
vessel subscription for commercial operators.

---

## 6. Market entry — start where the credibility already is

The entry sequence follows credibility, not market size. Each step is only
possible because the previous one happened.

**Step 1 — Publish the honest paper trail.** `WEAKNESS_ANALYSIS.md`,
`TRUE_CLAIMS.md`, the withdrawn 17.4-day number, the null result on stale data.
In a scientific-institution market, a team that documents its own failures is
buying trust with the only currency that works there. This costs nothing and is
already done.

**Step 2 — Go through the door that is already open.** NCPOR has a sea-ice
research group, a national polar data centre, and an annual expedition. The entry
is a research collaboration, not a sales call. Nobody in this market buys from a
cold email.

**Step 3 — Attach to a purchase that already exists.** Two are live:
the charter tender (which already requires ice-information equipment with nothing
Indian behind it), and Maitri II (₹2,000 crore, multi-season cargo, hard 2029
deadline, on a coast we measured as closed 31/31).

**Step 4 — Be in the PRV design conversation while it is still a design.** GRSE
and Kongsberg are working the design now, and it must account for NCPOR's
requirement. A domestic decision-support system aligned to a domestic ship is a
defensible ask precisely while the ship is on paper.

**Step 5 — Only then go abroad,** with one verified season behind us, to the
programmes most likely to buy from India: those already buying commercially
(Germany, Australia), and those without a large in-house capability.

**What we will not do.** We will not try to displace a national ice service, we
will not sell satellite data, and we will not pitch insurers before we have loss
evidence. All three are attractive on a slide and dead in the field.

---

## 7. The money — with the arithmetic shown

### 7.1 First, the ceiling of the obvious model, because it is the wrong model

Take the per-vessel subscription that every hackathon deck proposes.

Ice-constrained hulls, worldwide, our estimate:

```
national programme vessels genuinely working fast ice     30 – 40   [judgment on a sourced count of 55]
ice-going expedition ships beyond the Peninsula           10 – 15   [ASSUMPTION — no source gives this split]
krill vessels in Area 48                                      14    [SOURCED]
                                                          ---------
serviceable fleet                                         54 – 69
```

At the top of the sourced weather-routing price band, USD 20,000 per vessel-year:

```
60 hulls  x  $20,000  =  $1.2 M / year   at 100% of every hull on earth
60 hulls  x  25% share x  $20,000  =  $300 k / year   at a realistic share
```

**Three hundred thousand dollars a year is the honest ceiling of the subscription
business.** It supports about five people. Which is, to the person, the size
Drift+Noise reached after twelve years with *Polarstern* and *Nuyina* as
customers.

Put that number on the slide. A judge who has done this arithmetic will trust
everything else we say afterwards.

### 7.2 So the money comes from programme contracts

The value is not spread thinly across many hulls. It is concentrated in a few
programmes where a single bad decision costs more than a decade of subscriptions.

**Anchor 1 — the saved ship-day.** By the tender's own formula, one day is ~1% of
the season's hire. **[SOURCED ratio.]** We do not know the day rate. **[GAP.]**
So price the service as *the value of N saved ship-days* and let the customer
substitute their own rate:

```
service price  =  N  x  (NCPOR's own charter day rate)
```

At N = 3, the service pays for itself if it saves three days of waiting in a
100-day charter. That is a claim a logistics manager can check against their own
books without us knowing their numbers. **[ASSUMPTION: that N = 3 is
achievable — unproven until Stage 2.]**

**Anchor 2 — the station build.** Maitri II is ₹2,000 crore over seven years with
a January 2029 deadline. **[SOURCED, secondary.]** Planning software at even a
hundredth of one percent of that programme is ₹20 lakh. The argument is not
"we're cheap"; it is that a fixed-deadline programme delivering across a coast
that closed 31 days out of 31 has a scheduling risk it currently prices at zero.

**Anchor 3 — the metered link.** Communication charges on the charter are
*payable as per actual.* **[SOURCED, tender §15.4.]** A design that moves
kilobytes instead of megabytes is a line-item saving on a bill NCPOR already
receives, not an engineering preference.

### 7.3 Rough shape of revenue by stage

Every figure below is **[ASSUMPTION]**. They are shown so they can be argued
with, not because they are known.

| Stage | Model | Rough annual | Basis |
|---|---|---|---|
| 1 (to 2027) | Research collaboration / grant | ₹0 – 25 lakh | Non-dilutive only |
| 2 (2027–29) | One programme service contract, per season | ₹40 – 80 lakh | Priced as ~3 saved ship-days at an assumed day rate; unverified |
| 2b | Maitri II logistics planning support | ₹20 – 50 lakh / yr | A fraction of a hundredth of the programme |
| 3 (2029+) | 3–6 foreign programme licences | $60 – 120 k each | Above the sourced weather-routing band; polar niche |
| 3 | 10–20 commercial vessel subscriptions | $15 – 25 k each | Within the sourced band |
| **Stage 3 total** | | **≈ $1 – 2 M / yr** | 8–12 people |

**Stated plainly: at full success this is a one-to-two-million-dollar-a-year
specialist company.** It is a good business and a bad venture story. We should say
that, because it is true, and because the version of this slide with a hockey
stick on it will be disbelieved by anyone who has counted the ships.

The scale case, if there is one, is the Arctic — India's 2027 NSR pilot and the
much larger ice-going commercial fleet. That is **ROADMAP**, unbuilt, and
requires retraining on a different ice regime.

---

## 8. Why these features survive deployment

The master prompt's test is whether features "genuinely work in the market and
solve daily user problems." Four of ours pass, and they pass for reasons rooted
in the customer's own documents.

**1. It answers the question the charter actually asks.** The contract's failure
clause is about whether ice permits discharge at Prydz Bay. Our destination-window
output answers exactly that. Most routing tools answer a question — how fast is
the transit — that this customer is not asking.

**2. It works on the link the ship actually has.** Comms are billed as per
actual, and geostationary VSAT does not reliably cover south of ~70°S. A design
that assumes a live API call is a design for a ship that does not exist.

**3. It refuses to run on missing data.** The demo will not start if a day's
satellite file is absent. On a bridge, a product that quietly renders a gap as
open water is worse than no product. This is a small engineering decision that
becomes a large trust decision the first time it fires.

**4. It says what it cannot do.** `TRUE_CLAIMS.md` §4 lists it: no growlers or
bergy bits, no steering, no fuel number, no POLARIS compliance claim yet. Systems
that overstate get switched off after the first season. Systems that state their
limits get used within them.

---

## 9. What could kill this — the honest list

| Risk | Why it is real | What we do |
|---|---|---|
| **Very few buyers, all slow** | ~24 countries, ~55 hulls; government procurement cycles run in years | Start where a purchase already recurs annually; do not build a plan that needs many customers |
| **The public-good ceiling** | INCOIS gives ship routing away free; national ice services give charts away free | Never sell data. Sell the decision layer and the operations, to the ministry |
| **PRV may not happen on any timeline** | It is an MoU and design-preparatory work, nothing more | Do not make the PRV load-bearing. The chartered vessel is the customer today |
| **Incumbent relationships** | AWI and AAD already buy from a vendor with an eleven-year record | Do not attack it. Compete on route decision and corridor specificity, not on ice imagery |
| **We have not proven a saved day** | The N = 3 saved-days pricing is an assumption, and our own stale-data experiment came back at 0.03 days on the one date tested | Stage 2 exists to measure this. If it comes back near zero, the pricing model changes, and we say so |
| **A student team is not a supplier** | No turnover, no track record, no company | DPIIT recognition waives exactly these barriers on GeM — it is a form, not a fight |
| **Single-market concentration** | If NCPOR says no, Stage 2 has no substitute | This is genuinely unmitigated. It is the plan's biggest single point of failure and should be named as such |

---

## 10. Sourced versus assumed — the ledger

**Sourced and checkable**

- NCPOR charter structure, ice-failure clause, ice-information equipment
  requirement, comms billed as per actual, operating box, cargo handling, bid
  bond USD 75,000 — NCPOR tender NCPOR/14(102)/21
- COMNAP register: 55 vessels in service, 24 countries, 2 under construction —
  counted directly from the published CSV; India's entry is *Vasiliy Golovnin*
- Drift+Noise: founded 2014, 7 core staff, named users including *Polarstern* and
  *Nuyina*, subscription model, no public price
- StormGeo: ~13,000 vessels, 75,000 voyages/year; AWT acquired January 2014
- IAATO 2024–25: 58 ships + 14 yachts
- CCAMLR: 14 krill vessels notified for 2024; 2025 quota closed early
- GRSE–Kongsberg PRV MoU, June 2025, design-preparatory stage in 2026; distinct
  from the ₹839.55 crore ORV contract of 16 July 2024
- INCOIS Ocean State Forecast along Ship Routes, operational since March 2013
- India's NSR pilot cargo vessel planned for 2027 (announced 13 August 2026)
- GeM/DPIIT startup exemptions on turnover, experience and EMD
- Weather-routing price bands (trade press, not audited)
- Shokalskiy rescue AUD 2.4 M; Aurora Australis diversion >AUD 900 k; Mawson 2021
  partial resupply; ASOC >25 Southern Ocean incidents 2006–2019
- Our own: +18.5%/+24.9%/+22.1%/+30.6% over persistence; Bharati closed 23/31,
  approach 0/31, Maitri coast 31/31; 33 protected-area polygons, zero marine

**Assumption, reasoning shown**

- Ice-constrained fleet of 54–69 hulls (built on sourced counts plus a judgment
  about which hulls genuinely meet fast ice)
- USD 20,000/vessel-year as the polar price point
- 25% share as a "realistic" penetration
- N = 3 saved ship-days as the pricing anchor
- All rupee and dollar figures in the stage table
- Reachable set of 6–10 foreign programmes

**Not found, and we should stop claiming to know**

- NCPOR's charter day rate or awarded contract value
- Any list price for IcySea or any polar ice service
- Any credible market-size figure for polar ice or routing intelligence
- What ice information NCPOR uses today, and from whom
- The cost of the 2021 Mawson partial resupply
- PRV cost, contract or delivery date — none announced
- The split of IAATO vessels that operate beyond the Peninsula

---

## 11. The three sentences for the slide

> **Antarctic resupply is a supply chain with one ship, one window and no second
> attempt. We measured the delivery point: Bharati was shut 23 days out of 31,
> while the approach 100 km out was open every single day — so the crossing was
> never the problem, the last hundred kilometres was.**
>
> **India already writes "ice-information receiving equipment" into its own
> charter tender and has nothing Indian on the other end of it. That is the gap.**
>
> **This is a small market — about fifty-five ships and twenty-four countries —
> and we are sizing it that way on purpose. The company this becomes is eight to
> twelve people serving national programmes, not a subscription business, and the
> scale, if it comes, is the Arctic route India plans to pilot in 2027.**
