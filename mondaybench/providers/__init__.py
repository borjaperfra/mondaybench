"""Provider construction from config objects."""

from __future__ import annotations

from ..config import EvaluatorConfig, ModelConfig
from .anthropic_native import AnthropicProvider, rejects_temperature
from .base import GenerationResult, ModelProvider, ProviderError
from .openai_compatible import OpenAICompatibleProvider

__all__ = [
    "AnthropicProvider",
    "GenerationResult",
    "ModelProvider",
    "OpenAICompatibleProvider",
    "ProviderError",
    "build_judge_provider",
    "build_model_provider",
    "rejects_temperature",
]


def build_model_provider(model: ModelConfig) -> ModelProvider:
    if model.api_style == "anthropic":
        return AnthropicProvider(api_key=model.api_key())
    base_url = model.base_url()
    api_key = model.api_key()
    assert base_url and api_key  # ModelConfig marks both required for this style
    return OpenAICompatibleProvider(base_url=base_url, api_key=api_key)


def build_judge_provider(evaluator: EvaluatorConfig) -> ModelProvider:
    if evaluator.api_style == "anthropic":
        return AnthropicProvider(api_key=evaluator.api_key())
    base_url = evaluator.base_url()
    api_key = evaluator.api_key()
    assert base_url and api_key
    # The judge returns short JSON; streaming buys nothing and TTFT is not scored.
    return OpenAICompatibleProvider(base_url=base_url, api_key=api_key, stream=False)
