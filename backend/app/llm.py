"""The LLM client. The planner only needs an object with complete(prompt) -> str."""
import os
from typing import Optional

DEFAULT_MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 4000
TIMEOUT_SECONDS = 30.0


class AnthropicLLM:
    def __init__(self, client=None, model: Optional[str] = None, timeout: float = TIMEOUT_SECONDS):
        if client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not set")
            import anthropic

            client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        self._client = client
        self._model = model or os.environ.get("ONTARGET_MODEL", DEFAULT_MODEL)

    def complete(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if block.type == "text")


class OpenAICompatibleLLM:
    """Works with any provider that offers the OpenAI chat-completions format:
    Google Gemini, Groq, OpenRouter, Ollama (local), and others, many with free tiers."""

    def __init__(self, base_url: str, model: str, api_key: Optional[str] = None, client=None,
                 timeout: float = 60.0):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._model = model
        self._api_key = api_key
        if client is None:
            import httpx

            client = httpx.Client(timeout=timeout)
        self._client = client

    def complete(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        response = self._client.post(
            self._url,
            headers=headers,
            json={"model": self._model, "max_tokens": MAX_TOKENS,
                  "messages": [{"role": "user", "content": prompt}]},
        )
        response.raise_for_status()
        try:
            return response.json()["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise RuntimeError(f"unexpected response from the LLM provider: {response.text[:200]}") from exc


def default_llm():
    """Pick the LLM from environment variables, or None (the planner then uses its default plan).

    ONTARGET_LLM_BASE_URL + ONTARGET_LLM_MODEL (+ ONTARGET_LLM_API_KEY)  -> any OpenAI-compatible provider
    ANTHROPIC_API_KEY                                                    -> Anthropic
    """
    base_url = os.environ.get("ONTARGET_LLM_BASE_URL")
    if base_url:
        model = os.environ.get("ONTARGET_LLM_MODEL")
        if not model:
            raise RuntimeError("ONTARGET_LLM_MODEL must be set when ONTARGET_LLM_BASE_URL is set")
        return OpenAICompatibleLLM(base_url, model, os.environ.get("ONTARGET_LLM_API_KEY"))
    return AnthropicLLM() if os.environ.get("ANTHROPIC_API_KEY") else None
