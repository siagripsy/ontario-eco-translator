from datetime import datetime, timezone
from pathlib import Path

from app.utils.text import slugify_filename


def build_upload_path(base_dir: Path, filename: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_name = slugify_filename(filename)
    return base_dir / f"{timestamp}_{safe_name}"


def write_bytes_to_file(file_path: Path, content: bytes) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)
