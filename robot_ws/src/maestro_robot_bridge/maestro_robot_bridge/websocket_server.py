from __future__ import annotations

import json
from threading import Thread

from websockets.sync.server import Server, ServerConnection, serve

from .bridge_core import BridgeCore
from .read_only_query_service import ReadOnlyQueryService


class BridgeWebSocketServer:
    def __init__(
        self,
        core: BridgeCore,
        read_only_query_service: ReadOnlyQueryService,
        host: str,
        port: int,
    ):
        self._core = core
        self._read_only_query_service = read_only_query_service
        self._host = host
        self._port = port
        self._server: Server | None = None
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._server is not None:
            return
        self._server = serve(self._handle_connection, self._host, self._port)
        self._thread = Thread(target=self._server.serve_forever, name="maestro-websocket", daemon=True)
        self._thread.start()

    def close(self) -> None:
        if self._server is not None:
            self._server.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None

    def _handle_connection(self, connection: ServerConnection) -> None:
        for message in connection:
            response = self._response_for(connection.request.path, message)
            connection.send(json.dumps(response.to_dict(), separators=(",", ":")))

    def _response_for(self, path: str, message: str):
        if path == "/read-only":
            return self._read_only_query_service.handle(message)
        return self._core.handle(message)
