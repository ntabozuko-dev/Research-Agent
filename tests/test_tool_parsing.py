import pytest
from tool_parsing import parse_tool_call

CALL = '{"tool": "run_research", "args": {"topic": "solar"}}'
EXPECTED = {'tool': 'run_research', 'args': {'topic': 'solar'}}


@pytest.mark.parametrize('text', [
    CALL,
    f'  {CALL}\n',
    f'```{CALL}```',
    f'```json\n{CALL}\n```',
    f'Sure!\n```json\n{CALL}\n```',
    f'{CALL}\nHope that helps.',
])
def test_parses_valid_tool_calls(text):
    assert parse_tool_call(text) == EXPECTED


@pytest.mark.parametrize('text', [
    '', None, 'Hello there!', '{not json}',
    '{"tool": "x"}',                       # missing args
    '{"tool": 5, "args": {}}',             # tool not a string
    '{"tool": "x", "args": "topic"}',      # args not an object
    '["tool", "args"]',
])
def test_rejects_everything_else(text):
    assert parse_tool_call(text) is None
