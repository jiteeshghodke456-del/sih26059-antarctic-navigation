# Pitch Script — Team Krisis, PS 26059

For the AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory, and Navigation
Decision Support System. Built to be spoken, not read — say it in your own
words once you know the shape of it, don't recite it.

**How to use this file:** each slide section below is a script, timed at a
natural, unhurried ~130–140 words/minute. Read each one out loud twice before
you touch the actual pitch — the second read is always faster and cleaner
than the first. Bold text marks the numbers and phrases judges will latch
onto; hit them clearly, don't rush past them. Part 2 is your viva armor —
read it until nothing in it surprises you.

Slide order below follows the **physical order in your PDF** (Title →
Solution → Technical Approach → Feasibility/Viability → Impact/Benefits →
Research), not the page-number badges printed on the slides themselves —
see the note at the very end of this file about that mismatch.

Total pitch run time: **~13 minutes** across 6 slides. If your slot is
shorter, cut Slide 3's middle paragraph (the "why not X" reasoning) first —
it's the most compressible, not the least important.

---

## Slide 1 — Title (~0:30, no minimum required)

> Good [morning/afternoon], panel. We're Team Krisis, Problem Statement
> **26059** — the AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory, and
> Navigation Decision Support System, for the Ministry of Earth Sciences,
> under Smart Automation.
>
> Here's the one sentence to hold onto for the next ten minutes: once a
> year, **one ship** carries the entirety of India's Antarctic resupply
> through water full of moving ice and icebergs the size of small cities —
> and today, nobody tells that ship's captain, with real numbers, which way
> is actually safe. We built the thing that does. Let's show you how.

**Delivery note:** say this standing still, making eye contact, not reading
off the slide. It's the only 30 seconds where nobody expects data yet — use
it to make them curious, not to cram in facts.

---

## Slide 2 — Solution Idea & Proposed Approach (~2:15)

> Every year, the MV Vasiliy Golovnin sails from Cape Town to India's
> Bharati and Maitri stations, carrying fuel, food, and scientists for the
> next expedition. The two things that can end that voyage badly are sea
> ice that moves faster than any forecast keeps up with, and icebergs —
> some the size of a small city — drifting across the route. Our system
> answers exactly three questions for that captain: **where will the ice
> actually be, where will the icebergs actually drift, and given both,
> which way should we sail.**
>
> For ice, we don't build a forecaster from nothing — we **correct the
> official one**. Our AI looks at the Copernicus Marine forecast and learns
> exactly where and how it tends to be wrong. On real held-out satellite
> data, that correction beats the raw baseline by **18.5% one day out, and
> 30.6% seven days out** — and the gap grows with time, which is exactly
> when a captain needs help most.
>
> For icebergs, we use a **proven physics model** — not a guess, and not a
> black box — to project drift for every live iceberg tracked in our
> corridor.
>
> For routing, the router doesn't just find a path — it **avoids protected
> areas**, weighs real satellite ice data, and **replans automatically** the
> moment new data lands.
>
> And because this ship barely has internet — Iridium, not broadband — all
> the heavy computing happens ashore. The ship gets **one small daily
> update** and runs the entire router **offline**, on a laptop, on the
> bridge.
>
> Every step, the system explains itself: what changed, why, and which
> safety fallback level it's currently running on. The captain sees the
> reasoning. **The captain always makes the final call** — this is decision
> support, not autopilot.

**Delivery note:** the flowchart on this slide is dense — don't narrate it
box by box. Point at it once, say "this whole loop — captain logs a route,
system checks it, suggests changes, captain finalizes — runs every single
time," and move on.

---

## Slide 3 — Technical Approach (~3:00, the deep-knowledge slide)

> Here's the engineering, and the reasoning behind every choice.
>
> Our core rule: **ashore handles everything heavy** — GPU training,
> bandwidth-hungry downloads. **Aboard handles real-time questions** on a
> laptop. And what moves between them is a compressed environmental state —
> never a finished answer that can go stale.
>
> Ashore, ten steps happen automatically, every day: we ingest satellite and
> forecast data, quality-check and regrid it, assemble fourteen input
> channels, train our correction model on GPU, and output not just a
> predicted ice number but an **uncertainty band** around it. We fuse in
> disagreement between multiple satellite sources, run our iceberg drift
> physics, build a routing mesh with **meshiphi**, sweep routes with
> **PolarRoute**, and package everything into one signed, versioned voyage
> pack.
>
> Now — why correct the forecast instead of building our own from scratch?
> Because Copernicus already runs a full physics simulation of the ocean,
> constantly corrected by real satellites. Competing with that from zero,
> on our timeline, is a losing bet. So our model's only job is: look at
> that forecast, and predict exactly how wrong it is. If our correction is
> ever zero, **we're exactly as good as the official forecast** — we
> genuinely cannot be much worse. That's why we beat the baseline instead
> of merely matching it.
>
> For icebergs, we deliberately used **no neural network**. We only get
> position updates on a few hundred big icebergs, at most once a day —
> that's too little data for deep learning to be honest. So the physics —
> the **Wagner 2017** drift model, wind, current, and Coriolis force —
> carries the answer, with a small gradient-boosted correction on top,
> the same pattern the newest 2025 iceberg research uses.
>
> For routing, we didn't reinvent Dijkstra's algorithm. The British
> Antarctic Survey already publishes **PolarRoute**, open source, and we
> read its actual code. We found it **throws away uncertainty** before
> routing — so we feed our uncertainty back in. And it has **no iceberg
> model** — so we plug ours into its existing hazard hook, without touching
> their code at all.
>
> On the vessel, eight mirrored steps happen — receive the pack, load
> cached weights, run local inference, refresh with fresh observations, and
> **replan the entire route in seconds**, fully offline.
>
> And every single input — twelve real sources: NSIDC, Copernicus,
> Sentinel-1, USNIC, ECMWF, GEBCO, NCPOR's own portal — is public data
> we've actually pulled and verified ourselves. **Nothing here is
> placeholder.**

**Delivery note:** if a judge's eyes glaze at the ten-step / eight-step
list, that's fine — the two paragraphs that matter most are "why correct
instead of build from scratch" and "why physics not ML for icebergs." Those
are your two hardest-to-attack technical decisions; make sure they land
even if you compress everything else.

---

## Slide 4 — Feasibility and Viability (~2:30)

> This is the slide where we try to out-ask the judges before they ask us.
>
> **Feasibility:** our correction model isn't a claim, it's a measurement —
> **18.5%** better than baseline at one day, **30.6%** better at seven days,
> on real held-out satellite data the model never trained on. Our data
> pipeline has already processed **1,096 daily satellite files with zero
> failures**, harvested automatically, every single day, because a missed
> day can never be recovered later. And for routing, we're not reinventing
> anything fragile — PolarRoute and meshiphi, from the British Antarctic
> Survey, already compute our full **8.6-day route**.
>
> **Viability:** the entire daily voyage pack is **76 kilobytes**, and a
> route summary alone is **796 bytes** — both comfortably inside Iridium's
> 704 kilobits-per-second link. We compress each day's raw data from 42.6
> megabytes down to 5 — an **8.4x reduction**. And every tool in our stack —
> PyTorch, PolarRoute, meshiphi, FastAPI — is open source. Nothing to
> license, nothing that breaks if a subscription lapses.
>
> **Practical implementation**, and this is the part we're proudest of: the
> ship runs the full router locally, with zero internet. If our model ever
> fails, **it fails safe** — because we only ever output a correction on
> top of the official forecast, so the crew still has the official
> forecast, never nothing.
>
> And we've already stress-tested our own weak points, out loud: connectivity
> risk — we push the heavy work ashore. Ice moving faster than forecast — we
> recheck against the latest satellite image every day. Coastal blind spots,
> where satellites falsely read blocked coastline as open water — we
> identify and flag those ourselves. No fuel-burn number for this exact hull
> yet — so we rank routes by safety and efficiency, not a number we can't
> defend. And small growler ice invisible from orbit — that's what radar and
> a human lookout are still for, and we say so plainly.

**Delivery note:** the two charts (error-grows-with-horizon, advantage vs.
hardest baseline) are your strongest visual proof. If a judge's eyes go to
them mid-sentence, pause and let them look for two seconds before
continuing — don't talk over your own best evidence.

---

## Slide 5 — Impact and Benefits (~2:10)

> Who actually benefits from this, concretely.
>
> The **ship's crew** sees where the ice will be, which icebergs are near,
> and exactly why the route changed — with the captain always in command,
> never a machine making the call alone.
>
> **NCPOR** plans the real Cape Town to Bharati resupply on actual ice
> forecasts, and knows in advance when the Bharati approach is closed —
> instead of finding out when the ship is already there.
>
> **Scientists** get their supplies and their teams to Bharati and Maitri
> on time. And a side effect we didn't expect going in: our own coastal
> data audit exposed a real flaw in the satellite record NCPOR itself
> relies on — we found it, and we're reporting it, not hiding it.
>
> For **the nation**, this is a home-built decision tool for India's own
> Antarctic programme, built entirely on open data and open code — nobody
> else's black box, nobody else's licensing terms.
>
> And for **the environment**: the router stays inside the protected-area
> boundaries India itself co-proposed under the Antarctic Treaty system,
> and safer routes cut the real risk of grounding or a fuel spill in
> Antarctic waters.
>
> On benefits — **ship safety first**: the system always explains what
> changed and why, so the crew has reasons, not just a line on a map.
> **Economically**: fewer stuck days and smarter routes save real money on
> a chartered vessel, which is billed by the day. It's **danger-aware**:
> cautious routing through heavy ice lowers real hull-damage and spill
> risk. And **operationally**, it works with almost no internet — heavy
> computing stays ashore, the ship gets one small daily pack, and the
> bridge can replan in seconds.

**Delivery note:** this slide is your emotional beat, not just data. Slow
down slightly on "the coastal data audit exposed a real flaw" — that's a
genuinely surprising, credibility-building line; don't rush past it like
it's a bullet point.

---

## Slide 6 — Research and References (~2:05)

> Last slide, and it's the one that proves this isn't guesswork.
>
> Every non-obvious decision we made traces to a specific paper, not
> intuition. We replaced our first-draft 80% ice threshold with **POLARIS**
> — the IMO's actual risk-index framework for ice-class operating limits —
> because a single fixed percentage isn't how real polar operators assess
> risk. Our iceberg drift model implements the **Wagner 2017** analytical
> model directly, including fixing a drag-coefficient inconsistency in the
> original formulation. Our uncertainty reporting exists because the
> **Sea-Ice Round Robin** study showed published sea-ice algorithms can
> disagree significantly with each other, especially right at the ice edge
> — exactly where a ship needs to know the most. We calibrated that
> uncertainty using **Lavergne 2019's** documented exclusion criteria — melt
> ponds, thin ice, weather effects — the same criteria the actual producers
> of this satellite data use to flag their own uncertain pixels. And our
> live iceberg positions come straight from the **U.S. National Ice
> Center's** Antarctic dataset — the same operational source real ice
> centers use today.
>
> On the right, this isn't a mockup — that's a real comparison: the raw
> Copernicus three-day forecast, our corrected forecast, what actually
> happened, and a map of exactly where we improved it, in red. And below
> it, real July 2026 Antarctic sea ice cover and anomaly, from ERA5 and
> Copernicus — the actual climate backdrop our corridor sits inside.
>
> Every citation on this slide is a real, peer-reviewed source, linked at
> the bottom. We didn't design this system to sound scientific — **we
> designed it by reading the science first.**

**Delivery note:** close on the last line, then stop talking. Don't add "so
that's our project" or similar filler — silence after a strong closing line
reads as confidence, not as running out of things to say.

---

# PART 2 — Bulletproof Viva & Q&A

Read this until nothing surprises you. The goal isn't to memorize answers —
it's to understand *why* each answer is true, so a follow-up question
doesn't break it.

## The one line to fall back on if you blank

> "We correct an existing forecast instead of replacing it, we use physics
> where data is scarce and machine learning where it's abundant, and we
> test ourselves harder than the judges will."

Every hard question below traces back to one of these three ideas. If you
lose the thread mid-answer, land on this sentence and rebuild from there.

---

## "Why this, specifically?" — the opening gambit

**Q: What's actually novel here? Walk me through the real engineering, not
the pitch.**
Honestly: the biggest wins here are **integration discipline and honesty
engineering**, not one giant new algorithm — say that plainly, a judge who
counts lines of novel code will respect it more than a dodge. Concretely:
we correct CMEMS instead of replacing it (a smaller, more learnable
problem than most teams attempt); we route on a *measured, calibrated*
uncertainty band instead of a point forecast — something the field's own
tool, PolarRoute, actively discards; and the entire system is designed
around Iridium's real bandwidth, enforced by a CI test that fails the
build if a pack gets too big, not just a design doc that says "offline
mode."

**Q: Why didn't you build your own iceberg-drift model or your own routing
algorithm from scratch — isn't that "less impressive"?**
The opposite. A domain-literate judge already knows PolarRoute exists. A
from-scratch A* invites the question "why did you ignore the field's own
open-source tool?" We read PolarRoute's actual source code and found two
real, specific things it doesn't do — throw away uncertainty, and have no
iceberg model — and fixed exactly those, without forking it. That's a
stronger position than reimplementing Dijkstra to look busy.

**Q: Why no LLM, no chatbot, no RAG layer? Everyone else seems to have one.**
Because there's no natural-language task in this problem statement — every
piece here is numerical prediction or graph search. A chatbot wrapper over
real data is *easier* than what we built, not harder — we checked, and
several SIH teams on sibling MoES problem statements did exactly that
last year (FloatChat, Ocean Hazard Reporting) and it converges into "a UI
on top of real data," not a trained model. We declined the easier path on
purpose. If a judge specifically wants a natural-language interface, we can
say: it's a legitimate future layer on top of this decision engine, but it
would be decoration, not the hard problem this PS actually asks for.

---

## "What does the competition use?" — comparison table

| Dimension | What most competing teams will build | What we built |
|---|---|---|
| Ice forecast | From-scratch U-Net, competing with CMEMS directly — and usually losing | **Bias-correction on top of the CMEMS operational forecast** — can't be much worse, often better |
| Baseline compared against | Naive persistence (yesterday = tomorrow), which flatters almost any model | **Raw CMEMS itself**, held to a build-blocking bar |
| Uncertainty | None, or a number shown once in a legend | **Calibrated bound that changes the actual route**, with measured coverage |
| Iceberg drift | Physics **or** ML, rarely both | **Physics (Wagner 2017) plus a small learned correction** — the same hybrid pattern 2025's own iceberg research (IDRIFTNET) validated |
| Routing | Grid A*/Dijkstra, single fixed cost, from scratch | **PolarRoute, the actual BAS tool**, extended in two source-verified places |
| Connectivity | Assumes a live backend / API call | **Offline-first by design**, sized against Iridium's real ~704 kbps |
| Ice "truth" | One source (usually CMEMS alone), presented as ground truth | **Multi-source, with disagreement surfaced**, not hidden |
| Fuel/cost numbers | Confident absolute figures | **Relative comparisons only**; absolutes explicitly labelled uncalibrated |
| UI layer | Dashboard + chat/query wrapper (the "FloatChat" pattern) | Real nautical-chart color conventions, staleness always shown, no chat layer because there's no NL task here |

If asked "have you actually looked at what other teams / real companies do
here" — yes, name them plainly: **StormGeo** (the real commercial
incumbent — and notably, even they keep human route analysts in the loop
24/7, because full automation isn't trusted at the edges either), **IceNet**
(BAS/Turing Institute — but validated for the Arctic, not Antarctica, so
directly reusing its weights would be extrapolating outside its own proven
domain), and the **FloatChat-pattern** teams from SIH 2025's sibling MoES
problem statements.

---

## Rapid-fire nitpick Q&A, grouped by topic

### On the ice model

**Q: Why not just use CMEMS directly — why do you even exist?**
Three real reasons: we add a measured uncertainty band CMEMS doesn't
publish in a routable form; our correction can run *on the ship* with a
few KB of fresh observation to re-correct the whole forecast without
re-downloading it; and we cross-check multiple ice sources instead of
trusting one. And it's a promise enforced in code, not marketing: we ship
raw CMEMS for any forecast day where we can't prove we beat it.

**Q: How do you know your model isn't just memorizing?**
We split by time, not randomly — train on earlier days, test on later ones
the model has genuinely never seen. A random split would leak Tuesday into
training and test on Wednesday, and sea ice barely changes overnight, so
that would look spectacular and mean nothing.

**Q: Isn't yesterday's satellite image already a good forecast?**
Yes — and we tested this ourselves before a judge could catch us on it.
Persistence (today = yesterday) scores 0.0359 error at 1 day — genuinely
better than an early version of our model. But persistence decays fast —
0.0610 at 3 days, 0.0893 at 7 — while our correction gets *relatively*
stronger with lead time, which is why we score both at the same range and
report it honestly.

**Q: Would a simple average bias-correction do as well as your neural
network?**
We test exactly that, before training even starts — a per-pixel average
bias map and a flat offset, scored on the same held-out data as the real
model. If they matched, we'd say the network is decoration. They don't.

**Q: What are your 14 input channels, really?**
The forecast being corrected, the last several days of real satellite
observations, an "innovation" channel (how wrong the forecast was against
the newest real observation — the single most useful signal), seasonal
signals, and a land mask.

### On icebergs

**Q: Why physics instead of AI here, when you used AI for ice?**
Data volume. Ice: a full satellite map, every day, for decades. Icebergs:
position updates maybe weekly, only for the largest few hundred. Machine
learning on that little data produces confident nonsense; physics doesn't.
Using the right tool per problem is the engineering — not a shortcut.

**Q: You only track huge icebergs. What about the small ones that actually
hole a hull?**
Correct, and we say so on the interface instead of hiding it. Tracking
databases (USNIC/BYU) only cover icebergs above roughly 10 nautical miles.
Small "growlers" aren't tracked by anyone globally — that's what radar and
a human lookout are still for, and we'd rather state that limitation
plainly than imply we've solved iceberg safety end-to-end.

**Q: Why only 72 hours of drift projection, not the full voyage?**
Because honest physics-only error compounds past that — beyond 72 hours
the uncertainty radius grows past 100 km, and a "danger zone" that wide
would blockade the entire corridor. Technically thorough, practically
useless. We cap it, and refresh daily from new observations instead.

### On routing

**Q: You used someone else's routing library. What did *you* actually
build?**
The ice forecast, the correction model, the uncertainty layer that
actually changes the route, the iceberg drift layer, the offline sync
architecture, and the interface. For routing specifically: we found the
domain's own real tool and extended it in two places we identified by
reading its source — that's a stronger claim than reimplementing Dijkstra
to look impressive.

**Q: What if your forecast is wrong and the ship gets stuck anyway?**
Layered, on purpose: we route on a cautious upper bound, not the average.
Beyond our proven skill horizon, the system marks the route as
planning-grade with a wide band instead of a falsely precise line. And
fundamentally — it's decision *support*. It doesn't replace the captain or
official navigation charts, and it says so on screen.

### On honesty, limits, and the "kill shot" question

**Q: What's the single weakest part of your system? Don't dodge this.**
The uncertainty calibration for our full production model. Our safety
margin only means something if it's genuinely right the percentage of time
it claims to be. We've written down the exact numeric pass/fail test in
advance — and what happens if it fails, including publicly demoting our
own headline claim about uncertainty-aware routing back to "uncertainty as
a cross-check." That test and its failure branch exist specifically so we
can't quietly move the goalposts after we see the numbers.

**Q: Is any of your data or output fake, synthetic, or placeholder?**
No. Every input traces to a named, live, public source we verified by
actually fetching real files ourselves — not just checking that a webpage
loads. We can show the download logs.

**Q: What can your system genuinely not do?**
Predict small growlers. Give a calibrated, absolute fuel-burn number for
the real hull (we show relative comparisons and label absolutes as
uncalibrated). Replace official navigation charts. And much of the
corridor's seafloor depth is satellite-*predicted*, not surveyed — so we
apply a larger safety margin exactly where that's true, and disclose it.

**Q: What would you do with three more months?**
The full 5-model ensemble with fully calibrated uncertainty, sea-ice radar
(SAR) imagery for sharper ice-edge detection, and validation against
NCPOR's own station measurements. These are scheduled next steps, not
vague aspirations.

### Small specific things on the slides themselves

**Q: What is POLARIS, and why does it replace a flat 80% threshold?**
POLARIS is the IMO's own Polar Operational Limits Assessment Risk Indexing
System — the framework real polar operators already use to judge ice risk
by ice class and ice type, not a single blunt percentage. A flat 80% cutoff
ignores ice thickness and the vessel's actual ice class; POLARIS doesn't.

**Q: What are the "4 safety nets" / fallback levels?**
Graceful degradation: when confidence drops — stale data, sources
disagreeing, forecast beyond its proven skill horizon — the system doesn't
go silent, it steps down through defined levels, from full corrected-model
routing down to raw-official-forecast routing with a wider caution margin.
It always tells the captain exactly which level it's currently running on.

**Q: What's the "coastal blind spot" you mention?**
A known satellite sensor artifact — passive microwave readings near
coastlines can misread nearby land as open water or ice. We flag it during
quality control instead of feeding it straight into the router, because an
uncaught artifact either invents a phantom hazard or hides a real one.

**Q: Which "protected areas" does the router avoid, and on what basis?**
Antarctic Specially Protected and Managed Areas under the Antarctic Treaty
system — the same boundaries any compliant Antarctic operator already has
to respect, including ones India itself helped co-propose. The router
treats them as hard excluded zones, the same mechanism used for iceberg
hazards.

---

## Numbers to have cold — memorize these, don't paraphrase them

- **18.5%** better than baseline at 1-day lead, **30.6%** at 7-day lead
- **76 KB** full daily voyage pack, **796 B** route summary alone
- Iridium link: **~704 kbps**
- Daily archive: **42.6 MB → 5.0 MB**, an **8.4x** compression
- **1,096** daily satellite files processed, **zero** failures
- **8.6-day** computed route (Cape Town → Bharati corridor, current conditions)
- Iceberg drift projection capped at **72 hours**
- Physics model: **Wagner, Dell & Eisenman, 2017**
- Ice threshold framework: **POLARIS** (IMO)
- Ship: **MV Vasiliy Golovnin**, chartered, diesel-electric, Cape Town →
  Bharati/Maitri, austral summer
- CI-enforced pack budget: **50 KB daily delta / ~1 MB full corridor
  refresh** — build fails if exceeded

## The rule for anything not on this list

If a judge asks a number you genuinely don't have memorized: say what you
*do* know, name where the real answer lives (a specific doc or test), and
never invent a figure on the spot. That is not weakness in front of an
MoES/NCPOR-adjacent panel — guessing a number and being caught is far worse
than "that's measured in Phase 3, here's the test that governs it."

---

## One thing to fix before you present, not part of the script

Your PDF's printed page badges don't match the slides' physical order —
the slide titled **"FEASIBILITY AND VIABILITY"** carries a printed **"5"**,
and the slide titled **"IMPACT AND BENEFITS"** carries a printed **"4"**,
but Feasibility/Viability actually comes *before* Impact/Benefits in the
file. This script follows the real physical order. Either swap the two
slides in your Canva file so the badges match the order, or just retype the
two badge numbers — either fix is under two minutes and worth doing before
this goes in front of judges who read slide numbers as a proxy for
attention to detail.
