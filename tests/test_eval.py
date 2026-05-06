"""
Pytest-based evaluation for the ADK multi-agent system.

Uses AgentEvaluator from google.adk.evaluation to run test files
following the official ADK evaluation pattern.

Run with:
    pytest tests/test_eval.py -v
"""

from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest


@pytest.mark.asyncio
async def test_greeter_agent():
    """Test the greeter sub-agent's ability to handle greetings and introductions."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/greeter.test.json",
    )


@pytest.mark.asyncio
async def test_researcher_agent():
    """Test the researcher sub-agent's ability to answer factual questions with tools."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/researcher.test.json",
    )


# Keep this aggregate test in addition to the focused tests above: ADK accepts
# a directory of evaluation fixtures, which helps catch cross-fixture regressions
# when new scenarios are added under tests/.
@pytest.mark.asyncio
async def test_all():
    """Run all test files in the tests directory."""
    await AgentEvaluator.evaluate(
        agent_module="multi_agent",
        eval_dataset_file_path_or_dir="tests/",
    )
