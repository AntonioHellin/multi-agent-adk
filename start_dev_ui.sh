#!/bin/bash
# Start the ADK Dev UI for the multi-agent system
# This launches a web interface for testing and debugging agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables if .env exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

# Check for GOOGLE_API_KEY
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set."
    echo "Please set it in your .env file or export it:"
    echo "  export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

# Install dependencies if not already installed
if ! python -c "import google.adk" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Starting ADK Dev UI..."
echo "Agent directory: $SCRIPT_DIR"
echo ""

# Launch the ADK web UI pointing to the current directory
# The UI will auto-discover the multi_agent package
cd "$SCRIPT_DIR"
adk web .
