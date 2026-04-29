#!/bin/bash
# Run the ADK agent from the command line (non-interactive)
# Usage: ./run_agent.sh "Your question here"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables if .env exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set."
    exit 1
fi

cd "$SCRIPT_DIR"
adk run multi_agent
