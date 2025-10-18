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
        self.step_count = 0
    
    def reset(self):
        """Reset agent state."""
        self.step_count = 0
    
    def predict(self, instruction: str, obs: dict) -> dict:
        """
        Predict next action based on instruction and observation.
        
        Args:
            instruction: Task instruction string
            obs: Observation dictionary from environment
        
        Returns:
            OSWorld-compatible action dict (click/type/enter/wait)
        """
        self.step_count += 1
        
        # Task-specific heuristics (deterministic, no LLMs)
        # Use common keybindings to avoid brittle coordinates
        
        # Chrome search keyword
        # chrome_search_keyword: "search for OSWorld benchmark"
        if "search" in instruction.lower() and "chrome" in instruction.lower():
            # Step sequence:
            # 1. ctrl+l (focus location bar)
            # 2. type query
            # 3. enter
            # 4. wait for results
            if self.step_count == 1:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "l"]}}
            elif self.step_count == 2:
                query = "OSWorld benchmark"  # extract from instruction if needed
                return {"action_type": "type", "args": {"text": query}}
            elif self.step_count == 3:
                return {"action_type": "key", "args": {"key": "enter"}}
            else:
                return {"action_type": "wait", "args": {"seconds": 0.5}}
        
        # LibreOffice Calc: edit cell
        # calc_edit_cell: "set cell B2 to 42"
        if ("calc" in instruction.lower() or "cell" in instruction.lower()) and ("b2" in instruction.lower() or "42" in instruction.lower()):
            # Step sequence:
            # 1. ctrl+g (goto dialog)
            # 2. type "B2"
            # 3. enter
            # 4. type "42"
            # 5. ctrl+s (save)
            if self.step_count == 1:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "g"]}}
            elif self.step_count == 2:
                return {"action_type": "type", "args": {"text": "B2"}}
            elif self.step_count == 3:
                return {"action_type": "key", "args": {"key": "enter"}}
            elif self.step_count == 4:
                return {"action_type": "type", "args": {"text": "42"}}
            elif self.step_count == 5:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "s"]}}
            else:
                return {"action_type": "wait", "args": {"seconds": 0.2}}
        
        # OS: make folder
        # os_make_folder: "create folder demo_folder on Desktop"
        if ("folder" in instruction.lower() or "directory" in instruction.lower()) and "desktop" in instruction.lower():
            # Step sequence:
            # 1. super+e or click Files (open file manager)
            # 2. click Desktop
            # 3. right-click → New Folder or ctrl+shift+n
            # 4. type "demo_folder"
            # 5. enter
            if self.step_count == 1:
                return {"action_type": "hotkey", "args": {"keys": ["super", "e"]}}
            elif self.step_count == 2:
                return {"action_type": "click", "args": {"target": "Desktop"}}  # or navigate
            elif self.step_count == 3:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "shift", "n"]}}
            elif self.step_count == 4:
                return {"action_type": "type", "args": {"text": "demo_folder"}}
            elif self.step_count == 5:
                return {"action_type": "key", "args": {"key": "enter"}}
            else:
                return {"action_type": "wait", "args": {"seconds": 0.2}}
        
        # LibreOffice Writer: bold text
        # writer_bold_text: "type Hello and make it bold"
        if ("writer" in instruction.lower() or ("bold" in instruction.lower() and "hello" in instruction.lower())):
            # Step sequence:
            # 1. type "Hello"
            # 2. ctrl+a (select all)
            # 3. ctrl+b (bold)
            # 4. ctrl+s (save)
            if self.step_count == 1:
                return {"action_type": "type", "args": {"text": "Hello"}}
            elif self.step_count == 2:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "a"]}}
            elif self.step_count == 3:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "b"]}}
            elif self.step_count == 4:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "s"]}}
            else:
                return {"action_type": "wait", "args": {"seconds": 0.2}}
        
        # GIMP: export PNG
        # gimp_export_png: "export image as PNG to ~/Pictures/out.png"
        if "gimp" in instruction.lower() and ("export" in instruction.lower() or "png" in instruction.lower()):
            # Step sequence:
            # 1. File menu (alt+f or ctrl+shift+e for export)
            # 2. Export As
            # 3. type path: ~/Pictures/out.png
            # 4. enter
            # 5. confirm PNG settings
            # 6. export button
            if self.step_count == 1:
                return {"action_type": "hotkey", "args": {"keys": ["ctrl", "shift", "e"]}}
            elif self.step_count == 2:
                return {"action_type": "type", "args": {"text": "~/Pictures/out.png"}}
            elif self.step_count == 3:
                return {"action_type": "key", "args": {"key": "enter"}}
            elif self.step_count == 4:
                return {"action_type": "key", "args": {"key": "enter"}}  # confirm export
            else:
                return {"action_type": "wait", "args": {"seconds": 0.2}}
        
        # Default fallback
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
