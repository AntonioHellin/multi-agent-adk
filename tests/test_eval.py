"""
Pytest-based evaluation for the ADK multi-agent system.

Uses AgentEvaluator from google.adk.evaluation to run test files
following the official ADK evaluation pattern.

Run with:
    pytest tests/test_eval.py -v
"""

import os

from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest


def _has_adk_model_credentials() -> bool:
    """Return True when live ADK evaluation has model credentials available."""
    has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
    uses_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    has_vertex_project = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    return has_api_key or (uses_vertex_ai and has_vertex_project)


live_adk_eval = pytest.mark.skipif(
    not _has_adk_model_credentials(),
    reason="Live ADK evaluation requires GOOGLE_API_KEY or Vertex AI credentials.",
)


@live_adk_eval
@pytest.mark.asyncio
async def test_greeter_agent():
    """Test the greeter sub-agent's ability to handle greetings and introductions."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/greeter.test.json",
    )


@live_adk_eval
@pytest.mark.asyncio
async def test_researcher_agent():
    """Test the researcher sub-agent's ability to answer factual questions with tools."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/researcher.test.json",
    )


@live_adk_eval
@pytest.mark.asyncio
async def test_all():
    """Run all test files in the tests directory."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/",
    )
