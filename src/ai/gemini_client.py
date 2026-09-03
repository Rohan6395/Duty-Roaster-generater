from __future__ import annotations

from dataclasses import dataclass

from config.settings import get_secret_or_env, get_settings


@dataclass
class GeminiClient:
    """Lightweight Gemini configuration wrapper for API readiness checks."""

    model_name: str
    api_key: str | None

    @classmethod
    def from_settings(cls) -> "GeminiClient":
        settings = get_settings()
        key = get_secret_or_env("GEMINI_API_KEY") or settings.gemini_api_key
        model_name = get_secret_or_env("GEMINI_MODEL") or settings.gemini_model
        return cls(model_name=model_name, api_key=key)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model_name)
