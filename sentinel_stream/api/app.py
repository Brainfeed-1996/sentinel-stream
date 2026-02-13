from __future__ import annotations

from fastapi import FastAPI

from ..config import Settings
from ..storage.sqlite import SQLiteStorage


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="sentinel-stream", version="0.2.0")

    storage = SQLiteStorage(settings.sqlite_path)
    storage.setup()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/detections")
    def detections(limit: int = 100) -> list[dict]:
        limit = max(1, min(limit, 1000))
        return storage.get_detections(limit=limit)

    return app
