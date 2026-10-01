# ComicCraft — AI Comic Story Creator

ComicCraft is an AI-powered web application that converts a
user's story idea into a five-panel illustrated comic.

The application uses:

- FastAPI
- Jinja2
- Google Gemini
- Hugging Face image generation
- Pillow
- FPDF2
- Pydantic

---

# Features

ComicCraft allows users to enter:

- Story prompt
- Character name
- Setting
- Story tone
- Art style

The application then:

1. Generates a five-panel comic outline.
2. Expands the outline into narration and dialogue.
3. Generates an illustration for each panel.
4. Displays the comic in the browser.
5. Exports the comic as a PDF.

---

# Project Structure

```text
ComicCraft/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── files.py
│
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
│
├── static/
│   ├── style.css
│   ├── panels/
│   └── exports/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
