#!/usr/bin/env python3
"""Shared OpenAI-compatible chat client for crof/Greg APIs."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def resolve_api_key() -> str | None:
    return os.environ.get("FAKEGREG_API_KEY") or os.environ.get("CROF_API_KEY")


def resolve_base_url() -> str:
    return os.environ.get(
        "FAKEGREG_BASE_URL",
        os.environ.get("CROF_BASE_URL", "https://crof.ai/v1"),
    )


def resolve_model(default: str = "greg-2-super") -> str:
    return os.environ.get("FAKEGREG_MODEL", os.environ.get("CROF_MODEL", default))


def post_chat_completion(
    *,
    messages: list[dict[str, str]],
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float | None = 0.4,
    max_tokens: int | None = None,
) -> str:
    key = api_key or resolve_api_key()
    if not key:
        raise RuntimeError(
            "Set FAKEGREG_API_KEY or CROF_API_KEY to call the Greg/Crof API."
        )

    url = (base_url or resolve_base_url()).rstrip("/") + "/chat/completions"
    payload: dict[str, Any] = {
        "model": model or resolve_model(),
        "messages": messages,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed: {error.code} {detail}") from error

    return body["choices"][0]["message"]["content"]
