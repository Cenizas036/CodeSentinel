"""Ollama Local LLM Client."""
import aiohttp
from typing import Optional
from .orchestrator import BaseLLMClient, LLMResponse


class OllamaClient(BaseLLMClient):
    def __init__(self, model: str = "llama3:70b", api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        super().__init__(model, api_key)
        self.base_url = base_url

    async def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        self._request_count += 1
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            async with session.post(f"{self.base_url}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama error: {resp.status}")
                data = await resp.json()

        return LLMResponse(
            content=data.get("response", ""),
            model=self.model,
            provider="ollama",
            tokens_used=data.get("eval_count", 0),
        )

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    return resp.status == 200
        except Exception:
            return False
