from unittest import mock

from agents.citation_agent import CitationAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.search_agent import SearchAgent
from agents.summariser_agent import SummariserAgent

RESULTS = [{'title': 'T', 'url': 'https://e.org', 'snippet': 'S'}]


def test_search_agent_prompt_includes_tool_parameters():
    # Regression: the old helper left the "query" parameter out of the prompt.
    assert '{"query": "string"}' in SearchAgent().system_prompt


def test_search_agent_follows_tool_call():
    reply = '```json\n{"tool": "web_search", "args": {"query": "better query"}}\n```'
    with mock.patch('agents.base_agent.chat', return_value=reply), \
         mock.patch('agents.search_agent.web_search', return_value=RESULTS) as ws:
        assert SearchAgent().run('topic') == RESULTS
    ws.assert_called_once_with('better query')


def test_search_agent_falls_back_to_topic_when_no_tool_call():
    with mock.patch('agents.base_agent.chat', return_value='I would search for it.'), \
         mock.patch('agents.search_agent.web_search', return_value=RESULTS) as ws:
        SearchAgent().run('topic')
    ws.assert_called_once_with('topic')


def test_summariser_agent_returns_llm_text_and_sends_extract():
    with mock.patch('agents.base_agent.chat', return_value='- bullet') as chat:
        assert SummariserAgent().run('First. Second.') == '- bullet'
    assert 'First. Second.' in chat.call_args.args[0][1]['content']


def test_fact_checker_agent_returns_llm_text():
    with mock.patch('agents.base_agent.chat', return_value='- all good'):
        assert FactCheckerAgent().run('summary') == '- all good'


def test_citation_agent_formats_each_result():
    citations = CitationAgent().run(RESULTS + RESULTS)
    assert len(citations) == 2 and all('https://e.org' in c for c in citations)
