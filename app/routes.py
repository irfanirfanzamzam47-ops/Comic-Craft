from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import PromptRequest

from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf

from app.utils.files import public_static_url


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ============================================================
# GENERATION WORKFLOW
# ============================================================

def run_generation(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):
    settings = get_settings()

    print()
    print("=" * 70)
    print("              COMICCRAFT GENERATION STARTED")
    print("=" * 70)

    print()
    print("USER INPUT")
    print("-" * 70)
    print("Story Prompt :", story_prompt)
    print("Character    :", character_name)
    print("Setting      :", setting)
    print("Tone         :", tone)
    print("Art Style    :", art_style)

    # ========================================================
    # STEP 1 - GENERATE OUTLINE
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 1 - GENERATING OUTLINE")
    print("=" * 70)

    outlines = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    print()
    print("OUTLINE RESULT:")
    print(outlines)

    if outlines is None:
        raise RuntimeError(
            "generate_outline() returned None."
        )

    if not outlines:
        raise RuntimeError(
            "No outlines were generated."
        )

    print(
        "Number of outlines:",
        len(outlines)
    )

    # ========================================================
    # STEP 2 - GENERATE STORY
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 2 - GENERATING STORY")
    print("=" * 70)

    stories = generate_story(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        outlines=outlines,
    )

    print()
    print("STORY RESULT:")
    print(stories)

    if stories is None:
        raise RuntimeError(
            "generate_story() returned None."
        )

    if not stories:
        raise RuntimeError(
            "No stories were generated."
        )

    print(
        "Number of stories:",
        len(stories)
    )

    # ========================================================
    # STEP 3 - GENERATE IMAGES
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 3 - GENERATING COMIC IMAGES")
    print("=" * 70)

    image_paths = []

    for index, panel in enumerate(
        stories,
        start=1,
    ):

        print()
        print("-" * 70)
        print(f"GENERATING IMAGE FOR PANEL {index}")
        print("-" * 70)

        print()
        print("Panel:")
        print(panel)

        # ----------------------------------------------------
        # GET PANEL NUMBER
        # ----------------------------------------------------

        if isinstance(panel, dict):

            panel_number = panel.get(
                "panel_number",
                index,
            )

            image_prompt = panel.get(
                "image_prompt",
                "",
            )

        else:

            panel_number = getattr(
                panel,
                "panel_number",
                index,
            )

            image_prompt = getattr(
                panel,
                "image_prompt",
                "",
            )

        print()
        print("Panel number:")
        print(panel_number)

        print()
        print("Image prompt:")
        print(image_prompt)

        if not image_prompt:

            raise RuntimeError(
                f"Panel {index} does not contain an image_prompt."
            )

        # ----------------------------------------------------
        # GENERATE IMAGE
        # ----------------------------------------------------

        image_path = generate_image(
            image_prompt=image_prompt,
            panel_number=panel_number,
        )

        print()
        print("Generated image path:")
        print(image_path)

        if not image_path:

            raise RuntimeError(
                f"Image generation failed for panel {index}."
            )

        image_paths.append(
            Path(image_path)
        )

    # ========================================================
    # IMAGE CHECK
    # ========================================================

    print()
    print("=" * 70)
    print("IMAGE GENERATION COMPLETE")
    print("=" * 70)

    print()
    print("Number of images:")
    print(len(image_paths))

    if len(image_paths) == 0:
        raise RuntimeError(
            "No comic images were generated."
        )

    # ========================================================
    # STEP 4 - BUILD LAYOUT
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 4 - BUILDING COMIC LAYOUT")
    print("=" * 70)

    layout = build_comic_layout(
        stories=stories,
        image_paths=image_paths,
    )

    print()
    print("LAYOUT RESULT:")
    print(layout)

    if layout is None:
        raise RuntimeError(
            "build_comic_layout() returned None."
        )

    if not layout:
        raise RuntimeError(
            "build_comic_layout() returned an EMPTY layout."
        )

    print()
    print(
        "Number of layout panels:",
        len(layout)
    )

    # ========================================================
    # STEP 5 - CREATE PDF
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 5 - CREATING PDF")
    print("=" * 70)

    pdf_path = save_pdf(
        stories=stories,
        image_paths=image_paths,
    )

    print()
    print("PDF path:")
    print(pdf_path)

    if not pdf_path:
        raise RuntimeError(
            "PDF generation failed."
        )

    # ========================================================
    # STEP 6 - CREATE PDF URL
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 6 - CREATING PDF URL")
    print("=" * 70)

    pdf_url = public_static_url(
        pdf_path,
        settings.output_dir,
    )

    print()
    print("PDF URL:")
    print(pdf_url)

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 70)
    print("          COMICCRAFT GENERATION COMPLETE")
    print("=" * 70)

    print()
    print("Panels:", len(layout))
    print("Images:", len(image_paths))
    print("PDF:", pdf_path)
    print("PDF URL:", pdf_url)

    print()
    print("=" * 70)

    return {
        "layout": layout,
        "pdf_path": pdf_path,
        "pdf_url": pdf_url,
    }


# ============================================================
# HOME PAGE
# ============================================================

@router.get("/")
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# ============================================================
# GENERATE COMIC
# ============================================================

@router.post("/generate")
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        result = run_generation(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        print()
        print("=" * 70)
        print("SENDING RESULT TO comic_preview.html")
        print("=" * 70)

        print()
        print("Number of panels:")
        print(len(result["layout"]))

        print()
        print("PDF URL:")
        print(result["pdf_url"])

        print()
        print("=" * 70)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "layout": result["layout"],
                "pdf_url": result["pdf_url"],
            },
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("              COMICCRAFT ERROR")
        print("=" * 70)

        print()
        print("ERROR TYPE:")
        print(type(exc).__name__)

        print()
        print("ERROR:")
        print(str(exc))

        print()
        print("=" * 70)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
            },
            status_code=500,
        )


# ============================================================
# JSON API
# ============================================================

@router.post("/generate-comic/json")
async def generate_comic_json(
    payload: PromptRequest,
):

    try:

        result = run_generation(
            story_prompt=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
        )

        return JSONResponse(
            content={
                "success": True,
                "layout": result["layout"],
                "pdf_url": result["pdf_url"],
            }
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("JSON GENERATION ERROR")
        print("=" * 70)

        print()
        print("ERROR TYPE:")
        print(type(exc).__name__)

        print()
        print("ERROR:")
        print(str(exc))

        print()
        print("=" * 70)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
            },
        )


# ============================================================
# EXPORT SUCCESS
# ============================================================

@router.get("/export-success")
async def export_success(
    request: Request,
    pdf_url: str = "",
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "pdf_url": pdf_url,
        },
    )


# ============================================================
# TEST IMAGE
# ============================================================

@router.get("/test-image")
async def test_image():

    try:

        print()
        print("=" * 70)
        print("              TEST IMAGE GENERATION")
        print("=" * 70)

        image_path = generate_image(
            image_prompt=(
                "A young adventurer standing in an enchanted forest, "
                "professional comic book illustration"
            ),
            panel_number=999,
        )

        print()
        print("Generated image path:")
        print(image_path)

        if not image_path:
            raise RuntimeError(
                "generate_image() returned an empty image path."
            )

        settings = get_settings()

        image_url = public_static_url(
            image_path,
            settings.output_dir,
        )

        print()
        print("Image URL:")
        print(image_url)

        print()
        print("=" * 70)

        return {
            "success": True,
            "image_url": image_url,
        }

    except Exception as exc:

        print()
        print("=" * 70)
        print("IMAGE TEST ERROR")
        print("=" * 70)

        print()
        print("ERROR TYPE:")
        print(type(exc).__name__)

        print()
        print("ERROR:")
        print(str(exc))

        print()
        print("=" * 70)

        return {
            "success": False,
            "error": str(exc),
        }
