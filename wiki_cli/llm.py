"""Thin client for the local Ollama server. The only place that talks to the model."""
import functools
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config


class ModelUnavailable(RuntimeError):
    """Raised when the local runtime is not running or the model is not downloaded."""


@functools.cache
def _check_server() -> None:
    """Fail fast (3 s) if nothing is listening, instead of waiting for the long generation timeout."""
    url = urllib.parse.urlparse(config.OLLAMA_URL)
    try:
        socket.create_connection((url.hostname, url.port or 80), timeout=3).close()
    except OSError as e:
        raise ModelUnavailable(
            f"Cannot reach the local model runtime at {config.OLLAMA_URL} ({e}). "
            "Start Ollama (the Ollama app on Windows, or `ollama serve`) and try again.") from None


def _post(path: str, payload: dict, timeout: float = 600) -> dict:
    _check_server()
    req = urllib.request.Request(
        config.OLLAMA_URL + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code == 404 and "not found" in body:
            raise ModelUnavailable(
                f"Model '{payload.get('model')}' is not downloaded. "
                f"While online, run: ollama pull {payload.get('model')}") from None
        raise ModelUnavailable(f"Ollama error {e.code}: {body}") from None
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise ModelUnavailable(
            f"Cannot reach the local model runtime at {config.OLLAMA_URL} ({e}). "
            "Start Ollama (the Ollama app on Windows, or `ollama serve`) and try again.") from None


def chat(messages: list[dict], temperature: float = config.TEMPERATURE,
         json_mode: bool = False, think: bool = False) -> dict:
    """Send messages to Gemma. Returns {"text", "seconds", "prompt_tokens", "output_tokens"}."""
    payload = {
        "model": config.CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "think": think,  # Gemma 4 thinking mode: off by default, slow on CPU
        "options": {"num_ctx": config.NUM_CTX, "temperature": temperature},
    }
    if json_mode:
        payload["format"] = "json"
    start = time.time()
    d = _post("/api/chat", payload)
    return {
        "text": d["message"]["content"].strip(),
        "seconds": round(time.time() - start, 1),
        "prompt_tokens": d.get("prompt_eval_count", 0),
        "output_tokens": d.get("eval_count", 0),
    }


def embed(texts: list[str]) -> list[list[float]]:
    """Embed texts with the local embedding model (EmbeddingGemma)."""
    d = _post("/api/embed", {"model": config.EMBED_MODEL, "input": texts})
    return d["embeddings"]


def runtime_info() -> dict:
    """Model identity for evidence records. Never raises."""
    info = {"runtime": "Ollama", "url": config.OLLAMA_URL, "model": config.CHAT_MODEL,
            "embed_model": config.EMBED_MODEL, "execution": "local"}
    try:
        info["runtime_version"] = _get("/api/version")["version"]
        for m in _get("/api/tags")["models"]:
            if m["name"] == config.CHAT_MODEL:
                info["quantization"] = m["details"].get("quantization_level")
                info["parameters"] = m["details"].get("parameter_size")
                info["digest"] = m["digest"][:12]
    except Exception:
        info["runtime_version"] = "unreachable"
    return info


def _get(path: str) -> dict:
    _check_server()
    with urllib.request.urlopen(config.OLLAMA_URL + path, timeout=5) as r:
        return json.load(r)
