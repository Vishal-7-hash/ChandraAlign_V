import csv
import io

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.logs import ExecutionLog
from app.services.logs import get_execution, list_executions


router = APIRouter(prefix="/logs", tags=["Execution Logs"])


@router.get(
    "",
    response_model=list[ExecutionLog],
    summary="List pipeline execution logs",
)
def execution_logs() -> list[ExecutionLog]:
    return list_executions()


@router.get(
    "/{job_id}/download",
    summary="Download an execution log",
)
def download_execution_log(job_id: str) -> StreamingResponse:
    log = get_execution(job_id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution log '{job_id}' was not found.",
        )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "timestamp", "status", "rmse", "time", "error"],
    )
    writer.writeheader()
    writer.writerow(log.model_dump())
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{job_id}.csv"',
        },
    )
