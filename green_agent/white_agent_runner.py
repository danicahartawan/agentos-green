"""
White Agent Runner

Provides uniform interface wrapper for white agents.
Returns agents with reset() and predict(instruction, obs) -> action.
"""

from __future__ import annotations
from typing import Any


class NaiveClickerWhiteAgent:
    """Deterministic, no-LLM white agent for curated tasks."""
    
    def __init__(self, seed: int = 7):
        self.seed = seed
    
    def reset(self):
        """Reset agent state."""
        pass
    
    def predict(self, instruction: str, obs: dict) -> dict:
        """
        Predict next action based on instruction and observation.
        
        Args:
            instruction: Task instruction string
            obs: Observation dictionary from environment
        
        Returns:
            OSWorld-compatible action dict (click/type/enter/wait)
        """
        # TODO: wire minimal, robust actions keyed by known task ids or UI cues
        # Return OSWorld-compatible action dict (click/type/enter/wait)
        return {"action_type": "wait", "args": {"seconds": 0.5}}


def build_white_agent(agent_key: str, seed: int = 7) -> Any:
    """
    Build a white agent instance by key.
    
    Args:
        agent_key: Agent identifier (e.g., "naive_clicker")
        seed: Random seed for reproducibility
    
    Returns:
        White agent instance with reset() and predict() methods
    """
    key = agent_key.lower()
    if key == "naive_clicker":
        return NaiveClickerWhiteAgent(seed=seed)
    # TODO: add wrappers to mm_agents.* if you choose to demo a baseline
    print(f"[white_agent] {agent_key} not available; falling back to naive_clicker.")
    return NaiveClickerWhiteAgent(seed=seed)
