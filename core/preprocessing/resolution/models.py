from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ResolutionInfo:
    meters_per_pixel: float
    instrument: str
    metadata: dict


@dataclass(frozen=True)
class ResolutionResult:
    reference: np.ndarray
    source: np.ndarray
    reference_resolution: ResolutionInfo | None
    source_resolution: ResolutionInfo | None
    scale: float | None
    metadata: dict