from abc import ABC, abstractmethod

import numpy as np

from .models import ControlPoints


class ControlPointEstimator(ABC):

    @abstractmethod
    def estimate(
        self,
        reference: np.ndarray,
        source: np.ndarray,
    ) -> ControlPoints:
        raise NotImplementedError