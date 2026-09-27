from pathlib import Path
import sys

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.preprocessing.viewpoint import viewpoint_correction
from core.preprocessing.resolution import resolution_resampling
from core.matching.loftr import LoFTRConfig, LoFTRMatcher
from core.ui.loftr_viewer import render_loftr_results
from core.registration.ransac import (
    RANSACConfig,
    RANSACRegistration,
)


REFERENCE_PATH = (
    PROJECT_ROOT
    / "img_data"
    / "org_ref.jpeg"
)

SOURCE_PATH = (
    PROJECT_ROOT
    / "img_data"
    / "org_src.jpeg"
)

REFERENCE_XML = (
    PROJECT_ROOT
    / "img_data"
    / "reference"
)

SOURCE_XML = (
    PROJECT_ROOT
    / "img_data"
    / "source"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "img_data"
    / "op"
)

VIEWPOINT_OUTPUT_PATH = (
    OUTPUT_DIR
    / "viewpoint_output_src.png"
)

RESOLUTION_REFERENCE_OUTPUT_PATH = (
    OUTPUT_DIR
    / "resolution_output_reference.png"
)

RESOLUTION_SOURCE_OUTPUT_PATH = (
    OUTPUT_DIR
    / "resolution_output_src.png"
)


def load_image(path: Path):

    image = cv2.imread(
        str(path),
        cv2.IMREAD_UNCHANGED,
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {path}"
        )

    return image


def save_image(path: Path, image):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not cv2.imwrite(
        str(path),
        image,
    ):
        raise RuntimeError(
            f"Failed to save image: {path}"
        )


def create_matcher():

    config = LoFTRConfig(
        pretrained="outdoor",
        device="auto",
        use_amp=False,
        confidence_threshold=None,
    )

    return LoFTRMatcher(config)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


#loading
    print("\n=== LOAD ORIGINAL IMAGES ===")

    original_reference = load_image(
        REFERENCE_PATH
    )

    original_source = load_image(
        SOURCE_PATH
    )

    print(
        f"Reference: {original_reference.shape}"
    )

    print(
        f"Source: {original_source.shape}"
    )

#vc
    print("\n=== VIEWPOINT CORRECTION ===")

    viewpoint_source = viewpoint_correction(
        original_reference,
        original_source,
    )

    save_image(
        VIEWPOINT_OUTPUT_PATH,
        viewpoint_source,
    )

    print(
        f"Viewpoint output: {VIEWPOINT_OUTPUT_PATH}"
    )



#rr
    print("\n=== RESOLUTION RESAMPLING ===")

    resolution_reference, resolution_source = (
        resolution_resampling(
            original_reference,
            viewpoint_source,
            REFERENCE_XML,
            SOURCE_XML,
        )
    )

    save_image(
        RESOLUTION_REFERENCE_OUTPUT_PATH,
        resolution_reference,
    )

    save_image(
        RESOLUTION_SOURCE_OUTPUT_PATH,
        resolution_source,
    )

    print(
        f"Resolution reference output: "
        f"{RESOLUTION_REFERENCE_OUTPUT_PATH}"
    )

    print(
        f"Resolution source output: "
        f"{RESOLUTION_SOURCE_OUTPUT_PATH}"
    )





#loftr
    print("\n=== LOFTR MATCHING ===")

    matcher = create_matcher()

    gray_reference = cv2.cvtColor(
        resolution_reference,
        cv2.COLOR_BGR2GRAY,
    )

    gray_source = cv2.cvtColor(
        resolution_source,
        cv2.COLOR_BGR2GRAY,
    )

    result = matcher.match(
        image0=gray_reference,
        image1=gray_source,
    )

    print(
        f"LoFTR matches: {result.num_matches}"
    )

    print(
        f"Mean confidence: "
        f"{result.mean_confidence:.6f}"
    )

    print(
        f"Min confidence: "
        f"{result.min_confidence:.6f}"
    )

    print(
        f"Max confidence: "
        f"{result.max_confidence:.6f}"
    )

    print(
        f"Inference time: "
        f"{result.inference_time_ms:.2f} ms"
    )




#ransac
    print("\n=== RANSAC GEOMETRIC VERIFICATION ===")

    ransac = RANSACRegistration(
        RANSACConfig(
            reprojection_threshold=3.0,
            confidence=0.995,
            max_iterations=2000,
            min_matches=4,
        )
    )

    ransac_result = ransac.estimate(
        result.keypoints0,
        result.keypoints1,
    )

    print(
        f"Input matches: "
        f"{ransac_result.num_input_matches}"
    )

    print(
        f"Inliers: "
        f"{ransac_result.num_inliers}"
    )

    print(
        f"Outliers: "
        f"{ransac_result.num_outliers}"
    )

    print(
        f"Inlier ratio: "
        f"{ransac_result.inlier_ratio:.2%}"
    )

    print(
        f"Outlier ratio: "
        f"{ransac_result.outlier_ratio:.2%}"
    )

    print(
        f"Mean reprojection error: "
        f"{ransac_result.mean_reprojection_error:.4f} px"
    )

    print(
        f"Median reprojection error: "
        f"{ransac_result.median_reprojection_error:.4f} px"
    )

    print(
        f"RMSE: "
        f"{ransac_result.rmse:.4f} px"
    )

    print(
        "\nHomography:"
    )

    print(
        ransac_result.homography
    )










    print("\n=== MATCHING OUTPUT ===")

    print(
        "Reference points:",
        result.keypoints0.shape,
    )

    print(
        "Source points:",
        result.keypoints1.shape,
    )

    print(
        "Confidence:",
        result.confidence.shape,
    )

    print(
        "Combined matches:",
        result.matches.shape,
    )

    if result.num_matches > 0:

        print(
            "\nFirst 10 matches:"
        )

        print(
            result.matches[:10]
        )

    else:

        print(
            "\nLoFTR produced no correspondences."
        )


    render_loftr_results(
        image0=resolution_reference,
        image1=resolution_source,
        result=result,
        ransac_result=ransac_result,
    )


if __name__ == "__main__":
    main()
