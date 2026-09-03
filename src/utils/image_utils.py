from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


def preprocess_image_for_ai(input_path: Path, output_path: Path, max_side: int = 2200) -> Path:
    """Apply EXIF orientation and safe resize while preserving readability."""

    with Image.open(input_path) as img:
        fixed = ImageOps.exif_transpose(img)
        width, height = fixed.size
        longest = max(width, height)

        if longest > max_side:
            scale = max_side / float(longest)
            new_size = (int(width * scale), int(height * scale))
            fixed = fixed.resize(new_size, Image.Resampling.LANCZOS)

        fixed.save(output_path)
    return output_path
