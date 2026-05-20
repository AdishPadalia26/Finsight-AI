import json
import os
import re
import ast
from dotenv import load_dotenv

load_dotenv()

# Preferred Gemini model per agent role.
MODELS = {
    "extraction":   "gemini-2.5-flash",
    "analysis":     "gemini-2.5-flash",
    "reasoning":    "gemini-2.5-flash",
    "adversarial":  "gemini-2.5-flash",
    "compliance":   "gemini-2.5-flash",
}


class BaseAgent:
    """
    Base class for all FinSight AI agents.
    Each subclass declares PRIMARY and optional FALLBACK provider/model/key-var;
    llm_client routes accordingly with a deterministic fallback as final safety net.
    """

    MODEL_TYPE = "reasoning"
    # Primary LLM
    PROVIDER = None          # "gemini" | "nvidia" | "groq" | "openrouter"
    MODEL_ID = None          # provider-specific model slug
    API_KEY_VAR = None       # env var name holding the API key, e.g. "GROQ_API_KEY_1"
    # Fallback LLM
    FALLBACK_PROVIDER = None
    FALLBACK_MODEL_ID = None
    FALLBACK_API_KEY_VAR = None
    MAX_TOKENS = 4096
    TEMPERATURE = 0.1

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.model = MODELS[self.MODEL_TYPE]

    def run(self, state: dict) -> dict:
        raise NotImplementedError(f"{self.name}.run() must be implemented by subclass")

    def _call_llm(self, user_message: str) -> str:
        from agents.llm_client import call_llm
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        if "injection_detected" in user_message.lower():
            raise ValueError("INJECTION_DETECTED in message")
        return call_llm(
            messages=messages,
            temperature=self.TEMPERATURE,
            max_tokens=self.MAX_TOKENS,
            preferred_model=self.model,
            provider=self.PROVIDER,
            model_id=self.MODEL_ID,
            api_key_var=self.API_KEY_VAR,
            fallback_provider=self.FALLBACK_PROVIDER,
            fallback_model_id=self.FALLBACK_MODEL_ID,
            fallback_api_key_var=self.FALLBACK_API_KEY_VAR,
        )

    def _call_llm_json(self, user_message: str) -> dict:
        """
        Call LLM and parse the response as JSON.
        Strips markdown fences, extracts the first complete JSON object (handles
        trailing markdown), and repairs truncated output.
        """
        raw = self._call_llm(user_message)
        cleaned = raw.strip()

        # Strip ```json ... ``` or ``` ... ``` fences
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            cleaned = "\n".join(inner).strip()

        # Fix: models sometimes write numbered array items as `1. "text"` (invalid JSON)
        cleaned = re.sub(r'(?m)^(\s*)\d+\.\s*"', r'\1"', cleaned)

        # Try parsing as-is first (fast path)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Extract the first complete balanced JSON object — handles trailing markdown
        extracted = self._extract_first_json_block(cleaned)
        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                pass

        # Last resort: close unclosed brackets (truncated output)
        repaired = self._repair_truncated_json(extracted or cleaned)
        if repaired:
            return repaired

        raise ValueError(
            f"{self.name}: LLM returned invalid JSON after cleanup and repair attempt.\n"
            f"Raw output (first 400 chars): {raw[:400]}"
            )

    @staticmethod
    def _extract_first_json_block(text: str) -> str | None:
        """
        Extract the first complete balanced JSON object or array from text.
        Handles models that output valid JSON followed by trailing markdown explanation.
        """
        start = -1
        open_char, close_char = None, None
        for i, ch in enumerate(text):
            if ch == "{":
                start, open_char, close_char = i, "{", "}"
                break
            if ch == "[":
                start, open_char, close_char = i, "[", "]"
                break
        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False
        for i, ch in enumerate(text[start:], start):
            if escaped:
                escaped = False
                continue
            if ch == "\\" and in_string:
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None

    @staticmethod
    def _repair_truncated_json(text: str) -> dict | None:
        """Close any unclosed brackets/braces left by a truncated LLM response."""
        depth_brace = 0
        depth_bracket = 0
        in_string = False
        escaped = False
        for ch in text:
            if escaped:
                escaped = False
                continue
            if ch == "\\" and in_string:
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth_brace += 1
            elif ch == "}":
                depth_brace -= 1
            elif ch == "[":
                depth_bracket += 1
            elif ch == "]":
                depth_bracket -= 1

        closing = "]" * max(depth_bracket, 0) + "}" * max(depth_brace, 0)
        if not closing:
            return None
        try:
            return json.loads(text.rstrip(",\n ") + closing)
        except json.JSONDecodeError:
            return None


class StubAgent(BaseAgent):
    """
    Placeholder for Phase 2 agents.
    Returns a structured stub response so the LangGraph pipeline stays intact.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.system_prompt = ""
        self.model = "stub"
        self.description = description

    def run(self, state: dict) -> dict:
        return {
            "status": "phase_2_not_implemented",
            "agent": self.name,
            "description": self.description,
            "phase": 2,
        }
