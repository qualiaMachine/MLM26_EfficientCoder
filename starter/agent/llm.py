"""Thin wrapper around any OpenAI-compatible chat completions endpoint.

Works with Ollama, vLLM, llama.cpp server, Together, Fireworks, Groq — anything
that speaks the OpenAI API. Configure via .env (see .env.example).
"""

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Provider prefixes used by Harbor's --model flag (litellm-style, e.g.
# "ollama/qwen2.5-coder:32b"). The OpenAI-compatible endpoint itself wants the
# bare model id, so we strip a known prefix if present.
_PROVIDER_PREFIXES = (
    "ollama/",
    "openai/",
    "hosted_vllm/",
    "together_ai/",
    "fireworks_ai/",
    "groq/",
)


def _resolve_model(model_name: str | None) -> str:
    model = os.environ.get("LLM_MODEL") or model_name
    if not model:
        raise ValueError(
            "No model configured. Set LLM_MODEL in .env or pass -m to harbor run."
        )
    for prefix in _PROVIDER_PREFIXES:
        if model.startswith(prefix):
            return model[len(prefix) :]
    return model


class LLMClient:
    def __init__(self, model_name: str | None = None):
        base_url = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
        api_key = os.environ.get("LLM_API_KEY", "none")
        self.model = _resolve_model(model_name)
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "2048"))
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def chat(self, messages: list[dict]) -> tuple[str, dict]:
        """Send the conversation, return (assistant_text, usage_dict)."""
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        text = response.choices[0].message.content or ""
        usage = {}
        if response.usage is not None:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
            }
        return text, usage
