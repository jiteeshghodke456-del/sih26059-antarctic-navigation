# The five-minute script

Plain language. Every button, and why it exists. Read it twice and you can
present without notes.

> **If the judge remembers one thing, make it this:**
> **"Our software has a colour for *I don't know*. It earns it — a gate goes
> grey the moment the data behind it is older than the skill it claims. And
> grey is never allowed to count as a pass."**
>
> Nobody else will stand in front of them and point at what their software
> cannot see. That is the whole pitch.

---

## First 30 seconds — say this before you touch anything

> "Ships have gone to Antarctica for a century. The hard part was never the
> ocean. **It's the last hundred kilometres.**
>
> We measured it: on real satellite data, the cell Bharati station sits in was
> **closed 23 days out of 31**. The waiting spot a hundred kilometres north was
> **open all 31**. And the five-thousand-eight-hundred-kilometre crossing to get
> there? **Six percent ice. Basically empty.**
>
> So every routing product optimises the easy part. We built for the part that
> actually decides the voyage."

Then point at the purple badge: **"That environment is synthetic — real physics,
invented weather. The real satellite data is on the other tab."** Say it now.
A judge who finds it themselves stops trusting you. A judge who's told trusts
everything after.

---

## The walk-through

### Sign in
**One box, one button.** Type a name, take the watch.

**Why:** a ship's log has a name on every entry. Every approval later carries
this one. *(Be honest if asked: it's identity, not a password. There's no user
database. We know.)*

### The top strip
- **ROUTE PLANNING → ROUTE MONITORING** — flips when you sail.
  **Why:** that's ECDIS's own split. Every ship's chart system already works
  this way. We didn't invent a workflow; we borrowed the one they know.
- **DAY / DUSK / NGT** — click DAY, then NGT.
  **Why:** bridges dim their screens at night. The chart standard has three
  palettes, so we have three.
- **ALM** — open alarms. Red when something needs a decision.
- **FUT** — the "not built yet" room. Everything in it is labelled.

### Voyage → Mission — **stop here, this is the point**
Two radio buttons: *reach the station* or *the waiting spot is good enough*.

> **"This one button is the most important field in the whole application.
> Station: closed 23 of 31 days. Waiting spot: open all 31. Same ship, same
> weather, same day — opposite answer."**

**Why it exists:** that choice isn't the captain's. It belongs to the expedition
leader ashore, and until now nobody computed what it costs.

### Route — the engine
- **Objective: least time / least fuel.** Run both.
  **Why:** they are genuinely different routes — **10.7 days and 195 tonnes**
  versus **17 days and 154 tonnes**. Fourteen percent less fuel for seventy-two
  percent more time. The captain picks; we price both.
- **Ice limit: 85 / 80 / 70 / 55 / 45 %.** Set 45 and press Solve.
  > **"No route. Not slower — there is no way through."**
  **Why it's a dropdown and not a fixed number:** no ice class anywhere in the
  world rates a ship by ice *concentration* — they all use thickness. So our 80%
  is an assumption, and we let you push on it until it breaks.
- **Solve** — two seconds, live.
  **Why it matters:** every cell is costed with the ice **at the hour the ship
  gets there**, not today's ice. Sounds obvious. Our own audit found the old
  router met day-one ice on day nine.

### Waypoints
The list. Position, arrival time, ice and sea state **at that leg's arrival**.

### Review — the nine lights
Nine questions with a colour each. Ice, weather, chart depth, ship capability,
comms, traffic, logistics, contingency, execution.

> **"Health is the worst of the nine. It's never a score — there's no
> 'safety = 82%' anywhere in this code. And if we can't answer a question, it
> goes grey, and grey can never count as a pass."**

Type a name → **Approve**.
**Why a name is required:** an unsigned decision isn't a decision.

### Begin navigation — **the thirty seconds that win it**
Drag the time slider.

> **"Watch the top right. Green leaving Cape Town… and there — it drops as we
> push into the ice and lose the satellite. And it tells you *which* of the nine
> changed. It's not a colour someone picked. It's derived."**

### The time bar
**HOME** (snaps back — one bad scroll used to lose everything) · **◀ ▶▶** six
hours · **▶** play · the slider stops at seven days.
**Why seven:** the only Antarctic ice forecast on Earth runs nine days, and this
ship takes fifteen to get there. **At departure, 41% of the voyage is beyond any
forecast that exists.** We show the edge instead of pretending past it.

### The left rail — eleven layers
ICE · **BRG icebergs** · WX wind · CUR current · RTE route · SHP ship · AIS
traffic · WRN warnings · ASPA protected areas · LND coast · GRD grid ·
**RIO POLARIS**.

**Turn on BRG and zoom in.** Each iceberg has an **arrow**.
> **"That arrow is where that berg will be tomorrow. Dashed means the wind can
> move it; solid means only the current can. The circle around it is how wrong
> we might be — and it stops at 72 hours, because past that we can't back it up.
> A hollow one with a line under it is aground. It isn't going anywhere, so it
> doesn't get an arrow."**

**Why:** the officer's only real question about a berg is *is it coming toward
me, and when.* Speed doesn't answer that. A position tomorrow does.

### The right rail
- **Alerts** — P1/P2/P3, each with what changed, where, how sure, **what it does
  to your route**, and what to do. Click to acknowledge.
  **Why:** nothing becomes an alarm unless it changes the plan. Otherwise it's
  just a number on a panel.
- **Own ship** — position, course, speed, next waypoint, ETA.
- **Ice** — at the ship, worst on the route, the limit, and the margin.
- **Weather in corridor** — *along your track*, not at a weather station.
- **Hazard timeline** — 6 / 12 / 24 / 48 hours ahead.
- **Icebergs** — how many we see, **how many the world catalogue actually
  tracks**, and how many are aground.
  > **"Only a handful of these are in the official iceberg catalogue —
  > it only lists bergs over eighteen kilometres. The other nineteen are real
  > and invisible to it. So this system is forbidden from ever printing the word
  > 'none'. There's a test that fails the build if it does."**
- **POLARIS** — pick an ice type and a band appears.
  > **"This is the international ice risk index. We show a **range**, not a
  > number — because there's no official row for this ship's class, and guessing
  > spans forty points. Look: under the harshest reading it says caution at 70%
  > ice, and our working limit is 80%. That gap is the finding."**
- **Alternatives** — hover one, its route previews on the chart.
- **Decision log** — every version, who signed it, what it replaced.
- **Link & pack** — **7.8 kilobytes a day, measured**. Nine hundredths of a
  second on a satellite phone.
  **Why:** below 70° south there is no broadband. If your product needs the
  internet, it doesn't work where it's needed.

### The bottom strip
Position, course, speed, ice, wind, sea, visibility, ETA, fuel, health — always
there. Borrowed from OpenCPN, which real sailors already use.

---

## The three questions that kill teams

**"Is any of this real?"**
> "The physics is real, the weather is invented, and the badge says so. The real
> satellite data — 1,096 days of it — is on the other tab, and it's where we
> found a bug in the official product: it reports suppressed coastal pixels as
> **open water**, on 43% of days, right where the ship has to go. Four of the
> eight days Bharati looked open were that bug."

**"What's your accuracy number?"**
> "Eighteen and a half percent better than the standard baseline at one day,
> thirty-point-six percent at seven — **and we'll tell you why we don't fully trust the
> thirty-point-six**. The field we corrected had already seen the answer. It's an upper
> bound, not a measurement. The test that settles it is written and we haven't
> run it."

**"What have you saved anyone?"**
> "Nothing proven yet, and I won't pretend otherwise. We measured one departure
> date and saved 0.03 days. We also measured daily re-planning and found it
> **slower**. We publish both. What we've built is the thing that tells you when
> the door is shut — the value of that needs a season to prove."

---

## Close on this

> **"Everyone here will show you what their system knows.
> We're the only team that will show you what ours doesn't —
> and then tell you exactly which satellite would fix it."**
