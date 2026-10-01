from pathlib import Path
from typing import List

from app.models import PanelStory
from app.utils.files import public_static_url


def build_comic_layout(
    stories: List[PanelStory],
    image_paths: List[Path],
) -> list[dict]:

    if not stories:
        raise RuntimeError("No panels received.")

    if not image_paths:
        raise RuntimeError("No images received.")

    if len(stories) != len(image_paths):
        raise RuntimeError(
            f"Panel/image count mismatch: "
            f"{len(stories)} panels, "
            f"{len(image_paths)} images."
        )

    settings_dir = (
        Path(__file__).resolve().parents[2] / "static"
    )

    layout = []

    for panel, image_path in zip(stories, image_paths):

        if hasattr(panel, "model_dump"):
            item = panel.model_dump()

        elif isinstance(panel, dict):
            item = panel.copy()

        else:
            raise RuntimeError(
                f"Unsupported panel type: {type(panel).__name__}"
            )

        image_url = public_static_url(
            image_path,
            settings_dir,
        )

        item["image_path"] = image_url

        layout.append(item)

    if not layout:
        raise RuntimeError("No comic panels were created.")

    return layout
