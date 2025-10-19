"""
Green Agent CLI

Clean, readable CLI that ties everything together.
"""

import argparse
import json
import os
from green_agent.config import from_args
from green_agent.task_loader import load_tasks
from green_agent.white_agent_runner import build_white_agent
from green_agent.evaluator import GreenEvaluator
from green_agent.reporter import write_agent_summary, write_combined_report, console_table


def main():
    p = argparse.ArgumentParser("OSWorld Green Agent")
    p.add_argument("--tasks-file", type=str, default=None)
    p.add_argument("--domains", nargs="*", default=None)
    p.add_argument("--white-agents", nargs="*", default=["naive_clicker"])
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--max-steps", type=int, default=50)
    p.add_argument("--timeout-sec", type=int, default=90)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--report", type=str, default="reports/osworld_green_report.json")
    p.add_argument("--provider", type=str, default="docker")
    p.add_argument("--region", type=str, default=None)
    p.add_argument("--path-to-vm", type=str, default=None)
    p.add_argument("--snapshot-name", type=str, default="init_state")
    p.add_argument("--action-space", type=str, default="pyautogui")
    p.add_argument("--headless", action="store_true", help="Run DesktopEnv in headless mode.")
    p.add_argument("--require-a11y-tree", action="store_true", help="Request accessibility tree in observations.")
    p.add_argument("--client-password", type=str, default=None)
    p.add_argument("--pause-after-action", type=float, default=1.0)
    p.add_argument("--success-threshold", type=float, default=0.99)
    p.add_argument("--results-root", type=str, default=None)
    p.add_argument("--reports-root", type=str, default=None)
    args = p.parse_args()

    cfg = from_args(args)
    tasks = load_tasks(args.tasks_file, args.domains)
    evaluator = GreenEvaluator(cfg)

    agent_summaries = []
    table_rows = []
    for agent_key in args.white_agents:
        agent = build_white_agent(agent_key, seed=args.seed)
        summary, per_task = evaluator.run_suite(agent_key, agent, tasks, repeats=args.repeats)
        # Persist per-agent and collect combined
        write_agent_summary(os.path.join(cfg.reports_root, f"{agent_key}.json"), agent_key, summary, per_task)
        agent_summaries.append({"name": agent_key, "summary": summary, "per_task": per_task})
        success_pct = round(summary["success_rate"] * 100, 1)
        table_rows.append({
            "ok": "✓" if success_pct >= 50 else "✗",
            "agent": agent_key,
            "success%": success_pct,
            "avg_steps": summary["avg_steps"],
            "time_ms": summary["median_wall_time_ms"],
            "errors%": round(summary["error_rate"] * 100, 1),
        })

    write_combined_report(args.report, cfg.__dict__, agent_summaries)
    console_table(table_rows, headers=[("ok", ""), ("agent", "Agent"), ("success%", "Success%"), ("avg_steps", "AvgSteps"), ("time_ms", "Time(ms)"), ("errors%", "Errors%")])


if __name__ == "__main__":
    main()
