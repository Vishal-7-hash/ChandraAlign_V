from typing import Literal

from pydantic import BaseModel, Field


LogStatus = Literal["SUCCESS", "FAILED"]


class ExecutionLog(BaseModel):
    id: str = Field(..., description="Unique pipeline job identifier")
    timestamp: str = Field(..., description="UTC execution timestamp")
    status: LogStatus
    rmse: float | None = Field(None, description="Registration RMSE in pixels")
    time: float = Field(..., description="Execution duration in seconds")
    error: str | None = Field(None, description="Failure detail when available")
