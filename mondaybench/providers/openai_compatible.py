"""OpenAI-compatible chat completions over raw httpx.

Covers both benchmark endpoints (Helmcode, NaN) and any OpenAI-compatible
judge. Streams by default so TTFT is measured rather than guessed; falls back
to a single non-streaming request when `stream=False` is requested.
"""

from __future__ import annotations

import json
import time
from typing import Any, Iterator

import httpx

from .anthropic_native import rejects_temperature
from .base import GenerationResult, ModelProvider, ProviderError

TRANSIENT_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}


class OpenAICompatibleProvider(ModelProvider):
    name = "openai_compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 300.0,
        stream: bool = True,
    ):
        if not base_url:
            raise ProviderError("openai_compatible provider requires a base_url")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.stream = stream

    # -- request building ---------------------------------------------------

    def _endpoint(self) -> str:
        # Accept a base_url given with or without the /v1 suffix.
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}/chat/completions"
        return f"{self.base_url}/v1/chat/completions"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        *,
        model_id: str,
        system_prompt: str | None,
        user_prompt: str,
        generation_config: dict[str, Any],
        stream: bool,
    ) -> tuple[dict[str, Any], list[str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "stream": stream,
        }
        unsupported: list[str] = []
        if generation_config.get("max_output_tokens") is not None:
            payload["max_tokens"] = generation_config["max_output_tokens"]
        if generation_config.get("temperature") is not None:
            # An OpenAI-compatible gateway may front a model that rejects
            # `temperature` outright. LiteLLM forwards the parameter verbatim, so
            # Anthropic returns a 400 and the whole evaluation dies. Drop it and
            # record the fact instead of failing on a parameter that cannot apply.
            if rejects_temperature(model_id):
                unsupported.append("temperature")
            else:
                payload["temperature"] = generation_config["temperature"]
        if generation_config.get("response_json_schema"):
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "verdict",
                    "strict": True,
                    "schema": generation_config["response_json_schema"],
                },
            }
        if stream:
            payload["stream_options"] = {"include_usage": True}
        for key, value in (generation_config.get("extra_body") or {}).items():
            payload[key] = value
        return payload, unsupported

    # -- calling ------------------------------------------------------------

    def generate(
        self,
        *,
        model_id: str,
        system_prompt: str | None,
        user_prompt: str,
        generation_config: dict[str, Any],
    ) -> GenerationResult:
        use_stream = generation_config.get("stream", self.stream)
        payload, unsupported = self._payload(
            model_id=model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            generation_config=generation_config,
            stream=use_stream,
        )
        result = (
            self._generate_streaming(payload) if use_stream else self._generate_blocking(payload)
        )
        result.unsupported_parameters = unsupported
        result.system_prompt_sent = bool(system_prompt)
        return result

    def _generate_blocking(self, payload: dict[str, Any]) -> GenerationResult:
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self._endpoint(), headers=self._headers(), json=payload)
        except httpx.HTTPError as exc:
            raise ProviderError(f"network error: {exc}", transient=True) from exc
        elapsed_ms = (time.perf_counter() - started) * 1000
        self._raise_for_status(response)

        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderError(f"non-JSON response body: {response.text[:400]}") from exc

        choices = body.get("choices") or []
        if not choices:
            raise ProviderError(f"response contained no choices: {json.dumps(body)[:400]}")
        message = choices[0].get("message") or {}
        text = message.get("content") or ""
        usage = body.get("usage") or {}

        return GenerationResult(
            text=text,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            reasoning_tokens=_reasoning_tokens(usage),
            ttft_ms=None,  # not measurable without streaming
            total_latency_ms=round(elapsed_ms, 1),
            generation_ms=None,
            provider_request_id=body.get("id") or response.headers.get("x-request-id"),
            finish_reason=choices[0].get("finish_reason"),
            raw_usage=usage,
        )

    def _generate_streaming(self, payload: dict[str, Any]) -> GenerationResult:
        chunks: list[str] = []
        # Thinking models stream their reasoning in a separate delta field
        # (`reasoning_content` on NaN's GLM, `reasoning` elsewhere). It is NOT
        # part of the answer and must never be scored, but it has to be counted:
        # a model can spend its whole output budget reasoning and emit no
        # answer at all, and that is a truncation, not a transport failure.
        reasoning_chars = 0
        usage: dict[str, Any] = {}
        finish_reason: str | None = None
        request_id: str | None = None
        ttft_ms: float | None = None
        ttfa_ms: float | None = None
        first_token_at: float | None = None  # first token of any kind
        first_answer_at: float | None = None  # first visible token

        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST", self._endpoint(), headers=self._headers(), json=payload
                ) as response:
                    if response.status_code >= 400:
                        response.read()
                        self._raise_for_status(response)
                    request_id = response.headers.get("x-request-id")
                    for event in _iter_sse(response):
                        if event.get("id") and not request_id:
                            request_id = event["id"]
                        if event.get("usage"):
                            usage = event["usage"]
                        for choice in event.get("choices") or []:
                            delta = choice.get("delta") or {}
                            thought = delta.get("reasoning_content") or delta.get("reasoning")
                            if isinstance(thought, str) and thought:
                                reasoning_chars += len(thought)
                                if first_token_at is None:
                                    first_token_at = time.perf_counter()
                                    ttft_ms = round((first_token_at - started) * 1000, 1)
                            piece = delta.get("content")
                            if piece:
                                now = time.perf_counter()
                                if first_token_at is None:
                                    first_token_at = now
                                    ttft_ms = round((now - started) * 1000, 1)
                                if first_answer_at is None:
                                    first_answer_at = now
                                    ttfa_ms = round((now - started) * 1000, 1)
                                chunks.append(piece)
                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
        except httpx.HTTPError as exc:
            raise ProviderError(f"network error: {exc}", transient=True) from exc

        ended = time.perf_counter()
        total_ms = round((ended - started) * 1000, 1)
        generation_ms = round((ended - first_token_at) * 1000, 1) if first_token_at else None

        text = "".join(chunks)
        if not text:
            if reasoning_chars:
                # Reasoning but no answer. Which failure this is depends
                # entirely on finish_reason, and the two need different fixes.
                if finish_reason == "length":
                    raise ProviderError(
                        f"model produced {reasoning_chars} characters of reasoning but no "
                        f"answer (finish_reason=length) - its output budget was consumed "
                        f"by thinking; raise generation.max_output_tokens",
                        kind="truncated_by_budget",
                    )
                # finish_reason=stop: the provider ended the turn deliberately
                # with an empty answer. The budget was not reached, so raising
                # it would change nothing. This is a result about the model, and
                # it is recorded as its own kind rather than filed with
                # truncation.
                raise ProviderError(
                    f"model produced {reasoning_chars} characters of reasoning and then "
                    f"ended its turn with no answer (finish_reason={finish_reason}) - "
                    f"not a truncation, so the output budget is not the cause",
                    kind="empty_final_answer",
                )
            raise ProviderError(
                f"stream produced no content at all (finish_reason={finish_reason})",
                kind="empty_stream",
            )

        return GenerationResult(
            text=text,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            reasoning_tokens=_reasoning_tokens(usage),
            ttft_ms=ttft_ms,
            ttfa_ms=ttfa_ms,
            total_latency_ms=total_ms,
            generation_ms=generation_ms,
            provider_request_id=request_id,
            finish_reason=finish_reason,
            raw_usage=usage,
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        detail = response.text[:400]
        raise ProviderError(
            f"HTTP {response.status_code} from provider: {detail}",
            transient=response.status_code in TRANSIENT_STATUSES,
            status=response.status_code,
        )


def _reasoning_tokens(usage: dict[str, Any]) -> int | None:
    details = usage.get("completion_tokens_details") or {}
    value = details.get("reasoning_tokens")
    if value is None:
        value = usage.get("reasoning_tokens")
    return value


def _iter_sse(response: httpx.Response) -> Iterator[dict[str, Any]]:
    for line in response.iter_lines():
        if not line or not line.startswith("data:"):
            continue
        data = line[len("data:") :].strip()
        if not data or data == "[DONE]":
            continue
        try:
            yield json.loads(data)
        except json.JSONDecodeError:
            # A malformed keep-alive frame must not abort a valid generation.
            continue
