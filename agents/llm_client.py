"""Centralized LLM client — per-agent provider routing with explicit API key support.

Each agent specifies:
  PROVIDER        — primary provider: "gemini" | "nvidia" | "groq" | "openrouter"
  MODEL_ID        — model slug for that provider
  API_KEY_VAR     — env var holding the API key (e.g. "GROQ_API_KEY_1")
  FALLBACK_PROVIDER / FALLBACK_MODEL_ID / FALLBACK_API_KEY_VAR — secondary attempt

If both primary and fallback fail, RuntimeError is raised and the agent's own
deterministic fallback kicks in so the user always sees something on screen.
"""

import os
import time
import random

import httpx
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ── Gemini config ──────────────────────────────────────────────────────────────

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

# ── NVIDIA NIM config ──────────────────────────────────────────────────────────

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODELS = [
    "meta/llama-3.3-70b-instruct",
    "nvidia/llama-3.3-nemotron-super-49b-v1",
    "meta/llama-3.1-70b-instruct",
    "mistralai/mixtral-8x22b-instruct-v0.1",
]

# ── Groq config ────────────────────────────────────────────────────────────────

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

# ── OpenRouter config ──────────────────────────────────────────────────────────

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Thinking models return content=null; pass reasoning:{enabled:false} to suppress trace.
THINKING_MODELS = {
    "z-ai/glm-4.5-air:free",
    "z-ai/glm-4.5-air",
    "nvidia/nemotron-nano-9b-v2:free",
    "nvidia/nemotron-nano-9b-v2",
}


# ── Gemini ─────────────────────────────────────────────────────────────────────

def _split_messages(messages: list[dict]) -> tuple[str | None, str | list]:
    system = None
    user_contents = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system = content
        elif role == "user":
            user_contents.append({"role": "user", "parts": [{"text": content}]})
        elif role == "assistant":
            user_contents.append({"role": "model", "parts": [{"text": content}]})
    if len(user_contents) == 1:
        return system, user_contents[0]["parts"][0]["text"]
    return system, user_contents if user_contents else ""


def _call_gemini(
    messages: list,
    temperature: float,
    max_tokens: int,
    model_id: str | None,
    api_key: str | None = None,
) -> str | None:
    """Call Gemini. Returns None on quota/safety failure."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return None

    model_name = model_id or os.getenv("GEMINI_MODEL") or GEMINI_MODELS[0]
    system_instruction, contents = _split_messages(messages)
    if not contents:
        return None

    client = genai.Client(api_key=key)

    for attempt in range(3):
        try:
            time.sleep(random.uniform(0, 0.5))
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config={
                    "system_instruction": system_instruction,
                    "temperature": temperature,
                    "max_output_tokens": min(max_tokens, 8192),
                },
            )
            return response.text
        except Exception as e:
            err_str = str(e).lower()
            if "quota" in err_str or "rate limit" in err_str or "429" in err_str or "resource exhausted" in err_str:
                print(f"[llm_client] Gemini quota exhausted")
                return None
            if "safety" in err_str or "blocked" in err_str:
                print(f"[llm_client] Gemini blocked (safety)")
                return None
            print(f"[llm_client] Gemini {model_name} error (attempt {attempt + 1}/3): {e}")
            if attempt < 2:
                time.sleep(3 * (attempt + 1))

    return None


# ── NVIDIA NIM ─────────────────────────────────────────────────────────────────

def _call_nvidia(
    messages: list,
    temperature: float,
    max_tokens: int,
    model_id: str | None,
    api_key: str | None = None,
) -> str | None:
    """Call NVIDIA NIM (OpenAI-compatible). Returns None on failure."""
    key = api_key or os.getenv("NVIDIA_API_KEY")
    if not key:
        return None

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    # Always try the requested model first, then fall back to defaults
    models = [model_id] + [m for m in NVIDIA_MODELS if m != model_id] if model_id else list(NVIDIA_MODELS)

    with httpx.Client(timeout=120) as client:
        for model in models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": min(max_tokens, 4096),
            }
            for attempt in range(3):
                try:
                    time.sleep(random.uniform(0, 0.5))
                    response = client.post(NVIDIA_API_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    status = getattr(getattr(e, "response", None), "status_code", None)
                    if status == 429:
                        wait = 8 * (attempt + 1) + random.uniform(0, 3)
                        print(f"[llm_client] NVIDIA {model} rate-limited, waiting {wait:.0f}s")
                        time.sleep(wait)
                        continue
                    elif status in (400, 404, 422):
                        # 404 = model not provisioned for this account — retrying
                        # won't help, so skip straight to the next NVIDIA model.
                        print(f"[llm_client] NVIDIA {model} {status} — trying next model")
                        break
                    else:
                        print(f"[llm_client] NVIDIA {model} error (attempt {attempt + 1}/3): {e}")
                        if attempt < 2:
                            time.sleep(3 * (attempt + 1))

    print("[llm_client] NVIDIA NIM exhausted")
    return None


# ── Groq ───────────────────────────────────────────────────────────────────────

def _call_groq(
    messages: list,
    temperature: float,
    max_tokens: int,
    model_id: str | None,
    api_key: str | None = None,
) -> str | None:
    """Call Groq. Returns None if key missing; raises RuntimeError if all models fail."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return None

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    models = [model_id] + [m for m in GROQ_MODELS if m != model_id] if model_id else list(GROQ_MODELS)
    last_error: Exception | None = None

    with httpx.Client(timeout=120) as client:
        for model in models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": min(max_tokens, 4096),
            }
            for attempt in range(3):
                time.sleep(random.uniform(0, 1))
                try:
                    response = client.post(GROQ_API_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    last_error = e
                    status = getattr(getattr(e, "response", None), "status_code", None)
                    if status == 429:
                        wait = 8 * (attempt + 1) + random.uniform(0, 3)
                        print(f"[llm_client] Groq {model} rate-limited, waiting {wait:.0f}s")
                        time.sleep(wait)
                        continue
                    elif status == 400:
                        print(f"[llm_client] Groq {model} 400 — trying next model")
                        break
                    else:
                        print(f"[llm_client] Groq {model} error (attempt {attempt + 1}/3): {e}")
                        if attempt < 2:
                            time.sleep(3 * (attempt + 1))

    print(f"[llm_client] Groq exhausted. Last error: {last_error}")
    return None


# ── OpenRouter ─────────────────────────────────────────────────────────────────

def _call_openrouter(
    messages: list,
    temperature: float,
    max_tokens: int,
    model_id: str | None,
    api_key: str | None = None,
) -> str | None:
    """Call OpenRouter. Returns None on failure."""
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key or not model_id:
        return None

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/AdishPadalia26/Finsight-AI",
        "X-Title": "FinSight AI",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": min(max_tokens, 8192),
    }
    if model_id in THINKING_MODELS:
        payload["reasoning"] = {"enabled": False}

    with httpx.Client(timeout=120) as client:
        for attempt in range(3):
            try:
                time.sleep(random.uniform(0, 0.5))
                response = client.post(OPENROUTER_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                msg = response.json()["choices"][0]["message"]
                content = msg.get("content")
                if content is None:
                    content = msg.get("reasoning") or ""
                    if content:
                        print(f"[llm_client] {model_id}: content=null, using reasoning field")
                    else:
                        print(f"[llm_client] {model_id}: content=null and no reasoning — failure")
                        return None
                return content
            except Exception as e:
                status = getattr(getattr(e, "response", None), "status_code", None)
                if status == 429:
                    wait = 8 * (attempt + 1) + random.uniform(0, 3)
                    print(f"[llm_client] OpenRouter {model_id} rate-limited, waiting {wait:.0f}s")
                    time.sleep(wait)
                    continue
                elif status in (400, 404, 422):
                    print(f"[llm_client] OpenRouter {model_id} {status} — skipping")
                    return None
                else:
                    print(f"[llm_client] OpenRouter {model_id} error (attempt {attempt + 1}/3): {e}")
                    if attempt < 2:
                        time.sleep(3 * (attempt + 1))

    print(f"[llm_client] OpenRouter {model_id} exhausted")
    return None


# ── Public API ─────────────────────────────────────────────────────────────────

def call_llm(
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    # Primary
    provider: str | None = None,
    model_id: str | None = None,
    api_key_var: str | None = None,
    # Fallback LLM
    fallback_provider: str | None = None,
    fallback_model_id: str | None = None,
    fallback_api_key_var: str | None = None,
    # Legacy compat
    preferred_model: str | None = None,
    retries: int = 3,
) -> str:
    """
    Route to primary provider → fallback provider → raise RuntimeError.
    RuntimeError propagates to the agent's own deterministic fallback,
    ensuring the user always sees output.

    provider: "gemini" | "nvidia" | "groq" | "openrouter"
    api_key_var: env var name, e.g. "GROQ_API_KEY_1"
    """

    # Provider-specific fallback env var names for single-key setups
    _KEY_FALLBACKS = {
        "GROQ_API_KEY_1": "GROQ_API_KEY",
        "GROQ_API_KEY_2": "GROQ_API_KEY",
        "GROQ_API_KEY_3": "GROQ_API_KEY",
        "OPENROUTER_API_KEY_1": "OPENROUTER_API_KEY",
        "OPENROUTER_API_KEY_2": "OPENROUTER_API_KEY",
        "OPENROUTER_API_KEY_3": "OPENROUTER_API_KEY",
        "NVIDIA_API_KEY_1": "NVIDIA_API_KEY",
        "NVIDIA_API_KEY_2": "NVIDIA_API_KEY",
    }

    def _resolve(key_var: str | None) -> str | None:
        if not key_var:
            return None
        value = os.getenv(key_var)
        if not value:
            fallback_var = _KEY_FALLBACKS.get(key_var)
            if fallback_var:
                value = os.getenv(fallback_var)
        return value

    def _dispatch(prov: str, mid: str | None, key: str | None) -> str | None:
        if prov == "gemini":
            return _call_gemini(messages, temperature, max_tokens, mid, api_key=key)
        if prov == "nvidia":
            return _call_nvidia(messages, temperature, max_tokens, mid, api_key=key)
        if prov == "groq":
            return _call_groq(messages, temperature, max_tokens, mid, api_key=key)
        if prov == "openrouter":
            return _call_openrouter(messages, temperature, max_tokens, mid, api_key=key)
        return None

    # ── 1. Primary provider ───────────────────────────────────────────────────
    if provider:
        result = _dispatch(provider, model_id, _resolve(api_key_var))
        if result is not None:
            return result
        print(f"[llm_client] Primary {provider}/{model_id} failed — trying fallback")

    # ── 2. Fallback provider ──────────────────────────────────────────────────
    if fallback_provider:
        result = _dispatch(fallback_provider, fallback_model_id, _resolve(fallback_api_key_var))
        if result is not None:
            return result
        print(f"[llm_client] Fallback {fallback_provider}/{fallback_model_id} also failed")

    # ── 3. Legacy default chain (no provider specified) ───────────────────────
    if not provider and not fallback_provider:
        result = _call_gemini(messages, temperature, max_tokens, preferred_model or GEMINI_MODELS[0])
        if result is not None:
            return result
        result = _call_nvidia(messages, temperature, max_tokens, preferred_model)
        if result is not None:
            return result
        result = _call_groq(messages, temperature, max_tokens, preferred_model)
        if result is not None:
            return result

    raise RuntimeError(
        f"All LLM providers exhausted (primary={provider}/{model_id}, "
        f"fallback={fallback_provider}/{fallback_model_id}). "
        "Agent deterministic fallback will be used."
    )
