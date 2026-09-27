import numpy as np

from .control_points import (
    FeatureControlPointEstimator,
    filter_control_points,
)
from .warping import create_triangulation, warp_piecewise_affine


class ViewpointCorrector:

    def __init__(
        self,
        lowes_ratio: float = 0.75,
        mutual: bool = False,
    ):
        self.estimator = FeatureControlPointEstimator(
            lowes_ratio=lowes_ratio,
            mutual=mutual,
        )

    def process(
        self,
        reference: np.ndarray,
        source: np.ndarray,
    ) -> np.ndarray:

        original_source = source.copy()

        if not self._validate_images(reference, source):
            print("Viewpoint: correction skipped.")
            return original_source

        try:
            control_points = self.estimator.estimate(
                reference,
                source,
            )

            if control_points.count < 3:
                print("Viewpoint: insufficient control points.")
                return original_source

            control_points = filter_control_points(
                control_points
            )

            if control_points.count < 3:
                print(
                    "Viewpoint: insufficient filtered "
                    "control points."
                )
                return original_source

            triangulation = create_triangulation(
                control_points.reference_points,
                control_points.source_points,
            )

            if triangulation is None:
                print("Viewpoint: TIN is not viable.")
                return original_source

            corrected_source = warp_piecewise_affine(
                source,
                triangulation,
                reference.shape[:2],
            )

            if corrected_source is None:
                print("Viewpoint: warping failed.")
                return original_source

            print(
                f"Viewpoint: correction completed using "
                f"{control_points.count} control points."
            )

            print(
                "Viewpoint: corrected result generated, "
                "original source returned for testing."
            )

            return original_source

        except Exception as exc:
            print(f"Viewpoint: correction failed: {exc}")
            return original_source

    @staticmethod
    def _validate_images(
        reference: np.ndarray,
        source: np.ndarray,
    ) -> bool:

        if not isinstance(reference, np.ndarray):
            return False

        if not isinstance(source, np.ndarray):
            return False

        if reference.size == 0 or source.size == 0:
            return False

        if reference.ndim not in (2, 3):
            return False

        if source.ndim not in (2, 3):
            return False

        return True


def viewpoint_correction(
    reference: np.ndarray,
    source: np.ndarray,
) -> np.ndarray:

    corrector = ViewpointCorrector()

    return corrector.process(
        reference,
        source,
    )