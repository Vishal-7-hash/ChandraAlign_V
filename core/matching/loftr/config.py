from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import torch 


PretrainedModel = Literal["outdoor", "indoor"]
DeviceType = Literal["auto", "cpu", "cuda"]


@dataclass(frozen=True)
class LoFTRConfig:
    """
    Configuration for the LoFTR matching engine.

    This class contains model/inference configuration only.

    Image preprocessing is intentionally NOT handled here.
    """

    pretrained: PretrainedModel = "outdoor"

    device: DeviceType = "auto"

    # Run inference using torch.inference_mode().
    inference_mode: bool = True

    # Whether to use automatic mixed precision on CUDA.
    use_amp: bool = False

    # Confidence threshold applied AFTER LoFTR inference.
    #
    # Important:
    # LoFTR itself performs its own internal coarse matching.
    # This threshold is an additional application-level filter.
    confidence_threshold: float | None = None

    def resolve_device(self) -> torch.device:
        """
        Resolve the requested device into a torch.device.
        """

        if self.device == "cpu":
            return torch.device("cpu")

        if self.device == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA was explicitly requested, but CUDA is not available."
                )

            return torch.device("cuda")

        # auto
        return torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    def validate(self) -> None:
        """Validate configuration values."""

        if self.confidence_threshold is not None:
            if not 0.0 <= self.confidence_threshold <= 1.0:
                raise ValueError(
                    "confidence_threshold must be between 0 and 1."
                )

        if self.use_amp and self.resolve_device().type != "cuda":
            raise ValueError(
                "use_amp=True is only supported with CUDA."
            )