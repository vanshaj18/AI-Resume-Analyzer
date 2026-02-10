from __future__ import annotations

import os
from types import SimpleNamespace

from groq import Groq

try:
    import google.generativeai as genai
except Exception:
    genai = None

DEFAULT_MODELS = {
    "groq": "llama-3.1-8b-instant",
    "gemini": "gemini-2.5-flash",
}

def _combine_messages(messages: list[dict]) -> str:
    parts = []
    for msg in messages or []:
        role = (msg or {}).get("role", "user")
        content = (msg or {}).get("content", "")
        parts.append(f"{role.upper()}:\n{content}")
    return "\n\n".join(parts).strip()


class _GeminiClientShim:
    def __init__(self, genai_module):
        self._genai = genai_module
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model: str, temperature: float | None, messages: list[dict]):
        prompt = _combine_messages(messages)
        generation_config = {"temperature": temperature} if temperature is not None else None
        model_obj = self._genai.GenerativeModel(model)
        response = model_obj.generate_content(prompt, generation_config=generation_config)
        content = getattr(response, "text", None)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content or ""))]
        )


def get_llm_client():
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if groq_key:
        return Groq(api_key=groq_key), "groq"
    if gemini_key:
        if genai is None:
            raise RuntimeError("Gemini client not installed. Install google-generativeai.")
        genai.configure(api_key=gemini_key)
        return _GeminiClientShim(genai), "gemini"

    raise RuntimeError("Set GROQ_API_KEY or GEMINI_API_KEY in the environment.")


def get_default_model(provider: str) -> str:
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["groq"])
