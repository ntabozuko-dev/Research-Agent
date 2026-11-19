"""Single place that talks to the local Ollama server."""
import requests

OLLAMA_URL = 'http://localhost:11434/api/chat'
MODEL = 'llama3'
TIMEOUT_SECONDS = 60


class OllamaError(RuntimeError):
    """Raised when the local Ollama server cannot be reached or misbehaves."""


def chat(messages: list[dict]) -> str:
    """Send messages to Ollama and return the assistant's reply text."""
    payload = {'model': MODEL, 'messages': messages, 'stream': False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()['message']['content']
    except requests.exceptions.ConnectionError as e:
        raise OllamaError(
            'Could not connect to Ollama. Make sure it is running with: ollama serve'
        ) from e
    except requests.exceptions.Timeout as e:
        raise OllamaError(
            'The request to Ollama timed out. The model may be too large for your '
            'machine - try a smaller one (e.g. phi3) by changing MODEL in llm.py.'
        ) from e
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            raise OllamaError(
                f"Ollama does not have the model '{MODEL}'. Run: ollama pull {MODEL}"
            ) from e
        raise OllamaError(f'Ollama returned an error: {e}') from e
    except requests.exceptions.RequestException as e:
        raise OllamaError(f'Unexpected network error talking to Ollama: {e}') from e
    except (KeyError, TypeError, ValueError) as e:
        raise OllamaError('Ollama returned a response in an unexpected format.') from e
