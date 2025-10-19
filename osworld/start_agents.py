#!/usr/bin/env python3
"""
AgentBeats Scenario Agent Launcher for OSWorld.

Starts the green evaluator agent (and optional companions) using the AgentBeats
CLI so that local development mirrors the hosted battle environment.
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Optional


SCENARIO_NAME = "osworld"

AGENT_COMMANDS = [
    {
        "name": "[OSWorld] Green Evaluator",
        "command": (
            "agentbeats run agents/green_agent/agent_card_osworld.toml "
            "--launcher_port 8450 --agent_port 8451 "
            "--backend http://localhost:9000 "
            "--tool agents/green_agent/tools.py "
            "--mcp http://localhost:9101/sse"
        ),
    }
]


class AgentLauncher:
    def __init__(self):
        self.processes = []
        self.project_dir = Path(__file__).resolve().parents[1]
        self.scenario_dir = Path(__file__).parent
        self.venv_command = f"source {self.project_dir}/venv/bin/activate"

    def _open_mac_terminal(self, name: str, full_command: str) -> bool:
        """Attempt to open command in macOS Terminal or iTerm."""
        apple_script_terminal = f"""
        tell application "Terminal"
            activate
            do script "{full_command}"
        end tell
        """
        try:
            subprocess.Popen(["osascript", "-e", apple_script_terminal])
            return True
        except Exception:
            apple_script_iterm = f"""
            tell application "iTerm"
                activate
                set newWindow to (create window with default profile)
                tell current session of newWindow
                    write text "{full_command}"
                end tell
            end tell
            """
            try:
                subprocess.Popen(["osascript", "-e", apple_script_iterm])
                return True
            except Exception:
                return False

    def start_agent_in_terminal(self, agent_config: dict) -> None:
        """Start agent in a separate terminal window."""
        name = agent_config["name"]
        command = agent_config["command"]
        print(f"Starting {name}...")

        system = platform.system()
        if system == "Windows":
            full_cmd = f'start cmd /k "title {name} && {command}"'
            subprocess.Popen(full_cmd, shell=True, cwd=self.scenario_dir)
            return

        if system == "Darwin":
            full_command = f"{self.venv_command} && cd '{self.scenario_dir}' && {command}"
            if self._open_mac_terminal(name, full_command):
                print("  (Opened in macOS terminal)")
            else:
                print(
                    f"  Warning: could not open a new terminal window for {name}. "
                    f"Run manually:\n{full_command}"
                )
            return

        # Linux
        terminal_cmds = [
            ["gnome-terminal", "--", "bash", "-c"],
            ["xterm", "-e", "bash", "-c"],
            ["konsole", "-e", "bash", "-c"],
            ["xfce4-terminal", "-e", "bash", "-c"],
        ]
        full_cmd = f"{command}; exec bash"
        for term_cmd in terminal_cmds:
            try:
                subprocess.Popen(term_cmd + [full_cmd], cwd=self.scenario_dir)
                return
            except FileNotFoundError:
                continue

        print(
            f"Warning: could not open terminal window for {name}. "
            f"Run manually:\n{command}"
        )

    def start_agent_in_current_terminal(self, agent_config: dict) -> None:
        """Start agent in the current terminal (background process)."""
        name = agent_config["name"]
        command = agent_config["command"]
        print(f"Starting {name} in current terminal...")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=self.scenario_dir,
            shell=True,
        )
        self.processes.append((name, process))

        def handle_output(agent_name: str, proc: subprocess.Popen) -> None:
            while True:
                output = proc.stdout.readline()
                if output == "" and proc.poll() is not None:
                    break
                if output:
                    print(f"[{agent_name}] {output.strip()}")

        thread = threading.Thread(target=handle_output, args=(name, process))
        thread.daemon = True
        thread.start()

    def start_all_agents(
        self, separate_terminals: bool = True, selected_agents: Optional[List[str]] = None
    ) -> None:
        agents_to_start = AGENT_COMMANDS
        if selected_agents:
            lowered = {s.lower() for s in selected_agents}
            agents_to_start = [
                agent
                for i, agent in enumerate(AGENT_COMMANDS)
                if str(i) in lowered or agent["name"].lower() in lowered
            ]

        if separate_terminals:
            print(f"Starting {len(agents_to_start)} agent(s) in separate terminals.")
            for agent in agents_to_start:
                self.start_agent_in_terminal(agent)
                time.sleep(1)
            print("All agents launched (check the opened terminals).")
            return

        print(f"Starting {len(agents_to_start)} agent(s) in current terminal.")
        try:
            for agent in agents_to_start:
                self.start_agent_in_current_terminal(agent)

            print("All agents started. Press Ctrl+C to stop.")
            for _, process in self.processes:
                process.wait()
        except KeyboardInterrupt:
            print("\nStopping agents...")
            for name, process in self.processes:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait()
            print("Agents stopped.")

    def show_commands(self) -> None:
        print(f"\n{SCENARIO_NAME} Scenario Agent Commands")
        print("=" * 40)
        for i, agent in enumerate(AGENT_COMMANDS, start=1):
            print(f"\n{i}. {agent['name']}")
            print(f"   {agent['command']}")
        print(f"\nRun from {self.scenario_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"Launch {SCENARIO_NAME} scenario agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_agents.py                 # Start agent(s) in separate terminals
  python start_agents.py --current       # Start in current terminal
  python start_agents.py --show          # Print commands only
        """,
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help="Start agents in current terminal.",
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        help="Start specific agents (index or name match).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show commands without running.",
    )

    args = parser.parse_args()
    launcher = AgentLauncher()

    if args.show:
        launcher.show_commands()
        return

    launcher.start_all_agents(
        separate_terminals=not args.current, selected_agents=args.agents
    )


if __name__ == "__main__":
    main()
