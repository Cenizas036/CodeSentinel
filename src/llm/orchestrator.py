"""
LLM Orchestrator — Multi-model routing with fallback, retry, and load balancing.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("CodeSentinel.LLM")


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    cached: bool = False


@dataclass
class ModelConfig:
    provider: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: int = 60


class BaseLLMClient(ABC):
    """Abstract base for LLM provider clients."""

    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self._request_count = 0
        self._total_tokens = 0

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @property
    def stats(self) -> dict:
        return {"requests": self._request_count, "total_tokens": self._total_tokens}


class LLMOrchestrator:
    """
    Orchestrates multiple LLM backends with:
    - Primary/fallback routing
    - Automatic failover
    - Response caching
    - Rate limiting
    - Token budget tracking
    """

    def __init__(self, config: dict):
        self.config = config
        self.primary_provider = config.get("primary", "openai")
        self.fallback_provider = config.get("fallback", "anthropic")
        self.models = config.get("models", {})
        self.clients: dict[str, BaseLLMClient] = {}
        self._cache: dict[str, LLMResponse] = {}
        self._cache_ttl = 3600  # 1 hour
        self._cache_timestamps: dict[str, float] = {}
        self._rate_limits: dict[str, list] = {}
        self._max_rpm = 60
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize LLM clients based on config."""
        import os

        provider_map = {
            "openai": ("openai_client", "OpenAIClient", "OPENAI_API_KEY"),
            "anthropic": ("anthropic_client", "AnthropicClient", "ANTHROPIC_API_KEY"),
            "ollama": ("ollama_client", "OllamaClient", None),
        }

        for provider, model in self.models.items():
            if provider in provider_map:
                module_name, class_name, env_key = provider_map[provider]
                api_key = os.environ.get(env_key, "") if env_key else None
                try:
                    module = __import__(
                        f"src.llm.{module_name}", fromlist=[class_name]
                    )
                    client_class = getattr(module, class_name)
                    self.clients[provider] = client_class(model=model, api_key=api_key)
                    logger.info(f"Initialized {provider} client with model {model}")
                except (ImportError, AttributeError) as e:
                    logger.warning(f"Could not initialize {provider}: {e}")

    def _check_rate_limit(self, provider: str) -> bool:
        """Check if provider is within rate limits."""
        now = time.time()
        if provider not in self._rate_limits:
            self._rate_limits[provider] = []

        # Clean old entries
        self._rate_limits[provider] = [
            t for t in self._rate_limits[provider] if now - t < 60
        ]
        return len(self._rate_limits[provider]) < self._max_rpm

    def _record_request(self, provider: str):
        if provider not in self._rate_limits:
            self._rate_limits[provider] = []
        self._rate_limits[provider].append(time.time())

    def _get_cached(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response if still valid."""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self._cache_ttl:
                response = self._cache[cache_key]
                response.cached = True
                return response
            else:
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
        return None

    def _set_cache(self, cache_key: str, response: LLMResponse):
        self._cache[cache_key] = response
        self._cache_timestamps[cache_key] = time.time()

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        use_cache: bool = True,
        provider: Optional[str] = None,
    ) -> str:
        """
        Generate response with automatic failover.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            use_cache: Whether to use response cache
            provider: Force specific provider

        Returns:
            Generated text content
        """
        cache_key = f"{prompt[:200]}:{max_tokens}:{temperature}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                logger.info(f"Cache hit for prompt (provider={cached.provider})")
                return cached.content

        providers_to_try = (
            [provider] if provider else [self.primary_provider, self.fallback_provider]
        )

        last_error = None
        for prov in providers_to_try:
            if prov not in self.clients:
                continue

            if not self._check_rate_limit(prov):
                logger.warning(f"Rate limit reached for {prov}, trying next")
                continue

            try:
                self._record_request(prov)
                start = time.time()
                response = await self.clients[prov].generate(prompt, max_tokens, temperature)
                response.latency_ms = (time.time() - start) * 1000

                if use_cache:
                    self._set_cache(cache_key, response)

                logger.info(
                    f"Generated via {prov}/{response.model} "
                    f"({response.tokens_used} tokens, {response.latency_ms:.0f}ms)"
                )
                return response.content

            except Exception as e:
                last_error = e
                logger.error(f"Provider {prov} failed: {e}")
                continue

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def generate_structured(
        self, prompt: str, schema: dict, max_tokens: int = 4096
    ) -> dict:
        """Generate structured JSON output conforming to a schema."""
        import json

        schema_str = json.dumps(schema, indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON conforming to this schema:
{schema_str}

Return ONLY the JSON, no other text."""

        response = await self.generate(structured_prompt, max_tokens=max_tokens)

        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse structured response: {response[:200]}")
            return {"error": "Failed to parse response", "raw": response}

    @property
    def stats(self) -> dict:
        return {
            provider: client.stats
            for provider, client in self.clients.items()
        }
