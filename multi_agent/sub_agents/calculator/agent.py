"""
Calculator Sub-Agent: Handles deterministic arithmetic calculations.
"""

import ast
import operator
from typing import Any

from google.adk.agents import Agent


class CalculationError(ValueError):
    """Raised when an expression cannot be safely calculated."""


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MAX_ABS_VALUE = 1_000_000_000
_MAX_POWER_EXPONENT = 10


def _evaluate_node(node: ast.AST) -> float | int:
    """Evaluate a whitelisted Python AST node as arithmetic only."""
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body)

    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPERATORS:
        operand = _evaluate_node(node.operand)
        return _ALLOWED_UNARY_OPERATORS[type(node.op)](operand)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POWER_EXPONENT:
            raise CalculationError(
                f"Exponents larger than {_MAX_POWER_EXPONENT} are not supported."
            )

        result = _ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)
        if abs(result) > _MAX_ABS_VALUE:
            raise CalculationError(
                f"Results larger than {_MAX_ABS_VALUE:,} are not supported."
            )
        return result

    raise CalculationError(
        "Only numeric arithmetic with +, -, *, /, //, %, **, and parentheses is supported."
    )


def calculate_expression(expression: str) -> dict[str, Any]:
    """Safely calculate a basic arithmetic expression.

    Args:
        expression: Arithmetic expression containing numbers, parentheses, and
            operators (+, -, *, /, //, %, **).

    Returns:
        dict: The original expression plus either the calculated result or an
            error message explaining why the expression could not be evaluated.
    """
    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = _evaluate_node(parsed_expression)
    except (CalculationError, SyntaxError, TypeError, ZeroDivisionError) as error:
        return {
            "expression": expression,
            "error": str(error) or "The expression could not be calculated.",
        }

    if isinstance(result, float) and result.is_integer():
        result = int(result)

    return {
        "expression": expression,
        "result": result,
    }


calculator_agent = Agent(
    name="calculator",
    model="gemini-3-flash-preview",
    description="Handles deterministic arithmetic and quick numeric calculations.",
    instruction="""You are a precise calculator assistant. Your responsibilities are:
- Handle arithmetic, numeric expressions, and quick calculations
- Always use calculate_expression for math instead of doing mental arithmetic
- Pass only the arithmetic expression to calculate_expression, without extra words
- Return the result clearly and concisely
- If the tool returns an error, explain the limitation briefly and ask for a simpler arithmetic expression
""",
    tools=[calculate_expression],
)
