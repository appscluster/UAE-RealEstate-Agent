"""OpenAI-compatible chat calls. The default route is the local OmniRoute gateway."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List

PREFERRED = ["auto/chat", "auto/best-chat", "auto/fast", "ollama/qwen3-coder:30b"]
# These ids are listed by the gateway and rejected on /chat/completions.
UNCALLABLE = {
    "gh/gpt-6.1-terra",
    "github/gpt-6.1-terra",
    "gh/gpt-6.1-sol",
    "github/gpt-6.1-sol",
}


def settings() -> Dict[str, Any]:
    return {
        "base_url": os.environ.get("LLM_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/"),
        "model": os.environ.get("LLM_MODEL", "auto/chat"),
        "timeout": float(os.environ.get("LLM_TIMEOUT_SECONDS", "90")),
    }


def chat(messages: List[Dict[str, str]], model: str | None = None) -> Dict[str, Any]:
    cfg = settings()
    chosen = model or cfg["model"]
    body = {"model": chosen, "messages": messages, "max_tokens": 700}
    req = urllib.request.Request(
        cfg["base_url"] + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    key = os.environ.get("LLM_API_KEY")
    if key:
        req.add_header("Authorization", "Bearer " + key)
    try:
        with urllib.request.urlopen(req, timeout=cfg["timeout"]) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            message = str(json.loads(raw)["error"]["message"])
        except Exception:
            message = raw or str(exc)
        raise RuntimeError(message) from exc
    message = (data.get("choices") or [{}])[0].get("message") or {}
    content = message.get("content") or ""
    if not str(content).strip():
        raise RuntimeError("model returned an empty reply")
    return {
        "content": str(content).strip(),
        "model": data.get("model") or chosen,
        "usage": data.get("usage") or {},
    }


def list_models() -> Dict[str, Any]:
    cfg = settings()
    found: List[str] = []
    try:
        req = urllib.request.Request(cfg["base_url"] + "/models")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
        found = [str(row.get("id")) for row in (data.get("data") or []) if row.get("id")]
    except Exception:
        found = []
    models = ["template"]
    for item in [cfg["model"], *PREFERRED, *found]:
        if item and item not in models and item not in UNCALLABLE:
            models.append(item)
    default = cfg["model"] if cfg["model"] in models else "template"
    return {"gateway": cfg["base_url"], "default": default, "models": models}
