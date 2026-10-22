
import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "gemma4:e4b",
    "prompt": "Reply with exactly: OK",
    "stream": False,
}

try:
    response = requests.post(url, json=payload, timeout=120)

    print("Status code:", response.status_code)
    print("Response body:", response.text)

except requests.exceptions.RequestException as exc:
    print("Request failed:", repr(exc))
