# -*- coding: utf-8 -*-
"""
Minimal MCP server exposing logging helpers for the OSWorld scenario.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from fastmcp import FastMCP


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
LOGGER.addHandler(handler)
LOGGER.propagate = False


BACKEND_URL = "http://localhost:9000"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"

server = FastMCP(
    "OSWorld Battle MCP",
    host="0.0.0.0",
    port=9101,
)


def _write_local_log(battle_id: str, message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{timestamp}] {battle_id}: {message}\n"
    with open(LOG_DIR / f"{battle_id}.log", "a", encoding="utf-8") as handle:
        handle.write(line)


@server.tool()
def update_battle_process(
    battle_id: str,
    message: str,
    reported_by: str,
    detail: Optional[Dict[str, Any]] = None,
    markdown_content: Optional[str] = None,
) -> str:
    """
    Report an interim battle status update to the AgentBeats backend.

    Falls back to local logging if the backend is unreachable.
    """
    event_data: Dict[str, Any] = {
        "is_result": False,
        "message": message,
        "reported_by": reported_by,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if detail:
        event_data["detail"] = detail
    if markdown_content:
        event_data["markdown_content"] = markdown_content

    try:
        response = requests.post(
            f"{BACKEND_URL}/battles/{battle_id}",
            json=event_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 204:
            LOGGER.info("Logged update for battle %s", battle_id)
            return "logged to backend"
        LOGGER.error(
            "Backend rejected update for battle %s: %s",
            battle_id,
            response.text,
        )
    except requests.exceptions.RequestException as exc:
        LOGGER.error("Backend logging error for battle %s: %s", battle_id, exc)

    _write_local_log(battle_id, message)
    return "logged locally"


@server.tool()
def store_battle_artifact(
    battle_id: str,
    filename: str,
    payload: Dict[str, Any],
) -> str:
    """
    Persist a JSON payload for later inspection.

    Useful when the green agent wants to retain evaluation reports alongside
    backend updates.
    """
    artifact_dir = LOG_DIR / battle_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / filename
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    LOGGER.info("Stored artifact %s for battle %s", path, battle_id)
    return str(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the OSWorld MCP server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9101,
        help="Port to bind the MCP server (default: 9101).",
    )
    args = parser.parse_args()

    server.run(
        transport="sse",
        host="0.0.0.0",
        port=args.port,
        log_level="ERROR",
    )
