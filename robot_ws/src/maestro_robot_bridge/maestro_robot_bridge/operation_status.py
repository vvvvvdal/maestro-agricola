from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock

from .models import Command


QUEUED = "QUEUED"
EXECUTING = "EXECUTING"
COMPLETED = "COMPLETED"
FAILED = "FAILED"
TERMINAL_STATES = {COMPLETED, FAILED}


@dataclass(frozen=True)
class OperationStatus:
    command_id: str
    intent: str
    target_id: str | None
    state: str


class OperationStatusTracker:
    """In-memory status for commands already accepted by the bridge."""

    def __init__(self, max_records: int = 100) -> None:
        self._max_records = max_records
        self._records: OrderedDict[str, OperationStatus] = OrderedDict()
        self._lock = Lock()

    def accepted(self, command: Command) -> None:
        self._set(
            OperationStatus(
                command_id=command.command_id,
                intent=command.intent,
                target_id=command.target.id if command.target is not None else None,
                state=QUEUED,
            )
        )

    def executing(self, command_id: str) -> None:
        self._transition(command_id, EXECUTING)

    def completed(self, command_id: str) -> None:
        self._transition(command_id, COMPLETED)

    def failed(self, command_id: str) -> None:
        self._transition(command_id, FAILED)

    def executing_latest(self, intent: str) -> None:
        self._transition_latest(intent, EXECUTING)

    def completed_latest(self, intent: str) -> None:
        self._transition_latest(intent, COMPLETED)

    def fail_in_flight(self) -> None:
        with self._lock:
            for command_id, record in tuple(self._records.items()):
                if record.state not in TERMINAL_STATES:
                    self._records[command_id] = OperationStatus(
                        command_id=record.command_id,
                        intent=record.intent,
                        target_id=record.target_id,
                        state=FAILED,
                    )

    def get(self, command_id: str) -> OperationStatus | None:
        with self._lock:
            record = self._records.get(command_id)
            if record is not None:
                self._records.move_to_end(command_id)
            return record

    def latest(self) -> OperationStatus | None:
        with self._lock:
            return next(reversed(self._records.values()), None)

    def _transition(self, command_id: str, state: str) -> None:
        with self._lock:
            record = self._records.get(command_id)
            if record is None:
                return
            self._records[command_id] = OperationStatus(
                command_id=record.command_id,
                intent=record.intent,
                target_id=record.target_id,
                state=state,
            )
            self._records.move_to_end(command_id)

    def _transition_latest(self, intent: str, state: str) -> None:
        with self._lock:
            for command_id, record in reversed(self._records.items()):
                if record.intent == intent and record.state not in TERMINAL_STATES:
                    self._records[command_id] = OperationStatus(
                        command_id=record.command_id,
                        intent=record.intent,
                        target_id=record.target_id,
                        state=state,
                    )
                    self._records.move_to_end(command_id)
                    return

    def _set(self, record: OperationStatus) -> None:
        with self._lock:
            self._records[record.command_id] = record
            self._records.move_to_end(record.command_id)
            while len(self._records) > self._max_records:
                self._records.popitem(last=False)
