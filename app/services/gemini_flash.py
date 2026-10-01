# OFFLINE FALLBACK - Works even when Gemini 503 error
def generate_comic_panels(story_prompt, character_name="Fox", setting="Forest", tone="Adventurous", art_style="Comic"):
    print("⚠️ Gemini 503 - Using OFFLINE fallback images")
    # NO API CALL - Direct images, no 503!
    panels = [
        {
            "image_url": "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=800",
            "caption": f"{character_name}, a red fox with intelligent eyes, stands at the edge of a dark, imposing forest in {setting}.",
            "narration": f"{character_name}, the bravest fox, stood at the threshold."
        },
        {
            "image_url": "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800",
            "caption": f"{character_name} cautiously enters the forest, the path barely visible. {story_prompt}",
            "narration": "An unnatural silence hangs in the air."
        }
    ]
    return panels

def generate_story(*args, **kwargs):
    return generate_comic_panels(*args, **kwargs)