from __future__ import annotations

from pathlib import Path

import fitz
import yaml


def _load_template_files(templates_dir: Path) -> list[dict]:
    templates: list[dict] = []
    for path in templates_dir.glob("*.yaml"):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if isinstance(data, dict):
                templates.append(data)
    return templates


def suggest_template_from_pdf(reference_pdf: Path, templates_dir: Path) -> str | None:
    """Return template_id suggestion based on keyword matching."""

    with fitz.open(reference_pdf) as doc:
        if doc.page_count == 0:
            return None
        text = doc[0].get_text("text").upper()

    for template in _load_template_files(templates_dir):
        template_id = template.get("template_id")
        keywords = [str(x).upper() for x in template.get("match_keywords", [])]
        if template_id and keywords and all(k in text for k in keywords):
            return str(template_id)

    for template in _load_template_files(templates_dir):
        template_id = template.get("template_id")
        keywords = [str(x).upper() for x in template.get("match_keywords", [])]
        if template_id and any(k in text for k in keywords):
            return str(template_id)

    return None
