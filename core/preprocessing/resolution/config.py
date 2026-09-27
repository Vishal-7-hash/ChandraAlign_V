from dataclasses import dataclass

import cv2


@dataclass(frozen=True)
class ResolutionConfig:
    interpolation: int = cv2.INTER_AREA