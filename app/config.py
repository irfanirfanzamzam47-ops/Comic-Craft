from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # -----------------------------
    # Gemini configuration
    # -----------------------------

    gemini_api_key: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY",
    )

    gemini_flash_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias="GEMINI_FLASH_MODEL",
    )

    gemini_pro_model: str = Field(
        default="gemini-3.8-pro",
        validation_alias="GEMINI_PRO_MODEL",
    )

    # -----------------------------
    # Hugging Face configuration
    # -----------------------------

    # The original project documentation calls this HF_API_KEY.
    hf_api_key: str = Field(
        default="",
        validation_alias="HF_API_KEY",
    )

    # Backwards-compatible alternative.
    hf_token: str = Field(
        default="",
        validation_alias="HF_TOKEN",
    )

    # -----------------------------
    # Image generation
    # -----------------------------

    image_model: str = Field(
        default="runwayml/stable-diffusion-v1-5",
        validation_alias="IMAGE_MODEL",
    )

    image_width: int = Field(
        default=768,
        validation_alias="IMAGE_WIDTH",
    )

    image_height: int = Field(
        default=512,
        validation_alias="IMAGE_HEIGHT",
    )

    image_steps: int = Field(
        default=28,
        validation_alias="IMAGE_STEPS",
    )

    image_guidance: float = Field(
        default=7.0,
        validation_alias="IMAGE_GUIDANCE",
    )

    # -----------------------------
    # Application settings
    # -----------------------------

    max_panels: int = Field(
        default=5,
        validation_alias="MAX_PANELS",
    )

    request_timeout_seconds: int = Field(
        default=180,
        validation_alias="REQUEST_TIMEOUT_SECONDS",
    )

    output_dir: Path = BASE_DIR / "static"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_hf_token(self) -> str:
        """
        Supports either:

        HF_API_KEY=hf_...
        or
        HF_TOKEN=hf_...
        """

        return self.hf_api_key or self.hf_token


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    # Make sure generated files have somewhere to go.
    (settings.output_dir / "panels").mkdir(
        parents=True,
        exist_ok=True,
    )

    (settings.output_dir / "exports").mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings