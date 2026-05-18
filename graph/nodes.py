import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class BaseAgent:
    """
    Base class for all FinSight AI agents.
    Each agent has a name, a fixed system prompt, and access to the Anthropic client.
    Subclasses implement run() with their specific logic.
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state: dict) -> dict:
        raise NotImplementedError(f"{self.name}.run() must be implemented by subclass")

    def _call_llm(self, user_message: str) -> str:
        """Call Claude with this agent's fixed system prompt."""
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _call_llm_json(self, user_message: str) -> dict:
        """Call Claude and parse the response as JSON. Raises ValueError on bad JSON."""
        raw = self._call_llm(user_message)
        # Strip markdown code fences if the model wraps output in ```json ... ```
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"{self.name}: LLM returned invalid JSON — {e}\nRaw: {raw[:300]}")


class StubAgent(BaseAgent):
    """
    Placeholder for Phase 2 agents.
    Returns a structured stub response so the LangGraph pipeline stays intact.
    """

    def __init__(self, name: str, description: str):
        super().__init__(name=name, system_prompt="")
        self.description = description

    def run(self, state: dict) -> dict:
        return {
            "status": "phase_2_not_implemented",
            "agent": self.name,
            "description": self.description,
            "phase": 2,
        }
