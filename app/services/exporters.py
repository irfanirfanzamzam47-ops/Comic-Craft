from pathlib import Path
from uuid import uuid4

from fpdf import FPDF
from PIL import Image

from app.config import get_settings


def _safe_pdf_text(text: str) -> str:
    """
    Built-in FPDF fonts don't support every Unicode character.

    Convert unsupported characters rather than allowing
    PDF generation to fail.
    """

    if text is None:
        return ""

    return (
        str(text)
        .encode(
            "latin-1",
            errors="replace",
        )
        .decode("latin-1")
    )


def _get_image_path(
    image_url: str,
    output_dir: Path,
) -> Path:
    """
    Convert a browser/static image URL into the
    actual filesystem path.
    """

    if not image_url:
        raise ValueError(
            "Comic panel does not contain an image path."
        )

    # Example:
    # /static/generated/panel-1.png
    #
    # becomes:
    # output_dir / generated / panel-1.png

    relative_path = image_url.removeprefix(
        "/static/"
    )

    image_path = (
        output_dir / relative_path
    )

    return image_path


def save_pdf(
    layout: list[dict],
) -> Path:
    """
    Generate a PDF from the completed comic layout.

    Expected layout item:

    {
        "panel_number": 1,
        "title": "...",
        "scene_description": "...",
        "caption": "...",
        "narration": "...",
        "dialogue": "...",
        "image_path": "/static/..."
    }
    """

    settings = get_settings()

    # ========================================================
    # OUTPUT DIRECTORY
    # ========================================================

    output_dir = (
        settings.output_dir
        / "exports"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # VALIDATE LAYOUT
    # ========================================================

    if not layout:

        raise ValueError(
            "Cannot create PDF because comic layout is empty."
        )

    # ========================================================
    # CREATE PDF PATH
    # ========================================================

    filename = (
        f"comic-{uuid4().hex[:10]}.pdf"
    )

    pdf_path = (
        output_dir / filename
    )

    # ========================================================
    # CREATE PDF
    # ========================================================

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    # ========================================================
    # PROCESS EACH PANEL
    # ========================================================

    for panel in layout:

        pdf.add_page()

        panel_number = panel.get(
            "panel_number",
            "",
        )

        title = panel.get(
            "title",
            "Untitled Panel",
        )

        # ----------------------------------------------------
        # PANEL TITLE
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.multi_cell(
            0,
            10,
            _safe_pdf_text(
                f"Panel {panel_number}: {title}"
            ),
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_url = panel.get(
            "image_path",
            "",
        )

        if image_url:

            image_path = _get_image_path(
                image_url,
                settings.output_dir,
            )

            if not image_path.exists():

                raise FileNotFoundError(
                    "Comic image was not found: "
                    f"{image_path}"
                )

            with Image.open(
                image_path
            ) as image:

                width, height = image.size

            if width <= 0 or height <= 0:

                raise ValueError(
                    f"Invalid image dimensions: "
                    f"{width}x{height}"
                )

            max_width = 180
            max_height = 105

            scale = min(
                max_width / width,
                max_height / height,
            )

            display_width = (
                width * scale
            )

            display_height = (
                height * scale
            )

            x = (
                210 - display_width
            ) / 2

            pdf.image(
                str(image_path),
                x=x,
                y=35,
                w=display_width,
                h=display_height,
            )

            current_y = (
                35 + display_height + 8
            )

            pdf.set_y(
                current_y
            )

        else:

            pdf.set_y(35)

            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                "Image was not generated for this panel.",
            )

        # ----------------------------------------------------
        # SCENE DESCRIPTION
        # ----------------------------------------------------

        scene_description = panel.get(
            "scene_description",
            "",
        )

        if scene_description:

            pdf.ln(3)

            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                _safe_pdf_text(
                    scene_description
                ),
            )

        # ----------------------------------------------------
        # CAPTION
        # ----------------------------------------------------

        caption = panel.get(
            "caption",
            "",
        )

        if caption:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                "Caption",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                _safe_pdf_text(
                    caption
                ),
            )

        # ----------------------------------------------------
        # NARRATION
        # ----------------------------------------------------

        narration = panel.get(
            "narration",
            "",
        )

        if narration:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                "Narration",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                _safe_pdf_text(
                    narration
                ),
            )

        # ----------------------------------------------------
        # DIALOGUE
        # ----------------------------------------------------

        dialogue = panel.get(
            "dialogue",
            "",
        )

        if dialogue:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                "Dialogue",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                _safe_pdf_text(
                    dialogue
                ),
            )

    # ========================================================
    # SAVE PDF
    # ========================================================

    pdf.output(
        str(pdf_path)
    )

    # ========================================================
    # VERIFY PDF
    # ========================================================

    if not pdf_path.exists():

        raise RuntimeError(
            "PDF generation completed but "
            "the PDF file was not created."
        )

    print()
    print("=" * 70)
    print("PDF GENERATED SUCCESSFULLY")
    print(f"PDF PATH: {pdf_path}")
    print("=" * 70)
    print()

    return pdf_path