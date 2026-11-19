import requests

DDG_URL = 'https://api.duckduckgo.com/'


def _flatten(topics):
    """DuckDuckGo nests some results inside {'Name': ..., 'Topics': [...]} groups."""
    for item in topics:
        if 'Topics' in item:
            yield from _flatten(item['Topics'])
        else:
            yield item


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search using DuckDuckGo's free Instant Answer API.
    Returns a list of {title, url, snippet} dicts (possibly empty).
    Raises requests.RequestException on network/HTTP failure.
    """
    params = {'q': query, 'format': 'json', 'no_redirect': 1, 'no_html': 1}
    response = requests.get(DDG_URL, params=params, timeout=10,
                            headers={'User-Agent': 'research-agent/1.0'})
    response.raise_for_status()
    data = response.json()

    results = []
    if data.get('AbstractText') and data.get('AbstractURL'):
        results.append({
            'title': data.get('Heading') or query,
            'url': data['AbstractURL'],
            'snippet': data['AbstractText'],
        })
    for item in _flatten(data.get('RelatedTopics', [])):
        if len(results) >= max_results:
            break
        if 'Text' in item and 'FirstURL' in item:
            results.append({
                'title': item['Text'][:80],
                'url': item['FirstURL'],
                'snippet': item['Text'],
            })
    return results[:max_results]
