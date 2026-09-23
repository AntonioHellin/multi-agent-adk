"""Unit and integration tests for the critical multi-agent configuration.

These tests intentionally avoid live model calls so they can run quickly and
reliably in CI while covering the deterministic behavior that the ADK runtime
relies on: agent wiring, tool registration, tool output contracts, and eval
fixture consistency.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from multi_agent.agent import root_agent
from multi_agent.sub_agents.calculator import calculator_agent
from multi_agent.sub_agents.calculator.agent import calculate_expression
from multi_agent.sub_agents.greeter import greeter_agent
from multi_agent.sub_agents.researcher import researcher_agent
from multi_agent.sub_agents.researcher.agent import get_current_date, lookup_topic

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests"
EXPECTED_MODEL = "gemini-3-flash-preview"


@pytest.mark.parametrize(
    ("agent", "expected_name", "expected_description", "required_instruction_terms"),
    [
        (
            root_agent,
            "root_agent",
            "orchestrator",
            ("delegate", "greeter", "researcher", "calculator", "Always delegate"),
        ),
        (
            greeter_agent,
            "greeter",
            "greetings",
            ("friendly greeter", "greet", "capabilities", "researcher assistant"),
        ),
        (
            researcher_agent,
            "researcher",
            "factual questions",
            ("lookup_topic", "get_current_date", "Always use the available tools"),
        ),
        (
            calculator_agent,
            "calculator",
            "arithmetic",
            ("calculator assistant", "arithmetic", "calculate_expression"),
        ),
    ],
)
def test_agent_metadata_and_instructions_are_configured(
    agent,
    expected_name: str,
    expected_description: str,
    required_instruction_terms: tuple[str, ...],
):
    """Critical agents should keep stable names, model, descriptions, and prompts."""
    assert agent.name == expected_name
    assert agent.model == EXPECTED_MODEL
    assert expected_description in agent.description
    for term in required_instruction_terms:
        assert term in agent.instruction


def test_root_agent_wires_exactly_the_expected_sub_agents():
    """The orchestrator must be able to transfer to specialized agents."""
    sub_agents_by_name = {agent.name: agent for agent in root_agent.sub_agents}

    assert set(sub_agents_by_name) == {"greeter", "researcher", "calculator"}
    assert sub_agents_by_name["greeter"] is greeter_agent
    assert sub_agents_by_name["researcher"] is researcher_agent
    assert sub_agents_by_name["calculator"] is calculator_agent
    assert greeter_agent.parent_agent is root_agent
    assert researcher_agent.parent_agent is root_agent
    assert calculator_agent.parent_agent is root_agent
    assert root_agent.tools == []


def test_calculator_agent_registers_the_required_tools():
    """Calculator agent should register only calculate_expression."""
    assert calculator_agent.tools == [calculate_expression]


def test_researcher_agent_registers_the_required_tools_in_order():
    """Tool registration order is part of the expected ADK trajectory fixtures."""
    assert researcher_agent.tools == [get_current_date, lookup_topic]


@pytest.mark.parametrize(
    ("topic", "expected_summary_fragment"),
    [
        ("Python", "high-level, interpreted programming language"),
        ("Tell me about Kubernetes", "open-source container orchestration platform"),
        ("Google ADK", "Agent Development Kit"),
        ("machine learning basics", "subset of artificial intelligence"),
        ("DOCKER containers", "running applications in containers"),
    ],
)
def test_lookup_topic_returns_known_topic_summaries(
    topic: str, expected_summary_fragment: str
):
    """Known topics should resolve case-insensitively and inside longer queries."""
    result = lookup_topic(topic)

    assert result["topic"] == topic
    assert expected_summary_fragment in result["summary"]


def test_lookup_topic_returns_limited_information_message_for_unknown_topic():
    """Unknown topics should produce the deterministic fallback contract."""
    result = lookup_topic("quantum gardening")

    assert result == {
        "topic": "quantum gardening",
        "summary": (
            "I have limited information about 'quantum gardening'. "
            "It's a topic worth exploring further using specialized resources."
        ),
    }


def test_lookup_topic_prefers_first_matching_knowledge_base_topic():
    """Overlapping input should remain deterministic by using knowledge-base order."""
    result = lookup_topic("Compare Python and Docker")

    assert result["topic"] == "Compare Python and Docker"
    assert "Python is a high-level" in result["summary"]
    assert "Docker is a platform" not in result["summary"]


def test_get_current_date_returns_parseable_date_time_contract():
    """Date tool output should stay parseable and internally consistent."""
    result = get_current_date()

    assert set(result) == {"date", "time", "day_of_week"}

    parsed_date = datetime.strptime(result["date"], "%Y-%m-%d")
    datetime.strptime(result["time"], "%H:%M:%S")
    assert result["day_of_week"] == parsed_date.strftime("%A")


def _load_eval_file(filename: str) -> dict:
    with (TESTS_DIR / filename).open(encoding="utf-8") as eval_file:
        return json.load(eval_file)


@pytest.mark.parametrize(
    ("filename", "expected_transfer_agent", "expected_tool_names"),
    [
        ("greeter.test.json", "greeter", {"transfer_to_agent"}),
        (
            "researcher.test.json",
            "researcher",
            {"transfer_to_agent", "lookup_topic"},
        ),
    ],
)
def test_eval_fixtures_match_configured_agent_names_and_tools(
    filename: str, expected_transfer_agent: str, expected_tool_names: set[str]
):
    """Integration fixtures should stay aligned with configured agents and tools."""
    eval_set = _load_eval_file(filename)

    assert eval_set["eval_set_id"]
    assert eval_set["eval_cases"]

    configured_agent_names = {agent.name for agent in root_agent.sub_agents}
    configured_researcher_tools = {tool.__name__ for tool in researcher_agent.tools}
    configured_tools = configured_researcher_tools | {"transfer_to_agent"}

    for eval_case in eval_set["eval_cases"]:
        assert eval_case["session_input"]["app_name"] == "multi_agent"
        assert eval_case["session_input"]["user_id"]
        assert eval_case["conversation"]

        for turn in eval_case["conversation"]:
            final_text = turn["final_response"]["parts"][0]["text"]
            assert final_text.strip()

            tool_uses = turn["intermediate_data"]["tool_uses"]
            assert {tool_use["name"] for tool_use in tool_uses} <= configured_tools
            assert {tool_use["name"] for tool_use in tool_uses} == expected_tool_names

            transfer_calls = [
                tool_use
                for tool_use in tool_uses
                if tool_use["name"] == "transfer_to_agent"
            ]
            assert transfer_calls == [
                {
                    "name": "transfer_to_agent",
                    "args": {"agent_name": expected_transfer_agent},
                }
            ]
            assert expected_transfer_agent in configured_agent_names


def test_researcher_eval_fixtures_use_known_lookup_topics():
    """Researcher integration cases should exercise deterministic lookup data."""
    eval_set = _load_eval_file("researcher.test.json")

    for eval_case in eval_set["eval_cases"]:
        lookup_calls = [
            tool_use
            for turn in eval_case["conversation"]
            for tool_use in turn["intermediate_data"]["tool_uses"]
            if tool_use["name"] == "lookup_topic"
        ]
        assert lookup_calls

        for lookup_call in lookup_calls:
            lookup_result = lookup_topic(lookup_call["args"]["topic"])
            assert "limited information" not in lookup_result["summary"]


def test_eval_config_enforces_tool_trajectory_and_response_thresholds():
    """Evaluation configuration should protect routing/tooling and response quality."""
    config = _load_eval_file("test_config.json")

    assert config == {
        "criteria": {
            "tool_trajectory_avg_score": 1.0,
            "response_match_score": 0.2,
        }
    }
