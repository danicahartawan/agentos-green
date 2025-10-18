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
├── reporter.py                 # Generate reports (JSON, Markdown, CSV)
└── evaluator.py                # Main orchestrator (GreenAgentEvaluator)
```

## Usage

### Quick Start (Dry Run)

```bash
# Test configuration without execution
python run_green_agent.py --dry_run --domains chrome
```

### Run Evaluation

```bash
# Basic evaluation on all tasks
python run_green_agent.py \
    --model gpt-4o \
    --provider_name docker \
    --headless

# Evaluate specific domains
python run_green_agent.py \
    --model gpt-4o \
    --domains chrome libreoffice_calc \
    --provider_name docker

# Parallel execution
python run_green_agent.py \
    --model gpt-4o \
    --num_parallel_envs 10 \
    --provider_name aws \
    --region us-east-1
```

### Custom White Agent

```bash
python run_green_agent.py \
    --white_agent_module mm_agents.custom_agent \
    --white_agent_type CustomAgent \
    --model claude-3-opus
```

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
- `--provider_name`: `docker`, `vmware`, `aws`, `azure`, `virtualbox`
- `--headless`: Run without GUI
- `--num_parallel_envs`: Parallel execution (default: 1)

**Execution:**
- `--max_steps`: Max steps per task (default: 15)
- `--action_space`: `pyautogui` or `computer_13`
- `--observation_type`: `screenshot`, `a11y_tree`, etc.

**Output:**
- `--result_dir`: Results directory (default: `./results`)
- `--report_dir`: Reports directory (default: `./reports`)
- `--run_name`: Custom run name (auto-generated if not provided)

**Modes:**
- `--dry_run`: Validate configuration without execution
- `--no_resume`: Don't skip completed tasks

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
- ⏳ Progress tracking with tqdm
- ⏳ Result caching
- ⏳ Custom evaluator plugins
- ⏳ More statistical metrics

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

Green Agent is designed to integrate seamlessly with the AgentBeats evaluation framework:

1. **Standardized Interface**: Compatible with AgentBeats hosting evaluator requirements
2. **Reproducible Metrics**: Deterministic scoring with detailed artifacts
3. **Flexible Configuration**: Support for various white agents and models
4. **Comprehensive Reporting**: Multiple output formats for analysis

## Contributing

When adding features:
1. Follow existing code structure and patterns
2. Add TODOs for incomplete implementations
3. Maintain compatibility with OSWorld infrastructure
4. Update this README with new capabilities

## License

Follows OSWorld's Apache 2.0 license.

