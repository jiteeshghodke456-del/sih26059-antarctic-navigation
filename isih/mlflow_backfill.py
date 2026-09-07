"""Backfill the Kaggle-trained ISIH SIC-correction results into MLflow.

Why backfill instead of "just log the training run"
-----------------------------------------------------
Master-prompt Section 42 asks for MLflow experiment/model tracking connected
to Claude Code. But the model these numbers describe was never trained in an
environment MLflow could have observed: it was trained on a **Kaggle T4 GPU
notebook** (`isih/kaggle/isih_train.ipynb`), because that is where the GPU,
the CMEMS credentials, and the ~1-2 hours of compute budget actually are.
Neither this sandbox nor the user's WSL laptop ran that training loop, so
there is no local run history for MLflow to have "connected to" — connecting
MLflow now cannot retroactively create one.

What this script does instead is log the real, already-recorded results of
that Kaggle run as MLflow runs, so they become queryable through the same
tracking store and UI that future *local* training runs will also write to.
This is a one-time backfill of history, not a substitute for tracking future
runs — the next model actually trained locally should call
`mlflow.log_metric` / `mlflow.log_param` directly from the training script,
the same way this file calls them for the Kaggle numbers.

Honesty constraint — read this before editing RESULTS_BY_LEAD below
----------------------------------------------------------------------
Every number in RESULTS_BY_LEAD, MODEL_PARAMETER_COUNT and INPUT_CHANNELS is
copied verbatim from `docs/ISIH_RESULTS.md`, the single source of truth for
this project's model results. This script does not compute, estimate, or
interpolate any metric — it only republishes numbers that already exist in
that document, into a system that can query and compare them.

Do NOT add a metric here that is not written in docs/ISIH_RESULTS.md. If a
number is needed that is not in that table, the fix is to run the real
experiment and update that document first, then reflect it here — never the
other way around. Every run created by this script is tagged
`source=kaggle-backfill` and carries an explanatory note (see
`_BACKFILL_NOTE` below) so nobody downstream mistakes a backfilled Kaggle
result for a locally-executed reproduction.

Usage
-----
    /home/agent/.venvs/isih-demo/bin/python isih/mlflow_backfill.py
    /home/agent/.venvs/isih-demo/bin/python isih/mlflow_backfill.py --force  # re-log even if already present

Re-running without --force is a no-op for any lead that already has a
backfilled run (checked by tag + param, not by wall-clock time), so this
script is safe to re-run after a fresh clone or a wiped mlruns/ directory.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# MLflow >= 3.x puts the plain filesystem tracking backend ("./mlruns", no
# database) into "maintenance mode": FileStore.__init__ raises unless this
# is set, pointing you at a sqlite/Postgres backend instead. We want the
# file-backed store on purpose -- it needs no server process to log to and
# is a plain directory a pendrive can carry, matching this project's offline
# deployment goal -- so we opt back in explicitly rather than switching to a
# database backend. The store is only constructed lazily (on set_experiment
# / start_run), so this just needs to run before those calls; it is placed
# ahead of `import mlflow` for visibility, not because import forces it.
# See docs/MLFLOW_SETUP.md for what this means for the user's own machine.
os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

import mlflow  # noqa: E402
from mlflow.tracking import MlflowClient  # noqa: E402

# --------------------------------------------------------------------------
# Source of truth: docs/ISIH_RESULTS.md, "Reproducing" and headline table.
# Verified against that document on 2026-09-07. If it and this file ever
# disagree, the document is authoritative and this file is stale — fix here.
# --------------------------------------------------------------------------

RESULTS_DOC = "docs/ISIH_RESULTS.md"
KAGGLE_NOTEBOOK = "isih/kaggle/isih_train.ipynb"
TRAINING_PLATFORM = "Kaggle (T4 GPU)"
TRAINING_DATE = "2026-08-31"

MODEL_PARAMETER_COUNT = 1_929_601
INPUT_CHANNELS = 12
SPLIT_STRATEGY = (
    "temporal: train 70% / val 15% (epoch selection only) / "
    "test 15% (scored exactly once) -- split by time, never randomly"
)

# lead time in days -> {test RMSE of our model, persistence baseline RMSE}
# Both columns come straight from the headline table in docs/ISIH_RESULTS.md.
RESULTS_BY_LEAD: dict[int, dict[str, float]] = {
    1: {"rmse": 0.0465, "persistence_rmse": 0.0570},
    3: {"rmse": 0.0720, "persistence_rmse": 0.0958},
    5: {"rmse": 0.0938, "persistence_rmse": 0.1204},
    7: {"rmse": 0.0968, "persistence_rmse": 0.1395},
}

EXPERIMENT_NAME = "isih-sic-forecast"

_BACKFILL_NOTE = (
    "Backfilled from a Kaggle T4 notebook run (isih/kaggle/isih_train.ipynb), "
    "trained 2026-08-31. This run did NOT execute locally or in this MLflow "
    "server's environment -- it republishes results already recorded in "
    f"{RESULTS_DOC} so they are queryable/comparable alongside future local "
    "runs. See that document for full methodology, caveats, and the ablation "
    "this headline number is still pending (background-channel leakage)."
)

REPO_ROOT = Path(__file__).resolve().parent.parent
MLRUNS_DIR = REPO_ROOT / "mlruns"


def _existing_backfilled_leads(client: MlflowClient, experiment_id: str) -> set[int]:
    """Leads that already have a kaggle-backfill run logged, so re-running
    this script is idempotent unless --force is passed."""
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string="tags.source = 'kaggle-backfill'",
    )
    leads = set()
    for run in runs:
        lead_str = run.data.params.get("horizon_days")
        if lead_str is not None:
            leads.add(int(lead_str))
    return leads


def backfill(force: bool = False) -> list[str]:
    """Log one MLflow run per forecast horizon. Returns the run_ids created
    (empty list if everything was already present and force=False)."""
    MLRUNS_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file://{MLRUNS_DIR}")
    mlflow.set_experiment(EXPERIMENT_NAME)

    client = MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    already_done = set() if force else _existing_backfilled_leads(client, experiment.experiment_id)

    created_run_ids: list[str] = []
    for lead_days, metrics in sorted(RESULTS_BY_LEAD.items()):
        if lead_days in already_done:
            print(f"lead={lead_days}d: already backfilled, skipping (use --force to re-log)")
            continue

        with mlflow.start_run(run_name=f"kaggle-backfill-lead-{lead_days}d") as run:
            mlflow.log_param("input_channels", INPUT_CHANNELS)
            mlflow.log_param("model_parameters", MODEL_PARAMETER_COUNT)
            mlflow.log_param("horizon_days", lead_days)
            mlflow.log_param("split", SPLIT_STRATEGY)

            mlflow.log_metric("rmse", metrics["rmse"])
            mlflow.log_metric("persistence_rmse", metrics["persistence_rmse"])

            mlflow.set_tag("source", "kaggle-backfill")
            mlflow.set_tag("training_platform", TRAINING_PLATFORM)
            mlflow.set_tag("training_date", TRAINING_DATE)
            mlflow.set_tag("kaggle_notebook", KAGGLE_NOTEBOOK)
            mlflow.set_tag("results_doc", RESULTS_DOC)
            mlflow.set_tag("mlflow.note.content", _BACKFILL_NOTE)

            created_run_ids.append(run.info.run_id)
            print(
                f"lead={lead_days}d: logged run {run.info.run_id} "
                f"(rmse={metrics['rmse']}, persistence_rmse={metrics['persistence_rmse']})"
            )

    return created_run_ids


def verify_and_print(experiment_name: str = EXPERIMENT_NAME) -> None:
    """Query the runs back via the MLflow API and print them, so 'it logged
    something' is checked rather than assumed."""
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        print(f"No experiment named {experiment_name!r} found.")
        return

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["params.horizon_days ASC"],
    )
    print(f"\nQueried back {len(runs)} run(s) from experiment "
          f"{experiment_name!r} (id={experiment.experiment_id}) "
          f"at {mlflow.get_tracking_uri()}:\n")
    header = f"{'lead_days':>9}  {'rmse':>8}  {'persistence_rmse':>17}  {'source':>16}  run_id"
    print(header)
    print("-" * len(header))
    for run in sorted(runs, key=lambda r: int(r.data.params.get("horizon_days", 0))):
        lead = run.data.params.get("horizon_days", "?")
        rmse = run.data.metrics.get("rmse", float("nan"))
        persistence = run.data.metrics.get("persistence_rmse", float("nan"))
        source = run.data.tags.get("source", "?")
        print(f"{lead:>9}  {rmse:>8}  {persistence:>17}  {source:>16}  {run.info.run_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-log all horizons even if a kaggle-backfill run already exists for them.",
    )
    args = parser.parse_args()

    backfill(force=args.force)
    verify_and_print()


if __name__ == "__main__":
    main()
