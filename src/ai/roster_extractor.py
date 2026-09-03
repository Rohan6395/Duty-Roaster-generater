from __future__ import annotations

import json
import logging
from pathlib import Path

import google.generativeai as genai
from PIL import Image

from config.settings import get_secret_or_env, get_settings
from src.models.roster import RosterData

logger = logging.getLogger(__name__)


class RosterExtractor:
    """Gemini Vision-based handwritten roster extraction."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._init_api()

    def _init_api(self) -> None:
        """Initialize Gemini API with free-tier models."""
        api_key = get_secret_or_env("GEMINI_API_KEY") or self.settings.gemini_api_key
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        genai.configure(api_key=api_key)

    def extract(self, image_paths: list[Path], prompt_text: str) -> RosterData:
        """Extract roster data from handwritten images using Gemini Vision."""
        if not image_paths:
            raise ValueError("No images provided for extraction")

        logger.info("Extracting roster from %d image(s) using Gemini Vision", len(image_paths))

        # Use free-tier flash model for faster processing
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Prepare images
        image_data = []
        for img_path in image_paths:
            img = Image.open(img_path)
            image_data.append(img)

        # Build request with all images
        request_parts = []
        for img in image_data:
            request_parts.append(img)

        request_parts.append(prompt_text)

        try:
            response = model.generate_content(request_parts)
            text_response = response.text

            logger.debug("Gemini raw response: %s", text_response)

            # Parse JSON from response
            json_str = self._extract_json_from_response(text_response)
            roster_dict = json.loads(json_str)

            # Validate and construct RosterData
            roster = RosterData(**roster_dict)
            logger.info(
                "Successfully extracted roster: %d/%d, %d staff members",
                roster.month,
                roster.year,
                len(roster.staff),
            )
            return roster

        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON response from Gemini: %s", exc)
            raise ValueError("Could not parse roster data from image. Please ensure the image is clear.") from exc
        except Exception as exc:
            logger.exception("Gemini extraction failed")
            raise

    @staticmethod
    def _extract_json_from_response(response_text: str) -> str:
        """Extract JSON object from Gemini response."""
        # Try to find JSON block markers
        if "```json" in response_text:
            start = response_text.find("```json") + len("```json")
            end = response_text.find("```", start)
            if end > start:
                return response_text[start:end].strip()

        # Try to find any JSON object
        if "{" in response_text and "}" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return response_text[start:end]

        raise ValueError("No JSON found in Gemini response")
