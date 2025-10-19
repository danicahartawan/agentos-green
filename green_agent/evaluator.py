"""
Green Agent Evaluator

Coordinates task execution inside OSWorld's ``DesktopEnv`` and aggregates
results for reporting back to AgentBeats tooling.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .reporter import write_run_row
from .scorer import combine, fallback_eval, native_eval_if_available

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - external dependency
    from desktop_env.desktop_env import DesktopEnv  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    DesktopEnv = None


class GreenEvaluator:
    """Main evaluator that orchestrates task execution and evaluation."""

    def __init__(self, config: Config):
        """
        Initialize Green Evaluator.

        Args:
            config: Green Agent configuration
        """
        if DesktopEnv is None:
            raise RuntimeError(
                "desktop_env is not available. Install OSWorld or ensure it is on PYTHONPATH."
            )
        self.cfg = config
        random.seed(config.seed)

    # --------------------------------------------------------------------- #
    # Environment helpers
    # --------------------------------------------------------------------- #

    def _create_env(self) -> DesktopEnv:
        """Instantiate a DesktopEnv using the configuration parameters."""
        kwargs: Dict[str, Any] = {
            "provider_name": self.cfg.provider or "docker",
            "action_space": self.cfg.action_space,
            "headless": self.cfg.headless,
            "require_a11y_tree": self.cfg.require_a11y_tree,
        }
        if self.cfg.region:
            kwargs["region"] = self.cfg.region
        if self.cfg.path_to_vm:
            kwargs["path_to_vm"] = self.cfg.path_to_vm
        if self.cfg.snapshot_name:
            kwargs["snapshot_name"] = self.cfg.snapshot_name
        if self.cfg.client_password:
            kwargs["client_password"] = self.cfg.client_password

        LOGGER.debug("Creating DesktopEnv with kwargs=%s", kwargs)
        return DesktopEnv(**kwargs)

    def _load_example(self, example_path: str) -> Dict[str, Any]:
        """Load the OSWorld task definition JSON."""
        with open(example_path, "r", encoding="utf-8") as fp:
            example_json = json.load(fp)
        return example_json

    # --------------------------------------------------------------------- #
    # Action conversion helpers
    # --------------------------------------------------------------------- #

    def _pyautogui_action_from_dict(self, action: Dict[str, Any]) -> Optional[str]:
        """Convert a simple action dictionary to a PyAutoGUI command string."""
        a_type = action.get("action_type")
        args = action.get("args", {})

        if a_type == "wait":
            return None  # wait handled outside
        if a_type == "hotkey":
            keys = args.get("keys", [])
            joined = ", ".join(f"'{k}'" for k in keys)
            return f"pyautogui.hotkey({joined})"
        if a_type == "key":
            key = args.get("key")
            return f"pyautogui.press('{key}')" if key else None
        if a_type == "type":
            text = args.get("text", "")
            escaped = text.replace("\\", "\\\\").replace("'", "\\'")
            return f"pyautogui.typewrite('{escaped}')"
        if a_type == "click":
            # Expect explicit coordinates if provided
            x = args.get("x")
            y = args.get("y")
            if x is None or y is None:
                raise ValueError("click action requires 'x' and 'y' coordinates for pyautogui space.")
            return f"pyautogui.click({int(x)}, {int(y)})"
        return None

    def _format_action(
        self, action: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Convert agent action dict to DesktopEnv action payload based on action space.

        Returns:
            Tuple of (action_payload, wait_override_seconds)
        """
        if action.get("action_type") == "wait":
            return None, float(action.get("args", {}).get("seconds", 1.0))

        if self.cfg.action_space == "pyautogui":
            cmd = self._pyautogui_action_from_dict(action)
            return cmd, None

        # Additional action spaces can be added here when needed
        raise ValueError(f"Unsupported action_space '{self.cfg.action_space}' for action {action}")

    # --------------------------------------------------------------------- #
    # Execution
    # --------------------------------------------------------------------- #

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
        example_json = self._load_example(task_spec["example_path"])
        instruction = example_json.get("instruction", "")
        env = self._create_env()

        white_agent.reset()
        steps = 0
        errors: List[str] = []
        action_history: List[dict] = []
        eval_detail: Dict[str, Any] = {}
        success = False
        score: Optional[float] = None
        last_obs: Dict[str, Any] = {}

        start_time = time.time()
        try:
            try:
                last_obs = env.reset(task_config=example_json)
            except Exception as exc:  # pragma: no cover - environment failure
                errors.append(f"reset_failed: {exc}")
                LOGGER.exception("Environment reset failed for %s", task_spec["id"])
                return self._finalize_run(
                    agent_name,
                    task_spec,
                    steps=steps,
                    errors=errors,
                    success=False,
                    eval_detail={"reason": "reset_failed", "error": str(exc)},
                    score=score,
                    started_at=start_time,
                )

            for _ in range(self.cfg.max_steps):
                steps += 1
                try:
                    agent_action = white_agent.predict(
                        instruction,
                        {"observation": last_obs, "step": steps},
                    )
                except Exception as exc:
                    errors.append(f"agent_predict_failed: {exc}")
                    LOGGER.exception("Agent predict failed on step %s", steps)
                    break

                action_history.append(agent_action)
                try:
                    formatted_action, wait_override = self._format_action(agent_action)
                except Exception as exc:
                    errors.append(f"action_translation_failed: {exc}")
                    LOGGER.warning(
                        "Action translation failed for task %s on step %s: %s",
                        task_spec["id"],
                        steps,
                        exc,
                    )
                    break

                if formatted_action is None:
                    # Wait / noop, but still respect configured pause or override
                    pause = wait_override or self.cfg.pause_after_action
                    time.sleep(max(pause, 0.0))
                    continue

                try:
                    pause = wait_override or self.cfg.pause_after_action
                    last_obs, reward, done, info = env.step(
                        formatted_action,
                        pause=pause,
                    )
                except Exception as exc:  # pragma: no cover - environment failure
                    errors.append(f"env_step_failed: {exc}")
                    LOGGER.exception("Environment step failed on task %s", task_spec["id"])
                    break

                if done:
                    LOGGER.debug("Task %s finished early at step %s", task_spec["id"], steps)
                    break

            # Perform evaluation (prefer DesktopEnv.evaluate)
            try:
                score = env.evaluate()
                success = score is not None and score >= self.cfg.success_threshold
                eval_detail = {"score": score, "threshold": self.cfg.success_threshold}
            except Exception as exc:  # pragma: no cover - falls back
                LOGGER.warning("DesktopEnv.evaluate failed: %s", exc)
                native_ok, native_detail = native_eval_if_available(example_json, env)
                if native_ok is None or native_ok is False:
                    native_ok, native_detail = fallback_eval(task_spec, env, action_history)
                success = bool(native_ok)
                eval_detail = native_detail

        finally:
            try:
                env.close()
            except Exception:  # pragma: no cover - best effort
                LOGGER.debug("DesktopEnv close raised", exc_info=True)

        return self._finalize_run(
            agent_name,
            task_spec,
            steps=steps,
            errors=errors,
            success=success,
            eval_detail=eval_detail,
            score=score,
            started_at=start_time,
        )

    # --------------------------------------------------------------------- #
    # Aggregation
    # --------------------------------------------------------------------- #

    def run_suite(
        self,
        agent_name: str,
        white_agent,
        tasks: List[Dict[str, Any]],
        repeats: int,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
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
        for task_spec in tasks:
            for _ in range(repeats):
                row = self.run_one(agent_name, white_agent, task_spec)
                per_task.append(row)
                successes.append(row["success"])
                steps.append(row["steps"])
                times.append(row["wall_time_ms"])
                errs.append(row["errors"])
        summary = combine(successes, steps, times, errs)
        return summary, per_task

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _finalize_run(
        self,
        agent_name: str,
        task_spec: Dict[str, Any],
        *,
        steps: int,
        errors: List[str],
        success: bool,
        eval_detail: Dict[str, Any],
        score: Optional[float],
        started_at: float,
    ) -> Dict[str, Any]:
        """Persist the run row and return it."""
        wall_ms = int((time.time() - started_at) * 1000)
        run_row = {
            "task_id": task_spec["id"],
            "domain": task_spec["domain"],
            "repeat": 1,
            "success": bool(success),
            "steps": steps,
            "wall_time_ms": wall_ms,
            "errors": errors,
            "eval_detail": eval_detail,
        }
        if score is not None:
            run_row["score"] = score

        runlog = os.path.join(
            self.cfg.reports_root,
            "runs",
            agent_name,
            f"{task_spec['id']}.jsonl",
        )
        write_run_row(runlog, run_row)
        return run_row
