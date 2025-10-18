# Green Agent - OSWorld × AgentBeats Evaluator

**Green Agent**: A hosting evaluator that **(i)** loads a set of OSWorld tasks, **(ii)** orchestrates runs by one or more White Agents on those tasks, and **(iii)** scores them with deterministic, execution-based checks (producing reproducible metrics, artifacts, and summary reports).

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OSWorld repository (for tasks and environment)

### Installation

```bash
# Clone this repository
git clone https://github.com/danicahartawan/agentos-green.git
cd agentos-green

# Install dependencies
pip install -r requirements.txt

# Clone OSWorld (for task definitions and environment)
cd ..
git clone https://github.com/xlang-ai/OSWorld.git
cd OSWorld
pip install -r requirements.txt
```

### Usage

```bash
# Dry run to validate configuration
python run_green_agent.py --dry_run --domains chrome

# Run evaluation (requires OSWorld environment setup)
python run_green_agent.py \
    --domains chrome os \
    --white_agents naive_clicker \
    --repeats 3 \
    --max_steps 50
```

## 📁 Structure

```
green_agent/
├── __init__.py              # Package exports
├── config.py                # Config dataclass + from_args()
├── task_loader.py           # Load OSWorld tasks
├── white_agent_runner.py    # White agent interface + NaiveClicker
├── scorer.py                # Native-first evaluation + combine()
├── reporter.py              # JSON/JSONL + console tables
└── evaluator.py             # GreenEvaluator orchestrator

run_green_agent.py           # CLI entry point
reports/                     # Output directory
```

## 🎯 Key Features

- ✅ **No OSWorld modifications**: All code in `green_agent/` directory
- ✅ **Deterministic evaluation**: Execution-based, no LLM judgment
- ✅ **Reproducible**: Seed-based, with full artifacts
- ✅ **Multiple white agents**: Easy to add custom agents
- ✅ **Comprehensive reporting**: JSON, JSONL, console tables

## 📊 Output

### Reports Directory
```
reports/
├── runs/{agent_name}/{task_id}.jsonl  # Per-task JSONL logs
└── {run_name}/
    ├── report.json                     # Complete results
    ├── agent_summary.json              # Per-agent metrics
    └── combined_report.json            # Multi-agent comparison
```

### Results (OSWorld-compatible)
```
results/{action_space}/{observation_type}/{model}/{domain}/{task_id}/
├── result.txt
├── traj.jsonl
├── step_*.png
└── recording.mp4
```

## 🔧 Configuration

See `green_agent/config.py` for all options:
- `provider`: VM provider (docker, vmware, aws, etc.)
- `domains`: List of domains to evaluate
- `white_agents`: List of agent keys
- `repeats`: Number of repetitions per task
- `max_steps`: Maximum steps per task
- `seed`: Random seed for reproducibility

## 📚 Documentation

- **Green Agent**: `green_agent/README.md`
- **OSWorld**: https://github.com/xlang-ai/OSWorld

## 🤝 Integration

### With OSWorld
- Uses OSWorld task definitions from `evaluation_examples/`
- Compatible with OSWorld's native evaluators
- Outputs to OSWorld-compatible `results/` structure

### With AgentBeats
- Hosting evaluator interface
- Deterministic, execution-based scoring
- Reproducible metrics and artifacts

## 📝 License

Apache 2.0 (following OSWorld)

## 🙏 Acknowledgments

Built on top of [OSWorld](https://github.com/xlang-ai/OSWorld) by the xlang-ai team.

