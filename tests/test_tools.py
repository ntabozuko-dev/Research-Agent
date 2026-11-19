from unittest import mock

from tools.citation import format_citation
from tools.summariser import summarise_text
from tools.web_search import web_search


def test_summarise_text_keeps_first_n_sentences():
    text = 'One. Two! Three? Four. Five. Six. Seven.'
    assert summarise_text(text, max_sentences=3) == 'One. Two! Three?'


def test_citation_without_author_leads_with_title():
    c = format_citation(url='https://e.org/a', title='A Title')
    assert c.startswith('A Title. (n.d.). Retrieved ')
    assert c.endswith('from https://e.org/a')


def test_citation_with_author():
    c = format_citation(url='https://e.org/a', title='A Title', author='Doe, J.')
    assert c.startswith('Doe, J. (n.d.). A Title. Retrieved ')


def test_citation_author_without_trailing_period():
    assert format_citation('https://e.org', 'T', author='Acme Corp').startswith('Acme Corp. (n.d.). T.')


def _ddg(payload):
    resp = mock.Mock()
    resp.raise_for_status = lambda: None
    resp.json = lambda: payload
    return resp


def test_web_search_uses_abstract_and_flattens_nested_topics():
    payload = {
        'AbstractText': 'Abstract text.', 'AbstractURL': 'https://e.org/abs', 'Heading': 'Head',
        'RelatedTopics': [
            {'Name': 'Group', 'Topics': [{'Text': 'Nested one', 'FirstURL': 'https://e.org/n1'}]},
            {'Text': 'Flat one', 'FirstURL': 'https://e.org/f1'},
            {'Text': 'no url so skipped'},
        ],
    }
    with mock.patch('tools.web_search.requests.get', return_value=_ddg(payload)):
        results = web_search('q')
    assert [r['url'] for r in results] == ['https://e.org/abs', 'https://e.org/n1', 'https://e.org/f1']
    assert results[0]['title'] == 'Head'


def test_web_search_respects_max_results():
    payload = {'RelatedTopics': [{'Text': f't{i}', 'FirstURL': f'https://e.org/{i}'} for i in range(10)]}
    with mock.patch('tools.web_search.requests.get', return_value=_ddg(payload)):
        assert len(web_search('q', max_results=3)) == 3


def test_web_search_empty_response_returns_empty_list():
    with mock.patch('tools.web_search.requests.get', return_value=_ddg({})):
        assert web_search('q') == []


def test_citation_does_not_double_up_punctuation():
    c = format_citation('https://e.org', 'Already ends here.')
    assert c.startswith('Already ends here. (n.d.). Retrieved ') and '..' not in c
