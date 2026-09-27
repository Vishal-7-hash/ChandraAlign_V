from dataclasses import dataclass


@dataclass(frozen=True)
class RANSACConfig:

    reprojection_threshold: float = 3.0
    confidence: float = 0.995
    max_iterations: int = 2000
    min_matches: int = 4