# OSWorld AgentBeats Scenario

This scenario turns the `green_agent` evaluator package into an AgentBeats green agent
so you can run OSWorld desktop benchmarks inside the AgentBeats battle flow.

## Layout

```
osworld/
├── README.md
├── scenario.toml                # Scenario configuration for `agentbeats launch`
├── start_agents.py             # Helper launcher for local development
├── agents/
│   └── green_agent/
│       ├── agent_card_osworld.toml  # Green agent configuration & prompt
│       └── tools.py                  # Tool functions exposed to the agent
└── resources/
    └── mcp_server.py           # Lightweight MCP server for logging/artifacts
```

## Prerequisites

- Python environment with `agentbeats`, `fastmcp`, and OSWorld dependencies installed.
- OSWorld task assets checked out (e.g., clone `xlang-ai/OSWorld` alongside this repo).
- AgentBeats backend running at `http://localhost:9000` (adjust in `scenario.toml`/`mcp_server.py` if different).

## Local Quick Start

1. Start the MCP server:
   ```bash
   cd osworld/resources
   python mcp_server.py --port 9101
   ```
2. Launch the green agent:
   ```bash
   cd osworld
   python start_agents.py
   ```
3. From the AgentBeats CLI or UI, trigger a battle targeting the `[OSWorld] Green Evaluator`.
   The agent will call the tools to run the evaluation, log progress via MCP, and store reports
   under `reports/agentbeats/{battle_id}/`.

## Notes

- The default task list is `green_tasks_5.json`. Provide a custom task file or domain filter
  through the `run_osworld_suite` tool parameters when needed.
- The evaluator now drives OSWorld's `DesktopEnv` directly, so make sure the provider
  configuration (VM images, credentials, etc.) is valid before launching a battle.
- `run_osworld_suite` accepts additional keyword arguments (provider, action space,
  headless, pause timing, etc.) so you can match the deployment requirements of your
  DesktopEnv setup.
