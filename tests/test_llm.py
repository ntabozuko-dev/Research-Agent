from unittest import mock

import pytest
import requests

import llm


def _resp(status=200, payload=None):
    r = mock.Mock()
    r.status_code = status
    r.json = lambda: payload
    if status >= 400:
        r.raise_for_status.side_effect = requests.exceptions.HTTPError(response=r)
    return r


def test_chat_returns_message_content():
    ok = _resp(payload={'message': {'content': 'hi'}})
    with mock.patch('llm.requests.post', return_value=ok) as post:
        assert llm.chat([{'role': 'user', 'content': 'x'}]) == 'hi'
    assert post.call_args.kwargs['json']['model'] == llm.MODEL
    assert post.call_args.kwargs['json']['stream'] is False


@pytest.mark.parametrize('exc, fragment', [
    (requests.exceptions.ConnectionError(), 'ollama serve'),
    (requests.exceptions.Timeout(), 'timed out'),
    (requests.exceptions.RequestException('boom'), 'network error'),
])
def test_chat_translates_network_errors(exc, fragment):
    with mock.patch('llm.requests.post', side_effect=exc):
        with pytest.raises(llm.OllamaError, match=fragment):
            llm.chat([])


def test_chat_missing_model_gives_pull_hint():
    with mock.patch('llm.requests.post', return_value=_resp(status=404)):
        with pytest.raises(llm.OllamaError, match='ollama pull'):
            llm.chat([])


def test_chat_unexpected_payload_shape():
    with mock.patch('llm.requests.post', return_value=_resp(payload={'oops': 1})):
        with pytest.raises(llm.OllamaError, match='unexpected format'):
            llm.chat([])
