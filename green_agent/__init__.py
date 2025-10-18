"""
Green Agent - OSWorld × AgentBeats Hosting Evaluator

A hosting evaluator that:
(i) loads a set of OSWorld tasks,
(ii) orchestrates runs by one or more White Agents on those tasks, and
(iii) scores them with deterministic, execution-based checks (and OSWorld's native eval fns when available),
producing reproducible metrics, artifacts, and a summary report.
"""

from .evaluator import GreenEvaluator
from .config import Config

__version__ = "0.1.0"
__all__ = ["GreenEvaluator", "Config"]

