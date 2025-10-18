"""
Green Agent Configuration

Single source of truth for Green Agent evaluation configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Config:
    """Green Agent configuration dataclass."""
    
    provider: Optional[str] = "docker"        # or None → repo default
    tasks_file: Optional[str] = None          # if None, use test_all.json + filters
    domains: Optional[List[str]] = field(default_factory=lambda: ["chrome", "libreoffice_calc", "os", "libreoffice_writer", "gimp"])
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
    if getattr(args, "provider", None):
        cfg.provider = args.provider
    if getattr(args, "tasks_file", None):
        cfg.tasks_file = args.tasks_file
    if getattr(args, "domains", None):
        cfg.domains = args.domains
    if getattr(args, "white_agents", None):
        cfg.white_agents = args.white_agents
    if getattr(args, "repeats", None):
        cfg.repeats = int(args.repeats)
    if getattr(args, "max_steps", None):
        cfg.max_steps = int(args.max_steps)
    if getattr(args, "timeout_sec", None):
        cfg.timeout_sec = int(args.timeout_sec)
    if getattr(args, "seed", None):
        cfg.seed = int(args.seed)
    if getattr(args, "report", None):
        cfg.reports_root = args.report.rsplit("/", 1)[0]
    return cfg
