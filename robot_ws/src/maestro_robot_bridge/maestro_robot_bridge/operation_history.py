from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import datetime, timezone

from .models import OperationRecord


MAX_OPERATION_RECORDS = 100


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


class OperationHistory:
    """Ephemeral history of successful simulated spray arrivals."""

    def __init__(self, timestamp: Callable[[], str] = _utc_timestamp):
        self._timestamp = timestamp
        self._records: deque[OperationRecord] = deque(
            maxlen=MAX_OPERATION_RECORDS
        )

    def record_navigation_completion(
        self,
        *,
        succeeded: bool,
        command_id: str,
        plot_id: str,
    ) -> OperationRecord | None:
        if not succeeded:
            return None

        existing = next(
            (record for record in self._records if record.operation_id == command_id),
            None,
        )
        if existing is not None:
            return existing

        record = OperationRecord(
            schema_version="1.0",
            operation_id=command_id,
            kind="SIMULATED_SPRAY_ARRIVAL",
            plot_id=plot_id,
            completed_at=self._timestamp(),
            origin="GAZEBO_SIMULATOR",
        )
        self._records.append(record)
        return record

    def records(self) -> tuple[OperationRecord, ...]:
        return tuple(self._records)
