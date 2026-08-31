"""Residual U-Net that bias-corrects the CMEMS sea-ice concentration forecast.

Predicts the residual (delta-SIC), never the field itself, so a zero output
reproduces the operational forecast exactly and the model's floor is CMEMS's
skill rather than zero. See docs/ML_ARCHITECTURE.md §1.1.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class SICCorrectionUNet(nn.Module):
    """3-level U-Net. Measured parameter counts at depth=3, in_channels=19:

        base_filters=16 ->   485,041
        base_filters=24 -> 1,088,137
        base_filters=32 -> 1,931,617
        base_filters=40 -> 3,015,481   <- default, matches the ~3M the
                                          compute budget in §1.3 was costed on

    ML_ARCHITECTURE.md §1.1 pairs "16 base filters" with "~2-4M parameters";
    those two are inconsistent (16 filters gives 485K), so the default here
    follows the parameter count the compute plan actually depends on. Capacity
    should still be tuned empirically in Phase 2 — smaller may well be enough,
    and 485K would train ~6x faster.

    Input:  (B, in_channels, H, W) — the 19 channels of ML_ARCHITECTURE.md §1.2
    Output: (B, 1, H, W) — delta-SIC in SIC-fraction units, unbounded

    The output is deliberately unbounded: clipping to a valid concentration
    happens after adding the base forecast, in `apply_correction`, since it is
    the *sum* that must land in [0, 1], not the correction on its own.
    """

    def __init__(self, in_channels: int = 19, base_filters: int = 40, depth: int = 3):
        super().__init__()
        self.depth = depth

        self.encoders = nn.ModuleList()
        self.pools = nn.ModuleList()
        ch = in_channels
        for level in range(depth):
            out_ch = base_filters * (2 ** level)
            self.encoders.append(ConvBlock(ch, out_ch))
            self.pools.append(nn.MaxPool2d(2))
            ch = out_ch

        self.bottleneck = ConvBlock(ch, base_filters * (2 ** depth))
        ch = base_filters * (2 ** depth)

        self.upsamples = nn.ModuleList()
        self.decoders = nn.ModuleList()
        for level in reversed(range(depth)):
            skip_ch = base_filters * (2 ** level)
            self.upsamples.append(nn.ConvTranspose2d(ch, skip_ch, kernel_size=2, stride=2))
            self.decoders.append(ConvBlock(skip_ch * 2, skip_ch))
            ch = skip_ch

        self.head = nn.Conv2d(ch, 1, kernel_size=1)
        # Start as a no-op: an untrained model reproduces CMEMS exactly rather
        # than injecting random noise into an already-skilful forecast.
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_hw = x.shape[-2:]
        # Polar-stereographic grids (~332x316) are not divisible by 2^depth;
        # pad up so skip connections line up, then crop back at the end.
        x = self._pad_to_multiple(x, 2 ** self.depth)

        skips = []
        for encoder, pool in zip(self.encoders, self.pools):
            x = encoder(x)
            skips.append(x)
            x = pool(x)

        x = self.bottleneck(x)

        for upsample, decoder, skip in zip(self.upsamples, self.decoders, reversed(skips)):
            x = upsample(x)
            x = torch.cat([x, skip], dim=1)
            x = decoder(x)

        x = self.head(x)
        return x[..., : input_hw[0], : input_hw[1]]

    @staticmethod
    def _pad_to_multiple(x: torch.Tensor, multiple: int) -> torch.Tensor:
        h, w = x.shape[-2:]
        pad_h = (multiple - h % multiple) % multiple
        pad_w = (multiple - w % multiple) % multiple
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="replicate")
        return x


def apply_correction(base_forecast: torch.Tensor, delta: torch.Tensor) -> torch.Tensor:
    """corrected = clip(CMEMS forecast + predicted residual, 0, 1)."""
    return torch.clamp(base_forecast + delta, 0.0, 1.0)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
