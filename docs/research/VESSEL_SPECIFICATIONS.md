# Vessel specifications — MV Vasiliy Golovnin and SA Agulhas II

Research-only, 2026-09-07. Answers the open item in `docs/backlog.md` ("Golovnin's ice
class is RS old-system KM(★) ULA (verified), but the modern Arc/PC equivalent is not
sourced") and the IMO Polar Ship Category gap (`backlog.md` line 225), and supplies the
first sourced specification set for SA Agulhas II as the second vessel for the planned
same-ice-field, two-vessel routing comparison.

**Rule this document follows throughout, verbatim from the governing spec**: "Do not
invent vessel thresholds. Where a limit is ship-specific, obtain it from authoritative
ship/class/PWOM/certification information or explicitly represent it as an unverified
assumption." Every UNVERIFIED row below was searched for, not skipped.

## Confidence key

- **VERIFIED** — confirmed by two or more independently-run publishers of different
  types (e.g. a commercial AIS/registry database plus a peer-reviewed paper, or two
  different commercial registries), OR by one primary/authoritative document
  (classification society, shipyard/designer, or a named-byline trade-press article
  quoting the ship's literal certificate text).
- **SINGLE-SOURCE** — found in only one publisher, or corroborated only by sources of
  the *same* non-primary genre (e.g. two enthusiast ship-database sites, neither of
  which is the classification society, a shipyard, or a certificate). Treated as
  weaker than VERIFIED even when the values agree exactly, because agreement between
  same-genre secondary sources does not rule out a shared upstream error.
- **UNVERIFIED** — not found in any citable source after a genuine search. The "what
  would settle it" column says what document or lookup would close the gap.
- **CONFLICTING** — sources disagree on the number; both values are given, neither is
  silently picked.

---

## Vessel A — MV Vasiliy Golovnin (IMO 8723426)

| FIELD | VALUE | SOURCE | CONFIDENCE |
|---|---|---|---|
| IMO number | 8723426 | Consistent across all registries checked (VesselFinder, MarineTraffic, FleetMon, maritimeoptima.com, vesseltracker, fleetphoto.ru, korabel.ru) | VERIFIED |
| Flag | Russia (Russian Federation), port of registry Vladivostok | VesselFinder (vesselfinder.com/vessels/details/8723426); korabel.ru (korabel.ru/fleet/info/2146.html) | VERIFIED |
| Year built | 24 December 1988 | korabel.ru and fleetphoto.ru (fleetphoto.ru/vessel/15021) both give the exact date "24.12.1988"; VesselFinder/maritimeoptima give "1988" | VERIFIED |
| Builder | State Enterprise Kherson Shipbuilding Production Association named after the 60th Anniversary of Lenin's Komsomol ("Kherson Shipyard"), Kherson, Ukrainian SSR. Hull/yard no. 5004 | fleetphoto.ru (full formal name); corroborated as "Kherson Shipyard, Kherson, Ukraine" by a MarineTraffic-family ISM/company-data page | VERIFIED (name and location agree across two independent-genre sources; the two differ only in formality of the shipyard's name, not in identity) |
| Project / class type | Project 10620, "Vitus Bering" type. 5 sister ships built: Vitus Bering, Aleksey Chirikov, Vladimir Arsenyev, Vasiliy Golovnin, Stepan Krasheninnikov | fleetphoto.ru project page (fleetphoto.ru/projects/1952) | VERIFIED (matches NAVIGATION_RESEARCH.md's prior citation) |
| **Length overall (LOA)** | 163.9 m | VesselFinder (163.90 m), maritimeoptima.com (164 m), korabel.ru (163.9 m), fleetphoto.ru (163.9 m) — 4 independent-genre sources | VERIFIED |
| **Beam** | 22.4–22.45 m | Repo's existing verified figure (22.4 m, 4 registries); korabel.ru/fleetphoto.ru give 22.45 m. Difference is rounding, not conflict | VERIFIED (already established in repo; reconfirmed) |
| **Draft (design/scantling)** | 9.0 m | maritimeoptima.com ("summer draft: 9 m"), korabel.ru, fleetphoto.ru — 3 sources, 2 different genres. **Not the same field as** VesselFinder's "current draught: 6.5 m", which is a live AIS-reported loading condition at a point in time, not the design draft | VERIFIED |
| Displacement | **CONFLICTING: 16,100 t or 20,200 t.** Deadweight is not disputed (see below) | korabel.ru's own two pages disagree with each other — korabel.ru/fleet/info/34195.html (Project 10620 generic page) states 16,100 t; korabel.ru/fleet/info/2146.html (ship-specific page) states 20,200 t. fleetphoto.ru's project page agrees with the ship-specific figure (20,200 t) | CONFLICTING — reported as found, not averaged or picked |
| Deadweight (DWT) | 10,700 t | VesselFinder, maritimeoptima.com, korabel.ru, fleetphoto.ru — unanimous across 4 sources | VERIFIED |
| Gross tonnage | 13,514 GT | VesselFinder, korabel.ru, fleetphoto.ru — unanimous | VERIFIED |
| **Service speed** | 16.4 kn | Repo's existing verified figure (4 registries); reconfirmed independently by korabel.ru and fleetphoto.ru | VERIFIED |
| Maximum speed | Not distinguished from service speed in any source found | — | UNVERIFIED — no source states a maximum speed distinct from the 16.4 kn service speed figure |
| **Ice class / classification notation** | **RS (Russian Maritime Register of Shipping) class symbol: `KM(★) ULA[2] (at d ≤ 8.5 m) AUT2` — "special purpose ship"** | fleetphoto.ru (ship page + project page) **and** korabel.ru (ship page) independently state the identical string | SINGLE-SOURCE — two publishers agree exactly, but both are enthusiast ship-database sites, not RS's own register, a shipyard, or the ship's Polar Ship Certificate/PWOM. Downgraded from the repo's prior "verified" label (which rested on fleetphoto.ru alone) because a second same-genre source does not clear the bar a classification-society or certificate document would |
| **Modern IACS Polar Class / Arc equivalent** | **UNVERIFIED — and, per this repo's own prior research, structurally unverifiable from open sources.** `ULA` is a pre-1999 RS notation; RS's current nomenclature (Ice1–Ice3, Arc4–Arc9, Icebreaker6–9, PC1–PC7, IA Super/IA/IB/IC/II/III) contains no `ULA` mark. Canada's ASSPPR Schedule 2 — the one regulator-grade RS-to-IACS equivalence table found — stops one rung short: it maps `UL` (not `ULA`, which is a higher class) to `LU5`/`Arc5`/IACS PC1–PC7/FSICR 1A Super, and `ULA` appears nowhere in that regulation. A secondary, unsourceable ladder would extrapolate `ULA → LU6 → Arc6`, but no RS, Canadian, or IACS document states this, and this session's fresh search (Equasis, IMO GISIS, DNV, RS) did not surface one either | `docs/research/POLARIS_APPLICABILITY.md` §2 (this session's fresh search corroborates rather than overturns that finding) | UNVERIFIED. **What would settle it**: the ship's own Polar Ship Certificate §2.2/§5.1, the current RS class certificate (RS may have re-issued an Arc/PC mark since 1988), or the PWOM — all non-public, held by FESCO / the Russian flag administration / RS |
| **IMO Polar Ship Category (A/B/C)** | **UNVERIFIED** | IMO GISIS's public ship-particulars module now requires an authenticated account (this session's direct fetch of `gisis.imo.org/Public/SHIPS/ShipDetails.aspx?IMONumber=8723426` redirected to a login wall); no news, academic, or registry source states a category for this ship | UNVERIFIED. **What would settle it**: an authenticated IMO GISIS lookup, or the ship's own Polar Ship Certificate (same document that would settle the ice-class-equivalence gap above) |
| Propulsion type | Diesel-electric ("дизель-электроход") | FESCO's own press materials name the ship this way; matches the repo's existing docstring | VERIFIED |
| Propulsion / engine power | Main engine: Wärtsilä-Sulzer 12ZV40/48 (as transliterated by the sources), 2 × 5,730 kW = **11,460 kW total** | korabel.ru and fleetphoto.ru agree exactly (one reports the per-unit figure, the other the total; the two are arithmetically consistent) | SINGLE-SOURCE — same two-publisher genre as the ice class row. Also note: this is the diesel **prime-mover / generator** rating; no source gives a separately-converted propulsion-motor (shaft) power, so it should not be read as installed propulsion power in the same sense as Agulhas II's motor figure below |
| **Icebreaking capability (exact wording + ice thickness)** | **UNVERIFIED — no published figure found anywhere.** Confirmed absent from: Wikipedia, FESCO's own press releases (Russian and English), korabel.ru, fleetphoto.ru, and the maritime trade press searched | Matches the repo's own existing finding: `docs/backlog.md` line 90, "No published figure for this hull was found," re: the borrowed `force_limit` value | UNVERIFIED |
| Published operating limitation in ice | **UNVERIFIED — no PWOM, Polar Ship Certificate, or Ice Certificate is public.** The only real-world evidence is anecdotal: a 2019 trade-press sentence that the ship "had difficulty getting free of the ice pack on her return voyage" from the same Cape Town–Bharati–Maitri corridor this project models (English Wikipedia, "Vasiliy Golovnin (ship)"), which is operational history, not a stated limit | `docs/backlog.md` line 157 already flags this exact sentence as needing verification with FESCO/NCPOR before appearing in any deck | UNVERIFIED as a certificated limit; the 2019 incident is real but single-sourced to trade press |
| Ice-concentration operating limit | **UNVERIFIED — searched for directly this session, not found.** See the analysis section below | — | UNVERIFIED |

---

## Vessel B — SA Agulhas II (IMO 9577135)

| FIELD | VALUE | SOURCE | CONFIDENCE |
|---|---|---|---|
| IMO number | 9577135 | Consistent everywhere | VERIFIED |
| Flag | South Africa | Consistent everywhere; call sign ZSNO, MMSI 601986000 | VERIFIED |
| Year built | 2012 (keel laid 31 Jan 2011, launched 21 Jul 2011, delivered/completed 3 Apr 2012) | Deltamarin's own project sheet (deltamarin.com, the vessel's detail-design contractor); Wikipedia; Engineering News (16 Mar 2012, on-record interview) | VERIFIED |
| Builder | STX Finland Oy, Rauma Shipyard, Finland (yard no. 1369) | Deltamarin's spec sheet ("Shipyard: STX Finland Oy - Rauma Shipyard"); Engineering News ("built by STX Finland"); Wikipedia | VERIFIED |
| **Length overall (LOA)** | 134.2 m | Deltamarin spec sheet, VesselFinder, vesseltracker, Wikipedia — 4 sources. *(Distinct metric, not a conflict: the peer-reviewed POAC13 paper's Table 1 separately gives "Length, bpp. [between perpendiculars]: 121.8 m," a shorter, different measurement, consistent with normal bow/stern overhang)* | VERIFIED |
| **Beam** | 21.7 m | Deltamarin, VesselFinder, vesseltracker, POAC13 paper Table 1 ("Breadth, mould: 21.7 m") | VERIFIED |
| **Draft (design)** | 7.65 m | Deltamarin spec sheet, Wikipedia, vesseltracker, **and** the peer-reviewed POAC13 paper's Table 1 ("Draught, design: 7.65 m") | VERIFIED |
| Displacement | 13,687 t | Engineering News, 16 Mar 2012 (direct quote: "the SA Agulhas II is 134 m long, 22 m wide, and has a displacement of 13,687 t"), repeated by Wikipedia | SINGLE-SOURCE — traces to one dated, named-byline primary article; Wikipedia's figure is not independent of it |
| Deadweight (DWT) | 4,780 t (registered) | Deltamarin, VesselFinder, vesseltracker, Wikipedia | VERIFIED. *Note a second, non-conflicting figure*: the POAC13 paper's Table 1 gives "Deadweight at design displacement: 5,000 t" — a different technical condition (design-stage DWT vs. as-registered summer DWT), not a contradiction of the 4,780 t figure |
| Gross tonnage | 12,897 GT | Deltamarin, VesselFinder, vesseltracker, Wikipedia | VERIFIED |
| **Service speed** | 14.0 kn | Wikipedia, and independently the POAC13 peer-reviewed paper's Table 1 ("Speed, service: 14.0 kn") | VERIFIED |
| Maximum speed | 16 kn | Wikipedia, vesseltracker | VERIFIED (two independent-genre sources; no primary document seen giving max speed separately from service speed, so treat as SINGLE-SOURCE-adjacent in spirit even though two publishers agree) |
| **Ice class / classification notation** | **DNV, full official notation: "DNV + 1A1 Passenger Ship, Ice class IACS PC5 (ICE-10 for Hull), WINTERISED BASIC, DAT(-35), EO, RP, HELDK-SHF, CLEAN DESIGN, COMF V(2)/C(2), NAUT-AW, TMON, BIS, DYNPOS-AUT, DE-ICE, LFL."** In short: **IACS Polar Class PC5**, classed by **DNV** (Det Norske Veritas, now DNV) | Two independent primary-adjacent sources agree: (1) *Engineering News*, 16 Mar 2012, Irma Venter — quotes this as "the following official notation" verbatim; (2) Suominen, Karhunen, Bekker, Kujala et al., **POAC'13** (peer-reviewed, Aalto University / Univ. of Oulu / Univ. of Stellenbosch / Aker Arctic / **STX Finland Rauma** co-author) — "The ship was built to Polar ice class PC 5 and hull strength in accordance with DNV ICE-10." Corroborated further by Deltamarin's spec sheet ("Ice class: DNV / PC5") and by SANAP (the ship's own operator, sanap.ac.za) | **VERIFIED** — a peer-reviewed paper with a shipyard co-author, plus a trade-press article quoting the literal certificate string, plus the ship's own detail-designer and operator, is a materially stronger and more diverse evidence set than the Golovnin ice-class row above |
| **IMO Polar Ship Category (A/B/C)** | **UNVERIFIED.** Note the ship was delivered in 2012, five years before the Polar Code (and the Polar Ship Certificate concept) entered into force on 1 Jan 2017 — none of the 2012 delivery-era sources could have mentioned it, and no post-2017 source found states her category | Targeted search for "SA Agulhas II" + "Polar Ship Certificate"/"Category A" found nothing; IMO GISIS's public ship module requires login | UNVERIFIED. **Not derived from PC5** — the task's instruction to keep Polar Class and IMO Polar Ship Category separate is followed strictly here, even though a reader might guess "Category A" from PC5. **What would settle it**: an authenticated GISIS lookup, or the ship's actual Polar Ship Certificate (flag state: South Africa, or DNV as the issuing RO) |
| Propulsion type | Diesel-electric, two shafts, two controllable-pitch propellers, two bow thrusters, one stern thruster | Engineering News (direct quote), Deltamarin | VERIFIED |
| **Propulsion / installed power** | **Propulsion motors: 2 × 4,500 kW Converteam motors = 9 MW installed propulsion power.** Diesel generators: up to 4 × 3,000 kW Wärtsilä 6L32 = 12 MW installed generating power | Engineering News, 16 Mar 2012, direct quote: "Propulsion on the SA Agulhas II is diesel electric, using two 4,500 kW Converteam motors, powered by up to four Wärtsilä 3,000 kW diesel generators." Matches Wikipedia/vesseltracker exactly | VERIFIED (primary trade-press source, with the useful distinction — absent from the Golovnin data — between generator power and propulsion-motor power) |
| **Icebreaking capability (exact wording + ice thickness)** | **"Capable of navigating one-meter-thick pack ice at a speed of five knots"** (Engineering News); **"the ability to break one meter thick ice at five knots"** (defenceWeb, independent byline) | *Engineering News*, 16 Mar 2012, Irma Venter, quoting naval architect Robertson; independently, *defenceWeb*, 4 May 2012, Dean Wingrin — two different journalists, two different outlets, same figure | VERIFIED |
| Published operating limitation in ice | No numeric limit (concentration, thickness ceiling, or stand-off distance) found published beyond the PC5/ICE-10 class envelope itself. The Engineering News article notes she "will spend less than 10% of its time navigating in ice" as a design-profile statement, not an operating limit. The 2022 Endurance22 besetting (freed after several hours using engine power and crane-assisted rocking) is documented operational history, not a stated limit | Engineering News; multiple Endurance22-expedition press accounts (dailymaverick.co.za, maritime-executive.com) | UNVERIFIED as a certificated limit |
| Ice-concentration operating limit | **UNVERIFIED — searched for directly this session, not found.** See analysis below | — | UNVERIFIED |

---

## Is the ice-capability difference between these two ships real and defensible?

**Short answer: yes on evidence type and quality; not quantifiable as "X% more capable" — and that distinction matters and should not be blurred.**

### What is actually different, field by field

The one *directly comparable, ship-specific, numeric* field either ship publishes is
icebreaking performance in the form "speed in a stated ice thickness":

- **SA Agulhas II: 5 kn in 1.0 m level ice** — VERIFIED, two independent named-byline
  trade-press sources plus consistency with her IACS PC5 / DNV ICE-10 classification
  and a peer-reviewed instrumented-voyage literature going back to her 2012 delivery.
- **MV Vasiliy Golovnin: no equivalent figure exists in any source checked.** Not "a
  smaller number" — *absent*. The repo's own backlog already documents this (the
  `force_limit` used for Golovnin today is borrowed, uncalibrated, from BAS's RRS Sir
  David Attenborough).

So the defensible claim is **not** "Golovnin can only do half of what Agulhas II can in
ice" — no source supports a magnitude comparison like that. The defensible claim is:
**one ship has a modern, IACS-referenced Polar Class with a published, twice-sourced
performance figure, and the other has a superseded, non-IACS notation with no published
performance figure of any kind and a documented history of at least one real difficulty
in ice (2019, this exact corridor).** That is a genuine difference in *evidence quality
and modern certification*, which is a legitimate and important thing for a route
optimiser to represent — but it is a different claim from a quantified capability gap,
and the two should not be conflated in a slide or a paper.

### Which specific published field best justifies giving them different ice limits

**The icebreaking-capability statement, where it exists, is the right field to build
on — not the ice-class notation itself.** Reasoning:

1. Ice class notations are not commensurable across the two ships without an
   equivalence step this repo has already shown is unresolvable in the open literature
   (Golovnin's `KM(★)ULA[2]` has no sourceable modern IACS/RS equivalent — see the table
   above and `POLARIS_APPLICABILITY.md` §2). Trying to place both ships on one POLARIS
   RIV table would require inventing exactly the number the governing spec forbids.
2. Agulhas II's PC5/ICE-10 notation *does* carry a directly attached, twice-sourced
   performance sentence — "5 kn in 1.0 m ice" — which is usable as a speed-derating
   input without needing any class-equivalence step at all.
3. Golovnin has no such sentence, from any source, at any confidence level. The
   honest model input for Golovnin is not "assume a lower but plausible number" — it is
   an explicit UNVERIFIED placeholder, exactly as `isih/ice_meshes.py`'s own comments
   already flag for `force_limit`.

**Recommendation for the planned two-vessel experiment**: it is legitimate to give the
two ships different ice limits, provided the difference is presented as "one ship has a
sourced performance envelope and the other does not — and that asymmetry is itself the
finding," rather than as "we computed that Ship A is N% more ice-capable than Ship B."
The former is defensible from the table above. The latter is not supported by any
citation found in this session.

### Does any published source state an ice-concentration operating limit for either ship?

**No — and this should be stated plainly, exactly as suspected.** Three independent
lines of evidence converge on this, none of them merely "we didn't find it":

1. **Mechanism-level**: every ice classification system checked (IACS Polar Class
   Unified Requirements, RS's Rules, the Finnish-Swedish Ice Class Rules, and IMO
   MSC.1/Circ.1519's own POLARIS RIV table) is indexed by ice **type / stage of
   development / thickness**, not concentration. This repo's own prior research
   (`docs/research/POLARIS_APPLICABILITY.md` §1.3) already ran a word-frequency check
   on the full text of MSC.1/Circ.1519 and found zero occurrences of anything
   concentration-like as a scored limit; this session's fresh reading of two
   peer-reviewed Agulhas II papers (POAC'13, POAC'21) found the same — both discuss
   ice *thickness* and *mechanical properties* extensively and never state a
   concentration-based operating threshold.
2. **Document-availability level**: the one place a ship-specific concentration limit
   *could* legitimately live — the PWOM (Polar Water Operational Manual) or, for
   Golovnin, a Russian Ice Certificate/Ice Safety Passport — is not public for either
   ship. This was searched for directly and explicitly in this session (targeted
   queries for both ship names plus "concentration," "PWOM," "Polar Ship Certificate,"
   "operating limit") and turned up nothing for either vessel.
3. **Absence where presence would be expected**: Agulhas II's icebreaking-capability
   sentence, sourced twice, states thickness and speed and says nothing about
   concentration. If a concentration limit existed and were routinely cited, this is
   exactly the kind of sentence it would appear next to.

**Conclusion for the model**: `isih/ice_meshes.py`'s existing `max_ice_conc: 80` for
Golovnin is correctly flagged in-repo as "a working threshold, NOT derived from the ice
class" — this session's research confirms that characterization independently and
extends it to Agulhas II as well. **Any ice-concentration threshold used for either
ship in the route optimiser is an assumption, not a certificated limit, and must be
labelled as such in the model, the docs, and any slide that shows it** — precisely the
distinction the user asked not to have papered over.

---

## Sources consulted (primary/near-primary, this session)

- Suominen, Karhunen, Bekker, Kujala, Elo, von Bock und Polach, Enlund, Saarinen (2013),
  "Full-scale measurements on board PSRV S.A. Agulhas II in the Baltic Sea," POAC'13,
  Espoo — `poac.com/Papers/2013/pdf/POAC13_148.pdf`
- Suominen, Lu, Kujala, Bekker (2021), "Antarctic sea ice properties on zero meridian
  side during Austral summers 2012-14 and 2018-19," POAC'21, Moscow —
  `poac.com/Proceedings/2021/POAC21-074.pdf`
- Engineering News (Creamer Media), Irma Venter, 16 Mar 2012, "R1.3bn icebreaker rounds
  off SA's research investment south of Cape Agulhas" — archived at
  `web.archive.org/web/20191216025508/http://www.engineeringnews.co.za/article/r13bn-icebreaker-rounds-off-sas-research-investment-south-of-cape-agulhas-2012-03-16`
- defenceWeb, Dean Wingrin, 4 May 2012, "SA receives SA Agulhas II polar research ship"
  — `defenceweb.co.za/sea/sea-sea/sa-receives-sa-agulhas-ii-polar-research-ship/`
- Deltamarin Ltd. project sheet, "S.A. Agulhas II" —
  `deltamarin.com/app/uploads/pregenerate_pdf/sa-agulhas-ii.pdf`
- South African National Antarctic Programme (SANAP), "Vessels" —
  `sanap.ac.za/explore/vessels`
- fleetphoto.ru vessel page (`/vessel/15021`) and project page (`/projects/1952`) for
  Vasiliy Golovnin / Project 10620
- korabel.ru ship page (`/fleet/info/2146.html`) and project page
  (`/fleet/info/34195.html`) for Vasiliy Golovnin / Project 10620
- VesselFinder, vesseltracker, maritimeoptima.com, MarineTraffic-family pages (dimension
  and tonnage cross-checks, both vessels)
- English Wikipedia, "Vasiliy Golovnin (ship)" and "S. A. Agulhas II" (tertiary; used
  only to locate and then independently confirm primary citations, not as a standalone
  source)
- IMO GISIS public ship-particulars module — attempted directly for both IMO numbers;
  redirects to an authentication wall as of this session, so **not** usable as an
  anonymous public source (contrary to its general reputation for open ship-particulars
  lookup)
- `docs/research/POLARIS_APPLICABILITY.md` and `docs/backlog.md` (this repo's own prior
  research, corroborated rather than overturned by this session's fresh search)

## What remains open (see `docs/backlog.md` for the tracked one-liners)

- Golovnin's modern IACS/RS ice-class equivalent — structurally unverifiable without the
  Polar Ship Certificate, current RS class certificate, or PWOM (FESCO/NCPOR request).
- IMO Polar Ship Category (A/B/C) for **both** vessels — needs an authenticated GISIS
  lookup or the actual certificates.
- Golovnin's displacement — genuine 16,100 t vs. 20,200 t conflict between two korabel.ru
  pages, unresolved.
- Golovnin's icebreaking capability and any ice-concentration/thickness operating limit
  for either ship — no published figure exists for the former; no published
  concentration limit exists for either, and none should be assumed to.
