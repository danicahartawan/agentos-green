# -*- coding: utf-8 -*-
"""
AgentBeats tool implementations for the OSWorld green agent.

These helpers wrap the ``green_agent`` evaluator package so the hosted green
agent can trigger OSWorld task suites directly from an AgentBeats battle flow.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from time import perf_counter
from typing import List, Optional

from agentbeats import tool

from green_agent.config import Config
from green_agent.task_loader import load_tasks
from green_agent.white_agent_runner import build_white_agent
from green_agent.evaluator import GreenEvaluator

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASKS_JSON = PROJECT_ROOT / "green_tasks_5.json"
REPORTS_ROOT = PROJECT_ROOT / "reports"
RESULTS_ROOT = PROJECT_ROOT / "results"

logger = logging.getLogger(__name__)


def _resolve_path(path_str: Optional[str]) -> Optional[Path]:
    """Resolve a path relative to the project root."""
    if not path_str:
        return None
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _parse_domains(domains_csv: Optional[str]) -> Optional[List[str]]:
    """Parse a comma/space separated list of domains into a list."""
    if not domains_csv:
        return None
    parts = [p.strip() for chunk in domains_csv.split(",") for p in chunk.split()]
    return [p for p in parts if p]


@tool
async def run_osworld_suite(
    battle_id: str,
    white_agent_key: str = "naive_clicker",
    tasks_file: Optional[str] = None,
    domains: Optional[str] = None,
    repeats: int = 1,
    max_steps: int = 20,
    seed: int = 7,
) -> str:
    """
    Execute an OSWorld evaluation suite against a white agent.

    Args:
        battle_id: Unique battle identifier (used for report directory names)
        white_agent_key: Key understood by ``green_agent.white_agent_runner``
        tasks_file: Optional JSON file with curated task list
        domains: Optional comma/space separated domain filter
        repeats: Number of runs per task
        max_steps: Maximum interaction steps per task
        seed: Random seed for deterministic behaviour

    Returns:
        JSON string with summary metrics and per-task rows.
    """
    start = perf_counter()
    tasks_path = _resolve_path(tasks_file) if tasks_file else None
    if tasks_path is None and DEFAULT_TASKS_JSON.exists():
        tasks_path = DEFAULT_TASKS_JSON

    resolved_domains = _parse_domains(domains)

    report_dir = REPORTS_ROOT / "agentbeats" / battle_id / white_agent_key
    results_dir = RESULTS_ROOT / "agentbeats"
    report_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config(
        provider="docker",
        tasks_file=str(tasks_path) if tasks_path else None,
        domains=resolved_domains,
        repeats=repeats,
        max_steps=max_steps,
        seed=seed,
        white_agents=[white_agent_key],
        results_root=str(results_dir),
        reports_root=str(report_dir),
    )

    try:
        tasks = load_tasks(cfg.tasks_file, cfg.domains)
    except FileNotFoundError as err:
        payload = {
            "status": "error",
            "reason": "tasks_file_not_found",
            "detail": str(err),
            "tasks_file": str(tasks_path) if tasks_path else None,
            "hint": "Ensure OSWorld task assets are available (clone xlang-ai/OSWorld or supply a custom tasks_file).",
        }
        return json.dumps(payload, indent=2)

    if not tasks:
        payload = {
            "status": "error",
            "reason": "no_tasks_loaded",
            "tasks_file": str(tasks_path) if tasks_path else None,
            "domains": resolved_domains,
        }
        return json.dumps(payload, indent=2)

    evaluator = GreenEvaluator(cfg)
    agent = build_white_agent(white_agent_key, seed=seed)

    try:
        summary, per_task = evaluator.run_suite(
            white_agent_key, agent, tasks, repeats=cfg.repeats
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("OSWorld evaluation failed: %s", exc)
        payload = {
            "status": "error",
            "reason": "evaluation_failed",
            "detail": str(exc),
        }
        return json.dumps(payload, indent=2)

    elapsed = perf_counter() - start

    payload = {
        "status": "ok",
        "battle_id": battle_id,
        "white_agent": white_agent_key,
        "tasks_file": str(tasks_path) if tasks_path else None,
        "domains": resolved_domains,
        "repeats": repeats,
        "max_steps": max_steps,
        "seed": seed,
        "summary": summary,
        "per_task": per_task,
        "reports_dir": str(report_dir),
        "results_dir": str(results_dir),
        "elapsed_seconds": round(elapsed, 3),
    }
    return json.dumps(payload, indent=2)


@tool
async def list_osworld_tasks(
    tasks_file: Optional[str] = None,
    domains: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Enumerate OSWorld tasks available to this deployment.

    Args:
        tasks_file: Optional curated task list (defaults to green_tasks_5.json)
        domains: Optional domain filter (comma/space separated)
        limit: Maximum number of tasks to return (0 → all)

    Returns:
        JSON with task ids/domains/example paths for quick preview.
    """
    tasks_path = _resolve_path(tasks_file) if tasks_file else None
    if tasks_path is None and DEFAULT_TASKS_JSON.exists():
        tasks_path = DEFAULT_TASKS_JSON

    resolved_domains = _parse_domains(domains)
    try:
        tasks = load_tasks(
            str(tasks_path) if tasks_path else None, resolved_domains
        )
    except FileNotFoundError as err:
        payload = {
            "status": "error",
            "reason": "tasks_file_not_found",
            "detail": str(err),
            "tasks_file": str(tasks_path) if tasks_path else None,
            "hint": "Ensure OSWorld task assets are available (clone xlang-ai/OSWorld or supply a custom tasks_file).",
        }
        return json.dumps(payload, indent=2)

    if limit > 0:
        tasks = tasks[:limit]

    payload = {
        "status": "ok",
        "tasks_file": str(tasks_path) if tasks_path else None,
        "domains": resolved_domains,
        "count": len(tasks),
        "tasks": [
            {
                "id": t["id"],
                "domain": t["domain"],
                "example_path": t.get("example_path"),
                "fallback_check": t.get("fallback_check"),
            }
            for t in tasks
        ],
    }
    return json.dumps(payload, indent=2)
