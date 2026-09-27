import cv2
import numpy as np

from .triangulation import Triangulation


def warp_piecewise_affine(
    source: np.ndarray,
    triangulation: Triangulation,
    output_shape: tuple[int, int],
) -> np.ndarray:

    if source is None:
        return None

    if not isinstance(source, np.ndarray):
        return None

    if source.ndim not in (2, 3):
        return None

    output_height, output_width = output_shape

    if output_height <= 0 or output_width <= 0:
        return source.copy()

    if source.ndim == 2:
        output = np.zeros(
            (output_height, output_width),
            dtype=source.dtype,
        )
    else:
        output = np.zeros(
            (
                output_height,
                output_width,
                source.shape[2],
            ),
            dtype=source.dtype,
        )

    for triangle in triangulation.triangles:

        src_triangle = triangulation.source_points[triangle]
        ref_triangle = triangulation.reference_points[triangle]

        try:
            matrix = cv2.getAffineTransform(
                src_triangle.astype(np.float32),
                ref_triangle.astype(np.float32),
            )
        except Exception:
            continue

        x, y, w, h = cv2.boundingRect(
            ref_triangle.astype(np.float32)
        )

        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(output_width, x + w)
        y1 = min(output_height, y + h)

        if x0 >= x1 or y0 >= y1:
            continue

        local_w = x1 - x0
        local_h = y1 - y0

        translation = np.array(
            [
                [1.0, 0.0, -x0],
                [0.0, 1.0, -y0],
            ],
            dtype=np.float32,
        )

        local_matrix = translation @ np.vstack(
            [
                matrix,
                [0.0, 0.0, 1.0],
            ]
        )

        local_matrix = local_matrix[:2]

        try:
            warped = cv2.warpAffine(
                source,
                local_matrix,
                (local_w, local_h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT,
            )
        except Exception:
            continue

        mask = np.zeros(
            (local_h, local_w),
            dtype=np.uint8,
        )

        local_triangle = ref_triangle - np.array(
            [x0, y0],
            dtype=np.float32,
        )

        cv2.fillConvexPoly(
            mask,
            np.round(local_triangle).astype(np.int32),
            255,
        )

        roi = output[
            y0:y1,
            x0:x1,
        ]

        valid = mask > 0

        if output.ndim == 2:
            roi[valid] = warped[valid]
        else:
            roi[valid, :] = warped[valid, :]

    return output