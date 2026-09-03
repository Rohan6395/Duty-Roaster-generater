from __future__ import annotations

from pathlib import Path


def ensure_temp_dir(base: Path | None = None) -> Path:
    root = base or Path("tmp")
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_uploaded_file(target_dir: Path, file_name: str, content: bytes) -> Path:
    target = target_dir / file_name
    target.write_bytes(content)
    return target
