from __future__ import annotations

import json
from threading import Thread

from websockets.sync.server import Server, ServerConnection, serve

from .bridge_core import BridgeCore


class BridgeWebSocketServer:
    def __init__(self, core: BridgeCore, host: str, port: int):
        self._core = core
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
            response = self._core.handle(message)
            connection.send(json.dumps(response.to_dict(), separators=(",", ":")))
