"""OpenAI LLM Client."""
import asyncio
from typing import Optional
from .orchestrator import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client with async support."""

    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        super().__init__(model, api_key)
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        except ImportError:
            pass

    async def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY.")

        self._request_count += 1
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer specializing in security, quality, and architecture analysis."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        tokens = response.usage.total_tokens if response.usage else 0
        self._total_tokens += tokens

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=self.model,
            provider="openai",
            tokens_used=tokens,
        )

    async def health_check(self) -> bool:
        try:
            await self.generate("ping", max_tokens=5)
            return True
        except Exception:
            return False
