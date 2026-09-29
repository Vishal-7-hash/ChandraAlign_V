from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.schemas.logs import ExecutionLog, LogStatus


_LOG_FILE = settings.TEMP_DIR / "execution_logs.json"
_LOCK = threading.Lock()
_MAX_LOGS = 1000


def record_execution(
    status: LogStatus,
    duration: float,
    rmse: float | None = None,
    error: str | None = None,
) -> ExecutionLog:
    log = ExecutionLog(
        id=f"JOB-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        status=status,
        rmse=rmse,
        time=round(duration, 4),
        error=error,
    )

    with _LOCK:
        logs = _read_logs()
        logs.insert(0, log)
        _write_logs(logs[:_MAX_LOGS])

    return log


def list_executions() -> list[ExecutionLog]:
    with _LOCK:
        return _read_logs()


def get_execution(job_id: str) -> ExecutionLog | None:
    return next(
        (log for log in list_executions() if log.id == job_id),
        None,
    )


def _read_logs() -> list[ExecutionLog]:
    if not _LOG_FILE.exists():
        return []

    try:
        data = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
        return [ExecutionLog.model_validate(item) for item in data]
    except (OSError, ValueError):
        return []


def _write_logs(logs: list[ExecutionLog]) -> None:
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _LOG_FILE.write_text(
        json.dumps([log.model_dump() for log in logs], indent=2),
        encoding="utf-8",
    )
