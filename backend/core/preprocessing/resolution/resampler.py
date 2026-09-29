from pathlib import Path

import cv2
import numpy as np

from .config import ResolutionConfig
from .models import ResolutionResult
from .parser import ResolutionParser


class ResolutionResampler:

    def __init__(
        self,
        config: ResolutionConfig | None = None,
    ):
        self.config = config or ResolutionConfig()
        self.parser = ResolutionParser()

    def _validate_image(
        self,
        image: np.ndarray,
        name: str,
    ) -> bool:

        if not isinstance(image, np.ndarray):
            print(
                f"Resolution: {name} is not a NumPy array."
            )
            return False

        if image.size == 0:
            print(
                f"Resolution: {name} image is empty."
            )
            return False

        if image.ndim not in (2, 3):
            print(
                f"Resolution: unsupported {name} dimensions."
            )
            return False

        return True

    def _calculate_scale(
        self,
        reference_resolution: float,
        source_resolution: float,
    ) -> float:

        return (
            source_resolution
            / reference_resolution
        )

    def _resample_source(
        self,
        source: np.ndarray,
        scale: float,
    ) -> np.ndarray:

        if not np.isfinite(scale) or scale <= 0:
            raise ValueError(
                "Invalid resolution scale."
            )

        if np.isclose(
            scale,
            1.0,
            rtol=1e-6,
            atol=1e-6,
        ):
            return source.copy()

        height, width = source.shape[:2]

        new_width = max(
            1,
            int(round(width * scale)),
        )

        new_height = max(
            1,
            int(round(height * scale)),
        )

        print(
            f"Resolution: source size "
            f"{width}x{height} -> "
            f"{new_width}x{new_height}"
        )

        return cv2.resize(
            source,
            (
                new_width,
                new_height,
            ),
            interpolation=self.config.interpolation,
        )

    def process(
        self,
        reference: np.ndarray,
        source: np.ndarray,
        reference_xml: str | Path,
        source_xml: str | Path,
    ) -> ResolutionResult:

        # print("\n=== RESOLUTION RESAMPLING ===")

        original_source = source.copy()

        if not self._validate_image(
            reference,
            "reference",
        ):
            print(
                "Resolution: skipped."
            )

            return ResolutionResult(
                reference=reference,
                source=original_source,
                reference_resolution=None,
                source_resolution=None,
                scale=None,
                metadata={
                    "status": "skipped",
                    "reason": "invalid_reference",
                },
            )

        if not self._validate_image(
            source,
            "source",
        ):
            print(
                "Resolution: skipped."
            )

            return ResolutionResult(
                reference=reference.copy(),
                source=original_source,
                reference_resolution=None,
                source_resolution=None,
                scale=None,
                metadata={
                    "status": "skipped",
                    "reason": "invalid_source",
                },
            )

        try:
            reference_info = self.parser.parse(
                reference_xml
            )

            source_info = self.parser.parse(
                source_xml
            )

            print(
                f"Resolution: "
                f"{reference_info.instrument} = "
                f"{reference_info.meters_per_pixel} m/pixel"
            )

            print(
                f"Resolution: "
                f"{source_info.instrument} = "
                f"{source_info.meters_per_pixel} m/pixel"
            )

            scale = self._calculate_scale(
                reference_info.meters_per_pixel,
                source_info.meters_per_pixel,
            )

            print(
                f"Resolution: source scale = "
                f"{scale:.6f}"
            )

            resampled_source = self._resample_source(
                source,
                scale,
            )

            print(
                "Resolution: resampling completed."
            )

            return ResolutionResult(
                reference=reference.copy(),
                source=resampled_source,
                reference_resolution=reference_info,
                source_resolution=source_info,
                scale=scale,
                metadata={
                    "status": "success",
                    "reference_shape": reference.shape,
                    "source_shape": source.shape,
                    "output_source_shape": resampled_source.shape,
                },
            )

        except Exception as exc:
            print(
                f"Resolution: failed: {exc}"
            )

            print(
                "Resolution: returning original source."
            )

            return ResolutionResult(
                reference=reference.copy(),
                source=original_source,
                reference_resolution=None,
                source_resolution=None,
                scale=None,
                metadata={
                    "status": "skipped",
                    "reason": "processing_error",
                    "error": str(exc),
                },
            )


def resolution_resampling(
    reference: np.ndarray,
    source: np.ndarray,
    reference_xml: str | Path,
    source_xml: str | Path,
) -> tuple[np.ndarray, np.ndarray]:

    resampler = ResolutionResampler()

    result = resampler.process(
        reference,
        source,
        reference_xml,
        source_xml,
    )

    return (
        result.reference,
        result.source,
    )