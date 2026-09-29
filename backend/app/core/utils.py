import base64
import os
import uuid
import logging
from pathlib import Path
import cv2
import numpy as np
from fastapi import UploadFile, HTTPException, status
from app.config import settings

logger = logging.getLogger(__name__)

async def save_upload_file_tmp(upload_file: UploadFile, expected_ext: set[str]) -> Path:
    """
    Saves an uploaded file to the temporary directory with a unique UUID filename.
    Validates file extension and size constraints.
    """
    filename = upload_file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in expected_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}' for file '{filename}'. Expected one of {expected_ext}"
        )

    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = settings.TEMP_DIR / unique_filename

    try:
        content = await upload_file.read()
        
        # Check size constraint
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )

        with open(file_path, "wb") as f:
            f.write(content)
            
        logger.info(f"Saved file {filename} -> {file_path}")
        return file_path
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Failed to save uploaded file '{filename}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file '{filename}' to disk."
        )

def encode_image_to_base64(img: np.ndarray, file_format: str = ".png") -> str:
    """
    Encodes an OpenCV image array (BGR/Grayscale) to a base64 string.
    """
    success, buffer = cv2.imencode(file_format, img)
    if not success:
        raise ValueError("Failed to encode image to buffer")
    return base64.b64encode(buffer).decode("utf-8")

def cleanup_files(file_paths: list[Path]) -> None:
    """
    Safely removes temporary files from disk.
    """
    for path in file_paths:
        try:
            if path and path.exists():
                os.remove(path)
                logger.info(f"Cleaned up temp file: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {path}: {str(e)}")