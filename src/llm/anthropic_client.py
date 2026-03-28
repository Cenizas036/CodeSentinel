"""Anthropic Claude Client."""
from typing import Optional
from .orchestrator import BaseLLMClient, LLMResponse


class AnthropicClient(BaseLLMClient):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(model, api_key)
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None
        except ImportError:
            pass

    async def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

        self._request_count += 1
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are an expert code reviewer specializing in security, quality, and architecture analysis.",
            messages=[{"role": "user", "content": prompt}],
        )

        tokens = response.usage.input_tokens + response.usage.output_tokens
        self._total_tokens += tokens

        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            provider="anthropic",
            tokens_used=tokens,
        )

    async def health_check(self) -> bool:
        try:
            await self.generate("ping", max_tokens=5)
            return True
        except Exception:
            return False
