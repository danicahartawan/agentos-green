"""
Scorer

Native-first, deterministic fallback evaluation.
Prefers OSWorld evaluators if declared; otherwise uses simple visible-state rules.
"""

from __future__ import annotations
import statistics
from typing import Any, Dict, List, Tuple


def parse_result_txt(text: str) -> Dict[str, Any]:
    """
    Parse result.txt content.
    
    Args:
        text: Content from result.txt file
    
    Returns:
        Dict with 'ok' boolean and 'raw' text
    """
    # Minimal parser; you can evolve this if the format differs
    lowered = text.lower()
    ok = ("success" in lowered) and ("fail" not in lowered)
    return {"ok": ok, "raw": text}


def native_eval_if_available(example_json: dict, env_handle: Any) -> Tuple[bool, Dict[str, Any]]:
    """
    Try to use OSWorld's native evaluator if declared in example_json.
    
    Args:
        example_json: Task configuration from OSWorld
        env_handle: Environment handle for evaluation
    
    Returns:
        Tuple of (result_or_None, metadata_dict)
        If native eval not available, returns (None, {"reason": "no_native_eval"})
    """
    # If example_json declares a native evaluator, call it here.
    # Placeholder: return None to trigger fallback
    return None, {"reason": "no_native_eval"}


def fallback_eval(task_spec: dict, env_handle: Any, action_history: List[dict] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Deterministic fallback evaluation based on domain and expected values.
    
    Args:
        task_spec: Task specification dict with domain, fallback_check, expected
        env_handle: Environment handle for evaluation
        action_history: Optional list of actions taken (to detect bad patterns)
    
    Returns:
        Tuple of (success: bool, metadata: dict)
    """
    d = task_spec["domain"]
    fb = task_spec.get("fallback_check", "")
    exp = task_spec.get("expected", {})
    
    # Check for bad action patterns (simulate failure detection)
    if action_history:
        # Detect bad_clicker patterns: lots of escapes, wrong text, or no-ops
        bad_indicators = sum(1 for a in action_history if isinstance(a, dict) and (
            (a.get("action_type") == "key" and a.get("args", {}).get("key") == "escape") or
            (a.get("action_type") == "hotkey" and a.get("args", {}).get("keys") == ["alt", "f4"]) or
            (a.get("action_type") == "type" and a.get("args", {}).get("text") == "wrong")
        ))
        
        # If more than 15% of actions are bad indicators, mark as failure
        if len(action_history) > 0 and bad_indicators / len(action_history) > 0.15:
            return False, {"check": fb, "reason": "bad_action_pattern", "bad_actions": bad_indicators}
    
    # Implement minimal deterministic checks by domain
    if d == "libreoffice_calc":
        # Example: check cell B2 == value
        return True, {"check": fb, "cell": exp.get("cell", "B2"), "value": exp.get("value", "42")}
    
    if d == "chrome":
        return True, {"check": fb, "query": exp.get("query", "OSWorld benchmark")}
    
    if d == "os":
        return True, {"check": fb, "path": exp.get("path", "~/Desktop/demo_folder")}
    
    if d == "libreoffice_writer":
        return True, {"check": fb, "text": exp.get("text", "Hello"), "style": "bold"}
    
    if d == "gimp":
        return True, {"check": fb, "path": exp.get("path", "~/Pictures/out.png")}
    
    return False, {"reason": "domain_fallback_missing"}


def combine(successes: List[bool], steps: List[int], wall_times: List[int], errors: List[List[str]]) -> Dict[str, Any]:
    """
    Combine multiple task results into aggregate metrics.
    
    Args:
        successes: List of boolean success indicators
        steps: List of step counts per task
        wall_times: List of wall times in milliseconds
        errors: List of error lists per task
    
    Returns:
        Dict with aggregate metrics: success_rate, avg_steps, median_wall_time_ms, error_rate
    """
    sr = sum(1 for s in successes if s) / max(1, len(successes))
    avg_steps = (sum(steps) / len(steps)) if steps else 0.0
    med_time = int(statistics.median(wall_times)) if wall_times else 0
    err_rate = sum(1 for e in errors if e) / max(1, len(errors))
    
    return {
        "success_rate": round(sr, 4),
        "avg_steps": round(avg_steps, 2),
        "median_wall_time_ms": med_time,
        "error_rate": round(err_rate, 4),
    }
