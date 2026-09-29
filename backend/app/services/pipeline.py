import time
import logging
from pathlib import Path
import sys

import cv2
import numpy as np

from app.core.loader import load_image, parse_xml_metadata
from app.core.utils import encode_image_to_base64

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from core.matching.loftr import LoFTRConfig, LoFTRMatcher
from core.preprocessing.resolution import resolution_resampling
from core.preprocessing.viewpoint import viewpoint_correction
from core.registration.ransac import RANSACConfig, RANSACRegistration

logger = logging.getLogger(__name__)

def run_pipeline(
    src_img_path: Path,
    src_xml_path: Path,
    ref_img_path: Path,
    ref_xml_path: Path
) -> dict:
    """
    Main Execution Pipeline for Lunar Image Alignment.

    1. Loads images and XML metadata
    2. Applies viewpoint and resolution preprocessing
    3. Computes LoFTR correspondences and RANSAC homography
    4. Generates match visualizations and aligned image output
    5. Calculates RMSE, inlier ratio, and execution time
    """
    start_time = time.perf_counter()

    # 1. Load resources & metadata
    logger.info("Pipeline Execution: Loading images & metadata...")
    src_img_raw = load_image(src_img_path)
    ref_img_raw = load_image(ref_img_path)

    src_meta = parse_xml_metadata(src_xml_path)
    ref_meta = parse_xml_metadata(ref_xml_path)

    # 2. Run the root preprocessing stages.
    viewpoint_source = viewpoint_correction(ref_img_raw, src_img_raw)
    ref_processed, src_processed = resolution_resampling(
        ref_img_raw,
        viewpoint_source,
        ref_xml_path,
        src_xml_path,
    )

    ref_gray = _to_grayscale(ref_processed)
    src_gray = _to_grayscale(src_processed)

    # 3. Match with LoFTR, falling back to SIFT if weights are unavailable.
    try:
        matcher = LoFTRMatcher(
            LoFTRConfig(
                pretrained="outdoor",
                device="auto",
                use_amp=False,
                confidence_threshold=None,
            )
        )
        match_result = matcher.match(ref_gray, src_gray)
        reference_points = match_result.keypoints0
        source_points = match_result.keypoints1
        confidence = match_result.confidence
        matcher_name = "LoFTR"
    except Exception as exc:
        logger.warning(
            "LoFTR unavailable (%s). Falling back to SIFT matching.",
            exc,
        )
        reference_points, source_points = _sift_matches(ref_gray, src_gray)
        confidence = np.ones(len(reference_points), dtype=np.float32)
        matcher_name = "SIFT fallback"

    ransac_result = None
    if len(reference_points) >= 4:
        ransac_result = RANSACRegistration(
            RANSACConfig(
                reprojection_threshold=3.0,
                confidence=0.995,
                max_iterations=2000,
                min_matches=4,
            )
        ).estimate(reference_points, source_points)

    h_ref, w_ref = ref_processed.shape[:2]
    aligned_img_out = src_processed
    if ransac_result is not None:
        aligned_img_out = cv2.warpPerspective(
            src_processed,
            ransac_result.homography,
            (w_ref, h_ref),
        )

    match_img_out = _draw_matches(
        ref_gray,
        src_gray,
        reference_points,
        source_points,
        None if ransac_result is None else ransac_result.inlier_mask,
    )

    rmse = 0.0 if ransac_result is None else round(ransac_result.rmse, 4)
    inlier_ratio = 0.0 if ransac_result is None else round(ransac_result.inlier_ratio, 4)

    # 4. Encode images to Base64 strings
    match_b64 = encode_image_to_base64(match_img_out)
    aligned_b64 = encode_image_to_base64(aligned_img_out)

    compute_time = round(time.perf_counter() - start_time, 4)
    logger.info(f"Pipeline Execution Complete in {compute_time}s | RMSE: {rmse} | Inliers: {inlier_ratio}")

    match_details = {
        "matcher": matcher_name,
        "keypoints0": reference_points.tolist(),
        "keypoints1": source_points.tolist(),
        "confidence": confidence.tolist(),
        "image0_shape": list(ref_gray.shape),
        "image1_shape": list(src_gray.shape),
        "num_input_matches": int(len(reference_points)),
        "num_inliers": 0 if ransac_result is None else ransac_result.num_inliers,
        "num_outliers": 0 if ransac_result is None else ransac_result.num_outliers,
        "inlier_ratio": inlier_ratio,
        "outlier_ratio": 0.0 if ransac_result is None else round(ransac_result.outlier_ratio, 4),
        "inlier_mask": [] if ransac_result is None else ransac_result.inlier_mask.astype(bool).tolist(),
        "reprojection_errors": [] if ransac_result is None else ransac_result.reprojection_errors.tolist(),
        "mean_reprojection_error": 0.0 if ransac_result is None else ransac_result.mean_reprojection_error,
        "median_reprojection_error": 0.0 if ransac_result is None else ransac_result.median_reprojection_error,
        "rmse": rmse,
    }

    return {
        "match_image": match_b64,
        "aligned_image": aligned_b64,
        "rmse": rmse,
        "inlier_ratio": inlier_ratio,
        "compute_time": compute_time,
        "match_details": match_details,
    }


def _sift_matches(
    reference: np.ndarray,
    source: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    detector = cv2.SIFT_create(nfeatures=5000)
    reference_keypoints, reference_descriptors = detector.detectAndCompute(
        reference,
        None,
    )
    source_keypoints, source_descriptors = detector.detectAndCompute(
        source,
        None,
    )

    empty = np.empty((0, 2), dtype=np.float32)
    if reference_descriptors is None or source_descriptors is None:
        return empty, empty.copy()

    matcher = cv2.BFMatcher(cv2.NORM_L2)
    candidate_matches = matcher.knnMatch(
        reference_descriptors,
        source_descriptors,
        k=2,
    )
    good_matches = [
        first
        for pair in candidate_matches
        if len(pair) == 2
        for first, second in [pair]
        if first.distance < 0.75 * second.distance
    ]

    return (
        np.asarray(
            [reference_keypoints[match.queryIdx].pt for match in good_matches],
            dtype=np.float32,
        ).reshape(-1, 2),
        np.asarray(
            [source_keypoints[match.trainIdx].pt for match in good_matches],
            dtype=np.float32,
        ).reshape(-1, 2),
    )


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        grayscale = image
    elif image.shape[2] == 4:
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else:
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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


def _draw_matches(
    reference: np.ndarray,
    source: np.ndarray,
    reference_points: np.ndarray,
    source_points: np.ndarray,
    inlier_mask: np.ndarray | None,
) -> np.ndarray:
    reference_bgr = cv2.cvtColor(reference, cv2.COLOR_GRAY2BGR)
    source_bgr = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
    height = max(reference_bgr.shape[0], source_bgr.shape[0])
    canvas = np.zeros((height, reference_bgr.shape[1] + source_bgr.shape[1], 3), dtype=np.uint8)
    canvas[:reference_bgr.shape[0], :reference_bgr.shape[1]] = reference_bgr
    source_offset = reference_bgr.shape[1]
    canvas[:source_bgr.shape[0], source_offset:] = source_bgr

    limit = min(len(reference_points), 50)
    for index in range(limit):
        if inlier_mask is not None and not inlier_mask[index]:
            color = (90, 90, 90)
        else:
            color = (0, 220, 200)
        ref_point = tuple(np.round(reference_points[index]).astype(int))
        src_point = tuple(np.round(source_points[index]).astype(int))
        shifted_source = (src_point[0] + source_offset, src_point[1])
        cv2.circle(canvas, ref_point, 3, color, -1)
        cv2.circle(canvas, shifted_source, 3, color, -1)
        cv2.line(canvas, ref_point, shifted_source, color, 1)

    return canvas