import cv2
import numpy as np

from .config import RANSACConfig
from .exceptions import (
    HomographyEstimationError,
    InsufficientMatchesError,
)
from .models import RANSACResult


class RANSACRegistration:

    def __init__(
        self,
        config: RANSACConfig | None = None,
    ):
        self.config = config or RANSACConfig()

    def _validate_points(
        self,
        points0: np.ndarray,
        points1: np.ndarray,
    ):

        points0 = np.asarray(points0, dtype=np.float32)
        points1 = np.asarray(points1, dtype=np.float32)

        if points0.ndim != 2 or points0.shape[1] != 2:
            raise ValueError(
                f"points0 must have shape (N, 2), got {points0.shape}"
            )

        if points1.ndim != 2 or points1.shape[1] != 2:
            raise ValueError(
                f"points1 must have shape (N, 2), got {points1.shape}"
            )

        if len(points0) != len(points1):
            raise ValueError(
                "points0 and points1 must contain the same number of points."
            )

        if len(points0) < self.config.min_matches:
            raise InsufficientMatchesError(
                f"At least {self.config.min_matches} matches are required."
            )

        if not np.isfinite(points0).all():
            raise ValueError("points0 contains invalid values.")

        if not np.isfinite(points1).all():
            raise ValueError("points1 contains invalid values.")

        return points0, points1

    def _calculate_reprojection_errors(
        self,
        points0: np.ndarray,
        points1: np.ndarray,
        homography: np.ndarray,
    ) -> np.ndarray:

        projected = cv2.perspectiveTransform(
            points0.reshape(-1, 1, 2),
            homography,
        ).reshape(-1, 2)

        errors = np.linalg.norm(
            projected - points1,
            axis=1,
        )

        return errors

    def estimate(
        self,
        points0: np.ndarray,
        points1: np.ndarray,
    ) -> RANSACResult:

        points0, points1 = self._validate_points(
            points0,
            points1,
        )

        homography, mask = cv2.findHomography(
            points0,
            points1,
            method=cv2.RANSAC,
            ransacReprojThreshold=self.config.reprojection_threshold,
            maxIters=self.config.max_iterations,
            confidence=self.config.confidence,
        )

        if homography is None or mask is None:
            raise HomographyEstimationError(
                "RANSAC could not estimate a homography."
            )

        mask = mask.ravel().astype(bool)

        reprojection_errors = (
            self._calculate_reprojection_errors(
                points0,
                points1,
                homography,
            )
        )

        inlier_points0 = points0[mask]
        inlier_points1 = points1[mask]

        outlier_points0 = points0[~mask]
        outlier_points1 = points1[~mask]

        num_input_matches = len(points0)
        num_inliers = int(mask.sum())
        num_outliers = num_input_matches - num_inliers

        inlier_ratio = (
            num_inliers / num_input_matches
            if num_input_matches > 0
            else 0.0
        )

        outlier_ratio = (
            num_outliers / num_input_matches
            if num_input_matches > 0
            else 0.0
        )

        inlier_errors = reprojection_errors[mask]

        if len(inlier_errors) > 0:

            mean_reprojection_error = float(
                np.mean(inlier_errors)
            )

            median_reprojection_error = float(
                np.median(inlier_errors)
            )

            rmse = float(
                np.sqrt(
                    np.mean(
                        inlier_errors ** 2
                    )
                )
            )

        else:

            mean_reprojection_error = float("inf")
            median_reprojection_error = float("inf")
            rmse = float("inf")

        return RANSACResult(
            homography=homography,
            inlier_mask=mask,
            inlier_points0=inlier_points0,
            inlier_points1=inlier_points1,
            outlier_points0=outlier_points0,
            outlier_points1=outlier_points1,
            num_input_matches=num_input_matches,
            num_inliers=num_inliers,
            num_outliers=num_outliers,
            inlier_ratio=inlier_ratio,
            outlier_ratio=outlier_ratio,
            reprojection_errors=reprojection_errors,
            mean_reprojection_error=mean_reprojection_error,
            median_reprojection_error=median_reprojection_error,
            rmse=rmse,
        )