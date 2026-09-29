import cv2
import numpy as np

def convert_to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Converts image to single-channel grayscale if needed.
    """
    if len(img.shape) == 2:
        return img  # Already grayscale
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    raise ValueError(f"Unsupported image shape for grayscale conversion: {img.shape}")

def normalize_image(img: np.ndarray) -> np.ndarray:
    """
    Performs min-max contrast normalization for feature extraction consistency.
    """
    return cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)