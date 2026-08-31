from __future__ import annotations

import json
import urllib.error
import urllib.request


def status(model: str = "qwen2.5:3b") -> tuple[bool, str]:
    try:
        request = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
        with urllib.request.urlopen(request, timeout=2) as response:
            models = [item.get("name") for item in json.load(response).get("models", [])]
        return (model in models or any(name.startswith(model.split(":")[0]) for name in models), "Ollama is running locally")
    except (urllib.error.URLError, TimeoutError):
        return False, "Ollama is not running; deterministic offline mode is active"
