"""Validation helpers for MCP tool parameters.

Some MCP clients serialize nested objects/arrays as JSON strings.
The parse_if_string validator detects and parses them back to Python objects.
This is the Python equivalent of the fork's Zod parseIfString preprocessor.
"""

import json
from typing import Annotated, Any

from pydantic import BeforeValidator


def parse_if_string(value: Any) -> Any:
    """Parse JSON strings that MCP clients send for nested objects.

    If value is a string that contains valid JSON, parse and return it.
    Otherwise, return the value unchanged. Never raises.
    """
    if isinstance(value, str) and value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


JsonParsed = Annotated[dict[str, Any], BeforeValidator(parse_if_string)]
"""Type alias for dict parameters that may arrive as JSON strings from MCP clients."""

JsonParsedList = Annotated[list[Any], BeforeValidator(parse_if_string)]
"""Type alias for list parameters that may arrive as JSON strings from MCP clients."""
