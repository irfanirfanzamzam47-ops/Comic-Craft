import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
BASE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE, "static")
os.makedirs(os.path.join(STATIC_DIR, "exports"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Cartoon fox images - you saved these correctly
P1 = "/static/panel1_cartoon.png"
P2 = "/static/panel2_cartoon.png"
P_FINAL = "/static/comic_final.png"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return HTMLResponse("""
<html>
<head>
<style>
body{
 margin:0;
 min-height:100vh;
 background-image: url('https://images.unsplash.com/photo-1448375240586-882707db888b?w=1600&q=80&auto=format&fit=crop');
 background-size: cover;
 background-position: center;
 background-attachment: fixed;
 font-family: Arial, sans-serif;
}
.overlay{
 background: rgba(0,20,0,0.55);
 position: fixed;
 top:0; left:0; right:0; bottom:0;
 z-index:0;
}
.content{
 position: relative;
 z-index:1;
 text-align:center;
 color:white;
 padding:20px;
}
.form-box{
 max-width:600px;
 margin:30px auto;
 background: rgba(255,255,255,0.96);
 padding:28px;
 border-radius:18px;
 text-align:left;
 color:#222;
 box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
input, textarea{
 width:100%;
 padding:12px;
 margin:8px 0;
 border-radius:10px;
 border:1px solid #ccc;
 box-sizing:border-box;
}
button{
 background: linear-gradient(90deg, #ff8c00, #ff5500);
 color:white;
 padding:15px;
 width:100%;
 border:none;
 border-radius:12px;
 font-size:18px;
 cursor:pointer;
 margin-top:10px;
}
</style>
</head>
<body>
<div class="overlay"></div>
<div class="content">
<h1 style="font-size:42px; margin-bottom:5px;">🦊 ComicCraft</h1>
<p style="font-size:18px; opacity:0.9;">Whispering Woods - Foxtale Cartoon Adventure</p>
<div class="form-box">
<h3 style="text-align:center; margin-top:0;">🌲 Create Your Forest Comic</h3>
<form action="/generate" method="post">
<label>Character Name:</label>
<input name="character_name" value="Free the Fox">
<label>Setting:</label>
<input name="setting" value="Whispering Woods">
<label>Your Story:</label>
<textarea name="story_prompt" style="height:90px;">Free is a small red fox who wants to explore the mysterious Whispering Woods and make new friends</textarea>
<input type="hidden" name="tone" value="Adventurous">
<input type="hidden" name="art_style" value="Cartoon">
<button type="submit">🌲 Generate Cartoon Comic</button>
</form>
</div>
<p style="margin-top:20px; font-size:14px; opacity:0.8;">Background: Full Forest Covered | Style: Pixar Cartoon</p>
</div>
</body>
</html>
""")

@app.post("/generate", response_class=HTMLResponse)
def generate_comic(request: Request, story_prompt: str = Form(...), character_name: str = Form("Free the Fox"), setting: str = Form("Whispering Woods"), tone: str = Form(""), art_style: str = Form("")):
    return HTMLResponse(f"""
<html>
<body style="font-family:Arial; padding:25px; text-align:center; background: #e8f5e9;">
<h2 style="color:#2e7d32;">🦊 {character_name} in {setting} - Cartoon Foxtale</h2>
<p style="color:#555;">{story_prompt}</p>

<div style="max-width:680px; margin:20px auto; background:white; padding:22px; border-radius:20px; box-shadow: 0 6px 20px rgba(0,0,0,0.12);">

<div style="margin-bottom:28px; border:3px solid #ff9800; border-radius:18px; padding:14px; background:#fff8e1;">
<img src="{P1}" style="width:100%; border-radius:14px;">
<p style="margin-top:12px;"><b>Panel 1: Meet Pip, the curious little red Fox - Forest Background FULL Covered</b><br><span style="color:#666; font-style:italic;">Once upon a time, there was a curious little red fox named Pip who dreamed of adventure beyond his cozy den.</span></p>
</div>

<div style="margin-bottom:10px; border:3px solid #4caf50; border-radius:18px; padding:14px; background:#e8f5e9;">
<img src="{P2}" style="width:100%; border-radius:14px;">
<p style="margin-top:12px;"><b>Panel 2 DOWN: Pip ventures deeper into the whispering woods</b><br><span style="color:#333;">{story_prompt} - The magical forest was full of whispering trees and hidden paths!</span></p>
</div>

</div>

<div style="margin-top:25px;">
<form action="/download_pdf" method="post" style="display:inline-block; margin:5px;">
<input type="hidden" name="story_prompt" value="{story_prompt}">
<input type="hidden" name="character_name" value="{character_name}">
<input type="hidden" name="setting" value="{setting}">
<button type="submit" style="background: #2e7d32; color:white; padding:14px 32px; border:none; border-radius:12px; font-size:16px; cursor:pointer;">📄 Download PDF for Upload</button>
</form>
<a href="/" style="display:inline-block; margin:5px; background:#ff9800; color:white; padding:14px 32px; border-radius:12px; text-decoration:none;">← Back to Forest Home</a>
</div>

</body>
</html>
""")

@app.post("/download_pdf")
def download_pdf(story_prompt: str = Form(...), character_name: str = Form("Free the Fox"), setting: str = Form("Whispering Woods")):
    from PIL import Image, ImageDraw, ImageFont
    pdf_path = os.path.join(STATIC_DIR, "exports", "ComicCraft_Output.pdf")
    W, H = 1240, 2200
    final_img = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(final_img)
    try:
        title_font = ImageFont.truetype("arial.ttf", 38)
        text_font = ImageFont.truetype("arial.ttf", 22)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    draw.text((50, 30), f"ComicCraft - {character_name} in {setting}", fill="black", font=title_font)
    try:
        img1 = Image.open(os.path.join(STATIC_DIR, "panel1_cartoon.png")).convert("RGB").resize((560, 560))
        img2 = Image.open(os.path.join(STATIC_DIR, "panel2_cartoon.png")).convert("RGB").resize((560, 560))
        final_img.paste(img1, (340, 100))
        draw.text((340, 680), "Panel 1: Meet Pip - Forest FULL Covered - Cartoon", fill="black", font=text_font)
        final_img.paste(img2, (340, 720))
        draw.text((340, 1300), f"Panel 2 DOWN: {story_prompt[:85]}", fill="black", font=text_font)
        draw.text((50, 1400), "Tales of the Whispering Woods - Foxtale Cartoon Style", fill="#2e7d32", font=text_font)
    except Exception as e:
        draw.text((50, 150), f"Image load error: {e} - Make sure panel images are in static folder", fill="red", font=text_font)
    final_img.save(pdf_path, "PDF")
    return FileResponse(pdf_path, filename="ComicCraft_Output.pdf", media_type="application/pdf")