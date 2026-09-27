from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class LoFTRResult:
    keypoints0: np.ndarray
    keypoints1: np.ndarray
    confidence: np.ndarray

    image0_shape: tuple[int, int]
    image1_shape: tuple[int, int]

    inference_time_ms: float

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def num_matches(self) -> int:
        return int(len(self.confidence))

    @property
    def mean_confidence(self) -> float:
        if self.num_matches == 0:
            return 0.0

        return float(np.mean(self.confidence))

    @property
    def min_confidence(self) -> float:
        if self.num_matches == 0:
            return 0.0

        return float(np.min(self.confidence))

    @property
    def max_confidence(self) -> float:
        if self.num_matches == 0:
            return 0.0

        return float(np.max(self.confidence))

    @property
    def matches(self) -> np.ndarray:
        if self.num_matches == 0:
            return np.empty((0, 5), dtype=np.float32)

        return np.column_stack(
            (
                self.keypoints0,
                self.keypoints1,
                self.confidence,
            )
        ).astype(np.float32)

    def filter_by_confidence(
        self,
        threshold: float,
    ) -> "LoFTRResult":

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Confidence threshold must be between 0 and 1."
            )

        mask = self.confidence >= threshold

        return LoFTRResult(
            keypoints0=self.keypoints0[mask],
            keypoints1=self.keypoints1[mask],
            confidence=self.confidence[mask],
            image0_shape=self.image0_shape,
            image1_shape=self.image1_shape,
            inference_time_ms=self.inference_time_ms,
            metadata={
                **self.metadata,
                "confidence_threshold": threshold,
            },
        )