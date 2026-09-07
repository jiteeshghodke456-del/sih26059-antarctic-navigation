# MLflow setup (master prompt §42)

Status: tracking store, backfill script and verification are done and tested
in the sandbox. Starting a persistent local server and connecting it to
Claude Code through MCP cannot be finished here — see "What is still on your
machine" below for why, and the exact commands to finish it.

## What §42 actually asks for, and why a sandbox can only do part of it

Master prompt §42 describes **the user's WSL machine**: Claude Code 2.1.252,
a project-local `.venv`, MLflow "not yet connected to Claude Code," desired
for experiment/model tracking plus MCP access, with the MCP tool surface
kept minimal and no W&B. That machine is not this sandbox — this is a
separate, ephemeral Linux environment. MCP connects a client (Claude Code)
to a server process; both have to be reachable from wherever Claude Code
itself is running. A server started in this sandbox is gone when the
sandbox is, and this sandbox's `localhost` is not the WSL box's `localhost`.
So the parts of §42 that are inherently "on your machine" — starting a
server that persists, and registering it in **your** Claude Code's MCP
config — are done here only as tested instructions, not as a live
connection.

What a sandbox *can* do, and what this one did:

1. Confirm nothing MLflow-related existed yet, anywhere in this repo or in
   either available Python environment. (Checked — nothing found.)
2. Install MLflow into a real environment and prove the tracking store
   works: create it, write real runs into it, read them back through the
   MLflow API, and serve them through an actual `mlflow ui` HTTP server.
3. Write the runs that should exist — not fabricated, not placeholders, but
   the model's real recorded results, backfilled from the document that
   already holds them, with every run tagged as a Kaggle backfill so it is
   never mistaken for a locally-executed run.
4. Research, rather than guess, whether a real MLflow MCP server exists.
5. Write down the exact commands for the one machine that can finish this.

## 1. What was installed, and where

MLflow was not present anywhere in this repo, in `.venv-demo` (py3.12,
repo-local), or in `/home/agent/.venvs/isih-demo` (py3.14, this sandbox's
working demo environment) before this task.

Installed: **`mlflow==3.16.0`** into `/home/agent/.venvs/isih-demo` (the
venv named in the task as this sandbox's demo environment), via:

```bash
uv pip install --python /home/agent/.venvs/isih-demo/bin/python mlflow
```

`.venv-demo` (py3.12) was checked too — `mlflow` resolves cleanly there as
well — but nothing was installed into it, to avoid growing an environment
that is not otherwise this project's Python-package answer. This is a
sandbox-only install; it does not touch the user's WSL `.venv`.

## 2. The tracking store: `mlruns/` at the repo root

A plain filesystem (`file://`) store, no server required to write to it:

```
mlruns/
  <experiment_id>/
    <run_id>/
      meta.yaml, metrics/, params/, tags/, artifacts/
  .trash/
```

Tracking URI: `file://<repo_root>/mlruns`. This is what `isih/mlflow_backfill.py`
points at, and what `mlflow ui` should be pointed at too (command below).
It is added to `.gitignore` — it is regenerable (by re-running the backfill
script, or by future training runs logging into it), and the project's
existing convention is to not commit regenerable binary data (see the
`isih/data/` and `isih/checkpoints/` entries already in `.gitignore`).

**Consequence worth being explicit about:** because `mlruns/` is gitignored,
the four runs created in this sandbox do **not** travel with the branch.
Pulling this branch on your WSL machine will not show them in your MLflow
UI — you get the script, not its output. Re-running the script (step 4
below) regenerates the identical runs, since it reads the same fixed
numbers from `docs/ISIH_RESULTS.md` every time. This is intentional, not an
oversight: the alternative was committing binary run data to git.

### A version-specific wrinkle you will hit too

MLflow 3.x puts the plain filesystem backend into "maintenance mode": the
first call that touches the store raises unless `MLFLOW_ALLOW_FILE_STORE=true`
is set, pushing you toward a database backend (`sqlite:///mlflow.db`)
instead. This is real, current MLflow behavior (confirmed by reading
`FileStore.__init__` in the installed 3.16.0 source), not a sandbox quirk.

We opted back into the file store on purpose — it needs no running server
to log to and is a plain directory, which is what "pendrive-friendly,
offline-deployment-friendly" means in practice — rather than switching to a
database file. `isih/mlflow_backfill.py` sets
`os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")` itself, so you do
not need to set it by hand to run the script. You **do** need it set when
you start `mlflow ui` by hand (command below includes it).

If a future MLflow major version removes the filesystem backend outright
(rather than just gating it), the fallback is `mlflow server
--backend-store-uri sqlite:///mlflow.db` — still a single local file, still
no external service, just not a bare directory.

## 3. `isih/mlflow_backfill.py` — what it logs, and why backfill at all

The model in this project was trained on a **Kaggle T4 GPU notebook**
(`isih/kaggle/isih_train.ipynb`), not locally — that is where the GPU, the
CMEMS credentials, and the ~1-2 hour compute budget actually are. Neither
this sandbox nor your WSL laptop ran that training loop, so there is no
local run history for MLflow to have been "missing a connection to." MLflow
cannot retroactively observe a run that already finished elsewhere.

What the script does instead: log the real, already-recorded results as
MLflow runs, one per forecast horizon, so they are queryable and comparable
in the same store that future local runs will also write to. Every number
is copied verbatim from `docs/ISIH_RESULTS.md` — nothing is computed,
estimated, or invented by the script.

Per horizon, it logs:

- **Params**: `input_channels` (12), `model_parameters` (1,929,601),
  `horizon_days` (1/3/5/7), `split` (the temporal 70/15/15 train/val/test
  description from the results doc).
- **Metrics**: `rmse` (the model's test RMSE) and `persistence_rmse` (the
  persistence baseline at the same horizon, for comparison).
- **Tags**: `source=kaggle-backfill`, `training_platform`, `training_date`,
  `kaggle_notebook`, `results_doc`, and an `mlflow.note.content` explanation
  — so nobody downstream mistakes a backfilled Kaggle result for a run this
  machine executed.

It is idempotent: re-running it skips any horizon that already has a
`kaggle-backfill`-tagged run (checked via the MLflow API, not a file flag);
`--force` re-logs anyway.

## 4. What was actually run, and what it logged (verified, not assumed)

```bash
MLFLOW_DISABLE_AGENT_HINT=1 /home/agent/.venvs/isih-demo/bin/python isih/mlflow_backfill.py
```

Logged 4 runs into experiment `isih-sic-forecast`. Immediately queried back
independently (a **separate** Python process, not the same one that wrote
them) via `MlflowClient.search_runs`, and separately again through a real
`mlflow ui` HTTP server (`GET /api/2.0/mlflow/runs/search`) started against
this same store — both confirm the same four rows:

| lead (days) | rmse (ours) | persistence_rmse | channels | parameters | source |
|---|---|---|---|---|---|
| 1 | 0.0465 | 0.0570 | 12 | 1,929,601 | kaggle-backfill |
| 3 | 0.0720 | 0.0958 | 12 | 1,929,601 | kaggle-backfill |
| 5 | 0.0938 | 0.1204 | 12 | 1,929,601 | kaggle-backfill |
| 7 | 0.0968 | 0.1395 | 12 | 1,929,601 | kaggle-backfill |

Every value matches `docs/ISIH_RESULTS.md`'s headline table exactly — no
discrepancy was found between that document and the numbers logged.
Re-running the script a second time correctly reported all four horizons as
"already backfilled, skipping" rather than duplicating them.

## 5. Commands for your WSL machine

Run from the repo root, inside your project's `.venv` (create one first if
`§42`'s "a project-local Python `.venv` is being set up" hasn't finished —
`python3 -m venv .venv && source .venv/bin/activate`; `python` was reported
unavailable there, use `python3`/the venv's `python`).

**Install MLflow** (matches what this sandbox tested against; a newer
version should work identically but re-check the file-store note above if
it doesn't):

```bash
pip install mlflow==3.16.0
# or, if you also have uv: uv pip install mlflow==3.16.0
```

**Regenerate the backfilled runs locally** (they don't come with the repo —
see the gitignore note in §2):

```bash
python isih/mlflow_backfill.py
```

**Start the local MLflow server**, pointed at this repo's store:

```bash
cd /path/to/SIH26059-antarctic-navigation   # repo root, wherever you cloned it
MLFLOW_ALLOW_FILE_STORE=true mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 127.0.0.1 --port 5000
```

Open `http://localhost:5000` (WSL2 forwards `localhost` to Windows
automatically in the default configuration) — you should see the
`isih-sic-forecast` experiment with the 4 backfilled runs, plus any real
local training runs you log afterward, side by side.

**Going forward**: any script that actually trains locally should call
`mlflow.log_param(...)` / `mlflow.log_metric(...)` directly against this
same store (same pattern as `isih/mlflow_backfill.py`), so local runs and
the Kaggle backfill land in the same experiment and are directly comparable.

## 6. MCP connection — investigated, not invented

§42 asks to "connect MLflow to Claude Code through MCP," with the tool
surface kept minimal. Two claims to keep separate: whether a maintained
package exists (checked, below), and whether installing it is the right
call given "keep it minimal" (it probably isn't, as-is).

**A real, maintained MLflow MCP server does exist:**
[`kkruglik/mlflow-mcp`](https://github.com/kkruglik/mlflow-mcp) — MIT
licensed, on PyPI as `mlflow-mcp` (latest release 0.4.1, pushed 2026-08-08),
15 stars, 5 forks, not archived. Verified directly via the PyPI JSON API and
the GitHub API, not from memory. A second package,
[`yesid-lopez/mlflow-mcp-server`](https://github.com/yesid-lopez/mlflow-mcp-server),
also exists on PyPI but has 0 stars and no commits since March 2026 — far
less established, not recommended over the first.

**The problem: `mlflow-mcp`'s tool surface is not minimal.** Its README
lists roughly **40 tools** — 8 for experiments, 7 for runs, 2 for
metrics/params, 3 for artifacts, 2 for run comparison, 2 for MLflow 3
logged models, and **15 for the model registry** (register, tag, alias,
promote, transition stage, delete). That directly cuts against §42's "keep
the MCP tool surface minimal to avoid unnecessary context/token usage" —
this sandbox's own Claude Code session defers full MCP tool-schema loading
until a tool is searched for, which softens but does not remove the cost
(every tool still appears as a named, described entry). Installing a
40-tool server to read four numbers back is disproportionate.

**Recommendation, in order:**

1. **Don't add an MCP server for this yet.** Claude Code already has shell
   access, and MLflow already exposes a REST API and a `mlflow` CLI. Once
   the server from step 5 is running, Claude Code can query it directly —
   `curl http://127.0.0.1:5000/api/2.0/mlflow/runs/search -d '...'` or the
   `mlflow` Python client from a script — with **zero** added tool
   definitions. This is the option that actually satisfies "keep the tool
   surface minimal": no server to add at all.
2. **If you specifically want MCP-native tool calls** (structured calls
   Claude can invoke directly, plus its built-in prompts like
   `find_best_run` / `compare_runs`) rather than shell commands, `mlflow-mcp`
   is the one real, maintained option found. Add it project-scoped via a
   `.mcp.json` at the repo root on your machine (none exists yet, so this
   would not overwrite anything):

   ```json
   {
     "mcpServers": {
       "mlflow": {
         "command": "uvx",
         "args": ["mlflow-mcp"],
         "env": { "MLFLOW_TRACKING_URI": "http://127.0.0.1:5000" }
       }
     }
   }
   ```

   Accept that this brings in the full ~40-tool surface — there is no
   documented flag in `mlflow-mcp` to expose a subset. If Claude Code's
   permission system lets you allow only specific `mcp__mlflow__*` tool
   names, that reduces what gets *invoked* but not what gets *listed*.
3. **Do not** install `mlflow-mcp-server` (the second package) over option 2
   without your own review — it was not maintained-enough to recommend
   here, only noted so it isn't mistaken for missing from this search.

No other MLflow-specific MCP package was found. This section did not name a
package without confirming it first; if something better exists, it wasn't
findable via PyPI/GitHub search from this sandbox.

## 7. What remains impossible here, and must happen on your machine

- **Starting a server that persists** — anything started in this sandbox
  dies with the sandbox. Command is in §5.
- **Registering the MCP server (if you choose option 2 above) in your own
  Claude Code's config** — `.mcp.json` lives on your machine, and Claude
  Code 2.1.252 there is a different process from this sandbox's session.
- **Verifying an actual MCP tool call round-trips inside your real Claude
  Code** — this sandbox verified the store and the REST API work; it cannot
  verify your specific client-to-server MCP handshake, since that handshake
  can only happen between processes on your machine.
- **Regenerating `mlruns/` locally** — gitignored by design (§2); run
  `python isih/mlflow_backfill.py` there to get the same four runs.
- **No W&B was added** — §42 says not to unless there's a concrete reason;
  none arose during this task.
