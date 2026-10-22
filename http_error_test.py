import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "gemma4:e4b",
    "prompt": "Reply with OK",
    "stream": False,
}

try:
    response = requests.post(url, json=payload, timeout=30)

    print("HTTP status:", response.status_code)
    response.raise_for_status()

    result = response.json()
    print("Answer:", result.get("response"))

except requests.exceptions.HTTPError as exc:
    print("The server returned an HTTP error:", exc)
    print("Server details:", exc.response.text)

except requests.exceptions.ConnectionError as exc:
    print("Could not connect to Ollama:", exc)

except requests.exceptions.Timeout:
    print("The request timed out.")