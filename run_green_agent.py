#!/usr/bin/env python3
"""
Green Agent Runner Script

Entry point for running Green Agent evaluations.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from green_agent import GreenEvaluator, Config
from green_agent.config import from_args


def setup_logging(log_level: str):
    """Configure logging."""
    level = getattr(logging, log_level.upper())
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(name)s\x1b[1;33m] \x1b[0m%(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    datetime_str = datetime.now().strftime("%Y%m%d@%H%M%S")
    file_handler = logging.FileHandler(
        os.path.join("logs", f"green_agent-{datetime_str}.log"),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s %(name)s] %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Green Agent - OSWorld × AgentBeats Evaluator"
    )
    
    # Task Selection
    parser.add_argument(
        "--test_all_meta_path",
        type=str,
        default="evaluation_examples/test_all.json",
        help="Path to test_all.json"
    )
    parser.add_argument(
        "--domains",
        type=str,
        nargs="+",
        default=None,
        help="Specific domains to evaluate (default: all)"
    )
    parser.add_argument(
        "--task_ids",
        type=str,
        nargs="+",
        default=None,
        help="Specific task IDs to evaluate (default: all in selected domains)"
    )
    
    # White Agent Configuration
    parser.add_argument(
        "--white_agent_type",
        type=str,
        default="PromptAgent",
        help="White agent class name"
    )
    parser.add_argument(
        "--white_agent_module",
        type=str,
        default="mm_agents.agent",
        help="Module containing white agent"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="Model to use for white agent"
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=1500,
        help="Max tokens for LLM"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Temperature for LLM"
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=0.9,
        help="Top-p for LLM"
    )
    
    # Environment Configuration
    parser.add_argument(
        "--provider_name",
        type=str,
        default="docker",
        choices=["vmware", "docker", "aws", "azure", "virtualbox"],
        help="VM provider"
    )
    parser.add_argument(
        "--path_to_vm",
        type=str,
        default=None,
        help="Path to VM (for vmware/virtualbox)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode"
    )
    parser.add_argument(
        "--screen_width",
        type=int,
        default=1920,
        help="Screen width"
    )
    parser.add_argument(
        "--screen_height",
        type=int,
        default=1080,
        help="Screen height"
    )
    parser.add_argument(
        "--client_password",
        type=str,
        default="password",
        help="VM client password"
    )
    
    # Action/Observation Space
    parser.add_argument(
        "--action_space",
        type=str,
        default="pyautogui",
        choices=["pyautogui", "computer_13"],
        help="Action space"
    )
    parser.add_argument(
        "--observation_type",
        type=str,
        default="screenshot",
        choices=["screenshot", "a11y_tree", "screenshot_a11y_tree", "som"],
        help="Observation type"
    )
    
    # Execution Parameters
    parser.add_argument(
        "--max_steps",
        type=int,
        default=15,
        help="Max steps per task"
    )
    parser.add_argument(
        "--max_trajectory_length",
        type=int,
        default=3,
        help="Max trajectory length"
    )
    parser.add_argument(
        "--sleep_after_execution",
        type=float,
        default=0.0,
        help="Sleep time after each action"
    )
    parser.add_argument(
        "--num_parallel_envs",
        type=int,
        default=1,
        help="Number of parallel environments"
    )
    
    # Output Configuration
    parser.add_argument(
        "--result_dir",
        type=str,
        default="./results",
        help="Directory for results"
    )
    parser.add_argument(
        "--report_dir",
        type=str,
        default="./reports",
        help="Directory for reports"
    )
    parser.add_argument(
        "--run_name",
        type=str,
        default=None,
        help="Run name (auto-generated if not provided)"
    )
    
    # Modes
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry run mode (no execution)"
    )
    parser.add_argument(
        "--no_resume",
        action="store_true",
        help="Don't skip completed tasks"
    )
    
    # Logging
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger("green_agent.main")
    
    logger.info("Green Agent - OSWorld × AgentBeats Evaluator")
    logger.info("=" * 80)
    
    # Create configuration from args
    config = from_args(args)
    
    # Create and run evaluator
    try:
        evaluator = GreenEvaluator(config)
        metrics = evaluator.run()
        
        # Exit with appropriate code
        if metrics.get("dry_run"):
            sys.exit(0)
        
        overall = metrics.get("overall", {})
        success_rate = overall.get("success_rate", 0)
        
        # Exit code 0 if success rate > 50%, else 1
        sys.exit(0 if success_rate > 0.5 else 1)
        
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

