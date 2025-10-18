"""
Reporter

Simple, dependency-free reporting.
Writes JSON/JSONL files and console tables.
"""

from __future__ import annotations
import json
import os
import time
from typing import Dict, Any, List, Tuple


def _ensure_dir(p: str):
    """Ensure directory exists."""
    os.makedirs(p, exist_ok=True)


def write_run_row(jsonl_path: str, row: Dict[str, Any]) -> None:
    """
    Append a row to JSONL file.
    
    Args:
        jsonl_path: Path to JSONL file
        row: Dictionary to write as JSON line
    """
    _ensure_dir(os.path.dirname(jsonl_path))
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_agent_summary(json_path: str, agent_name: str, summary: Dict[str, Any], per_task: List[Dict[str, Any]]) -> None:
    """
    Write agent summary JSON file.
    
    Args:
        json_path: Path to output JSON file
        agent_name: Name of the agent
        summary: Summary metrics dictionary
        per_task: List of per-task result dictionaries
    """
    _ensure_dir(os.path.dirname(json_path))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"name": agent_name, "summary": summary, "per_task": per_task}, f, indent=2)


def write_combined_report(json_path: str, config: Dict[str, Any], agent_summaries: List[Dict[str, Any]]) -> None:
    """
    Write combined report JSON file.
    
    Args:
        json_path: Path to output JSON file
        config: Configuration dictionary
        agent_summaries: List of agent summary dictionaries
    """
    _ensure_dir(os.path.dirname(json_path))
    payload = {
        "benchmark": "OSWorld-Green-5",
        "seed": config.get("seed"),
        "agents": agent_summaries,
        "generated_at_ms": int(time.time() * 1000),
        "config": config,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def console_table(rows: List[Dict[str, Any]], headers: List[Tuple[str, str]]):
    """
    Print a console table.
    
    Args:
        rows: List of row dictionaries
        headers: List of (key, title) tuples
    """
    # headers: list of (key, title)
    widths = [max(len(h[1]), max((len(str(r.get(h[0], ""))) for r in rows), default=0)) for h in headers]
    line = "  ".join(h[1].ljust(w) for (w, h) in zip(widths, headers))
    print(line)
    for r in rows:
        print("  ".join(str(r.get(h[0], "")).ljust(w) for (w, h) in zip(widths, headers)))
