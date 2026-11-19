from unittest import mock

import pytest

from conversation_manager import ConversationManager
from llm import OllamaError

TOOL = '{"tool": "run_research", "args": {"topic": "solar"}}'


@pytest.fixture
def manager():
    m = ConversationManager()
    m.orchestrator.run = mock.Mock(return_value='REPORT')
    return m


def test_plain_chat_skips_pipeline_and_records_history(manager):
    with mock.patch('conversation_manager.chat', return_value='Hello!'):
        assert manager.send('hi') == 'Hello!'
    manager.orchestrator.run.assert_not_called()
    assert [h['role'] for h in manager.history] == ['user', 'assistant']


@pytest.mark.parametrize('first', [TOOL, f'```json\n{TOOL}\n```'])
def test_research_request_routes_to_pipeline(manager, first):
    with mock.patch('conversation_manager.chat', side_effect=[first, 'Nice summary']) as chat:
        assert manager.send('research solar') == 'Nice summary'
    manager.orchestrator.run.assert_called_once_with('solar')
    assert 'REPORT' in chat.call_args_list[1].args[0][-1]['content']
    assert manager.history[-1] == {'role': 'assistant', 'content': 'Nice summary'}


def test_second_tool_call_falls_back_to_report(manager):
    with mock.patch('conversation_manager.chat', side_effect=[TOOL, TOOL]):
        assert manager.send('research solar') == 'REPORT'


def test_missing_topic_falls_back_to_user_input(manager):
    call = '{"tool": "run_research", "args": {}}'
    with mock.patch('conversation_manager.chat', side_effect=[call, 'ok']):
        manager.send('research wind')
    manager.orchestrator.run.assert_called_once_with('research wind')


def test_ollama_error_is_returned_and_not_stored_in_history(manager):
    with mock.patch('conversation_manager.chat', side_effect=OllamaError('Ollama is down')):
        assert manager.send('hi') == 'Ollama is down'
    assert manager.history == []
