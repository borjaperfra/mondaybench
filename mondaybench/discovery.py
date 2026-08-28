"""Ask an OpenAI-compatible endpoint what it actually serves.

Model ids drift and documentation lags. This exists so a `models.yaml` entry
can be confirmed against the endpoint rather than trusted from a doc page - a
wrong id fails a call instead of quietly scoring badly.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from .config import ConfigError, ModelConfig, resolve_env


@dataclass(frozen=True)
class Endpoint:
    provider: str
    base_url_env: str
    api_key_env: str


# Endpoints worth probing even when models.yaml currently enables no model on
# them. Without this, commenting out the last model for a provider silently
# removes that provider from `mondaybench endpoints` - which is exactly when you
# most need to ask it what is available.
KNOWN_ENDPOINTS: tuple[Endpoint, ...] = (
    Endpoint(provider="helmcode", base_url_env="HELMCODE_BASE_URL", api_key_env="HELMCODE_API_KEY"),
    Endpoint(provider="nan", base_url_env="NAN_BASE_URL", api_key_env="NAN_API_KEY"),
)


def endpoints_from_models(models: dict[str, ModelConfig]) -> list[Endpoint]:
    """Endpoints to probe: those models.yaml references, plus known ones.

    A known endpoint is included only if its environment variables are actually
    set, so an unconfigured provider is skipped rather than reported broken.
    """
    seen: dict[tuple[str, str, str], Endpoint] = {}

    def add(endpoint: Endpoint) -> None:
        seen.setdefault(
            (endpoint.provider, endpoint.base_url_env, endpoint.api_key_env), endpoint
        )

    for model in models.values():
        if model.api_style != "openai_compatible":
            continue
        if not model.base_url_env or not model.api_key_env:
            continue
        add(
            Endpoint(
                provider=model.provider,
                base_url_env=model.base_url_env,
                api_key_env=model.api_key_env,
            )
        )

    for endpoint in KNOWN_ENDPOINTS:
        configured = resolve_env(endpoint.base_url_env, required=False) and resolve_env(
            endpoint.api_key_env, required=False
        )
        if configured:
            add(endpoint)

    return sorted(seen.values(), key=lambda e: e.provider)


def list_models(endpoint: Endpoint, timeout: float = 30.0) -> list[str]:
    """Return the model ids an endpoint reports from GET /v1/models."""
    base_url = resolve_env(endpoint.base_url_env, required=True)
    api_key = resolve_env(endpoint.api_key_env, required=True)
    assert base_url and api_key

    base = base_url.rstrip("/")
    url = f"{base}/models" if base.endswith("/v1") else f"{base}/v1/models"

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {api_key}"})
    except httpx.HTTPError as exc:
        raise ConfigError(f"{endpoint.provider}: could not reach {url}: {exc}") from exc

    if response.status_code >= 400:
        raise ConfigError(
            f"{endpoint.provider}: HTTP {response.status_code} from {url}: "
            f"{response.text[:200]}"
        )

    try:
        body = response.json()
    except ValueError as exc:
        raise ConfigError(f"{endpoint.provider}: non-JSON response from {url}") from exc

    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(data, list):
        raise ConfigError(f"{endpoint.provider}: unexpected /models payload shape")

    return sorted(str(item.get("id")) for item in data if isinstance(item, dict) and item.get("id"))
