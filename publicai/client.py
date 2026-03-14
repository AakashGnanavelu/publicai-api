from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional

import requests

from .version import __version__


DEFAULT_BASE_URL = "https://api.publicai.co/v1"
DEFAULT_USER_AGENT = f"publicai-python/{__version__}"


class PublicAIError(Exception):
    """Base error for all Public AI client exceptions."""


class PublicAIAuthenticationError(PublicAIError):
    """Raised when no API key is provided or authentication fails."""


class PublicAIAPIError(PublicAIError):
    """Raised when the Public AI API returns a non-success HTTP status."""

    def __init__(self, status_code: int, message: str, payload: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.payload = payload


@dataclass
class ChatMessage:
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class PublicAIClient:
    """
    High-level client for the Public AI Gateway.

    Authentication and headers follow the official documentation:
    see `https://platform.publicai.co/docs`.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: Optional[str] = None,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Create a new PublicAIClient.

        - If `api_key` is omitted, the client will read it from
          `PUBLICAI_API_KEY`.
        - If `user_agent` is omitted, the client will read it from
          `PUBLICAI_USER_AGENT`, falling back to a library default.
        """
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
        self._session = session or requests.Session()

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "PublicAIClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session:
            self._session.close()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def list_models(self) -> Dict[str, Any]:
        """
        List available models.

        Wraps:
          GET /models
        as described in the Public AI docs:
        `https://platform.publicai.co/docs`.
        """
        return self._get("/models")

    def chat_completions(
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
        Call the chat completions endpoint.

        This corresponds to:
          POST /chat/completions

        Minimal example:

            client = PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0")
            resp = client.chat_completions(
                model="swiss-ai/apertus-8b-instruct",
                messages=[ChatMessage(role="user", content="Hello! Can you help me understand open-source AI?")],
            )
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

        return self._post("/chat/completions", json=payload)

    def chat(
        self,
        model: str,
        messages: Iterable[ChatMessage | Mapping[str, Any]],
        **kwargs: Any,
    ) -> str:
        """
        Convenience wrapper around `chat_completions` that returns the
        first choice's message content as a plain string.

        This mirrors the ergonomics of the OpenAI Python client, where
        a high-level helper is commonly used for simple chat use cases.
        """
        response = self.chat_completions(model=model, messages=messages, **kwargs)
        # The exact response schema is defined by Public AI; we assume a
        # standard `choices[0].message.content` layout here.
        try:
            choices = response.get("choices") or []
            message = choices[0]["message"]
            return str(message.get("content", ""))
        except Exception:
            # Fall back to returning the raw response stringified.
            return str(response)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": self._user_agent,
        }

    def _get(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        resp = self._session.get(url, headers=self._headers(), params=params, timeout=self._timeout)
        return self._handle_response(resp)

    def _post(self, path: str, *, json: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {**self._headers(), "Content-Type": "application/json"}
        resp = self._session.post(url, headers=headers, json=json, timeout=self._timeout)
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: requests.Response) -> Dict[str, Any]:
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


def _normalize_message(msg: ChatMessage | Mapping[str, Any]) -> Dict[str, Any]:
    if isinstance(msg, ChatMessage):
        return msg.to_dict()
    # assume it is already in wire format
    return {"role": msg["role"], "content": msg["content"]}

