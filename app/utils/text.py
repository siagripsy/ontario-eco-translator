import re
from pathlib import Path


def normalize_whitespace(value: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join([line for line in lines if line]).strip()


def clip_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 3].rstrip() + "..."


def slugify_filename(filename: str) -> str:
    path = Path(filename)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("-") or "document"
    suffix = path.suffix if path.suffix.lower() == ".pdf" else ".pdf"
    return f"{stem}{suffix}"
