from unittest import mock

from llm import OllamaError
from orchestrator import ResearchOrchestrator

RESULTS = [{'title': 'T', 'url': 'https://e.org', 'snippet': 'S'}]


def _orch():
    o = ResearchOrchestrator()
    o.search_agent.run = mock.Mock(return_value=RESULTS)
    o.summariser_agent.run = mock.Mock(return_value='- sum')
    o.fact_checker_agent.run = mock.Mock(return_value='- fact')
    return o


def test_full_pipeline_builds_report_in_order():
    o = _orch()
    report = o.run('solar')
    o.fact_checker_agent.run.assert_called_once_with('- sum')
    for part in ('RESEARCH REPORT', 'Query: solar', '- sum', '- fact', '[1] T. (n.d.).'):
        assert part in report
    assert report.index('SUMMARY') < report.index('FACT CHECK') < report.index('SOURCES')


def test_no_results_short_circuits():
    o = _orch()
    o.search_agent.run.return_value = []
    assert o.run('x') == 'No results found. Try a different query.'
    o.summariser_agent.run.assert_not_called()


def test_ollama_failure_is_reported_not_swallowed_as_content():
    o = _orch()
    o.summariser_agent.run.side_effect = OllamaError('Could not connect to Ollama.')
    out = o.run('x')
    assert 'could not reach the language model' in out and 'Could not connect' in out
    assert 'RESEARCH REPORT' not in out


def test_other_failures_are_reported():
    o = _orch()
    o.search_agent.run.side_effect = RuntimeError('network down')
    assert 'network down' in o.run('x')
