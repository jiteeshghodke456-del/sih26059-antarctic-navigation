# Run it

## On your WSL laptop

```bash
cd <repo>/.claude/worktrees/v3-compliance
rm -rf .venv-demo                       # the sandbox one links to the wrong python
uv venv .venv-demo --python 3.12
uv pip install --python .venv-demo/bin/python -r isih/demo/requirements.txt
.venv-demo/bin/python -m uvicorn isih.demo.app:app --port 8000
```

Open <http://127.0.0.1:8000>.

The world is seeded, so **your screen is the same as mine** — the draws come
from blake2b rather than NumPy's generator precisely so a different Python does
not give a different world.

## Two consoles

| Path | What it is |
|---|---|
| `/` | **The bridge console.** Synthetic environment, real physics, live routing |
| `/legacy` | The December 2019 NSIDC replay. **Real satellite observations** |
| `/future` | Baymax and the local assistant, badged simulated |

Keep `/legacy`. It is the only page that renders real observations, and it is
the strongest evidence the project has.

## The eight clicks

sign in → command centre → new voyage → mission → route (**Solve**) →
waypoints → review → **Approve** → begin navigation.

Then: drag the time slider. The ship moves, the ice edge moves because the wind
moved it, alerts appear, and route health changes as a consequence.

## What to show, in order

1. **The nine gates at Review.** Six are grey. *"A gate we cannot evaluate is
   never a pass, and each grey one names the dataset that would settle it."*
2. **Approve, then advance the clock.** Health changes and the console names the
   gate that broke. Step back: it says nothing, because nothing changed.
3. **Alternatives.** Corridor C is the interesting one — at a 55 % ice limit
   there is **no route at all**. Not slower: unreachable.
4. **An iceberg.** Click one in the Icebergs panel: projected track with an
   uncertainty circle that grows and **stops at 72 h**, and a CPA measured
   against the ship's *future* track.
5. **The link panel.** The daily pack is **7.8 KB gzipped, 0.09 s at Certus** —
   measured by building and compressing the real payload, not asserted.

## Say this, out loud, early

> The environment is synthetic — real physics, invented initial conditions. It
> is on the badge in the header. The real satellite data is on `/legacy`.

## Do not say

`docs/RUN_OF_SHOW.md` has the list. The four most recent additions are the ones
the submitted deck got wrong: automatic re-planning, "1,096 files every day",
the compression ratio, and the 76 KB pack.

## Tests

```bash
python -m pytest isih models -q        # 156, no browser needed
python -m pytest isih/demo/test_bridge_ui.py -q   # 7, needs playwright + a running server
```

## Publishing the port from the sandbox

The demo binds `0.0.0.0:8000`. To reach it from the host, run **on the host**:

```bash
sbx ports claude-jiteesh --publish 8000:8000/tcp
```
