"""Slice 1 check: all four trained checkpoints load, with the exact prototype
parameter count, and run a forward pass on the real NSIDC grid shape."""
from pathlib import Path

import pytest
import torch

from model_io import CHECKPOINT_DIR, LEADS, load_checkpoint

pytestmark = pytest.mark.skipif(
    not (CHECKPOINT_DIR / "SHA256SUMS").exists(),
    reason="checkpoints not yet pulled from Kaggle (slice 1 in progress)",
)


@pytest.mark.parametrize("lead", LEADS)
def test_load_and_forward(lead):
    model = load_checkpoint(lead)
    n_params = sum(p.numel() for p in model.parameters())
    assert n_params == 1_929_601
    with torch.no_grad():
        out = model(torch.zeros(1, 12, 332, 316))
    assert out.shape == (1, 1, 332, 316)
    assert torch.isfinite(out).all()


def test_checksum_rejects_tampering(tmp_path, monkeypatch):
    # the guard the loader exists for: a corrupted file must not load
    import model_io

    sums = CHECKPOINT_DIR / "SHA256SUMS"
    bad = tmp_path / f"isih_prototype_lead{LEADS[0]}.pt"
    bad.write_bytes(b"not a checkpoint")
    monkeypatch.setattr(model_io, "CHECKPOINT_DIR", tmp_path)
    (tmp_path / "SHA256SUMS").write_text(sums.read_text())
    with pytest.raises(ValueError, match="checksum mismatch|not listed"):
        model_io.load_checkpoint(LEADS[0])
