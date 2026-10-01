import re
from pathlib import Path

def safe_filename(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:50] or "comic"

def public_static_url(file_path: Path, static_dir: Path) -> str:
    try:
        relative = file_path.resolve().relative_to(static_dir.resolve())
        return f"/static/{relative.as_posix()}"
    except:
        return f"/static/{file_path.name}"