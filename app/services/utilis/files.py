import re
from pathlib import Path
from uuid import uuid4


def safe_filename(
    text: str,
    suffix: str = ".png",
) -> str:
    """
    Convert arbitrary text into a safe filename.
    """

    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        text,
    )

    cleaned = (
        cleaned
        .strip("-")
        .lower()
    )

    cleaned = cleaned[:60]

    if not cleaned:
        cleaned = "panel"

    return (
        f"{cleaned}-"
        f"{uuid4().hex[:8]}"
        f"{suffix}"
    )


def public_static_url(
    path: Path,
    static_dir: Path,
) -> str:
    """
    Convert a filesystem path such as:

    static/panels/panel-1.png

    into:

    /static/panels/panel-1.png
    """

    relative = (
        path.resolve()
        .relative_to(
            static_dir.resolve()
        )
    )

    return (
        "/static/"
        + relative.as_posix()
    )