# Module 7 - Google ADK Multi-Agent System

A simple multi-agent system built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) featuring a root orchestrator agent with three specialized sub-agents.

## Features

- **Multi-Agent Architecture**: Root agent orchestrates three specialized sub-agents
- **Greeter Agent**: Handles greetings, introductions, and casual conversation
- **Researcher Agent**: Answers factual questions with tool-backed knowledge lookups
- **Calculator Agent**: Safely evaluates arithmetic expressions with a deterministic tool
- **ADK Dev UI**: Built-in web interface for testing and debugging agents
- **Evaluation Suite**: Automated tests for agent quality
- **Cloud Run Deployment**: Containerized deployment to Google Cloud Run
- **CI/CD Pipeline**: GitHub Actions workflow with evaluation gate + auto-deploy

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Root Agent                          │
│                       (Orchestrator)                        │
│              Delegates based on user intent                 │
└──────────┬──────────────────┬───────────────┬───────────────┘
           │                  │               │
    ┌──────▼──────┐    ┌──────▼──────┐ ┌──────▼──────┐
    │   Greeter   │    │ Researcher  │ │ Calculator  │
    │   Agent     │    │   Agent     │ │   Agent     │
    │             │    │             │ │             │
    │ - Greetings │    │ - Facts     │ │ - Arithmetic│
    │ - Intros    │    │ - Lookups   │ │ - Safe eval │
    │ - Casual    │    │ - Date/Time │ │ - Math      │
    └─────────────┘    └─────────────┘ └─────────────┘
```

## Project Structure

```
module-7/
├── multi_agent/                  # ADK agent package
│   ├── __init__.py               # Exposes root_agent
│   ├── agent.py                  # Root orchestrator agent
│   └── sub_agents/
│       ├── calculator/
│       │   ├── __init__.py
│       │   └── agent.py          # Calculator sub-agent (safe arithmetic tool)
│       ├── greeter/
│       │   ├── __init__.py
│       │   └── agent.py          # Greeter sub-agent
│       └── researcher/
│           ├── __init__.py
│           └── agent.py          # Researcher sub-agent (with tools)
├── tests/                        # ADK evaluation tests
│   ├── greeter.test.json         # Greeter agent eval cases
│   ├── researcher.test.json      # Researcher agent eval cases
│   ├── test_config.json          # Evaluation criteria config
│   ├── test_calculator_tools.py   # Unit tests for calculator tool safety
│   └── test_eval.py              # Pytest test runner
├── start_dev_ui.sh               # Launch ADK Dev UI
├── run_agent.sh                  # Run agent in terminal
├── deploy_to_cloud_run.sh        # Deploy to Cloud Run
├── Dockerfile                    # Container image for Cloud Run
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # CI/CD pipeline
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Google API Key (Gemini)

### 1. Set up environment

```bash
cd module-7

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Run the ADK Dev UI

```bash
chmod +x start_dev_ui.sh
./start_dev_ui.sh
```

This launches the ADK web interface at `http://localhost:8000` where you can:
- Chat with your agents in real-time
- See which sub-agent handles each request
- Inspect tool calls and agent delegation
- Debug agent behavior

### 3. Run from command line

```bash
chmod +x run_agent.sh
./run_agent.sh
```

### 4. Run evaluations

You can run evaluations in three ways following the [official ADK evaluation docs](https://google.github.io/adk-docs/evaluate/):

**Option A: pytest (recommended for CI/CD)**
```bash
python3 -m pytest tests/test_eval.py -v
```

**Option B: ADK CLI**
```bash
adk eval \
    multi_agent \
    tests/greeter.test.json tests/researcher.test.json \
    --config_file_path=tests/test_config.json \
    --print_detailed_results
```

**Option C: ADK Web UI**
```bash
adk web .
# Navigate to the Eval tab in the web interface
```


### Calculator Tool Safety

The calculator sub-agent uses a deterministic `calculate_expression` tool instead of relying on the language model for arithmetic. The tool parses expressions with Python's `ast` module and only permits numeric literals, parentheses, and basic arithmetic operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`). Function calls, imports, variable access, and other Python code are rejected before evaluation.

## Evaluation

The evaluation follows the [ADK evaluation framework](https://google.github.io/adk-docs/evaluate/) using `.test.json` files backed by the EvalSet/EvalCase Pydantic schema.

### Test Files

| File | Agent | Eval Cases |
|------|-------|------------|
| `greeter.test.json` | Greeter | `greeting_hello`, `greeting_introduction` |
| `researcher.test.json` | Researcher | `research_python`, `research_kubernetes`, `research_adk` |
| `test_calculator_tools.py` | Calculator | Tool-level tests for arithmetic, safety, and errors |

### Evaluation Criteria (`test_config.json`)

| Criteria | Threshold | Description |
|----------|-----------|-------------|
| `tool_trajectory_avg_score` | 1.0 | Exact match of expected tool call trajectory |
| `response_match_score` | 0.2 | ROUGE-1 similarity to reference response |

Each test case defines:
- **`user_content`**: The user query
- **`final_response`**: Expected agent response (used for `response_match_score`)
- **`intermediate_data.tool_uses`**: Expected tool call trajectory (used for `tool_trajectory_avg_score`)
- **`intermediate_data.intermediate_responses`**: Expected sub-agent responses

The `test_config.json` file is auto-discovered by the ADK evaluation framework from the same directory as the `.test.json` files.

## Deployment

### Manual deployment to Cloud Run

```bash
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs automatically on pushes to `main` affecting `module-7/`:

1. **Evaluate** — Installs deps, runs `python3 -m pytest tests/test_eval.py` and `adk eval`, uploads results as artifact
2. **Deploy** — Only if evals pass and on `main` branch:
   - Builds Docker image
   - Pushes to Google Container Registry
   - Deploys to Cloud Run
   - Runs a smoke test

#### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `GOOGLE_API_KEY` | Google API key for Gemini |
| `GCP_PROJECT_ID` | Google Cloud project ID |
| `GCP_SA_KEY` | Service account JSON key for Cloud Run deployment |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | API key for Gemini models |
| `GOOGLE_CLOUD_PROJECT` | For deploy | GCP project ID |
| `GOOGLE_CLOUD_REGION` | For deploy | GCP region (default: `us-central1`) |
