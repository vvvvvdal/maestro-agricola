from __future__ import annotations

from .models import ReadOnlyOperationSummary, ReadOnlyResponse
from .operation_history import OperationHistory
from .read_only_contract import (
    LAST_SIMULATED_SPRAY_FOR_PLOT,
    ReadOnlyContractError,
    SCHEMA_VERSION,
    parse_read_only_query,
)
from .target_map import TargetMap


class ReadOnlyQueryService:
    def __init__(self, target_map: TargetMap, operation_history: OperationHistory):
        self._target_map = target_map
        self._operation_history = operation_history

    def handle(self, raw_message: str) -> ReadOnlyResponse:
        try:
            query = parse_read_only_query(raw_message)
        except ReadOnlyContractError as exc:
            return ReadOnlyResponse(
                schema_version=SCHEMA_VERSION,
                request_id=exc.request_id,
                kind=LAST_SIMULATED_SPRAY_FOR_PLOT,
                status="INVALID_QUERY",
            )

        if self._target_map.get(query.plot_id) is None:
            return ReadOnlyResponse(
                schema_version=SCHEMA_VERSION,
                request_id=query.request_id,
                kind=query.kind,
                status="INVALID_QUERY",
            )

        record = self._operation_history.latest_for_plot(query.plot_id)
        return ReadOnlyResponse(
            schema_version=SCHEMA_VERSION,
            request_id=query.request_id,
            kind=query.kind,
            status="FOUND" if record is not None else "NOT_FOUND",
            record=(
                ReadOnlyOperationSummary(
                    plot_id=record.plot_id,
                    completed_at=record.completed_at,
                    origin=record.origin,
                )
                if record is not None
                else None
            ),
        )
