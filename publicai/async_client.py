from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional

import httpx

from .version import __version__
from .client import (
    ChatMessage,
    PublicAIAPIError,
    PublicAIAuthenticationError,
    PublicAIError,
    _normalize_message,
)


DEFAULT_BASE_URL = "https://api.publicai.co/v1"
DEFAULT_USER_AGENT = f"publicai-python-async/{__version__}"


class AsyncPublicAIClient:
    """
    Async client for the Public AI Gateway.

    Mirrors the interface of `PublicAIClient` but uses `httpx.AsyncClient`
    under the hood.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: Optional[str] = None,
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("PUBLICAI_API_KEY")
        if not resolved_api_key:
            raise PublicAIAuthenticationError(
                "No API key provided. Set `api_key` or the PUBLICAI_API_KEY environment variable."
            )

        resolved_user_agent = user_agent or os.getenv("PUBLICAI_USER_AGENT") or DEFAULT_USER_AGENT

        self._api_key = resolved_api_key
        self._base_url = base_url.rstrip("/")
        self._user_agent = resolved_user_agent
        self._timeout = timeout
        self._client = client or httpx.AsyncClient(timeout=self._timeout)

    # ------------------------------------------------------------------
    # Async context manager support
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AsyncPublicAIClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        if self._client:
            await self._client.aclose()

    # ------------------------------------------------------------------
    # Public async methods
    # ------------------------------------------------------------------

    async def list_models(self) -> Dict[str, Any]:
        """Async variant of `PublicAIClient.list_models`."""
        return await self._get("/models")

    async def chat_completions(
        self,
        model: str,
        messages: Iterable[ChatMessage | Mapping[str, Any]],
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Async variant of `PublicAIClient.chat_completions`.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [_normalize_message(m) for m in messages],
        }

        if max_output_tokens is not None:
            payload["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if extra_params:
            payload.update(dict(extra_params))

        return await self._post("/chat/completions", json=payload)

    async def chat(
        self,
        model: str,
        messages: Iterable[ChatMessage | Mapping[str, Any]],
        **kwargs: Any,
    ) -> str:
        """
        Async convenience wrapper returning the first choice's content
        as a plain string.
        """
        response = await self.chat_completions(model=model, messages=messages, **kwargs)
        try:
            choices = response.get("choices") or []
            message = choices[0]["message"]
            return str(message.get("content", ""))
        except Exception:
            return str(response)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": self._user_agent,
        }

    async def _get(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        resp = await self._client.get(url, headers=self._headers(), params=params)
        return self._handle_response(resp)

    async def _post(self, path: str, *, json: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {**self._headers(), "Content-Type": "application/json"}
        resp = await self._client.post(url, headers=headers, json=json)
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: httpx.Response) -> Dict[str, Any]:
        try:
            data = resp.json()
        except ValueError:
            data = None

        if 200 <= resp.status_code < 300:
            return data if isinstance(data, dict) else {"data": data}

        message = ""
        if isinstance(data, dict):
            message = data.get("error") or data.get("message") or ""
        if not message:
            message = resp.text
        raise PublicAIAPIError(resp.status_code, message, payload=data)

