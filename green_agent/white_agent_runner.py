"""
White Agent Runner

Provides uniform interface wrapper for white agents.
Returns agents with reset() and predict(instruction, obs) -> action.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependencies
    from a2a.client import A2ACardResolver, A2AClient
    from a2a.types import (
        AgentCard,
        Message,
        MessageSendParams,
        Part,
        Role,
        SendStreamingMessageRequest,
        SendStreamingMessageSuccessResponse,
        TaskArtifactUpdateEvent,
        TaskStatusUpdateEvent,
        TextPart,
    )
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    A2AClient = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from mm_agents.agent import PromptAgent  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    # Attempt to add ../OSWorld to path if available
    candidate = Path(__file__).resolve().parents[2] / "OSWorld"
    if candidate.exists():
        sys.path.append(str(candidate))
        try:
            from mm_agents.agent import PromptAgent  # type: ignore
        except ModuleNotFoundError:
            PromptAgent = None  # type: ignore
    else:
        PromptAgent = None  # type: ignore


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


class BadClickerWhiteAgent:
    """
    Error-injected white agent for testing failure detection.
    
    Randomly skips or mis-clicks one step in ~10-20% of runs to demonstrate
    that Green Agent detects failures correctly.
    """
    
    def __init__(self, seed: int = 7, error_rate: float = 0.35):
        """
        Initialize bad clicker agent.
        
        Args:
            seed: Random seed for reproducibility
            error_rate: Probability of injecting an error (0.0 to 1.0)
        """
        self.seed = seed
        self.error_rate = error_rate
        self.step_count = 0
        import random
        random.seed(seed)
        self.random = random
        # Create a delegate naive clicker for correct actions
        self.naive_delegate = NaiveClickerWhiteAgent(seed=seed)
    
    def reset(self):
        """Reset agent state."""
        self.step_count = 0
        self.naive_delegate.reset()
    
    def predict(self, instruction: str, obs: dict) -> dict:
        """
        Predict action with occasional errors injected.
        
        Args:
            instruction: Task instruction string
            obs: Observation dictionary from environment
        
        Returns:
            OSWorld-compatible action dict (sometimes wrong)
        """
        self.step_count += 1
        
        # Decide whether to inject error this step
        if self.random.random() < self.error_rate:
            # Inject a bad action: noop, wrong key, or close window
            error_actions = [
                {"action_type": "wait", "args": {"seconds": 0.1}},  # no-op
                {"action_type": "key", "args": {"key": "escape"}},  # cancel
                {"action_type": "type", "args": {"text": "wrong"}},  # wrong input
                {"action_type": "key", "args": {"key": "tab"}},  # wrong navigation
            ]
            return self.random.choice(error_actions)
        else:
            # Use correct action from naive clicker
            return self.naive_delegate.predict(instruction, obs)


def build_white_agent(agent_key: str, seed: int = 7) -> Any:
    """
    Build a white agent instance by key.
    
    Args:
        agent_key: Agent identifier (e.g., "naive_clicker", "bad_clicker")
        seed: Random seed for reproducibility
    
    Returns:
        White agent instance with reset() and predict() methods
    """
    key = agent_key.lower()
    if key == "naive_clicker":
        return NaiveClickerWhiteAgent(seed=seed)
    elif key == "bad_clicker":
        return BadClickerWhiteAgent(seed=seed)
    elif key.startswith("osworld_prompt"):
        if PromptAgent is None:
            raise RuntimeError(
                "OSWorld PromptAgent not available. Install OSWorld (pip install -e ../OSWorld) before using 'osworld_prompt'."
            )
        config = _parse_osworld_agent_config(agent_key)
        return OSWorldPromptWhiteAgent(**config)
    elif key.startswith("a2a::"):
        url = agent_key.split("::", 1)[1].strip()
        if not url:
            raise ValueError("A2A white agent URL cannot be empty (use format 'a2a::http://host:port').")
        if A2AClient is None:
            raise RuntimeError(
                "a2a package is not available. Install the AgentBeats SDK to use A2A white agents."
            )
        return A2AWhiteAgent(base_url=url)
    # TODO: add wrappers to mm_agents.* if you choose to demo a baseline
    print(f"[white_agent] {agent_key} not available; falling back to naive_clicker.")
    return NaiveClickerWhiteAgent(seed=seed)


def _parse_osworld_agent_config(agent_key: str) -> Dict[str, Any]:
    """Extract configuration options from a key like 'osworld_prompt:model=gpt-4o,obs=screenshot'."""
    defaults: Dict[str, Any] = {
        "model": "gpt-4o-mini",
        "observation_type": "screenshot",
        "action_space": "pyautogui",
        "platform": "ubuntu",
        "client_password": "password",
        "max_tokens": 1500,
        "top_p": 0.9,
        "temperature": 0.5,
    }

    if ":" not in agent_key:
        return defaults

    _, config_str = agent_key.split(":", 1)
    for item in config_str.split(","):
        if not item:
            continue
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in {"model", "observation_type", "action_space", "platform", "client_password"}:
            defaults[key] = value
        elif key in {"max_tokens"}:
            defaults[key] = int(value)
        elif key in {"top_p", "temperature"}:
            defaults[key] = float(value)
    return defaults


class OSWorldPromptWhiteAgent:
    """Wraps OSWorld's PromptAgent for use as a white agent."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        observation_type: str = "screenshot",
        action_space: str = "pyautogui",
        platform: str = "ubuntu",
        client_password: str = "password",
        max_tokens: int = 1500,
        top_p: float = 0.9,
        temperature: float = 0.5,
    ):
        if PromptAgent is None:
            raise RuntimeError("PromptAgent is unavailable; ensure OSWorld is installed.")
        self.action_space = action_space
        self._default_wait = 1.5
        self.agent = PromptAgent(
            platform=platform,
            model=model,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            action_space=action_space,
            observation_type=observation_type,
            client_password=client_password,
        )

    def reset(self):
        self.agent.reset()

    def predict(self, instruction: str, obs: Dict) -> Dict[str, Any] | str:
        observation = obs.get("observation") if isinstance(obs, dict) else None
        observation = observation if observation is not None else obs
        response, actions = self.agent.predict(instruction, observation)
        logger.debug("OSWorld agent response: %s", response)
        if not actions:
            return {"action_type": "wait", "args": {"seconds": self._default_wait}}

        action = actions[0]

        if isinstance(action, dict):
            upper_action = action.get("action", "").lower()
            if upper_action == "wait":
                seconds = action.get("time", self._default_wait)
                return {"action_type": "wait", "args": {"seconds": seconds}}
            if upper_action == "terminate":
                status = action.get("status", "success")
                return {"action_type": "done", "args": {"status": status}}
            if self.action_space == "computer_13":
                return {"action_type": "computer_13", "args": action}
            # For other dict responses, fall back to wait
            return {"action_type": "wait", "args": {"seconds": self._default_wait}}

        if isinstance(action, str):
            stripped = action.strip()
            upper = stripped.upper()
            if upper == "WAIT":
                return {"action_type": "wait", "args": {"seconds": self._default_wait}}
            if upper == "DONE":
                return {"action_type": "done", "args": {"status": "success"}}
            if upper == "FAIL":
                return {"action_type": "done", "args": {"status": "failure"}}
            if self.action_space == "pyautogui":
                return {"action_type": "pyautogui_code", "args": {"code": stripped}}

        # Default: treat as wait to avoid crashing the run loop
        return {"action_type": "wait", "args": {"seconds": self._default_wait}}


class A2AWhiteAgent:
    """
    Wrapper that proxies action decisions to a remote AgentBeats A2A service.
    
    Expects the remote agent to return a JSON object describing the action
    (same schema our evaluator uses) in the text body of the streaming response.
    """

    def __init__(self, base_url: str, timeout_seconds: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client: Optional[A2AClient] = None
        self._task_id: Optional[str] = None
        self._message_history: list[Dict[str, Any]] = []
        self.reset()

    async def _ensure_client(self) -> A2AClient:
        if self._client is not None:
            return self._client

        resolver = A2ACardResolver(base_url=self.base_url)
        card: AgentCard | None = await resolver.get_agent_card(
            relative_card_path="/.well-known/agent.json"
        )
        if card is None:
            raise RuntimeError(f"Failed to resolve agent card from {self.base_url}")
        self._client = A2AClient(agent_card=card)
        return self._client

    def reset(self):
        """Reset local conversation state (remote agent should handle new task IDs)."""
        self._task_id = uuid4().hex
        self._message_history.clear()

    def predict(self, instruction: str, obs: dict) -> dict:
        """
        Request an action from the remote agent via A2A.

        The payload sent to the agent includes the instruction, latest observation,
        and minimal conversation history for context.
        """
        text = json.dumps(
            {
                "instruction": instruction,
                "observation": obs,
                "history": self._message_history,
            },
            ensure_ascii=False,
        )
        response_text = asyncio.run(self._send_message(text))

        try:
            action = json.loads(response_text)
            if not isinstance(action, dict):
                raise ValueError("Action response must be a JSON object.")
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Remote agent returned non-JSON action: {response_text}"
            ) from exc

        # Persist exchange history for optional context in subsequent turns
        self._message_history.append(
            {"instruction": instruction, "observation": obs, "action": action}
        )
        return action

    async def _send_message(self, text: str) -> str:
        client = await self._ensure_client()
        task_id = self._task_id or uuid4().hex
        params = MessageSendParams(
            message=Message(
                role=Role.user,
                parts=[Part(TextPart(text=text))],
                messageId=uuid4().hex,
                taskId=task_id,
            )
        )
        request = SendStreamingMessageRequest(id=str(uuid4()), params=params)

        chunks: list[str] = []

        async for chunk in client.send_message_streaming(
            request, timeout_seconds=self.timeout_seconds
        ):
            if not isinstance(chunk.root, SendStreamingMessageSuccessResponse):
                continue
            event = chunk.root.result

            if isinstance(event, TaskArtifactUpdateEvent):
                for part in event.artifact.parts:
                    if hasattr(part, "root") and isinstance(part.root, TextPart):
                        chunks.append(part.root.text)
            elif isinstance(event, TaskStatusUpdateEvent):
                if event.status.message:
                    for part in event.status.message.parts:
                        if hasattr(part, "root") and isinstance(part.root, TextPart):
                            chunks.append(part.root.text)

        response = "".join(chunks).strip()
        if not response:
            raise RuntimeError(f"Remote agent {self.base_url} returned empty response.")
        return response
