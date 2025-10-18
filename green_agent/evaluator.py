"""
Green Agent Evaluator

Orchestration module that coordinates task execution, evaluation, and reporting.
Reuses OSWorld environment pieces; keeps it small and deterministic.
"""

from __future__ import annotations
import json
import os
import time
import random
from typing import Any, Dict, List, Tuple
from .config import Config
from .scorer import native_eval_if_available, fallback_eval, combine
from .reporter import write_run_row

# If you wire DesktopEnv directly later, import here:
# from desktop_env.desktop_env import DesktopEnv  # adjust to repo path


class GreenEvaluator:
    """Main evaluator that orchestrates task execution and evaluation."""
    
    def __init__(self, config: Config):
        """
        Initialize Green Evaluator.
        
        Args:
            config: Green Agent configuration
        """
        self.cfg = config
        random.seed(config.seed)
    
    def _prepare_env_and_instruction(self, example_path: str) -> Tuple[Any, str]:
        """
        Load task example and prepare environment.
        
        Args:
            example_path: Path to task JSON file
        
        Returns:
            Tuple of (env_handle, instruction_string)
        """
        with open(example_path, "r", encoding="utf-8") as f:
            ex = json.load(f)
        instruction = ex.get("instruction", "")
        env = None  # TODO: integrate DesktopEnv init or reuse lib_run_single helpers
        return env, instruction
    
    def run_one(self, agent_name: str, white_agent, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single task with a white agent.
        
        Args:
            agent_name: Name of the agent
            white_agent: White agent instance with reset() and predict() methods
            task_spec: Task specification dict
        
        Returns:
            Run result dictionary with success, steps, timing, errors
        """
        env, instruction = self._prepare_env_and_instruction(task_spec["example_path"])
        white_agent.reset()
        steps = 0
        t0 = time.time()
        errors: List[str] = []
        
        # Minimal loop; you'll wire real env.step() when ready
        for _ in range(self.cfg.max_steps):
            steps += 1
            try:
                action = white_agent.predict(instruction, {"obs": "stub"})
                # TODO: obs = env.step(action)
                time.sleep(0.05)  # simulate
            except Exception as e:
                errors.append(str(e))
                break
            # TODO: break if done condition
        
        # Prefer native eval, else fallback
        with open(task_spec["example_path"], "r", encoding="utf-8") as f:
            example_json = json.load(f)
        ok, detail = native_eval_if_available(example_json, env)
        if ok is None or ok is False:
            ok, detail = fallback_eval(task_spec, env)
        
        wall = int((time.time() - t0) * 1000)
        run_row = {
            "task_id": task_spec["id"],
            "domain": task_spec["domain"],
            "repeat": 1,
            "success": bool(ok),
            "steps": steps,
            "wall_time_ms": wall,
            "errors": errors,
            "eval_detail": detail,
        }
        # Persist per-run row (one file per agent)
        runlog = os.path.join(self.cfg.reports_root, "runs", agent_name, f"{task_spec['id']}.jsonl")
        write_run_row(runlog, run_row)
        return run_row
    
    def run_suite(self, agent_name: str, white_agent, tasks: List[Dict[str, Any]], repeats: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run a full suite of tasks with repeats.
        
        Args:
            agent_name: Name of the agent
            white_agent: White agent instance
            tasks: List of task specification dicts
            repeats: Number of times to repeat each task
        
        Returns:
            Tuple of (summary_dict, per_task_results_list)
        """
        per_task: List[Dict[str, Any]] = []
        successes, steps, times, errs = [], [], [], []
        for t in tasks:
            for _ in range(repeats):
                row = self.run_one(agent_name, white_agent, t)
                per_task.append(row)
                successes.append(row["success"])
                steps.append(row["steps"])
                times.append(row["wall_time_ms"])
                errs.append(row["errors"])
        summary = combine(successes, steps, times, errs)
        return summary, per_task
