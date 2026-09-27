
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from core.matching.loftr.result import LoFTRResult
from core.registration.ransac.models import RANSACResult


def _confidence_to_color(confidence: float):
    confidence = float(
        np.clip(confidence, 0.0, 1.0)
    )

    if confidence < 0.5:
        t = confidence / 0.5
        return (1.0, t, 0.0)

    t = (confidence - 0.5) / 0.5
    return (1.0 - t, 1.0, 0.0)


def _prepare_image(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image)

    if image.ndim == 2:
        return image

    if image.ndim == 3 and image.shape[2] == 1:
        return image[:, :, 0]

    if image.ndim == 3 and image.shape[2] == 3:
        return image

    raise ValueError(
        f"Unsupported image shape: {image.shape}"
    )


def _calculate_statistics(
    keypoints0: np.ndarray,
    keypoints1: np.ndarray,
    confidence: np.ndarray,
):
    dx = keypoints1[:, 0] - keypoints0[:, 0]
    dy = keypoints1[:, 1] - keypoints0[:, 1]

    displacement = np.sqrt(
        dx ** 2 + dy ** 2
    )

    return {
        "dx": dx,
        "dy": dy,
        "displacement": displacement,
        "confidence_min": float(np.min(confidence)),
        "confidence_max": float(np.max(confidence)),
        "confidence_mean": float(np.mean(confidence)),
        "confidence_median": float(np.median(confidence)),
        "dx_mean": float(np.mean(dx)),
        "dy_mean": float(np.mean(dy)),
        "displacement_mean": float(
            np.mean(displacement)
        ),
        "displacement_median": float(
            np.median(displacement)
        ),
        "displacement_min": float(
            np.min(displacement)
        ),
        "displacement_max": float(
            np.max(displacement)
        ),
    }


def render_loftr_results(
    image0: np.ndarray,
    image1: np.ndarray,
    result: LoFTRResult,
    ransac_result: RANSACResult,
) -> None:

    st.header("LoFTR Matching Results")

    keypoints0 = np.asarray(
        result.keypoints0,
        dtype=np.float32,
    )

    keypoints1 = np.asarray(
        result.keypoints1,
        dtype=np.float32,
    )

    confidence = np.asarray(
        result.confidence,
        dtype=np.float32,
    )

    total_matches = len(confidence)

    if not (
        len(keypoints0)
        == len(keypoints1)
        == len(confidence)
    ):
        st.error(
            "LoFTR result contains inconsistent "
            "numbers of keypoints and confidence values."
        )
        return

    if total_matches == 0:
        st.warning("LoFTR returned zero matches.")
        return

    if len(ransac_result.inlier_mask) != total_matches:
        st.error(
            "RANSAC result is inconsistent with "
            "the LoFTR correspondence count."
        )
        return

    stats = _calculate_statistics(
        keypoints0,
        keypoints1,
        confidence,
    )

    st.subheader("RANSAC Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "LoFTR Matches",
            ransac_result.num_input_matches,
        )

    with col2:
        st.metric(
            "RANSAC Inliers",
            ransac_result.num_inliers,
        )

    with col3:
        st.metric(
            "RANSAC Outliers",
            ransac_result.num_outliers,
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "Inlier Ratio",
            f"{ransac_result.inlier_ratio:.2%}",
        )

    with col5:
        st.metric(
            "Outlier Ratio",
            f"{ransac_result.outlier_ratio:.2%}",
        )

    with col6:
        st.metric(
            "RANSAC Threshold",
            f"{ransac_result.config.reprojection_threshold:.2f} px"
            if hasattr(ransac_result, "config")
            else "3.00 px",
        )

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Mean Reprojection Error",
            f"{ransac_result.mean_reprojection_error:.4f} px",
        )

    with col8:
        st.metric(
            "Median Reprojection Error",
            f"{ransac_result.median_reprojection_error:.4f} px",
        )

    with col9:
        st.metric(
            "RMSE",
            f"{ransac_result.rmse:.4f} px",
        )

    st.caption(
        "RANSAC inliers are geometrically consistent "
        "with the estimated homography. Only inliers "
        "are shown in the correspondence visualization."
    )

    inlier_mask = np.asarray(
        ransac_result.inlier_mask,
        dtype=bool,
    )

    inlier_keypoints0 = keypoints0[
        inlier_mask
    ]

    inlier_keypoints1 = keypoints1[
        inlier_mask
    ]

    inlier_confidence = confidence[
        inlier_mask
    ]

    inlier_matches = len(
        inlier_confidence
    )

    st.subheader("Match Filtering")

    threshold = st.slider(
        "Minimum confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
    )

    mask = (
        inlier_confidence
        >= threshold
    )

    filtered_keypoints0 = (
        inlier_keypoints0[mask]
    )

    filtered_keypoints1 = (
        inlier_keypoints1[mask]
    )

    filtered_confidence = (
        inlier_confidence[mask]
    )

    filtered_matches = len(
        filtered_confidence
    )

    sort_order = np.argsort(
        filtered_confidence
    )[::-1]

    filtered_keypoints0 = (
        filtered_keypoints0[sort_order]
    )

    filtered_keypoints1 = (
        filtered_keypoints1[sort_order]
    )

    filtered_confidence = (
        filtered_confidence[sort_order]
    )

    st.subheader("Visualization Limit")

    max_display = st.slider(
        "Maximum matches per page",
        min_value=100,
        max_value=2000,
        value=100,
        step=100,
    )

    if (
        "loftr_page_start"
        not in st.session_state
    ):
        st.session_state.loftr_page_start = 0

    max_page_start = max(
        0,
        (
            (filtered_matches - 1)
            // max_display
        ) * max_display,
    )

    if (
        st.session_state.loftr_page_start
        > max_page_start
    ):
        st.session_state.loftr_page_start = (
            max_page_start
        )

    page_start = (
        st.session_state.loftr_page_start
    )

    page_end = min(
        page_start + max_display,
        filtered_matches,
    )

    st.write(
        f"Showing RANSAC inliers "
        f"**{page_start + 1}–{page_end}** "
        f"of **{filtered_matches}** "
        f"filtered inliers."
    )

    previous_col, next_col, page_col = (
        st.columns([1, 1, 2])
    )

    with previous_col:

        if st.button(
            "← Previous",
            disabled=(page_start == 0),
            use_container_width=True,
        ):
            st.session_state.loftr_page_start = (
                max(
                    0,
                    page_start - max_display,
                )
            )
            st.rerun()

    with next_col:

        if st.button(
            "Next →",
            disabled=(
                page_end >= filtered_matches
            ),
            use_container_width=True,
        ):
            st.session_state.loftr_page_start = (
                min(
                    page_start + max_display,
                    max_page_start,
                )
            )
            st.rerun()

    with page_col:

        current_page = (
            page_start // max_display
        ) + 1

        total_pages = max(
            1,
            int(
                np.ceil(
                    filtered_matches
                    / max_display
                )
            ),
        )

        st.info(
            f"Page {current_page} / {total_pages}"
        )

    page_keypoints0 = filtered_keypoints0[
        page_start:page_end
    ]

    page_keypoints1 = filtered_keypoints1[
        page_start:page_end
    ]

    page_confidence = filtered_confidence[
        page_start:page_end
    ]

    st.subheader("Match Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total LoFTR Matches",
            total_matches,
        )

    with col2:
        st.metric(
            "RANSAC Inliers",
            inlier_matches,
        )

    with col3:
        st.metric(
            "After Confidence Filter",
            filtered_matches,
        )

    with col4:
        st.metric(
            "Displayed",
            len(page_confidence),
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            "Mean Confidence",
            f"{stats['confidence_mean']:.3f}",
        )

    with col6:
        st.metric(
            "Median Confidence",
            f"{stats['confidence_median']:.3f}",
        )

    with col7:
        st.metric(
            "Maximum Confidence",
            f"{stats['confidence_max']:.3f}",
        )

    with col8:

        percentage = (
            filtered_matches
            / inlier_matches
            * 100.0
            if inlier_matches > 0
            else 0.0
        )

        st.metric(
            "Inliers Kept",
            f"{percentage:.1f}%",
        )

    st.subheader(
        "Correspondence Statistics"
    )

    st.caption(
        "These values describe the relative coordinates "
        "of all LoFTR correspondences. They are not "
        "accuracy measurements."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mean ΔX",
            f"{stats['dx_mean']:.2f} px",
        )

    with col2:
        st.metric(
            "Mean ΔY",
            f"{stats['dy_mean']:.2f} px",
        )

    with col3:
        st.metric(
            "Mean Displacement",
            f"{stats['displacement_mean']:.2f} px",
        )

    with col4:
        st.metric(
            "Median Displacement",
            f"{stats['displacement_median']:.2f} px",
        )

    st.subheader(
        "Confidence Distribution"
    )

    fig_hist, ax_hist = plt.subplots(
        figsize=(9, 3.5)
    )

    ax_hist.hist(
        confidence,
        bins=20,
        range=(0.0, 1.0),
        edgecolor="black",
    )

    ax_hist.axvline(
        threshold,
        linestyle="--",
        linewidth=1.5,
        label=f"Threshold = {threshold:.2f}",
    )

    ax_hist.set_xlabel(
        "LoFTR Confidence"
    )

    ax_hist.set_ylabel(
        "Number of Matches"
    )

    ax_hist.set_title(
        "LoFTR Match Confidence Distribution"
    )

    ax_hist.set_xlim(
        0.0,
        1.0,
    )

    ax_hist.legend()

    st.pyplot(
        fig_hist,
        clear_figure=True,
    )

    st.subheader(
        "Correspondence Coordinates"
    )

    page_dx = (
        page_keypoints1[:, 0]
        - page_keypoints0[:, 0]
    )

    page_dy = (
        page_keypoints1[:, 1]
        - page_keypoints0[:, 1]
    )

    page_displacement = np.sqrt(
        page_dx ** 2
        + page_dy ** 2
    )

    match_ids = np.arange(
        page_start + 1,
        page_end + 1,
    )

    coordinate_data = {
        "Match ID": match_ids,

        "Reference X": np.round(
            page_keypoints0[:, 0],
            2,
        ),

        "Reference Y": np.round(
            page_keypoints0[:, 1],
            2,
        ),

        "Moving X": np.round(
            page_keypoints1[:, 0],
            2,
        ),

        "Moving Y": np.round(
            page_keypoints1[:, 1],
            2,
        ),

        "LoFTR Confidence": np.round(
            page_confidence,
            4,
        ),

        "ΔX": np.round(
            page_dx,
            2,
        ),

        "ΔY": np.round(
            page_dy,
            2,
        ),

        "Displacement (px)": np.round(
            page_displacement,
            2,
        ),
    }

    st.dataframe(
        coordinate_data,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(
        "Correspondence Visualization"
    )

    if len(page_confidence) == 0:
        st.warning(
            "No RANSAC inliers satisfy the selected "
            "confidence threshold."
        )
        return

    img0 = _prepare_image(image0)
    img1 = _prepare_image(image1)

    h0, w0 = img0.shape[:2]
    h1, w1 = img1.shape[:2]

    canvas_height = max(
        h0,
        h1,
    )

    gap = 80

    canvas_width = (
        w0 + gap + w1
    )

    if np.issubdtype(
        img0.dtype,
        np.integer,
    ):
        background_value = np.iinfo(
            img0.dtype
        ).max
    else:
        background_value = 1.0

    if img0.ndim == 2:

        canvas = np.full(
            (
                canvas_height,
                canvas_width,
            ),
            background_value,
            dtype=img0.dtype,
        )

    else:

        canvas = np.full(
            (
                canvas_height,
                canvas_width,
                3,
            ),
            background_value,
            dtype=img0.dtype,
        )

    canvas[
        :h0,
        :w0
    ] = img0

    moving_x_start = (
        w0 + gap
    )

    canvas[
        :h1,
        moving_x_start:
        moving_x_start + w1
    ] = img1

    fig, ax = plt.subplots(
        figsize=(18, 9)
    )

    ax.imshow(
        canvas,
        cmap=(
            "gray"
            if canvas.ndim == 2
            else None
        ),
    )

    for point0, point1, conf in zip(
        page_keypoints0,
        page_keypoints1,
        page_confidence,
    ):

        x0, y0 = point0
        x1, y1 = point1

        x1_canvas = (
            x1 + moving_x_start
        )

        color = _confidence_to_color(
            conf
        )

        ax.plot(
            [x0, x1_canvas],
            [y0, y1],
            color=color,
            linewidth=0.35,
            alpha=0.65,
        )

        ax.scatter(
            [x0, x1_canvas],
            [y0, y1],
            color=color,
            s=5,
            alpha=0.95,
            linewidths=0,
        )

    ax.axvline(
        w0 + gap / 2,
        linestyle="--",
        linewidth=0.8,
        alpha=0.8,
    )

    ax.text(
        w0 / 2,
        20,
        "REFERENCE",
        ha="center",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            facecolor="white",
            alpha=0.75,
            edgecolor="none",
        ),
    )

    ax.text(
        moving_x_start + w1 / 2,
        20,
        "MOVING",
        ha="center",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            facecolor="white",
            alpha=0.75,
            edgecolor="none",
        ),
    )

    ax.set_title(
        (
            "RANSAC Inlier Correspondences "
            f"({page_start + 1}–{page_end})"
        ),
        fontsize=14,
    )

    ax.axis("off")

    st.pyplot(
        fig,
        clear_figure=True,
    )

    st.markdown(
        """
        **Confidence color**

        🔴 Low confidence  
        🟡 Medium confidence  
        🟢 High confidence
        """
    )

    st.info(
        "The visualization contains only RANSAC inliers. "
        "LoFTR outliers are excluded from the image view. "
        "The confidence filter and page limit only control "
        "which inliers are displayed."
    )


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
    config: object
