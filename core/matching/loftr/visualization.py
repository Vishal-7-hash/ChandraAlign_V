from __future__ import annotations

import cv2
import numpy as np

from .result import LoFTRResult


def _to_display_image(
    image: np.ndarray,
) -> np.ndarray:
    """
    Convert an image into an OpenCV displayable image.

    IMPORTANT:
    This is visualization conversion only.
    It does NOT modify the image used for LoFTR.
    """

    image = np.asarray(image)

    if image.ndim == 2:

        display = cv2.normalize(
            image,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        )

        return display.astype(np.uint8)

    if image.ndim == 3:

        if image.shape[2] == 1:
            return _to_display_image(
                image[:, :, 0]
            )

        if image.shape[2] == 3:
            return image.astype(np.uint8)

    raise ValueError(
        f"Unsupported image shape: {image.shape}"
    )


def create_match_visualization(
    image0: np.ndarray,
    image1: np.ndarray,
    result: LoFTRResult,
    max_matches: int = 500,
) -> np.ndarray:
    """
    Create a side-by-side LoFTR correspondence visualization.

    This function does NOT modify the original input images.
    """

    img0 = _to_display_image(image0)
    img1 = _to_display_image(image1)

    if img0.ndim == 2:
        img0 = cv2.cvtColor(
            img0,
            cv2.COLOR_GRAY2BGR,
        )

    if img1.ndim == 2:
        img1 = cv2.cvtColor(
            img1,
            cv2.COLOR_GRAY2BGR,
        )

    h0, w0 = img0.shape[:2]
    h1, w1 = img1.shape[:2]

    canvas_height = max(h0, h1)

    canvas_width = w0 + w1

    canvas = np.zeros(
        (canvas_height, canvas_width, 3),
        dtype=np.uint8,
    )

    canvas[:h0, :w0] = img0
    canvas[:h1, w0:w0 + w1] = img1

    num_matches = result.num_matches

    if num_matches == 0:
        return canvas

    # We visualize strongest matches first.
    order = np.argsort(
        result.confidence
    )[::-1]

    order = order[:max_matches]

    for index in order:

        x0, y0 = result.keypoints0[index]
        x1, y1 = result.keypoints1[index]

        x0 = int(round(x0))
        y0 = int(round(y0))

        x1 = int(round(x1)) + w0
        y1 = int(round(y1))

        cv2.line(
            canvas,
            (x0, y0),
            (x1, y1),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.circle(
            canvas,
            (x0, y0),
            2,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

        cv2.circle(
            canvas,
            (x1, y1),
            2,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

    return canvas


def create_match_heatmap(
    image: np.ndarray,
    result: LoFTRResult,
    image_index: int = 0,
    radius: int = 5,
) -> np.ndarray:
    """
    Create a visualization showing where LoFTR
    produced correspondences.

    image_index:
        0 -> keypoints from image0
        1 -> keypoints from image1
    """

    display = _to_display_image(image)

    if display.ndim == 2:
        display = cv2.cvtColor(
            display,
            cv2.COLOR_GRAY2BGR,
        )

    heatmap = np.zeros(
        display.shape[:2],
        dtype=np.uint8,
    )

    points = (
        result.keypoints0
        if image_index == 0
        else result.keypoints1
    )

    for x, y in points:

        x = int(round(x))
        y = int(round(y))

        if (
            0 <= x < heatmap.shape[1]
            and 0 <= y < heatmap.shape[0]
        ):
            cv2.circle(
                heatmap,
                (x, y),
                radius,
                255,
                -1,
            )

    heatmap = cv2.GaussianBlur(
        heatmap,
        (0, 0),
        sigmaX=5,
    )

    return heatmap