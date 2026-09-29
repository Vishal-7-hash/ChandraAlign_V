from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RANSACResult:

    homography: np.ndarray
    inlier_mask: np.ndarray
    inlier_points0: np.ndarray
    inlier_points1: np.ndarray
    outlier_points0: np.ndarray
    outlier_points1: np.ndarray
    num_input_matches: int
    num_inliers: int
    num_outliers: int
    inlier_ratio: float
    outlier_ratio: float
    reprojection_errors: np.ndarray
    mean_reprojection_error: float
    median_reprojection_error: float
    rmse: float