# POLARIS applicability — what role it should play in this system

Research-only, 2026-09-07. Governs: v3 §48A.4 and the late section "POLARIS / POLAR
RISK METHODS". **No design decision here is approved yet** — proposals belong in an ADR;
deferred items go to `docs/backlog.md`.

Primary sources were retrieved and read in full, not summarised from secondary
descriptions: IMO MSC.1/Circ.1519 (complete text, both RIV tables), the IMO Polar Code as
adopted (MEPC 68/21/Add.1 Annex 10), Transport Canada TP 12259E (AIRSS), Canada's ASSPPR
SOR/2017-286 including Schedule 2, Traficom's 2025 ice-class equivalence regulation, and
the AARI–NIC–NMI Antarctic ice-chart service. Where a claim rests on a secondary source it
says so.

This file complements `docs/NAVIGATION_RESEARCH.md` §1, which extracted the POLARIS
mechanics correctly and which this file does not repeat except where a new source changes
or sharpens the reading. It also closes loose ends flagged in
`docs/research/RESEARCH_MATRIX.md` rows 2, 3 and 4.

---

## 0. The recommendation, first

**POLARIS should be an advisory risk indicator and a comparative research layer in this
system. It should not be a hard constraint, and this project should not ship a numeric RIO
for MV Vasiliy Golovnin at all until her ice-class equivalency is on paper.**

Four independent reasons, each sourced below and each sufficient on its own:

1. **IMO says it is not a constraint.** MSC.1/Circ.1519 §1.4: any methodology built on this
   guidance "should not be interpreted as a 'Go/No Go' tool but as a decision support tool."
   Hard-constraining a route optimiser on RIO would be a stricter use of POLARIS than the
   regulator's own text supports, and a judge who has read the circular can say so.
2. **We cannot index the table for this ship.** POLARIS rows are IACS Polar Classes and
   Finnish–Swedish classes only. The Golovnin carries a superseded Russian notation
   (`KM(★) ULA`) that appears in no POLARIS row, in no current RS mark set, and in no
   regulator's equivalence table we could find. The Polar Code's own method for resolving
   this (Part I-B §4) is a per-ship, owner-initiated, flag-approved engineering assessment —
   there is no lookup table, by design. Across the plausible candidate rows the same ice
   regime yields RIO from **+19 (normal operation) to −21 (special consideration)**. That is
   not a number to put on a screen.
3. **We cannot supply the input.** RIO is indexed by WMO stage of development. The prototype
   has 25 km total concentration. Even the best free Antarctic ice-type product resolves five
   stage classes where POLARIS wants eleven, and the residual ambiguity alone spans all three
   operational tiers.
4. **The Antarctic evidence base is close to empty, and the Arctic one is thinner than most
   people assume.** PAME — the Arctic Council working group that owns the review — states
   that the maritime community has "limited understanding of the suitability of POLARIS,
   both as an operational tool and as a component of maritime regulation." That is the
   *Arctic* verdict from POLARIS's own constituency.

What this buys us on a slide is stronger than a RIO number would be: we can show the
regulator's framework, show precisely which two inputs are missing, show who holds them,
and show what the answer would swing between. Judges reward a project that knows the
boundary of its own evidence. They do not reward a plausible-looking index computed from
inputs that cannot produce it.

---

## 1. What POLARIS actually is

### 1.1 Status: interim guidance, explicitly not a go/no-go tool

**IMO MSC.1/Circ.1519, 6 June 2016**, "Guidance on methodologies for assessing operational
capabilities and limitations in ice". POLARIS is the Appendix; the circular body is the
guidance on methodologies generally.

Four status facts from the text, all load-bearing:

- **Circular ¶4:** "This guidance has been issued as 'interim guidance' in order to gain
  experience in its use. It should be reviewed four years after the entry into force of the
  Polar Code in order to make any necessary amendments based on experience gained." The
  Polar Code entered into force 1 January 2017. **That review was due around 2021 and has
  not happened** (§3.2 below).
- **§1.4 (guidance body, not the appendix):** "Any system or methodology for assessing
  structural capabilities and limitations based on this guidance should not be interpreted
  as a 'Go/No Go' tool but as a decision support tool. The decision for operating in specific
  ice regimes should be based on the consideration of personnel on board qualified in
  accordance with chapter 12 of the Polar Code…" This is the single most important sentence
  in the circular for our architecture and it is routinely ignored in the literature.
- **§4.2:** "Alternative methodologies to that contained in the appendix may be accepted
  provided that they meet the content described above." POLARIS is *an* acceptable
  methodology, not *the* methodology.
- **§3.4 footnote 1:** the Polar Ship Certificate §5.1 records "Name of system:
  …e.g. AIRSS, POLARIS, Ice Certificate". Three recognised systems, named by IMO.
  *(This settles the loose end flagged in `RESEARCH_MATRIX.md` row 4: the unnamed third
  system is the Russian Ice Certificate — see §4.3.)*

### 1.2 Mechanics — confirmed against the full text

`docs/NAVIGATION_RESEARCH.md` §1 already reproduces the formula, Table 1.1, Table 1.2 and
Table 1.3 correctly; re-reading the source confirms every value. Rather than duplicate,
here is what that section did not capture and what a reader needs to avoid getting wrong.

**Table 1.1 boundaries are half-open and the two columns differ.** `RIO ≥ 0` normal;
`−10 ≤ RIO < 0` is *elevated operational risk* for PC1–PC7 but already *operation subject to
special consideration* for ice classes below PC7 and ships with no ice class; `RIO < −10` is
special consideration for everyone. Secondary summaries get this wrong routinely — PAME's own
project page renders the middle band as "between -1 and -10", and Liu et al. (2025) write it
as both `−10 < RIO* < 0` and `−10 < RIO* ≤ 0` within four pages. **Use Table 1.1, never a
paraphrase.** For our vessel this distinction is not academic: if the Golovnin resolves to a
Finnish–Swedish equivalent rather than a Polar Class, the entire "elevated risk" band
disappears and every negative RIO becomes special consideration.

**Table 1.4 (decayed ice) is barred to us.** §1.1.3: the standard Table 1.3 values "should be
used unless ice decay is confirmed by ice information/visual observation by personnel on
board qualified in accordance with chapter 12 of the Polar Code. Only then may table 1.4 be
used." A shore-side forecast cannot authorise Table 1.4. This matters more in the Antarctic
than the Arctic — austral-summer ice *is* decaying (§3.4) — and it means the regulation forces
us onto the conservative table precisely where the conservatism is least physically justified.

**§1.2.1 wording is about limitation, not permission.** "POLARIS uses a Risk Index Outcome
(RIO) value to assess limitations for operation in ice." Combined with §1.4, the object is a
limitation on how you operate, not a gate on whether you go.

**§1.6.4, escort:** "For voyage planning purposes when icebreaker escort is intended to be
used, the RIO derived from non-escorted historical ice data may be assumed to be modified by
adding 10 to its calculated value. However, it is cautioned that this is an average value
which can vary significantly. For actual operations, the RIO under escort should not be
modified." Note the two clauses the repo's earlier extract compressed: the +10 is
**planning-only**, and it is **explicitly forbidden in real time**. Any convoy feature must
respect that split or it misapplies the rule it cites.

**§1.7, glacial ice:** three clauses, and none of them scores anything. §1.7.3: "Where
glacial ice is encountered, in addition to the RIO, a safe stand-off distance should be
observed by the ship. This stand-off distance should be recorded in the PWOM." The
regulation creates a stand-off *requirement* and then delegates the *number* to the ship's
own manual. We do not have the Golovnin's PWOM, so we do not have that number, and we must
not invent one.

### 1.3 What is provably absent from the text

Word-frequency over the complete extracted text of MSC.1/Circ.1519:

| Term | Occurrences |
|---|---|
| `Antarctic` | **0** |
| `pressure` | **0** |
| `compression` | **0** |
| `drift` | **0** |
| `ridge` / `ridging` | **0** (the single regex hit is inside "bridge", line 182) |
| `iceberg` / `growler` | **0** (the term used is "glacial ice", §1.7) |
| `Arctic` | 2 — both naming Canada's Arctic Ice Regime Shipping System |

This corroborates `NAVIGATION_RESEARCH.md` §7.2 and adds the important negative: **the
circular that governs POLARIS never uses the word "Antarctic".** POLARIS reaches the
Antarctic only because the Polar Code does (the Code defines Antarctic waters as the sea area
south of 60°S and applies bipolar), not because anything in POLARIS was written for, tested
in, or scoped to the Southern Ocean.

### 1.4 Provenance — the tell is in the appendix's own first paragraph

Appendix ¶I: "POLARIS has been developed incorporating experience and best practices from
Canada's Arctic Ice Regime Shipping System, the Russian Ice Certificate supplemented by pilot
ice assistance as prescribed in the Rules of Navigation on the water area of the Northern Sea
Route and other methodologies."

Every named ancestor is Arctic: the Canadian Arctic zone/date regime, the Russian Ice
Certificate, and the Northern Sea Route rules. Appendix ¶IV.1 then fixes the ice-class axis
as "a combination of IACS Polar Class ice classes and ice classes assigned equivalence to
Finnish-Swedish Ice Class Rules under HELCOM" — i.e. a Baltic winter-navigation regime and a
polar structural-design standard. **The risk index is an Arctic-and-Baltic construction end
to end.** That is not a criticism; it is the fact that decides how far south we may carry it.

---

## 2. The ice-class question, and why it is not a research failure

`docs/backlog.md` records the state accurately: Golovnin's ice class is RS old-system
`KM(★) ULA` (verified in-repo against a hull registry), the modern Arc/PC equivalent is not
sourced, and one Russian source denies `ULA = Arc5`. This section establishes *why* it is not
sourced, which turns out to be a stronger finding than a number would have been.

### 2.1 POLARIS has no row for this ship

Table 1.3 rows, exhaustively: PC1, PC2, PC3, PC4, PC5, PC6, PC7, IA Super, IA, IB, IC, Not
Ice Strengthened. **There is no Arc row and no ULA row.** A Russian-classed vessel cannot be
looked up; it must first be mapped onto a Polar Class or a Finnish–Swedish class.

### 2.2 RS itself no longer uses the notation

RS's current *Nomenclature of distinguishing marks* (retrieved from rs-class.org) lists the
ice-class marks RS assigns today: `Ice1–Ice3`, `Arc4–Arc9`, `Icebreaker6–Icebreaker9`,
`PC1–PC7`, and the Baltic classes `IA Super, IA, IB, IC, II, III`. Word-boundary search of
that document returns **zero** hits for `ULA`, `UL` or `LU5`. A ship still described as ULA
is being described by a mark from a superseded edition of the RS Rules — which is exactly
what a 1988 hull would carry if nobody has re-documented it.

### 2.3 The one regulator-grade RS mapping that exists stops one rung short

Canada's **Arctic Shipping Safety and Pollution Prevention Regulations (SOR/2017-286),
Schedule 2**, Column 13 "Russian Maritime Register of Shipping", verbatim:

| Canadian Type | RS notations (Column 13) | IACS column (Column 8) | FSICR column (Column 7) |
|---|---|---|---|
| Type A | **UL or LU5 or Arc5** | PC1 to PC7 | 1A Super |
| Type B | L1 or LU4 or Arc4 | – | 1A |
| Type C | L2 or LU3 or Ice 3 | – | 1B |
| Type D | L3 or LU2 or Ice 2 | – | 1C |
| Type E | L4 or LU1 or Ice 1 | – | Category II |

Three things follow. First, `UL → LU5 → Arc5` is a **regulator-grade** equivalence, not
folklore — which is why the naive "ULA = Arc5" reading is wrong: **ULA is a distinct, higher
old-system category than UL**, and equating it to Arc5 would map a higher class onto a lower
one. Second, **`ULA` does not appear anywhere in the regulation** (zero word-boundary
matches in the full consolidated text): Canada's own table stops at UL. Third, Canada's
equivalence is coarse to the point of uselessness for our purpose — it lumps PC1 through PC7
*and* 1A Super into a single Type A bucket, which spans RIV rows from `PC1` to `IA Super`,
i.e. most of Table 1.3.

Independent secondary sources describe the old→new ladder as `Л4/Л3/Л2/Л1/УЛ/УЛА` →
`ЛУ1…ЛУ9` → `Ice1–Ice3 / Arc4–Arc9`, with ЛУ*n* mapping one-to-one onto the modern
categories. **INFERENCE, clearly labelled as such:** extending Canada's own five-rung ladder
by one rung puts `ULA → LU6 → Arc6`. We could not source that final step from RS, from
Canada, or from Russian Wikipedia's own class table, all of which define ULA only
operationally — "independent navigation in all areas of the World Ocean during the
summer–autumn navigation season" — with no thickness and no modern equivalent. **Do not
build on this inference.**

### 2.4 The EU/Finnish route has been closed

Traficom's current equivalence regulation (**TRAFICOM/281964/03.04.01.00/2023**, in force
01.01.2025, "Finnish ice classes equivalent to class notations…") is the natural
regulator-grade path from a class-society notation to a Finnish–Swedish class, and therefore
to a POLARIS row. Its Annex 1 contains tables for ABS, BV, CCS, CRS, DNV, **IRS**, KR, LR,
ClassNK, PRS, RINA and a common Polar Class table. **There is no Russian Maritime Register of
Shipping table** — zero occurrences of "Russian" in the document. RS is not a recognised
classification society for this purpose in the current EU/Finnish regime. Table 12 does give
the Polar Class bridge we can use for anything that *is* PC-classed: `PC1–PC6 → IA Super`,
`PC7 → IA`, "in other respects than engine output".

### 2.5 The Polar Code says there is no table, on purpose

**IMO Polar Code, Part I-B, §4 "Method for determining equivalent ice class"** (text as
adopted, MEPC 68/21/Add.1 Annex 10). The relevant clauses:

> "The basic approach for considering equivalency for categories A and B ships can be the
> same for both new and existing ships. It involves comparing other ice classes to the IACS
> Polar Classes. … The responsibility for generating the equivalency request and supporting
> information required should rest with the owner/operator. Review/approval of any
> equivalency request should be undertaken by the flag State Administration, or by a
> recognized organization acting on its behalf…"

The process is: select a target Polar Class; compare materials against the IACS Polar Class
Unified Requirements; compare hull and machinery strength levels and quantify compliance.
§5 adds that for existing ships "service experience can assist in risk assessment" — a
shortfall in ice-belt extent may be accepted where there is no damage record.

**This is the finding.** The absence of a published `ULA → PC*n*` table is not a gap in our
literature search. **There is no such table because the Code deliberately makes equivalency a
per-ship, owner-initiated, flag-approved engineering assessment**, informed by that specific
hull's scantlings, machinery and service history. A software team cannot derive it, should
not estimate it, and should say so plainly.

The Bahamas Maritime Authority's Polar Code marine notice (MN 88) puts the operational
consequence bluntly, and it cuts directly at our vessel: for existing ships built to other
rules, "the operational assessment and assessment of limitations for operating in ice
conducted in accordance with Paragraph 2 of Part I-B of the Polar Code and MSC.1/Circ.1519
**may result in allowable ice conditions being less severe than those historically
encountered by a ship**", and flag administrations may therefore record *more severe*
historical conditions in Polar Ship Certificate §5.1 on the company's request, subject to an
RO assessment of the historical record. In other words: a naively computed POLARIS RIO can
tell a ship not to go where that ship demonstrably and safely goes every season, and the
regulator anticipated exactly that failure mode for exactly this class of vessel.

### 2.6 What the ambiguity is worth, in RIO points

Take a regime plausible for the fast-ice approach at Bharati or Maitri: **9/10 medium
first-year ice, 1/10 thick first-year ice.** Computed directly from Table 1.3:

| Candidate row | RIO | Table 1.1 outcome |
|---|---|---|
| PC4 | **+19** | Normal operation |
| PC5 | **+9** | Normal operation |
| PC6 | **−1** | Elevated operational risk |
| PC7 | **−11** | Operation subject to special consideration |
| IA Super | **−11** | Operation subject to special consideration |
| IA | **−21** | Operation subject to special consideration |

**A 40-point spread across all three operational tiers, driven by nothing but the unresolved
class question.** A milder regime (3/10 open water, 3/10 thin FY 2nd stage, 4/10 medium FY)
collapses the disagreement — every candidate row returns normal operation, RIO +1 to +19 —
which is itself instructive: the class ambiguity is harmless where the answer does not matter
and decisive where it does. That is the worst possible property for a safety indicator, and
it is the reason a single RIO number must not be shipped for this hull.

### 2.7 What would settle it, and who holds it

Exactly three documents, none of which are public, all of which NCPOR can request as
charterer:

1. **The Polar Ship Certificate**, §2.2 (operational limitations) and §5.1 (name of the
   accepted system and the reference document number). This says whether the Golovnin's
   accepted methodology is POLARIS, the Russian Ice Certificate, or something else, and it
   states her IMO Polar Ship Category (A/B/C). *Held by:* FESCO, and the Russian Federation
   flag administration (or RS acting as RO).
2. **The current RS class certificate**, giving the notation as RS records it *today* —
   which may already be a re-issued `Arc*n*` or `PC*n*` mark rather than the historical ULA.
   *Held by:* FESCO / RS.
3. **The PWOM**, which carries the ship-specific ice operating limitations, the recommended
   speeds under elevated risk (§1.4.4), and the glacial-ice stand-off distance (§1.7.3).
   *Held by:* the ship.

Until at least (1) is in hand, the honest state of item 2 is: **UNVERIFIED, and structurally
unverifiable from open sources.**

---

## 3. Antarctic applicability — the core question

### 3.1 The question, stated precisely

POLARIS is not "an Arctic system used in the Antarctic". It is a bipolar *instrument* — the
Polar Code applies south of 60°S, and MSC.1/Circ.1519 is the referenced methodology — built
on an *evidence base* that is entirely Arctic and Baltic. The question is not whether we are
allowed to use it (we are). It is whether the RIV numbers, calibrated on northern experience,
mean the same thing in the Southern Ocean, and whether the hazards it omits are the ones that
dominate here.

### 3.2 The evidence base is thin even in the Arctic — from POLARIS's own review body

PAME (Protection of the Arctic Marine Environment, an Arctic Council working group) runs the
project intended to feed the overdue IMO review. Its project page states, verbatim:

> "The POLARIS methodology was agreed at IMO as 'interim guidance' providing for a review
> four years after the entry into force of the Polar Code in 2017, in order to make any
> necessary amendments based on experience gained. **To date no review has taken place**…"

and, more damningly:

> "To date, data collection and formal evaluation of the effectiveness of POLARIS has been
> limited to **isolated university-based studies which have typically focused on single ship
> experiences / load monitoring. No known coordinated or comprehensive review has taken
> place.** Feedback from ship operations has not been forthcoming. As such the maritime
> community, including the Arctic States that rely on the Polar Code (and through it, the use
> of POLARIS) to ensure safety of shipping in their waters and protection of the environment,
> **have limited understanding of the suitability of POLARIS, both as an operational tool and
> as a component of maritime regulation.**"

ABS's Director of Polar Research told the IMO's own Polar Maritime Seminar (Nov 2022) the
same thing from the industry side: "POLARIS is interim guidelines, **no real proposals to
update because of lack of data**", followed by the slide question "Still we see some
surprising activities in polar waters — Is POLARIS 'getting the job done'?" The same deck
records that the decision guidance "is not fully being used as intended" and that "planning
voyage and 'desktop exercises' are incorporating negative RIOs with planned mitigation (this
was not the intent)".

**Two things follow for us.** First, the strongest possible statement about Antarctic
validation is bounded above by the Arctic one, and the Arctic one is that no coordinated
evaluation exists. Second — and this is the one an adversarial judge will reach for — the
specific misuse ABS names is *exactly what a route optimiser does by default*: computing
negative RIOs at the desk and routing through them with a mitigation attached. If we build
POLARIS into the optimiser we walk straight into the failure mode the regulator's own experts
have already flagged.

### 3.3 What Antarctic POLARIS literature actually exists

Four papers, and none of them is the validation we would want:

| Work | What it is | What it is not |
|---|---|---|
| **Kujala, Kämäräinen & Suominen, POAC 2019**, "Validation of the New Risk Based Design Approaches (POLARIS) for Arctic and Antarctic Operations" | Applies POLARIS to two ships — SA Agulhas II operating independently in the Antarctic, MT Uikku under escort in the Kara Sea — to determine a suitable *ice class*. Concludes "**PC 3 is the most suitable ice class for ships navigating in harsh Antarctic ice conditions**". | Not a validation of RIO thresholds against Antarctic outcomes, despite the title. It is a design-selection exercise. |
| **Liu, Yan, Peng, Xie & Sun (2025)**, *J. Mar. Sci. Eng.* 13(7):1267, "Vessel Safety Navigation Under the Influence of Antarctic Sea Ice" | The only Antarctic-focused POLARIS-adjacent paper we found. Satellite SIC + thickness, icebreaker-convoy kinematics, Antarctic routes. | **Does not compute the IMO RIO.** It computes a surrogate, `RIO* = RIV × SIC + 3 × (10 − SIC) − 10T`, from Li et al. (2020) and Xie et al. (2023), collapsing eleven ice-type columns into one RIV plus a binary first-year/multi-year flag and a −10 penalty that appears nowhere in MSC.1/Circ.1519. See §5.5. |
| **Xu, Xu, Ma, Qian & Li (2024)**, *J. Mar. Sci. Eng.* 12(5):827 | Applies POLARIS to Liaodong Bay, Bohai Sea — a low-latitude seasonal ice sea — with GF-4 imagery, and argues the outcome "concurs with acknowledged ice patterns and local maritime practices". | Not Antarctic; and "concurs with local practice" is corroboration, not validation against outcomes. |
| **Matsuzawa & Akane, POAC 2025**, paper 108 | POLARIS-based operational-limitation assessment for JAMSTEC's PC4 R/V Mirai II. Finds "the classification of multi-year ice is essential for accurate estimation of navigation risks and that parameters such as ice age and ice thickness have a considerable impact on it." | Arctic Ocean. Useful to us only for the input-sensitivity result. |

Adjacent and relevant: **Kujala's group has a genuine Antarctic full-scale dataset** — SA
Agulhas II has been instrumented for hull ice loads since her 2012 delivery and measured on
annual SANAE relief voyages. If POLARIS were ever going to be validated in the Antarctic,
that is the instrument. It has not been used for that.

Also relevant, from the negative side: a paper titled "Probabilistic analysis of operational
ice damage for Polar class vessels using full-scale data" (*Structural Safety*, Elsevier, PII
S0167473023001108) is reported to state that **no direct relationship between RIO values and
the probability of ice-induced hull structural damage has been established.** *(Read only via
a search-result summary — the full text is paywalled and we did not open it, and an attempted
DOI lookup returned a different paper, so we do not have a verified DOI or author list.
**UNVERIFIED**; settled by reading the article itself. If it holds, it is the single most
important sentence about POLARIS in the literature, and it is about the Arctic.)*

**Honest verdict, and it is the defensible one: there is no published validation of POLARIS
RIO thresholds against Antarctic operational outcomes. Say that plainly on the slide.**

### 3.4 The physical reasons an Arctic-calibrated index behaves differently here

Four, in decreasing order of how much they matter to our corridor.

**(a) The multi-year columns are inapplicable in our sector, which compresses POLARIS's
dynamic range to nothing.** NSIDC: "Multiyear ice is more common in the Arctic than in the
Antarctic", and "most of the multiyear ice that does occur in the Antarctic persists because
of a circulating current in the Weddell Sea, on the eastern side of the Antarctic Peninsula."
The Cape Town → Bharati/Maitri corridor is in the Indian Ocean sector, not the Weddell. The
POLARIS columns that carry the steep RIV penalties and therefore do most of the
discriminating — Second Year, Light Multi-Year, Heavy Multi-Year — are largely inapplicable
here. What is left to discriminate on is the first-year block, and across those columns the
RIV range for the classes we might plausibly assign the Golovnin is only about four points
(+2 to −2 for IA Super, +1 to −3 for IA, +1 to −2 for PC7). **POLARIS is a low-resolution
instrument in our sector specifically.**

**(b) Austral-summer Antarctic ice is measurably weak, and the framework forbids us from
saying so.** Suominen, Lu, Kujala & Bekker (POAC 2021) measured sea-ice properties from SA
Agulhas II **on the zero-meridian side** — i.e. the Dronning Maud Land approach, essentially
the Maitri leg — over austral summers 2012–14 and 2018–19: mean flexural strength ≈ **280 kPa**
(range 130–510 kPa), vertical compressive strength 100 kPa–3.0 MPa (mean 740 kPa), horizontal
100 kPa–1.5 MPa (mean 560 kPa), shelf ice 100–400 kPa (mean 160 kPa), salinity 1–8 ‰,
density 830–940 kg m⁻³. Their own reading: "the flexural strength of the sea ice is
relatively weak during the summer season… somewhat expected as the ice is in melting stage
during the summer season and the Antarctic waters are known for high salinity", with the
caveat that "the number of samples is small and should be verified with additional
measurements." *(We did not source a matched Arctic/Baltic winter flexural-strength figure in
this session, so the comparison is directional, not quantified — UNVERIFIED.)*
This is precisely the situation Table 1.4 exists for, and §1.1.3 bars us from using Table 1.4
without on-board confirmation by a qualified observer. **The framework has a mechanism for
our season and forbids us to use it remotely.**

**(c) The hazards that actually beset ships here are the ones POLARIS does not score.** Ice
pressure and compression against a fast-ice edge, ridging, rapid lead closure, marginal-ice-zone
swell — POLARIS scores none of them (§1.3). The repo has already established
(`NAVIGATION_RESEARCH.md` §7.2) that compression is the mechanism that beset MV Magdalena
Oldendorff and MV Akademik Shokalskiy, that "the most dangerous case for shipping is
compression at the fast-ice edge when the general drift sets into it at an angle", and that
this is exactly the Bharati/Maitri offloading geometry. It has also established that no
operational Antarctic pressure product exists anywhere. **A high RIO at a fast-ice edge in a
compression event is not a safety statement.**

**(d) Icebergs and their debris.** POLARIS §1.7 requires a stand-off distance and supplies no
number, no detection model and no scoring. In the Southern Ocean, glacial ice is not a corner
case; it is a defining feature of the corridor. The project's own iceberg pillar
(`models/iceberg/`) is doing work POLARIS does not attempt, and the growler/bergy-bit gap
already documented in `DIFFERENTIATION.md` is a gap POLARIS shares and does not mitigate.

**The net direction of bias, stated carefully.** On the one term POLARIS does score — ice type
× concentration — Arctic winter calibration applied to weaker Antarctic summer ice is
**conservative**, i.e. probably safe-side, and the Table 1.4 bar makes it more so. That is a
genuine argument in POLARIS's favour and we should make it rather than suppress it. But
conservatism on the scored term buys nothing against the unscored ones. **A framework that is
cautious about ice strength and silent about compression, bergs and the MIZ is not a
conservative safety envelope; it is a partial one.** That asymmetry is the honest reason not
to promote it to a constraint.

---

## 4. AIRSS and the other recognised methods

MSC.1/Circ.1519 footnote 1 names three systems for Polar Ship Certificate §5.1: **AIRSS,
POLARIS, Ice Certificate.** All three were read or sourced.

### 4.1 AIRSS — jurisdictionally irrelevant, methodologically instructive

**Transport Canada TP 12259E, Arctic Ice Regime Shipping System (AIRSS) Standard.** Scope,
§1.1.1: it "sets out the methodology to be used by the Master to assess vessel operations
capabilities and limitations in ice when navigating in the circumstances described in section
8(2) of the Arctic Shipping Safety and Pollution Prevention Regulations". Structure is the
same shape as POLARIS — `IN = (C1 × IM1) + … + (Cn × IMn)`, concentrations in tenths, Ice
Multipliers by ship category — with ship categories CAC 3, CAC 4 and Types A–E rather than
Polar Classes. ASSPPR §8(2)(a) sets the decision rule: for vessels constructed before
1 January 2017 other than Polar Class vessels, navigation outside the zone/date window is
permitted where "the ice numeral… is greater than or equal to zero".

The repo's existing backlog line — "do not cite AIRSS as applicable" — is **correct and
should stand.** The jurisdiction is the Canadian Arctic Shipping Safety Control Zones. It has
no reach south of 60°S.

But two AIRSS clauses do something POLARIS does not, and they are worth importing as *ideas*
under our own name:

- **§4.3 Ridged Ice:** "If the total ice concentration in a regime is 6/10 or greater, and
  3/10 or more is of an ice type (other than Brash Ice) that is deformed by Ridges, Rubbles
  or Hummocking, the IM **must be decreased by a value of 1**." A hard, quantified deformation
  penalty. POLARIS has no equivalent.
- **§4.2 Decayed Ice:** thaw holes or rotten ice raise the IM by 1 — the same idea as POLARIS
  Table 1.4 but expressed as a rule rather than a second table, and without the qualified-
  observer gate.

AIRSS also handles escort more concretely than POLARIS's flat +10: §4.5.1 says the Ice Numeral
under escort is computed on the ice *in the track ahead*, and floes under 2 m diameter in that
track may be treated as brash with `IM = +2`.

**Implication for us.** If we build a deformation or compression term — and
`NAVIGATION_RESEARCH.md` §7.2 argues we should, because it is genuine white space — AIRSS
§4.3 is the precedent that shows a regulator is willing to encode deformation as a discrete
index penalty. We must present any such term as **our own layer inspired by AIRSS**, never as
AIRSS compliance and never as a POLARIS extension.

### 4.2 The Canadian regulator's own multi-society mapping — usable context, not a POLARIS row

ASSPPR Schedule 2 (§2.3 above) is the only regulator-issued table we found that puts RS
notations, IACS Polar Classes and Finnish–Swedish classes in the same row. It is worth
keeping in the repo for context, and worth *not* over-reading: it establishes equivalence for
Canadian zone/date entry, not structural equivalence, and its Type A bucket is too wide to
select a RIV row.

### 4.3 The Russian Ice Certificate / Ice Safety Passport — the method most appropriate to *this* ship

This is the third IMO-named system and the one the repo has not previously identified.

RS's own service description (rs-class.org, "Ice Navigation Ship Certificate, Ice
Certificate"): the **Ice Navigation Ship Certificate (Form 3.1.5)** "is intended to reduce the
risk of damage to ship's hull when interacting with ice, as well as to specify the permissible
speed in ice and other parameters depending on the design features and technical
characteristics of the ship." It "may be issued for ships in service regardless of whether the
ship has an ice class assigned or is an RS-classed ship", full-term for up to five years or
short-term for a specific port and season, and "the basis for issuing a Certificate of
acceptable conditions for ice navigation of a vessel is an **Ice Safety Passport**." The
Indian Register of Shipping's own polar guidance (IRS-G-SAF-01, 2017, §2.2.3) lists the same
system as "Ice Passport by Russia" alongside AIRSS and the Canadian zone/date system as
methodologies that "may be used according to ship's intended navigation area in polar waters".

**Why this matters more than it looks.** The Golovnin is a Russian-flagged, RS-classed hull
whose ice-class notation cannot be indexed into POLARIS. The Ice Certificate is
*ship-specific* rather than *class-row-indexed* — it is computed for that hull's actual
scantlings and machinery and outputs permissible speeds in ice directly. It sidesteps the
entire equivalency problem in §2, and MSC.1/Circ.1519 §4.2 explicitly permits it. There is a
real chance that **the Golovnin's Polar Ship Certificate §5.1 names the Ice Certificate, not
POLARIS.** If so, computing a POLARIS RIO for her would be computing the wrong index — a
detail that would look very bad under questioning and very good if we raise it first.

We could not obtain a specimen Ice Certificate, its input format, or its output schema; RS
publishes the procedure in Appendix 22 to the *Manual on Technical Supervision of Vessels in
Operation* but we did not retrieve that document. **UNVERIFIED**, and settled by the same
request to FESCO/NCPOR that settles §2.7.

### 4.4 Verdict on alternatives

Nothing here displaces POLARIS as the framework to *research and display*. But two facts
should be on the record and, ideally, on the slide: **AIRSS encodes ridging and POLARIS does
not**, and **the methodology actually accepted for this specific vessel may not be POLARIS at
all.** Neither should be implemented on speculation.

---

## 5. POLARIS inputs versus what this project actually has

### 5.1 The requirement

RIO needs, per ice regime: the **concentration in tenths of each WMO stage of development
present**, mapped to POLARIS's eleven ice-type columns plus ice-free. Not total concentration.
Not thickness. Stage of development, partitioned.

### 5.2 What the prototype has

25 km NSIDC/NOAA **total** sea-ice concentration, plus a modelled thickness field available
from CMEMS (`GLOBAL_ANALYSISFORECAST_PHY_001_024`, `sithick`, ~1/12°, coverage to 80°S — as
established in `NAVIGATION_RESEARCH.md` §7.1) and the planned second U-Net output channel.
**No stage-of-development decomposition, from any source, at any resolution.**

**Therefore: this project cannot compute a real POLARIS RIO today. Confirmed, not estimated.**

### 5.3 What would supply the decomposition — the actual Antarctic options, priced

This is the part that has not previously been researched in this repo, and the answer is
better and worse than expected.

PolarView — the service the Australian Antarctic Program uses — states the situation plainly:

> "Many Arctic nations support national ice centres that produce regular ice charts to support
> shipping in their coastal waters. **There are no national ice centres producing sea ice
> charts for the Southern Ocean.** However the US National Ice Centre and Norwegian Ice
> Service provide regular charts for parts of the Antarctic."

| Option | Ice-type content | Coverage | Cadence / latency | Cost | Verdict for us |
|---|---|---|---|---|---|
| **AARI–NIC–NMI collaborative Antarctic analysis** (`ice.aari.aq`) | **Yes** — SIGRID-3 with stage of development; spec: "1 - New ice, 3 - Young ice, 7 - Thin first-year ice, 6 - First-year ice for ice thicker than 7, 7* - Old ice, ^* - Iceberg"; partial concentrations tracked for old ice | **Hemispheric** — covers our corridor | Spec says weekly, alternating AARI/NIC (Thursday) and met.no (Monday); **observed practice in 2026 is roughly fortnightly** (Aug: 6th and 20th–21st; Sep: 3rd only as of 6 Sep), posted 1–3 days after the analysis date | **Free**, plain HTTP, ~3.5 MB zipped shapefile per chart, plus CT and SoD PNGs | **The only viable source.** Live and current (2026-09-03 chart present). |
| **Met Norway / Norwegian Ice Service Antarctic charts** (`cryo.met.no`) | Yes, SIGRID-3 shapefile | **Wrong sector** — published areas are Antarctic (general), Adelaide Island, Bransfield Strait, Antarctic Peninsula, **Weddell Sea – East**, South Georgia. Atlantic sector and Peninsula only. | Mondays, October–April, after 1500 UTC | Free | Not usable for Prydz Bay (76°E) or Dronning Maud Land east of the Weddell. |
| **USNIC Arctic and Antarctic Sea Ice Charts in SIGRID-3 (NSIDC G10013)** | Yes — "total sea ice concentration, partial concentration, stage of development, and ice form as defined by the WMO" | Was bipolar | **"As of 9 June 2023, bi-weekly production of the Antarctic data in this data set has been suspended indefinitely. The Arctic data is not affected and will continue to be produced."** | Free | **Dead for the Antarctic.** Archive 2003–2023 remains usable for hindcast/backtesting only. |
| **CMEMS `sithick`** | No — modelled thickness, not observed stage | Global, to 80°S | Daily, 10-day forecast | Free (account) | A *proxy*: binning modelled thickness into WMO stages is an assumption we would author, not an observation. Usable for a research layer, not for a published RIO. |
| **AMSR2 (Bremen, 3.125 km) / NSIDC CDR** | No — concentration only | Hemispheric | Daily | Free | Already in the stack; does not address this gap at all. |

### 5.4 Even the best option cannot fill the table — and here is what that costs

The AARI–NIC–NMI product resolves **five** ice classes where POLARIS wants **eleven**. The
mapping losses, and whether each one bites:

| Chart class | POLARIS columns it must be split across | Does the split change RIV? |
|---|---|---|
| New ice | New Ice | No — one column. |
| Young ice | Grey Ice, Grey-White Ice | Not for PC1–PC7, IA Super, IA (identical RIVs). **Yes for IB and below** (8-point RIO swing at 8/10 concentration). |
| Thin first-year | Thin FY 1st Stage, Thin FY 2nd Stage | Not for PC1–PC5. **Yes for PC6, PC7, IA Super, IA, IB, IC.** |
| **First-year thicker than thin** | **Medium FY <1 m, Medium FY, Thick FY** | **Yes, for every class below PC4. This is the killer.** |
| Old ice | Second Year, Light MY, Heavy MY | Yes — but largely moot in our sector (§3.4a). |

Quantifying the worst one. Regime: **9/10 "first-year ice thicker than thin", 1/10 ice-free** —
a single chart polygon that a shore-side system must assign to one of three POLARIS columns:

| Assigned as | RIO (PC7) | Outcome (PC7) | RIO (IA Super) | Outcome (IA Super) |
|---|---|---|---|---|
| Medium FY <1 m | **+3** | Normal operation | **+3** | Normal operation |
| Medium FY | **−6** | Elevated operational risk | **−6** | Special consideration |
| Thick FY | **−15** | Special consideration | **−15** | Special consideration |

**One chart polygon, three POLARIS answers, all three operational tiers.** Combine this with
the class ambiguity of §2.6 and the compound uncertainty is larger than the quantity being
estimated. That is the technical case, in numbers, for not shipping a RIO.

Liu et al. (2025) quantify the same fragility from a different direction: with satellite SIC
uncertainty σ ≈ 8 % and a first-year/multi-year misclassification rate of 8–12 %, a single
type misclassification moves their index by a full **10 points** — one entire tier — and they
conclude that "the limitations of the linear model become most apparent when RIO* values
approach critical operational thresholds of −10 and 0. Small variations in input parameters
can dramatically alter operational recommendations, creating threshold sensitivity that may
lead to inappropriate navigation decisions." A route optimiser evaluates thousands of cells;
by construction it spends most of its time near the thresholds.

Corroborating, from the Arctic: analysis fusing Alaska Sea Ice Program charts with Copernicus
products found Copernicus "systematically underestimates ice concentration relative to ASIP,
particularly in nearshore and marginal ice zones", and that ~36 % of AIS observations in
ice-affected waters corresponded to negative RIO — i.e. the index says vessels routinely
operate in elevated risk, which is either a fleet-wide safety finding or a calibration
problem, and nobody has established which.

### 5.5 The surrogate trap — name it, and refuse it

There is a published shortcut, and it is exactly the one this project would be tempted by:

```
RIO* = RIV × SIC + 3 × (10 − SIC) − 10T        (Xie et al. 2023, used by Liu et al. 2025)
```

with `T = 0` for first-year and `T = 1` for multi-year, after Li et al. (2020)'s
`RIO* = RIV × SIC + 3 × (10 − SIC)`. It takes total concentration and a binary type flag —
precisely what a project with SIC plus a thickness channel can produce — and returns something
that looks like a RIO and is compared against POLARIS's −10/0 thresholds.

**We should not do this, and we should say why.** It is not POLARIS. It replaces the
eleven-column stage-of-development table with one RIV, and the `−10T` term appears nowhere in
MSC.1/Circ.1519. Publishing its output as "POLARIS RIO" or "IMO-compliant" would be a
misrepresentation that a domain-literate judge can catch by opening the circular. If we ever
compute it, it must be labelled as **a published surrogate index (Li 2020 / Xie 2023), not the
IMO RIO**, with the substitution stated on the same screen.

---

## 6. The decision, argued against the four roles v3 lists

### 6.1 Hard constraint — **reject**

Five reasons, any one sufficient. (i) MSC.1/Circ.1519 §1.4 says it is not a go/no-go tool;
constraining on it is a stricter reading than the source supports. (ii) We cannot index the
RIV row for this hull (§2), so the constraint would be applied at an unknown threshold. (iii)
We cannot supply the input decomposition (§5), so the constraint would be applied to an
unknown quantity. (iv) The ABS/IMO seminar record identifies desk-planning through negative
RIOs as the actual observed misuse — which is what constraint-based optimisation does. (v) The
BMA marine notice warns that for existing ships POLARIS can produce limits *less severe than
those the ship has historically and safely operated in* — meaning a hard constraint could
forbid the Golovnin's real, proven route. A constraint that contradicts a decade of the
charterer's own operational record does not survive its first demo.

### 6.2 Advisory risk indicator — **accept, conditionally**

This is the right primary role, and the condition is that it stays honest about what it is.
Displayed as a panel, not a number on a route line, showing on the same screen:

- **inputs**: which ice-type decomposition was used, from which chart, of which analysis date;
- **the class assumption made explicit** — not one row but the *band*, e.g. "RIO between −11
  (IA Super) and +9 (PC5); the vessel's Polar Class equivalence is not certified";
- **the result and the Table 1.1 tier**, with the correct half-open boundaries and the correct
  column for the assumed class;
- **applicability**: interim IMO guidance, review overdue, no published Antarctic validation,
  scores no compression / ridging / iceberg term;
- **source and timestamp** of both the circular and the ice chart;
- **the operational interpretation in the circular's own words**, not a colour.

If the class band is unresolved, the panel shows the band and the reason — it does not pick a
row. v3's own instruction, "display its inputs, result, applicability, source, timestamp, and
operational interpretation rather than presenting an unexplained generic 'risk score'", is
satisfied exactly by this and by nothing weaker.

### 6.3 Comparative research layer — **accept, and this is where the differentiation is**

The genuinely novel work is not computing RIO; it is **quantifying how much the RIO does not
know**, using this project's own machinery:

- **Sensitivity as a first-class output.** The tables in §2.6 and §5.4 are computable
  continuously along a route. "This corridor's RIO is stable across the class band" versus
  "this corridor's RIO flips tier on the class assumption" is a genuinely useful operational
  statement, and nobody publishes it.
- **RIO against our own hazard layers.** Overlay RIO with the compression geometry
  (`NAVIGATION_RESEARCH.md` §7.2) and the iceberg exclusion zones (`models/iceberg/`). Where
  RIO is comfortable and the compression test is not, that disagreement *is* the finding —
  it is the Oldendorff and Shokalskiy failure mode, and it is exactly what POLARIS is blind
  to. This is a demo moment that no competitor built on POLARIS alone can produce.
- **A ridging term of our own, informed by AIRSS §4.3**, labelled as ours.
- **Backtesting against the archive.** NSIDC G10013's suspended Antarctic series still covers
  2003–2023 with full stage of development. That is a real, free, historical Antarctic ice-type
  archive against which RIO can be reconstructed for past seasons and compared with what the
  Golovnin and her peers actually did. **This is the closest thing to Antarctic POLARIS
  validation anyone could do with public data, and it is within this project's reach.**

### 6.4 Something else — the part that is not optional

Two POLARIS clauses should be adopted **as requirements, independent of any RIO calculation**,
because they are regulatory statements about what a system must account for:

- **§1.7.3 glacial-ice stand-off.** The requirement to hold a stand-off distance from glacial
  ice, recorded in the PWOM, is the regulatory basis for this project's iceberg CPA buffer.
  We adopt the requirement; we do not have the number and must not invent one. (`backlog.md`
  already flags the CPA stand-off distance as unsourced — this is the source for the
  *requirement*, not the value.)
- **§1.6.4 escort +10, planning only.** If a convoy or escort feature is ever built, the +10
  applies to voyage planning from non-escorted data and is explicitly forbidden in real time.

### 6.5 What to say on the slide

> POLARIS (IMO MSC.1/Circ.1519) is the regulator's framework for ice-class operating limits,
> and we implement it as an advisory panel — not as a route constraint, because IMO's own text
> says it is "not a 'Go/No Go' tool but a decision support tool". We do not publish a Risk
> Index Outcome for MV Vasiliy Golovnin, for two reasons we can name precisely. Her ice class
> is a superseded Russian notation with no POLARIS row, and the Polar Code makes that
> equivalence a per-ship flag-approved assessment, not a lookup — across the plausible rows
> the same ice gives RIO from +19 to −21. And POLARIS is indexed by ice *type*: the only free
> Antarctic ice-type chart resolves five stages where POLARIS needs eleven, which alone spans
> all three operational tiers. What we ship instead is the sensitivity band, the two documents
> that would close it, and the hazards POLARIS scores nowhere — compression at the fast-ice
> edge and glacial ice — which are the ones that actually beset ships in this corridor.

### 6.6 What would upgrade POLARIS to a harder role

In order, each independently necessary:

1. Polar Ship Certificate §5.1 obtained → we learn whether POLARIS is even her accepted system.
2. Ice-class equivalency obtained or certified → a single RIV row becomes defensible.
3. AARI–NIC–NMI SIGRID-3 ingested, with the five→eleven mapping assumptions written down and
   their RIO spread reported alongside every value.
4. PWOM stand-off distance and elevated-risk speeds obtained → the vessel-specific numbers
   stop being placeholders.

Even with all four, the role would be *advisory with a documented band*, not a hard
constraint, because §1.4 does not change and neither does the Antarctic validation gap.

---

## 7. Unverified, and what would settle each

| Item | Status | What would settle it | Who holds it |
|---|---|---|---|
| Golovnin's modern Arc/PC equivalence | **UNVERIFIED and structurally unverifiable from open sources** (§2.5) | Polar Ship Certificate §2.2/§5.1 + current RS class certificate + the Part I-B §4 equivalency submission | FESCO; Russian Federation flag administration / RS as RO; requestable by NCPOR as charterer |
| Whether POLARIS is her *accepted* system at all | **UNVERIFIED** | Polar Ship Certificate §5.1 "Name of system" | as above |
| `ULA → LU6 → Arc6` | **INFERENCE ONLY** — extends Canada's ladder by one rung; not stated by RS, Canada or any regulator we read | An RS Rules edition containing the old→new correspondence, or a direct answer from RS | RS |
| RIO vs. actual hull-damage probability ("no direct relationship established") | **UNVERIFIED** — read only in a search summary; source paywalled and the DOI we tried resolved to a different paper | Read *Structural Safety* PII S0167473023001108 in full, or an open preprint | Elsevier / the authors |
| Antarctic vs Arctic flexural-strength comparison | **UNVERIFIED** — the Antarctic figure (280 kPa mean) is sourced; no matched Arctic winter figure was retrieved | Timco & Weeks (2010) sea-ice-strength review or equivalent | open literature |
| Russian Ice Certificate input/output schema | **UNVERIFIED** | RS *Manual on Technical Supervision of Vessels in Operation*, Appendix 22 | RS (states it is freely available on rs-class.org) |
| Whether AARI–NIC–NMI charts reliably cover Prydz Bay and DML at usable polygon density in Dec–Mar | **UNVERIFIED** — product is hemispheric by specification; we listed the directory and read the spec but did not open a shapefile and clip it to the corridor | Download `aari_antice_YYYYMMDD_pl_a.zip` for a December analysis and clip to the corridor bbox | free, immediate — this is a one-hour task and should be done before any RIO work is scoped |
| Whether met.no's "Weddell Sea – East" region reaches our longitudes | **UNVERIFIED** — region names suggest not; bounds not read | Fetch the region's shapefile extent from cryo.met.no | free, immediate |

---

## Sources

Primary — regulation and standards:

- [IMO MSC.1/Circ.1519, 6 June 2016 — Guidance on methodologies for assessing operational capabilities and limitations in ice (POLARIS)](https://www.nautinst.org/static/uploaded/2f01665c-04f7-4488-802552e5b5db62d9.pdf) — full text retrieved and parsed
- [IMO — International Code for Ships Operating in Polar Waters (Polar Code), text as adopted, MEPC 68/21/Add.1 Annex 10](https://wwwcdn.imo.org/localresources/en/MediaCentre/HotTopics/Documents/POLAR%20CODE%20TEXT%20AS%20ADOPTED.pdf) — Part I-B §4 "Method for determining equivalent ice class"
- [Transport Canada TP 12259E — Arctic Ice Regime Shipping System (AIRSS) Standard](https://tc.canada.ca/sites/default/files/migrated/tp12259e.pdf)
- [Arctic Shipping Safety and Pollution Prevention Regulations, SOR/2017-286 (consolidated) — §8 and Schedule 2](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2017-286/FullText.html)
- [Traficom Regulation TRAFICOM/281964/03.04.01.00/2023 — Finnish ice classes equivalent to class notations (in force 01.01.2025)](https://www.finlex.fi/api/media/authority-regulation/687392/mainPdf/main.pdf)
- [Russian Maritime Register of Shipping — Nomenclature of distinguishing marks](https://rs-class.org/upload/iblock/cea/075adcecaeabb290f33361e157293b17.pdf)
- [RS — Ice Navigation Ship Certificate, Ice Certificate (Form 3.1.5) / Ice Safety Passport](https://rs-class.org/en/services/ice-navigation-ship-certificate-ice-certificate/)
- [Indian Register of Shipping IRS-G-SAF-01 — Guidelines on Operational Assessment of Polar Ships, 2017](https://www.irclass.org/media/2643/irs-g-saf-01_guidelines-on-operational-assessment-of-polar-ships-2017.pdf)
- [Bahamas Maritime Authority Marine Notice MN 88 v1.0 — Polar Code](https://www.bahamasmaritime.com/wp-content/uploads/2021/12/MN088-Polar-Code-v1.0.pdf)

Status and review of POLARIS:

- [PAME — POLARIS project page](https://pame.is/ourwork/arctic-shipping/current-shipping-projects/polaris/) — "To date no review has taken place"; "limited understanding of the suitability of POLARIS"
- [James Bond (ABS), "IMO POLARIS Update: Current Usage and Status", IMO Polar Maritime Seminar, 1 Nov 2022](https://wwwcdn.imo.org/localresources/en/About/Events/Documents/Polar%20Maritime%20Seminar%202022%20presentations/Day%201/10_James_Bond-IMO%20POLARIS%20Update%20%20Current%20Usage%20and%20Status.pdf)

Antarctic and applicability literature:

- [Kujala, Kämäräinen & Suominen (2019), "Validation of the New Risk Based Design Approaches (POLARIS) for Arctic and Antarctic Operations", POAC 2019, Delft — record](https://trid.trb.org/view/1718078)
- [Liu, Yan, Peng, Xie & Sun (2025), "Vessel Safety Navigation Under the Influence of Antarctic Sea Ice", J. Mar. Sci. Eng. 13(7):1267](https://doi.org/10.3390/jmse13071267)
- [Xu, Xu, Ma, Qian & Li (2024), "Research on POLARIS for Ships Operating in Seasonal Sea-Ice Covered Waters", J. Mar. Sci. Eng. 12(5):827](https://doi.org/10.3390/jmse12050827)
- [Matsuzawa & Akane (2025), "POLARIS-based Assessment of Operational Limitation in the Arctic Ocean for R/V Mirai II", POAC 2025 paper 108](https://www.poac.com/Papers/2025/pdf/POAC25_paper_108.pdf)
- [Suominen, Lu, Kujala & Bekker (2021), "Antarctic sea ice properties on zero meridian side during Austral summers 2012-14 and 2018-19", POAC 2021](https://www.poac.com/Proceedings/2021/POAC21-074.pdf)
- [Integrating Regional Ice Charts and Copernicus Sea Ice Products for Navigation Risk in Alaskan Waters, arXiv:2512.11083](https://arxiv.org/pdf/2512.11083)
- ["Probabilistic analysis of operational ice damage for Polar class vessels using full-scale data", *Structural Safety* (paywalled — abstract only, DOI unverified)](https://www.sciencedirect.com/science/article/pii/S0167473023001108)

Antarctic ice-type data:

- [AARI–NIC–NMI pilot project on integrated sea ice analysis for Antarctic waters](http://ice.aari.aq/) — charts, SIGRID-3 archive, iceberg layer
- [Specifications for collaborative product on sea ice analysis for Antarctic waters](http://ice.aari.aq/docs/Specifications_for_collaborative_product\(final\).pdf)
- [NSIDC G10013 — U.S. National Ice Center Arctic and Antarctic Sea Ice Charts in SIGRID-3 Format, Version 1](https://nsidc.org/data/g10013/versions/1) — Antarctic production suspended 9 June 2023
- [Norwegian Ice Service — Ice Service charts](https://cryo.met.no/en/latest-ice-charts) and [about the Ice Service](https://cryo.met.no/en/ice-service)
- [PolarView — Information types (Antarctic)](https://www.polarview.aq/pages/index/info_types) — "There are no national ice centres producing sea ice charts for the Southern Ocean"
- [NSIDC — Science of Sea Ice](https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice) — Antarctic multi-year ice distribution
