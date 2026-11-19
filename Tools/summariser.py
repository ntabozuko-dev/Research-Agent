import re


def summarise_text(text: str, max_sentences: int = 5) -> str:
    """
    Very lightweight extractive summariser.
    Selects the first max_sentences sentences from the text; the
    SummariserAgent then asks the LLM to rewrite them as clean bullets.
    """
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return ' '.join(sentences[:max_sentences])
