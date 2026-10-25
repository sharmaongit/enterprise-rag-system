"""Optional Ollama adapter; standard library HTTP, no hidden model dependency."""
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from enterprise_rag.exceptions import ModelProviderError

class OllamaProvider:
    def __init__(self, base_url: str, model: str, timeout: float = 30):
        self.base_url, self.model, self.timeout = base_url.rstrip("/"), model, timeout
    def generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0}}).encode()
        req = Request(self.base_url + "/api/generate", data=payload, headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            answer = body.get("response")
            if not isinstance(answer, str) or not answer.strip(): raise ModelProviderError("Model returned an empty response")
            return answer.strip()
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            raise ModelProviderError(f"Ollama request failed: {exc.__class__.__name__}") from exc
