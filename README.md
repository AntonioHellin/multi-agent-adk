# google-adk-multi-agent

A modular, production-ready multi-agent system built with the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) featuring an orchestrator root agent and three specialized sub-agents.

## Overview

The system models conversational delegation using Google ADK and Google Gemini models (`gemini-3-flash-preview`). A centralized root agent acts as a router, analyzing incoming user requests and delegating to specialized sub-agents:

- **Root Agent (Orchestrator)**: Routes requests based on user intent and coordinates responses.
- **Greeter Agent**: Manages greetings, friendly conversation, and introductions.
- **Researcher Agent**: Answers factual queries via deterministic knowledge lookups and local system date/time tools.
- **Calculator Agent**: Evaluates mathematical expressions using AST-based safe evaluation without code execution risks.

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
google-adk-multi-agent/
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions evaluation and deployment pipeline
├── multi_agent/                  # ADK agent package
│   ├── __init__.py               # Package entry point exposing root_agent
│   ├── agent.py                  # Root orchestrator agent configuration
│   └── sub_agents/
│       ├── calculator/           # Calculator sub-agent and AST evaluator
│       │   ├── __init__.py
│       │   └── agent.py
│       ├── greeter/              # Greeter sub-agent
│       │   ├── __init__.py
│       │   └── agent.py
│       └── researcher/           # Researcher sub-agent and lookup tools
│           ├── __init__.py
│           └── agent.py
├── tests/                        # Unit tests and ADK evaluation suites
│   ├── greeter.test.json         # Greeter evaluation cases
│   ├── researcher.test.json      # Researcher evaluation cases
│   ├── test_config.json          # ADK evaluation criteria configuration
│   ├── test_agents.py            # Agent wiring, prompt, and tool verification
│   ├── test_calculator_tools.py  # Arithmetic AST safety tests
│   └── test_eval.py              # Pytest evaluation runner
├── .dockerignore                 # Docker build exclusions
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore definitions
├── Dockerfile                    # Container definition for Cloud Run
├── deploy_to_cloud_run.sh        # Deployment automation script
├── pyproject.toml                # Project packaging and metadata
├── requirements.txt              # Production and evaluation dependencies
├── run_agent.sh                  # Terminal interactive agent runner
└── start_dev_ui.sh               # Local ADK Dev UI launch script
```

## Quick Start

### Prerequisites

- Python 3.11+
- Google API key for Gemini models (`GOOGLE_API_KEY`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AntonioHellin/multi_agent_adk.git
   cd multi_agent_adk
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and supply your Google API Key and Cloud Project ID
   ```

### Running Locally

#### 1. ADK Dev UI
Launch the interactive browser UI for agent testing and visualization:
```bash
./start_dev_ui.sh
# Open http://localhost:8000 in your browser
```

#### 2. Terminal Mode
Interact with the root agent directly in your console:
```bash
./run_agent.sh
```

## Security & Arithmetic Safety

### Safe AST Evaluation
The calculator agent rejects arbitrary Python execution. Expressions are parsed into an Abstract Syntax Tree (AST) via Python's built-in `ast` module. Only whitelisted numeric constants, unary operators (`+`, `-`), and binary arithmetic operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`) are processed. Calls, imports, attribute access, and excessively large exponents are rejected deterministically before execution.

### Secrets Protection
Never commit `.env` or cloud service credentials. Use Secret Manager or environment variables when deploying to production environments.

## Testing & Evaluation

### Unit Tests
Verify agent wiring, deterministic tools, and configuration without incurring API costs:
```bash
pytest tests/test_agents.py tests/test_calculator_tools.py -v
```

### ADK Live Evaluation
Run conversational evaluations against reference trajectories:
```bash
# Using pytest
pytest tests/test_eval.py -v

# Using ADK CLI
adk eval multi_agent tests/greeter.test.json tests/researcher.test.json --config_file_path=tests/test_config.json --print_detailed_results
```

## Deployment

### Cloud Run Deployment
Deploy the containerized service directly to Google Cloud Run:
```bash
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### CI/CD Automation
The included GitHub Actions workflow (`.github/workflows/ci-cd.yml`) executes on pushes to `main`:
1. Executes agent tests and ADK evaluations with pytest.
2. Authenticates to GCP using Workload Identity or Service Account keys.
3. Builds and pushes container images to Google Container Registry (GCR).
4. Deploys to Google Cloud Run and validates service health with an automated smoke test.

## License

Proprietary / All Rights Reserved.
