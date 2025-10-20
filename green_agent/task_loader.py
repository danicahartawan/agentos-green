"""
Task Loader

Loads OSWorld task configurations and returns TaskSpec dicts.
Uses existing OSWorld task structure without rewrites.
"""

from __future__ import annotations
import json
import os
from typing import List, Optional, Dict, Any

MASTER = "evaluation_examples/test_all.json"


def _read_json(path: str) -> dict:
    """Read JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_example_path(domain: str, task_id: str) -> str:
    """
    Normalize example path to OSWorld format.
    OSWorld: evaluation_examples/examples/{domain}/{task-id}.json
    """
    return os.path.join("evaluation_examples", "examples", domain, f"{task_id}.json")


def load_tasks(tasks_file: Optional[str], domains: Optional[List[str]]) -> List[Dict[str, Any]]:
    """
    Load tasks from a custom file or OSWorld master listing.
    
    Args:
        tasks_file: Optional path to custom tasks JSON file
        domains: Optional list of domains to filter (only used when tasks_file is None)
    
    Returns:
        List of TaskSpec dicts with keys: id, domain, example_path, fallback_check, expected?
    """
    tasks: List[Dict[str, Any]] = []
    
    if tasks_file:
        # Load from curated subset file
        data = _read_json(tasks_file)
        for t in data["tasks"]:
            tasks.append({
                "id": t["id"],
                "domain": t["domain"],
                "example_path": t.get("example_path") or _normalize_example_path(t["domain"], t["id"]),
                "fallback_check": t.get("fallback_check"),
                "expected": t.get("expected"),
            })
    else:
        # Fall back to OSWorld master listing
        master = _read_json(MASTER)
        for domain, items in master.items():
            if domains and domain not in domains:
                continue
            for task_id in items:
                tasks.append({
                    "id": task_id,
                    "domain": domain,
                    "example_path": _normalize_example_path(domain, task_id),
                    # "fallback_check": "native_or_visible_end_state",
                })
    
    return tasks
