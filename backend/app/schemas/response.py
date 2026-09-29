from typing import Any

from pydantic import BaseModel, Field

class MatchResponse(BaseModel):
    match_image: str = Field(..., description="Base64 encoded string of feature keypoint match visualization")
    aligned_image: str = Field(..., description="Base64 encoded string of final registered/aligned image")
    rmse: float = Field(..., description="Root Mean Square Error of image registration in pixels")
    inlier_ratio: float = Field(..., description="Ratio of feature matching inliers (0.0 to 1.0)")
    compute_time: float = Field(..., description="Pipeline processing duration in seconds")
    match_details: dict[str, Any] | None = Field(
        default=None,
        description="Optional LoFTR and RANSAC data for detailed visualization",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "match_image": "iVBORw0KGgoAAAANSUhEUgAA...",
                "aligned_image": "iVBORw0KGgoAAAANSUhEUgAA...",
                "rmse": 0.1245,
                "inlier_ratio": 0.842,
                "compute_time": 1.432
            }
        }

class ErrorDetailResponse(BaseModel):
    detail: str