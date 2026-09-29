import cv2
import numpy as np

from .base import ControlPointEstimator
from .models import ControlPoints


class FeatureControlPointEstimator(ControlPointEstimator):

    def __init__(
        self,
        lowes_ratio: float = 0.75,
        mutual: bool = False,
        max_features: int = 5000,
    ):
        self.lowes_ratio = lowes_ratio
        self.mutual = mutual
        self.max_features = max_features

    def estimate(
        self,
        reference: np.ndarray,
        source: np.ndarray,
    ) -> ControlPoints:

        try:
            reference_gray = self._to_grayscale(reference)
            source_gray = self._to_grayscale(source)

            detector = cv2.SIFT_create(
                nfeatures=self.max_features,
                contrastThreshold=0.01,
                edgeThreshold=10,
                sigma=1.6,
            )

            keypoints1, descriptors1 = detector.detectAndCompute(
                reference_gray,
                None,
            )

            keypoints2, descriptors2 = detector.detectAndCompute(
                source_gray,
                None,
            )

            reference_count = len(keypoints1)
            source_count = len(keypoints2)

            if descriptors1 is None or descriptors2 is None:
                return self._empty_result(
                    reference_count,
                    source_count,
                )

            matcher = cv2.BFMatcher(cv2.NORM_L2)

            forward_matches = matcher.knnMatch(
                descriptors1,
                descriptors2,
                k=2,
            )

            good_matches = []

            for pair in forward_matches:
                if len(pair) < 2:
                    continue

                first, second = pair

                if first.distance < self.lowes_ratio * second.distance:
                    good_matches.append(first)

            if self.mutual:
                reverse_matches = matcher.knnMatch(
                    descriptors2,
                    descriptors1,
                    k=2,
                )

                reverse_good = {}

                for pair in reverse_matches:
                    if len(pair) < 2:
                        continue

                    first, second = pair

                    if first.distance < self.lowes_ratio * second.distance:
                        reverse_good[first.queryIdx] = first.trainIdx

                good_matches = [
                    match
                    for match in good_matches
                    if reverse_good.get(match.trainIdx) == match.queryIdx
                ]

            candidate_reference = np.asarray(
                [
                    keypoints1[match.queryIdx].pt
                    for match in good_matches
                ],
                dtype=np.float32,
            ).reshape(-1, 2)

            candidate_source = np.asarray(
                [
                    keypoints2[match.trainIdx].pt
                    for match in good_matches
                ],
                dtype=np.float32,
            ).reshape(-1, 2)

            print(f"Feature estimator reference keypoints: {reference_count}")
            print(f"Feature estimator source keypoints: {source_count}")
            print(f"Feature estimator candidate matches: {len(good_matches)}")

            if len(candidate_reference) < 4:
                return self._empty_result(
                    reference_count,
                    source_count,
                    len(candidate_reference),
                )

            inlier_reference, inlier_source = self._magsac(
                candidate_reference,
                candidate_source,
            )

            print(
                f"Feature estimator MAGSAC inliers: "
                f"{len(inlier_reference)}"
            )

            return ControlPoints(
                reference_points=inlier_reference,
                source_points=inlier_source,
                metadata={
                    "method": "feature_based",
                    "backend": "opencv_sift",
                    "reference_keypoints": reference_count,
                    "source_keypoints": source_count,
                    "candidate_matches": len(candidate_reference),
                    "inlier_matches": len(inlier_reference),
                    "lowes_ratio": self.lowes_ratio,
                    "mutual": self.mutual,
                },
            )

        except Exception as exc:
            print(f"Feature estimator failed: {exc}")

            return self._empty_result(
                0,
                0,
                0,
                str(exc),
            )

    @staticmethod
    def _to_grayscale(image: np.ndarray) -> np.ndarray:

        if image.ndim == 2:
            grayscale = image
        elif image.ndim == 3:
            if image.shape[2] not in (3, 4):
                raise ValueError("Image must have 3 or 4 channels.")
            grayscale = cv2.cvtColor(
                image,
                cv2.COLOR_BGRA2GRAY if image.shape[2] == 4 else cv2.COLOR_BGR2GRAY,
            )
        else:
            raise ValueError("Image must be 2D or 3D.")

        if grayscale.size == 0:
            raise ValueError("Cannot extract features from an empty image")
        if grayscale.dtype != np.uint8:
            grayscale = cv2.normalize(
                grayscale,
                None,
                alpha=0,
                beta=255,
                norm_type=cv2.NORM_MINMAX,
                dtype=cv2.CV_8U,
            )

        return np.ascontiguousarray(grayscale)

    @staticmethod
    def _magsac(
        reference_points: np.ndarray,
        source_points: np.ndarray,
    ):

        try:
            _, mask = cv2.findHomography(
                source_points,
                reference_points,
                method=cv2.USAC_MAGSAC,
                ransacReprojThreshold=5.0,
                maxIters=10000,
                confidence=0.999,
            )
        except Exception:
            _, mask = cv2.findHomography(
                source_points,
                reference_points,
                method=cv2.RANSAC,
                ransacReprojThreshold=5.0,
                maxIters=10000,
                confidence=0.999,
            )

        if mask is None:
            return (
                np.empty((0, 2), dtype=np.float32),
                np.empty((0, 2), dtype=np.float32),
            )

        mask = mask.ravel().astype(bool)

        return (
            reference_points[mask],
            source_points[mask],
        )

    @staticmethod
    def _empty_result(
        reference_keypoints: int,
        source_keypoints: int,
        candidate_matches: int = 0,
        error: str | None = None,
    ) -> ControlPoints:

        metadata = {
            "method": "feature_based",
            "backend": "opencv_sift",
            "reference_keypoints": reference_keypoints,
            "source_keypoints": source_keypoints,
            "candidate_matches": candidate_matches,
            "inlier_matches": 0,
        }

        if error is not None:
            metadata["error"] = error

        return ControlPoints(
            reference_points=np.empty(
                (0, 2),
                dtype=np.float32,
            ),
            source_points=np.empty(
                (0, 2),
                dtype=np.float32,
            ),
            metadata=metadata,
        )