---
name: researchclaw
version: 1.0.0
description: |
  Autonomous research pipeline skill for Claude Code. Given a research topic, orchestrates 23 stages end-to-end: literature review, hypothesis generation, experiment design, code generation & sandbox execution, statistical analysis, paper writing, multi-agent peer review, and conference-ready LaTeX export. No babysitting required.
tags: ["research", "paper-writing", "autonomous", "pipeline", "academic", "latex", "experiment"]
---

# ResearchClaw — Autonomous Research Pipeline Skill

## Description

Run ResearchClaw's 23-stage autonomous research pipeline. Given a research topic, this skill orchestrates the entire research workflow: literature review → hypothesis generation → experiment design → code generation & execution → result analysis → paper writing → peer review → final export.

## Trigger Conditions

Activate this skill when the user:
- Asks to "research [topic]", "write a paper about [topic]", or "investigate [topic]"
- Wants to run an autonomous research pipeline
- Asks to generate a research paper from scratch
- Mentions "ResearchClaw" by name

## Instructions

### Prerequisites Check

1. Verify config file exists:
   ```bash
   ls config.yaml || ls config.researchclaw.example.yaml
   ```
2. If no `config.yaml`, create one from the example:
   ```bash
   cp config.researchclaw.example.yaml config.yaml
   ```
3. Ensure the user's LLM API key is configured in `config.yaml` under `llm.api_key` or via `llm.api_key_env` environment variable.

### Running the Pipeline

**Option A: CLI (recommended)**

```bash
researchclaw run --topic "Your research topic here" --auto-approve
```

Options:
- `--topic` / `-t`: Override the research topic from config
- `--config` / `-c`: Config file path (default: `config.yaml`)
- `--output` / `-o`: Output directory (default: `artifacts/rc-YYYYMMDD-HHMMSS-HASH/`)
- `--from-stage`: Resume from a specific stage (e.g., `PAPER_OUTLINE`)
- `--auto-approve`: Auto-approve gate stages (5, 9, 20) without human input

**Option B: Python API**

```python
from researchclaw.pipeline.runner import execute_pipeline
from researchclaw.config import RCConfig
from researchclaw.adapters import AdapterBundle
from pathlib import Path

config = RCConfig.load("config.yaml", check_paths=False)
results = execute_pipeline(
    run_dir=Path("artifacts/my-run"),
    run_id="research-001",
    config=config,
    adapters=AdapterBundle(),
    auto_approve_gates=True,
)

# Check results
for r in results:
    print(f"Stage {r.stage.name}: {r.status.value}")
```

**Option C: Iterative Pipeline (multi-round improvement)**

```python
from researchclaw.pipeline.runner import execute_iterative_pipeline

results = execute_iterative_pipeline(
    run_dir=Path("artifacts/my-run"),
    run_id="research-001",
    config=config,
    adapters=AdapterBundle(),
    max_iterations=3,
    convergence_rounds=2,
)
```

### Output Structure

After a successful run, the output directory contains:

```
artifacts/<run-id>/
├── stage-1/                # TOPIC_INIT outputs
├── stage-2/                # PROBLEM_DECOMPOSE outputs
├── ...
├── stage-10/
│   └── experiment.py       # Generated experiment code
├── stage-12/
│   └── runs/run-1.json     # Experiment execution results
├── stage-14/
│   ├── experiment_summary.json  # Aggregated metrics
│   └── results_table.tex        # LaTeX results table
├── stage-17/
│   └── paper_draft.md      # Full paper draft
├── stage-22/
│   └── charts/             # Generated visualizations
│       ├── metric_trajectory.png
│       └── experiment_comparison.png
└── pipeline_summary.json   # Overall pipeline status
```

### Experiment Modes

| Mode | Description | Config |
|------|-------------|--------|
| `simulated` | LLM generates synthetic results (no code execution) | `experiment.mode: simulated` |
| `sandbox` | Execute generated code locally via subprocess | `experiment.mode: sandbox` |
| `ssh_remote` | Execute on remote GPU server via SSH | `experiment.mode: ssh_remote` |

### Troubleshooting

- **Config validation error**: Run `researchclaw validate --config config.yaml`
- **LLM connection failure**: Check `llm.base_url` and API key
- **Sandbox execution failure**: Verify `experiment.sandbox.python_path` exists and has numpy installed
- **Gate rejection**: Use `--auto-approve` or manually approve at stages 5, 9, 20

## Tools Required

- File read/write (for config and artifacts)
- Bash (for CLI execution)
- No external MCP servers required for basic operation
