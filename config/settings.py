from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment and Streamlit secrets."""

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro", alias="GEMINI_MODEL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_image_side: int = Field(default=2200, alias="MAX_IMAGE_SIDE")
    min_font_size: int = Field(default=6, alias="MIN_FONT_SIZE")
    preferred_font_size: int = Field(default=10, alias="PREFERRED_FONT_SIZE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_secret_or_env(name: str) -> str | None:
    """Get secret from Streamlit secrets first, then environment."""

    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass

    value = os.getenv(name)
    return value if value else None
