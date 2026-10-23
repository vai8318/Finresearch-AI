
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:e4b"


def generate_response(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

        result = response.json()
        answer = result.get("response")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Ollama returned an empty or invalid response.")

        return answer.strip()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError("Ollama request timed out.") from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Check whether Ollama is running."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned an HTTP error: {exc.response.text}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc
