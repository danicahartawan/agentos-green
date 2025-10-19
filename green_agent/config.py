"""
Green Agent Configuration

Single source of truth for Green Agent evaluation configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Config:
    """Green Agent configuration dataclass."""

    provider: Optional[str] = "docker"        # virtualization provider
    region: Optional[str] = None              # provider-specific region (e.g., AWS)
    path_to_vm: Optional[str] = None          # VM image path / identifier
    snapshot_name: Optional[str] = "init_state"
    action_space: str = "pyautogui"
    headless: bool = False
    require_a11y_tree: bool = False
    client_password: Optional[str] = None
    pause_after_action: float = 1.0
    success_threshold: float = 0.99

    tasks_file: Optional[str] = None          # if None, use test_all.json + filters
    domains: Optional[List[str]] = field(
        default_factory=lambda: [
            "chrome",
            "libreoffice_calc",
            "os",
            "libreoffice_writer",
            "gimp",
        ]
    )
    repeats: int = 3
    max_steps: int = 50
    timeout_sec: int = 90
    seed: int = 7
    white_agents: List[str] = field(default_factory=lambda: ["naive_clicker"])
    results_root: str = "./results"           # OSWorld-native
    reports_root: str = "./reports"           # Green reports


def from_args(args) -> Config:
    """Create Config from argparse args."""
    cfg = Config()
    if hasattr(args, "provider") and args.provider:
        cfg.provider = args.provider
    if hasattr(args, "region") and args.region:
        cfg.region = args.region
    if hasattr(args, "path_to_vm") and args.path_to_vm:
        cfg.path_to_vm = args.path_to_vm
    if hasattr(args, "snapshot_name") and args.snapshot_name:
        cfg.snapshot_name = args.snapshot_name
    if hasattr(args, "action_space") and args.action_space:
        cfg.action_space = args.action_space
    if hasattr(args, "headless") and args.headless is not None:
        cfg.headless = bool(args.headless)
    if hasattr(args, "require_a11y_tree") and args.require_a11y_tree is not None:
        cfg.require_a11y_tree = bool(args.require_a11y_tree)
    if hasattr(args, "client_password") and args.client_password:
        cfg.client_password = args.client_password
    if hasattr(args, "pause_after_action") and args.pause_after_action is not None:
        cfg.pause_after_action = float(args.pause_after_action)
    if hasattr(args, "success_threshold") and args.success_threshold is not None:
        cfg.success_threshold = float(args.success_threshold)

    if hasattr(args, "tasks_file") and args.tasks_file:
        cfg.tasks_file = args.tasks_file
    if hasattr(args, "domains") and args.domains:
        cfg.domains = args.domains
    if hasattr(args, "white_agents") and args.white_agents:
        cfg.white_agents = args.white_agents
    if hasattr(args, "repeats") and args.repeats is not None:
        cfg.repeats = int(args.repeats)
    if hasattr(args, "max_steps") and args.max_steps is not None:
        cfg.max_steps = int(args.max_steps)
    if hasattr(args, "timeout_sec") and args.timeout_sec is not None:
        cfg.timeout_sec = int(args.timeout_sec)
    if hasattr(args, "seed") and args.seed is not None:
        cfg.seed = int(args.seed)
    if hasattr(args, "report") and args.report:
        cfg.reports_root = args.report.rsplit("/", 1)[0]
    if hasattr(args, "results_root") and args.results_root:
        cfg.results_root = args.results_root
    if hasattr(args, "reports_root") and args.reports_root:
        cfg.reports_root = args.reports_root
    return cfg
