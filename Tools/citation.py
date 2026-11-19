from datetime import date


def _end(text: str) -> str:
    """Terminate text with a full stop unless it already ends in sentence punctuation."""
    text = text.strip()
    return text if text.endswith(('.', '!', '?')) else text + '.'


def format_citation(url: str, title: str, author: str | None = None) -> str:
    """
    Format a basic APA 7 style web reference.

    Search results carry no publication date, so "(n.d.)" is used, and when the
    author is unknown the title leads the reference, as APA specifies.
    """
    accessed = date.today().strftime('%B %d, %Y')
    if author:
        lead = f'{_end(author)} (n.d.). {_end(title)}'
    else:
        lead = f'{_end(title)} (n.d.).'
    return f'{lead} Retrieved {accessed}, from {url}'
