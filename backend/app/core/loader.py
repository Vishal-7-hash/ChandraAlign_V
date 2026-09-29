import xml.etree.ElementTree as ET
import logging
from pathlib import Path
import cv2
import numpy as np
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def load_image(image_path: Path) -> np.ndarray:
    """
    Loads an image from disk using OpenCV.
    Raises an exception if the file cannot be read.
    """
    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image file not found at {image_path}"
        )
        
    img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if img is None or img.size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to decode image from path: {image_path.name}"
        )
        
    return img

def parse_xml_metadata(xml_path: Path) -> dict:
    """
    Parses lunar mission XML metadata.
    Returns extracted metadata dictionary or default values if structure is custom.
    """
    if not xml_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"XML metadata file not found at {xml_path}"
        )

    metadata = {
        "sensor": "Lunar Orbital Camera",
        "sun_elevation": 45.0,
        "resolution_m_per_px": 0.5,
    }

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Parse key elements if present
        sensor_elem = root.find("Sensor")
        if sensor_elem is not None and sensor_elem.text:
            metadata["sensor"] = sensor_elem.text

        resolution_elem = root.find("Resolution")
        if resolution_elem is not None and resolution_elem.text:
            metadata["resolution_m_per_px"] = float(resolution_elem.text)

    except ET.ParseError as e:
        logger.warning(f"XML parse warning for {xml_path.name}: {str(e)}. Using fallback metadata.")
    except Exception as e:
        logger.warning(f"Failed reading XML {xml_path.name}: {str(e)}")

    return metadata