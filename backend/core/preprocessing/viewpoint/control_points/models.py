from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ControlPoints:
    reference_points: np.ndarray
    source_points: np.ndarray
    confidence: np.ndarray | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.reference_points.ndim != 2 or self.reference_points.shape[1] != 2:
            raise ValueError("reference_points must have shape (N, 2)")

        if self.source_points.ndim != 2 or self.source_points.shape[1] != 2:
            raise ValueError("source_points must have shape (N, 2)")

        if len(self.reference_points) != len(self.source_points):
            raise ValueError(
                "reference_points and source_points must have equal length"
            )

        if self.confidence is not None:
            if len(self.confidence) != len(self.reference_points):
                raise ValueError(
                    "confidence length must match number of control points"
                )

    @property
    def count(self) -> int:
        return len(self.reference_points)