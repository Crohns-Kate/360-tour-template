"""
render-dusk.py — Send daytime panoramas to Gemini for BoxBrownie-style dusk rendering.

Usage:
    python render-dusk.py                  # Render all scenes missing a dusk version
    python render-dusk.py scene-2-day.jpg  # Render a specific scene
"""

import os
import sys
import io
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

# ── Config ────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

IMAGES_DIR = Path(__file__).parent / "images"

DUSK_PROMPT = """Transform this daytime property photo into a photorealistic BoxBrownie-style day-to-dusk rendering.

Requirements:
- Replace the sky with a deep blue-hour twilight sky (dark navy blue, not black)
- Make all windows glow with warm amber/golden interior light
- Add warm landscape uplighting on walls with visible light cones
- If there is a pool, make it glow turquoise/aqua with underwater lights visible
- Add subtle warm downlights under eaves and overhangs
- Increase contrast between warm interior tones and cool blue exterior
- The deck/ground should have warm bounce light from interior
- Keep the EXACT same composition, architecture, and perspective — only change lighting and sky
- Make it look like a professional real estate twilight photo, not a filter
- Maintain photorealistic quality throughout
- Output the full transformed image"""

MODEL = "gemini-3.1-flash-image-preview"


def get_scenes_to_render(specific_file=None):
    """Find day images that don't have a matching dusk version yet."""
    scenes = []
    if specific_file:
        day_path = IMAGES_DIR / specific_file
        if day_path.exists():
            dusk_name = specific_file.replace("-day.", "-dusk.")
            scenes.append((day_path, IMAGES_DIR / dusk_name))
        else:
            print(f"ERROR: {specific_file} not found in {IMAGES_DIR}")
        return scenes

    for f in sorted(IMAGES_DIR.glob("scene-*-day.jpg")):
        dusk_path = IMAGES_DIR / f.name.replace("-day.", "-dusk.")
        if not dusk_path.exists():
            scenes.append((f, dusk_path))

    return scenes


def render_dusk(day_path, dusk_path):
    """Send a daytime panorama to Gemini and save the dusk version."""
    print(f"\n{'='*60}")
    print(f"  Rendering: {day_path.name} -> {dusk_path.name}")
    print(f"{'='*60}")

    # Load image
    print("  Loading image...")
    img = Image.open(day_path)
    original_size = img.size

    # Resize for API if too large (Gemini has limits)
    max_dim = 4096
    if img.width > max_dim or img.height > max_dim:
        ratio = min(max_dim / img.width, max_dim / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        print(f"  Resizing {img.size} -> {new_size} for API...")
        img = img.resize(new_size, Image.LANCZOS)

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG", quality=95)
    img_bytes = img_bytes.getvalue()

    print("  Sending to Gemini (this may take a minute)...")

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    types.Part.from_text(text=DUSK_PROMPT),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    # Extract the generated image
    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            rendered = Image.open(io.BytesIO(part.inline_data.data))

            # Resize back to original dimensions
            if rendered.size != original_size:
                print(f"  Upscaling from {rendered.size} to {original_size}...")
                rendered = rendered.resize(original_size, Image.LANCZOS)

            rendered.save(str(dusk_path), "JPEG", quality=95)
            size_kb = dusk_path.stat().st_size // 1024
            print(f"  Saved: {dusk_path.name} ({size_kb}KB, {rendered.size[0]}x{rendered.size[1]})")
            image_saved = True
            break

    if not image_saved:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                print(f"  WARNING: Gemini returned text instead of image:")
                print(f"  {part.text[:300]}")
                break
        else:
            print(f"  ERROR: No image in response")

    return image_saved


def main():
    specific = sys.argv[1] if len(sys.argv) > 1 else None
    scenes = get_scenes_to_render(specific)

    if not scenes:
        print("All scenes already have dusk versions. Nothing to render.")
        print("To re-render, delete the scene-N-dusk.jpg file and run again.")
        return

    print(f"Found {len(scenes)} scene(s) to render:\n")
    for day, dusk in scenes:
        print(f"  {day.name}  ->  {dusk.name}")

    print(f"\nUsing model: {MODEL}")
    print(f"Starting renders...\n")

    success = 0
    failed = 0

    for i, (day_path, dusk_path) in enumerate(scenes):
        try:
            if render_dusk(day_path, dusk_path):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR rendering {day_path.name}: {e}")
            failed += 1

        # Rate limit
        if i < len(scenes) - 1:
            print("\n  Waiting 10s before next render (rate limit)...")
            time.sleep(10)

    print(f"\n{'='*60}")
    print(f"  DONE: {success} rendered, {failed} failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
