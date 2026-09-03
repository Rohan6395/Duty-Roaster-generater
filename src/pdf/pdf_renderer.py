from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image


def render_pdf_preview(pdf_path: Path, output_image_path: Path, zoom: float = 1.3) -> Path:
    """Render first PDF page to a preview image."""

    with fitz.open(pdf_path) as doc:
        if doc.page_count != 1:
            raise ValueError("Expected single-page PDF for duty roster output")
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image.save(output_image_path)
    return output_image_path
