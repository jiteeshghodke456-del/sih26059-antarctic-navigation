# Master audit — September 2026

The audit commissioned against the original master prompt, and the documents it
produced. Written to **not** defend the project: where the system overclaims,
these say so.

## Read in this order

| # | File | What it is |
|---|---|---|
| 1 | **[MASTER_AUDIT.md](MASTER_AUDIT.md)** | **The audit.** All 46 sections A–AT — lost requirements, problem and users, USPs, technical verdicts, survivability, regulation, business, a hostile judge's score, a rebuilt deck blueprint, and a blunt final verdict. Start at §AO and the FINAL VERDICT if you only read two parts |
| 2 | **[CORRECTIONS.md](CORRECTIONS.md)** | The short list. 39 findings turned into checkable changes — 26 done, 15 open. **This is what is still owed** |
| 3 | **[SIH_PPT_V2.md](SIH_PPT_V2.md)** | The corrected six-slide deck. The submitted one contradicts the repository in eight places |
| 4 | **[QUALITY_GATE.md](QUALITY_GATE.md)** | Three requirements that were lost when the master prompt was compressed, reinstated as a checklist: the operating rule, the definition of done, and the 10-point pre-feature gate |
| 5 | **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** | **The walkthrough.** Every control including the smallest button, what it does and why, the five competitor gaps we occupy, where it excels, and the ten attacks with their answers |
| 6 | **[QUICKSTART.md](QUICKSTART.md)** | How to run the console |
| 7 | **[WORLD_MODEL_DESIGN.md](WORLD_MODEL_DESIGN.md)** | Design for the synthetic environment, with the ice-edge climatology fitted from the real NSIDC archive |

## Method

Original master prompt → compressed six-stage bundle → this repository, compared
by reading and diffing files rather than by trusting documentation claims. Every
number carries a tag: **Measured** (a run produced it, the artefact exists) ·
**Sourced** · **Derived** · **Target** (specified, not achieved) · **Hypothesis**.

## The three findings that matter most

1. **The problem is the last 100 km, not the crossing.** Bharati's cell was
   closed 23 of 31 December days; the approach 100 km north was open 31 of 31;
   the 5,800 km ocean leg averages 6 % ice.
2. **The submitted deck contradicts the repository in eight places**, including
   a POLARIS claim one line of code disproves.
3. **The compression lost 8 of 78 sections**, and they were the newest ones —
   including the rule that would have caught the other seven.
