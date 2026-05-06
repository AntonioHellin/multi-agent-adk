"""Unit tests for deterministic calculator tool behavior."""

from multi_agent.sub_agents.calculator.agent import calculate_expression


def test_calculate_expression_honors_operator_precedence():
    result = calculate_expression("2 + 3 * 4")

    assert result == {"expression": "2 + 3 * 4", "result": 14}


def test_calculate_expression_supports_parentheses_and_division():
    result = calculate_expression("(10 + 5) / 3")

    assert result == {"expression": "(10 + 5) / 3", "result": 5}


def test_calculate_expression_rejects_unsafe_code():
    result = calculate_expression("__import__('os').system('echo unsafe')")

    assert result["expression"] == "__import__('os').system('echo unsafe')"
    assert "error" in result
    assert "Only numeric arithmetic" in result["error"]


def test_calculate_expression_reports_division_by_zero():
    result = calculate_expression("42 / 0")

    assert result["expression"] == "42 / 0"
    assert "error" in result
    assert "division by zero" in result["error"]
