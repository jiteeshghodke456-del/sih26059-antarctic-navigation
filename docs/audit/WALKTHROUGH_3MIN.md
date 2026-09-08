# The 3-minute walkthrough

Very simple language. What every number, button and short word on the screen
actually means.

Read the **bold spoken lines** out loud. The tables are for you to memorise so
you can answer "what's that number?" without pausing.

---

## 0:00 — Open with this (20 seconds)

> **"A ship leaves Cape Town for India's Antarctic station. It takes about two
> weeks. The whole voyage is easy except the last hundred kilometres — and that
> part is shut most days. We measured it: the station was blocked 23 days out of
> 31. The waiting spot just north of it was open all 31.**
>
> **So this screen has one job: tell the captain what he can't see, and what it
> costs him."**

Then point at the purple badge: **"This weather is made-up, on real physics. The
real satellite data is on the other tab."** Say it before they ask.

---

## 0:20 — The bottom strip (30 seconds)

This never disappears. Read it left to right.

> **"Everything the captain needs, always on screen. Where he is, how fast, how
> much ice, how big the waves, when he arrives, how much fuel, and one word for
> whether the plan is still good."**

| You see | Say it as | What it means |
|---|---|---|
| **POS** | position | Where the ship is right now |
| **COG** | course | The direction it's pointing |
| **SOG** | speed | How fast, in knots (1 knot ≈ 1.8 km/h) |
| **SIC** | ice | How much of the sea is covered in ice, 0–100% |
| **WIND** | wind | Wind speed in knots |
| **Hs** | waves | Height of the waves in metres. 5 m is rough. 8 m is dangerous |
| **VIS** | visibility | How far you can see, in nautical miles |
| **ETA D+** | arrival | Days from leaving. "D+11" = arrives 11 days after departure |
| **FUEL** | fuel | Tonnes burned for the whole trip |
| **HEALTH** | the verdict | One word for the whole plan — explained below |

---

## 0:50 — HEALTH: the one word that matters (30 seconds)

> **"This is the whole application in one word. It is never a score. There is no
> 'safety = 82%' anywhere in this software, because no captain can act on 82%."**

| Word | Colour | Means |
|---|---|---|
| **VALID** | green | The plan is good. Go |
| **DEGRADED** | amber | Something is worse than we'd like. Still legal, pay attention |
| **INVALID** | red | Something broke a limit. Do not sail this plan |

**Where it comes from — nine questions.** Ice · weather · depth of water · what
the ship can handle · radio · other ships · getting cargo ashore · a backup plan ·
are we where we said we'd be.

Each answers with one of four words:

| Word | Means |
|---|---|
| **PASS** | Checked, it's fine |
| **MARGINAL** | Checked, it's close to the edge |
| **FAIL** | Checked, it's over the limit |
| **UNKNOWN** | **We could not check it.** |

> **"Health is simply the worst of those nine. And UNKNOWN is the important one —
> it means we don't know, and we never let 'don't know' count as a pass. A gate
> turns grey by itself the moment its data gets older than it's allowed to be."**

---

## 1:20 — Down the left: the map layers (25 seconds)

Twelve buttons. Each turns one thing on the map on or off.

> **"The captain builds the picture he wants. Nothing is forced on him."**

| Button | Simple name | What appears |
|---|---|---|
| **ICE** | ice | Blue-to-white shading. Whiter = more ice |
| **BRG** | icebergs | The icebergs, each with an arrow |
| **WX** | weather | Wind arrows |
| **CUR** | current | Which way the water flows |
| **RTE** | route | The planned line |
| **SHP** | ship | The ship |
| **AIS** | other ships | Other vessels nearby |
| **WRN** | warnings | Danger zones |
| **ASPA** | protected areas | Legally protected wildlife areas — entry is restricted |
| **LND** | land | The coastline |
| **GRD** | grid | Latitude/longitude lines |
| **RIO** | ice risk | The POLARIS ribbon — explained below |

---

## 1:45 — The icebergs (25 seconds)

Turn on **BRG** and zoom in.

> **"Every iceberg has an arrow. The arrow is not its speed — it's where that
> berg will be tomorrow. That's the only question a sailor actually asks:
> is it coming towards me?"**

| What you see | What it means |
|---|---|
| **Arrow** | Where the berg will be in 24 hours |
| **Dashed arrow** | Wind can push this one — tomorrow's wind changes it |
| **Solid arrow** | Only the current moves this one — more predictable |
| **Circle around it** | How wrong we might be. It stops at 72 hours because past that we can't prove anything |
| **Hollow, no arrow** | **AGROUND** — stuck on the seabed. Not going anywhere |
| **CPA** | Closest Point of Approach — how near that berg gets to *your* track |

> **"And a warning: the official world iceberg list only counts bergs bigger
> than 18.5 kilometres. Most of these are invisible to it. So this software is
> banned from ever printing the word 'none'. There is a test that fails the
> build if it does."**

---

## 2:10 — Planning a route (30 seconds)

> **"Two dropdowns and one button."**

| Control | Choices | Plain meaning |
|---|---|---|
| **Mission** | station / waiting spot | Do we *have* to reach the station, or is stopping short OK? **The single most important button here** |
| **Objective** | least time / least fuel | Fastest, or cheapest |
| **Ice limit** | 85 / 80 / 70 / 55 / 45% | How much ice this ship is willing to push through |
| **Solve** | — | Calculate the route |

Press Solve twice — once on each Objective:

> **"Fastest is 10.7 days and 195 tonnes of fuel. Cheapest is 17 days and 154
> tonnes. Fourteen percent less fuel for seventy-two percent more time. Two real
> choices, and we price both. The captain decides — we never decide for him."**

Now set the ice limit to **45%** and press Solve:

> **"No route. Not slower — there is no way through at all."**

---

## 2:40 — The right side and the clock (20 seconds)

**The time slider at the bottom.** Drag it.

| Button | Does |
|---|---|
| **HOME** | Jump back to the start if you get lost |
| **◀ ▶▶** | Step back / forward six hours |
| **▶** | Play the voyage |

> **"Watch the word in the corner change as we sail. Green leaving Cape Town —
> and there, it drops, because we've gone so far south we've lost the satellite.
> It tells you which of the nine questions changed. Nobody picked that colour.
> It's calculated."**

**The slider stops at 7 days. That's on purpose:**

> **"The only Antarctic ice forecast in the world runs 9 days ahead. This ship
> takes 15 days to get there. So at the moment it leaves, 41% of the voyage is
> beyond any forecast that exists on Earth. We show you the edge instead of
> making things up past it."**

**Panels on the right, in one line each:**

| Panel | Answers |
|---|---|
| **Alerts** | What changed, and what it does to your plan. Click to accept |
| **Own ship** | Where you are, next turn, arrival time |
| **Ice** | Ice now, worst ice ahead, your limit, and the gap between them |
| **Weather in corridor** | Weather *along your route* — not at some weather station |
| **Hazard timeline** | What's coming in 6, 12, 24, 48 hours |
| **Icebergs** | How many we see, how many the world officially tracks, how many are stuck |
| **POLARIS** | The international ice risk score — shown as a **range**, not a number |
| **Alternatives** | Other routes. Hover one to preview it |
| **Decision log** | Every version, and who signed it |
| **Link & pack** | 7.8 kilobytes a day. It works on a satellite phone |

---

## 3:00 — Close

> **"Everyone else will show you what their system knows.
> We're the only ones who will show you what ours doesn't —
> and tell you exactly which satellite would fix it."**

---

## If they ask about POLARIS

> **"It's the international ice-risk rulebook. We show a **band**, not a single
> number, because there's no official row for this ship's class and guessing
> spans forty points. The honest answer is a range — and how wide it is, is the
> finding."**

## If they ask "is any of this real?"

> **"The physics is real. The weather is invented, and the badge says so. The
> real satellite data — 1,096 days of it — is on the other tab, and that's where
> we found a bug in the official product: it reports blocked-out coastal pixels
> as **open water**, on 43% of days, exactly where the ship has to go."**
