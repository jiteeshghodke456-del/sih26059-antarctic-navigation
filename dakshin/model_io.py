"""Load the trained September prototype checkpoints (HANDOFF_TONIGHT slice 1).

The four checkpoints (lead 1, 3, 5, 7 days) live in
models/sic_correction/checkpoints/ with a SHA256SUMS file written when they
were pulled from the Kaggle training run. Loading verifies the checksum first,
so a silently corrupted or swapped file can never reach the router.

The prototype config is in_channels=12, base_filters=32, depth=3
(set in dakshin/kaggle/make_notebook.py) — NOT the unet.py defaults, which are the
production model's.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.sic_correction.unet import SICCorrectionUNet  # noqa: E402

CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "models" / "sic_correction" / "checkpoints"
LEADS = (1, 3, 5, 7)
PROTOTYPE_CONFIG = {"in_channels": 12, "base_filters": 32, "depth": 3}


def checkpoint_path(lead: int) -> Path:
    if lead not in LEADS:
        raise ValueError(f"lead must be one of {LEADS}, got {lead}")
    # "isih_" is the historical artifact id from the Kaggle run; SHA256SUMS pins these names.
    return CHECKPOINT_DIR / f"isih_prototype_lead{lead}.pt"


def verify_checksum(path: Path) -> None:
    sums_file = CHECKPOINT_DIR / "SHA256SUMS"
    if not sums_file.exists():
        raise FileNotFoundError(f"{sums_file} missing — refusing to load unverified weights")
    expected = None
    for line in sums_file.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == path.name:
            expected = parts[0]
    if expected is None:
        raise ValueError(f"{path.name} not listed in {sums_file}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"checksum mismatch for {path.name}: expected {expected}, got {actual}")


def load_checkpoint(lead: int) -> SICCorrectionUNet:
    """Build the prototype U-Net and load verified weights for one lead."""
    path = checkpoint_path(lead)
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — pull it from the Kaggle run (slice 1)")
    verify_checksum(path)
    model = SICCorrectionUNet(**PROTOTYPE_CONFIG)
    state = torch.load(path, map_location="cpu", weights_only=True)
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    model.load_state_dict(state)
    model.eval()
    return model
