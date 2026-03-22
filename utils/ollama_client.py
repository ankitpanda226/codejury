import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"


def ask_ollama_json(model: str, system_prompt: str, user_prompt: str, schema: dict) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "format": schema,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    content = data["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ollama returned non-JSON content:\n{content}") from e