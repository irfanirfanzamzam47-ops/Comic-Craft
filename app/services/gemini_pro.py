import json
from typing import List

from google import genai

from app.config import get_settings
from app.models import PanelOutline, PanelStory


# ============================================================
# JSON EXTRACTION
# ============================================================

def _extract_json(text: str) -> list:
    """
    Extract a JSON array from Gemini's response.

    Supports:
        [
            {...}
        ]

    and fenced responses such as:

        ```json
        [
            {...}
        ]
        ```
    """

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # --------------------------------------------------------
    # Find JSON array
    # --------------------------------------------------------

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:

        raise ValueError(
            "Gemini did not return a JSON array."
        )

    json_text = text[start:end + 1]

    try:

        return json.loads(json_text)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc


# ============================================================
# GENERATE DETAILED STORY
# ============================================================

def generate_story(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    outlines: List[PanelOutline],
) -> List[PanelStory]:

    settings = get_settings()

    # ========================================================
    # CHECK API KEY
    # ========================================================

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    # ========================================================
    # CHECK OUTLINE
    # ========================================================

    if not outlines:

        raise RuntimeError(
            "No comic outlines were received by Gemini Pro."
        )

    if len(outlines) != 5:

        raise RuntimeError(
            f"Expected 5 outlines, received {len(outlines)}."
        )

    # ========================================================
    # CREATE GEMINI CLIENT
    # ========================================================

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    # ========================================================
    # CONVERT OUTLINE TO JSON
    # ========================================================

    outline_json = json.dumps(
        [
            panel.model_dump()
            for panel in outlines
        ],
        ensure_ascii=False,
        indent=2,
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are the detailed storytelling engine for an AI comic creator.

Create the final content for a five-panel comic.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

FIVE-PANEL OUTLINE:
{outline_json}

Requirements:

1. Preserve exactly five panels.
2. Preserve the order of the panels.
3. Keep the same main character throughout.
4. Keep the setting consistent.
5. Make the story flow naturally from panel to panel.
6. Create concise comic captions.
7. Create concise narration.
8. Add short character dialogue where appropriate.
9. Keep the dialogue family-friendly.
10. Create detailed visual image prompts.
11. Make every image prompt suitable for an AI image generator.
12. The art style should match: {art_style}.
13. The tone should match: {tone}.
14. Do not change the basic story idea.
15. Each panel must have all required fields.

Return ONLY a JSON array containing exactly five objects.

Each object MUST contain:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Example:

[
  {{
    "panel_number": 1,
    "title": "The Beginning",
    "scene_description": "A young fox stands at the edge of a mysterious forest.",
    "caption": "The adventure begins.",
    "narration": "The fox discovers that something important is missing.",
    "dialogue": "I have to find it!",
    "image_prompt": "A detailed comic book illustration of a young fox standing at the edge of an enchanted forest, dramatic lighting, expressive character, detailed environment, {art_style} style."
  }}
]

Important:

- Return ONLY valid JSON.
- Do not use markdown.
- Do not use ```json.
- Do not add explanations before or after the JSON.
"""

    # ========================================================
    # CALL GEMINI
    # ========================================================

    print()
    print("=" * 70)
    p