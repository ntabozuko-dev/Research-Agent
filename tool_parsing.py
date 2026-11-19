"""Parse tool calls emitted by the LLM as JSON."""
import json
import re

_FENCE = re.compile(r'```(?:json)?\s*(.*?)\s*```', re.DOTALL)


def parse_tool_call(text: str) -> dict | None:
    """Return {"tool": str, "args": dict} if text is a tool call, else None.

    Accepts bare JSON, JSON wrapped in a markdown code fence (``` or ```json),
    and JSON followed by trailing prose.
    """
    if not text:
        return None
    candidate = text.strip()
    fenced = _FENCE.search(candidate)
    if fenced:
        candidate = fenced.group(1).strip()
    if not candidate.startswith('{'):
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(candidate)
    except json.JSONDecodeError:
        return None
    if (isinstance(data, dict)
            and isinstance(data.get('tool'), str)
            and isinstance(data.get('args'), dict)):
        return data
    return None
