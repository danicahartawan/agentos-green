# Green Agent - OSWorld × AgentBeats Evaluator

A hosting evaluator that:
1. **Loads** a set of OSWorld tasks
2. **Orchestrates** runs by one or more White Agents on those tasks
3. **Scores** them with deterministic, execution-based checks (and OSWorld's native eval functions when available)
4. **Produces** reproducible metrics, artifacts, and summary reports

## Architecture

```
green_agent/
├── __init__.py                 # Package initialization
├── config.py                   # GreenAgentConfig dataclass
├── task_loader.py              # Load & filter OSWorld tasks
├── white_agent_runner.py       # Execute white agents on tasks
├── scorer.py                   # Aggregate results & calculate metrics
├── reporter.py                 # Generate report artifacts
└── evaluator.py                # Main orchestrator (GreenAgentEvaluator)
```

The AgentBeats-facing assets live in the `osworld/` directory:

```
osworld/
├── scenario.toml               # AgentBeats scenario definition
├── start_agents.py             # Helper launcher (calls agentbeats run …)
├── agents/
│   └── green_agent/
│       ├── agent_card_osworld.toml
│       └── tools.py            # MCP tool handlers (run_osworld_suite, …)
└── resources/
    └── mcp_server.py           # Logging / artifact MCP server
```

## Usage

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure OSWorld is available (for PromptAgent + task assets)
export PYTHONPATH="/path/to/OSWorld:${PYTHONPATH}"

# (Optional) export LLM credentials for the white agent
export OPENAI_API_KEY=...
```

### Local Benchmark Run

```bash
# Evaluate the curated tasks in green_tasks_5.json
python run_green_agent.py \
    --tasks-file green_tasks_5.json \
    --white-agents osworld_prompt:model=gpt-4o,observation_type=screenshot,action_space=pyautogui \
    --provider vmware \
    --path-to-vm /path/to/Ubuntu.vmx \
    --client-password password \
    --pause-after-action 3
```

### Alternate White Agents

```bash
# Built-in PromptAgent wrapper with a different model / action space
python run_green_agent.py \
    --tasks-file green_tasks_5.json \
    --white-agents osworld_prompt:model=gemini-2.5-flash,observation_type=screenshot,action_space=computer_13 \
    --provider vmware \
    --path-to-vm /path/to/Ubuntu.vmx
```

#### Remote (A2A) White Agent

To proxy decisions to a remotely hosted AgentBeats A2A service, use the special
`a2a::` prefix in the `--white_agents` flag:

```bash
python run_green_agent.py \
    --white_agents a2a::http://localhost:8061 \
    --provider vmware \
    --path-to-vm /path/to/Ubuntu.vmx \
    --client-password password
```

The remote agent must return an OSWorld action JSON payload in response to each
message. Make sure the AgentBeats SDK (`a2a` package) is installed locally so
the wrapper can resolve the remote agent card.

#### OSWorld Prompt Agent Wrapper

To reuse OSWorld's GPT-powered baseline directly, select the special
`osworld_prompt` key (requires the OSWorld repository on `PYTHONPATH` and
relevant LLM credentials):

```bash
python run_green_agent.py \
    --white_agents osworld_prompt:model=gpt-4o,observation_type=screenshot,action_space=pyautogui \
    --provider vmware \
    --path-to-vm /path/to/Ubuntu.vmx \
    --client-password password \
    --pause-after-action 3
```

You can override additional parameters (for example `observation_type` or
`temperature`) by adding comma-separated `key=value` pairs after the colon.

## Configuration

Key configuration parameters:

**Task Selection:**
- `--domains`: Filter by domain(s)
- `--task_ids`: Filter by specific task ID(s)

**White Agent:**
- `--white_agent_type`: Agent class (default: `PromptAgent`)
- `--white_agent_module`: Module path (default: `mm_agents.agent`)
- `--model`: Model name (e.g., `gpt-4o`, `claude-3-opus`)

**Environment:**
- `--provider`: `docker`, `vmware`, `aws`, `azure`, `virtualbox`
- `--headless`: Run without GUI
- `--path-to-vm`: VM image or snapshot path (provider specific)

**Execution:**
- `--max-steps`: Max steps per task (default: 50)
- `--action_space`: `pyautogui` or `computer_13`
- `--observation_type`: `screenshot`, `a11y_tree`, etc.
- `--pause-after-action`: Sleep after each action (seconds)
- `--timeout-sec`: Max wall-clock per task

**Output:**
- `--results-root`: Results directory (default: `./results`)
- `--reports-root`: Reports directory (default: `./reports`)

**Modes:**
- `--headless`: Run without VMware GUI
- `--require-a11y-tree`: Request accessibility tree in each observation

## Output Structure

### Results Directory
```
results/
└── {action_space}/
    └── {observation_type}/
        └── {model}/
            └── {domain}/
                └── {task_id}/
                    ├── result.txt           # Score (0.0 to 1.0)
                    ├── traj.jsonl          # Action trajectory
                    ├── step_*.png          # Screenshots
                    ├── recording.mp4       # Video recording
                    └── runtime.log         # Execution logs
```

### Reports Directory
```
reports/
└── {run_name}/
    ├── report.json              # Complete JSON report
    ├── report.md                # Markdown summary
    ├── results_per_task.csv     # Per-task results
    └── results_per_domain.csv   # Per-domain summary
```

## Design Notes

### Reuses OSWorld Infrastructure

- **Task definitions**: `evaluation_examples/test_all.json` and task JSONs
- **White agents**: `mm_agents/agent.py` interface
- **Environment**: `desktop_env.DesktopEnv` class
- **Execution**: `lib_run_single.run_single_example()`
- **Evaluation**: Native OSWorld evaluator functions
- **Patterns**: Multiprocessing from `run_multienv.py`, scoring from `show_result.py`

### Non-Invasive Design

- Zero modifications to core OSWorld code
- All new code in `green_agent/` directory
- Compatible with existing result structures
- Uses standard OSWorld configuration patterns

## Development Status

**Implemented:**
- ✅ Full scaffold and structure
- ✅ Configuration system
- ✅ Task loading and filtering
- ✅ Sequential execution
- ✅ Result aggregation and scoring
- ✅ Report generation (JSON, Markdown, CSV)
- ✅ Dry run mode
- ✅ Resume from checkpoint

**TODO (see code comments):**
- ⏳ Parallel execution (currently falls back to sequential)
- ⏳ Advanced error handling
- ⏳ Additional telemetry / dashboards

## Example Output

```
================================================================================
EVALUATION SUMMARY
================================================================================

Overall Results:
  Success Rate: 67.39%
  Total Tasks: 46
  Successful: 31
  Failed: 15

Results by Category:
  Daily: 67.39%

Execution Time: 3420.15s (57.00 minutes)
Report Directory: ./reports/green_agent_gpt-4o_20251018_103612
================================================================================
```

## Integration with AgentBeats

The project ships an AgentBeats-ready scenario so the green evaluator can be
launched like any other hosting agent:

1. `osworld/scenario.toml` registers the `[OSWorld] Green Evaluator` and points
   at the agent card, tool module (`osworld/agents/green_agent/tools.py`), and
   MCP server (`osworld/resources/mcp_server.py`).
2. `osworld/start_agents.py` is the helper launcher. It runs
   `agentbeats run agents/green_agent/agent_card_osworld.toml ...` so the agent
   is ready to accept battles.
3. When AgentBeats calls `run_osworld_suite`, the tool constructs a
   `GreenEvaluator`, boots DesktopEnv, drives the white agent (PromptAgent
   wrapper or A2A proxy), and writes metrics/artifacts under `reports/`.
4. Status updates and artifacts are pushed back over MCP via
   `update_battle_process` and `store_battle_artifact`, so the standard
   AgentBeats dashboards record progress.

For local testing you can run `python osworld/start_agents.py` alongside
`python osworld/resources/mcp_server.py --port 9101`, then trigger
assessments from the AgentBeats CLI/UI.
2. **Reproducible Metrics**: Deterministic scoring with detailed artifacts
3. **Flexible Configuration**: Support for various white agents and models
4. **Comprehensive Reporting**: Multiple output formats for analysis

## License

Follows OSWorld's Apache 2.0 license.
