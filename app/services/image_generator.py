from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image

from app.config import get_settings
from app.utils.files import safe_filename


def generate_image(
    image_prompt: str,
    panel_number: int,
) -> Path:

    settings = get_settings()

    token = settings.resolved_hf_token

    if not token:
        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Add HF_API_KEY=hf_... to your .env file."
        )

    client = InferenceClient(
        api_key=token,
        provider="auto",
    )

    enhanced_prompt = (
        f"{image_prompt}. "
        "High-quality sequential comic panel, "
        "clear composition, expressive character, "
        "clean line art, cinematic lighting, "
        "strong visual storytelling, "
        "detailed background, "
        "professional comic illustration, "
        "no text, no letters, no speech bubbles."
    )

    image = client.text_to_image(
        prompt=enhanced_prompt,
        model="black-forest-labs/FLUX.1-schnell",
    )

    if not isinstance(image, Image.Image):
        image = Image.open(image)

    output_dir = settings.output_dir / "panels"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = safe_filename(
        f"panel-{panel_number}"
    )

    path = output_dir / f"{filename}.png"

    image.convert("RGB").save(
        path,
        format="PNG",
    )

    if not path.exists():
        raise RuntimeError(
            f"Image was not saved: {path}"
        )

    return path
