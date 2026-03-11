"""
generate-ads.py — Generate 5 Facebook ad images using Gemini image generation.
"""

import os
import io
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

client = genai.Client(api_key=API_KEY)
OUT_DIR = Path(__file__).parent / "ad-creatives"
OUT_DIR.mkdir(exist_ok=True)

# Facebook ad recommended size: 1200x628 for feed, 1080x1080 for square
# We'll request landscape for split-screens and square for text-based

MODEL = "gemini-3.1-flash-image-preview"

ADS = [
    {
        "filename": "ad-1-sydney-vs-bali.jpg",
        "prompt": """Generate a dramatic split-screen real estate advertisement image for Facebook.

Left half: A tiny, cramped, dark Sydney apartment interior — grey walls, one small window with grey light, a microscopic galley kitchen, worn carpet, depressing and claustrophobic interior. Label at bottom of left side in clean white text: "Sydney Apartment"

Right half: A stunning luxury Bali villa at blue-hour dusk — glowing turquoise infinity pool in foreground, lush tropical palm gardens, warm amber/golden lights glowing from inside the open-plan villa, beautiful modern tropical architecture with clean lines. Label at bottom of right side in clean white text: "Bali Villa"

Center dividing line: thin gold vertical line.
Bottom center: large clean text "BOTH US$175,000"

Ultra high quality photography, luxury real estate advertising style, 1200x628 landscape format, cinematic lighting."""
    },
    {
        "filename": "ad-2-march-31-urgency.jpg",
        "prompt": """Generate a dark cinematic luxury real estate advertisement image.

Deep navy-to-black gradient background. In the center, large dramatic gold serif typography reading "MARCH 31" — this text should be very prominent and dominate the composition.

Behind the text, barely visible, a moody silhouette of a luxury Bali villa glowing at dusk with warm amber window lights and a faint turquoise pool glow — atmospheric and subtle, not competing with the text.

Below the date in smaller elegant gold text: "3 villas. From US$170K. North Canggu, Bali."

At the very bottom in small refined text: "ENQUIRE NOW"

Minimalist premium design, luxury watch/jewellery advertisement aesthetic, sophisticated urgency, moody atmospheric lighting. 1080x1080 square format."""
    },
    {
        "filename": "ad-3-fifo-escape.jpg",
        "prompt": """Generate a cinematic split-screen lifestyle advertisement.

Left half: An exhausted Australian FIFO mining worker — wearing dusty orange hi-vis vest and white hard hat, standing at a remote outback mine site. Red dusty earth, harsh midday sun casting hard shadows, industrial mining equipment in background. His face shows fatigue, sweat, strain. Muted desaturated color grading.

Right half: The same style of man (similar build, similar age, early 40s) completely relaxed and transformed — wearing casual board shorts and a linen shirt, holding a cocktail, genuinely laughing while standing at a stunning Bali infinity pool at golden dusk. Palm trees, warm glowing villa lights behind him, turquoise pool water reflecting sunset. Warm saturated tropical colors.

Thin gold vertical divider line in center.
Small text at bottom center: "Same budget. Different life. From US$170K"

Photorealistic, emotional, cinematic quality, Facebook ad landscape format 1200x628."""
    },
    {
        "filename": "ad-4-couple-retirement.jpg",
        "prompt": """Generate warm golden hour lifestyle photography for a luxury real estate advertisement.

A happy, relaxed Australian couple in their early 60s sitting together on a stunning Bali villa terrace at sunset. They look healthy, tanned, genuinely content. The woman has short silver-blonde hair, wearing a flowing linen dress. The man has grey hair, wearing a casual linen shirt.

Behind them: a beautiful infinity pool reflecting golden sunset light, lush tropical gardens with frangipani and palm trees, modern villa architecture with warm amber lights glowing from inside.

They're holding cold drinks (wine glasses), soft genuine smiles, completely at ease. Tropical flowers (bougainvillea, frangipani) frame the shot.

Color palette: warm amber, gold, soft coral sunset tones, deep tropical greens.
Mood: aspirational, peaceful, "this could be your life"

Small elegant text at bottom: "Your next chapter starts here. North Canggu, Bali."

Photorealistic, emotional, luxury travel photography style, Facebook ad landscape format 1200x628."""
    },
    {
        "filename": "ad-5-minimal-text.jpg",
        "prompt": """Generate an ultra-minimal luxury print advertisement image.

Pure deep black background. No people. No photography. Just elegant typography and thin gold horizontal divider lines.

Centered gold serif text layout (each line separated by thin gold horizontal lines):

"NORTH CANGGU"
—
"3 BEDROOMS · 3 BATHROOMS · PRIVATE POOL"
—
"28 YEAR LEASE"
—
"FROM US$170,000"
—
"SLF/PBG COMPLETE"

At the bottom in very small refined gold text: "ENQUIRE: arjan@insituasia.com"

Premium jewellery or luxury watch advertisement aesthetic. Sophisticated, exclusive, understated wealth. Perfect typography, generous spacing, exquisite minimalism. 1080x1080 square format."""
    },
]


def generate_ad(ad):
    filename = ad["filename"]
    prompt = ad["prompt"]
    out_path = OUT_DIR / filename

    print(f"\n{'='*60}")
    print(f"  Generating: {filename}")
    print(f"{'='*60}")

    print("  Sending to Gemini...")
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[types.Part.from_text(text=prompt)],
            ),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            img = Image.open(io.BytesIO(part.inline_data.data))
            img.save(str(out_path), "JPEG", quality=95)
            size_kb = out_path.stat().st_size // 1024
            print(f"  Saved: {filename} ({img.size[0]}x{img.size[1]}, {size_kb}KB)")
            return True

    # Check for text response
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            print(f"  WARNING: Text response: {part.text[:300]}")
            break
    return False


success = 0
failed = 0

for i, ad in enumerate(ADS):
    try:
        if generate_ad(ad):
            success += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        failed += 1

    if i < len(ADS) - 1:
        print("\n  Waiting 12s (rate limit)...")
        time.sleep(12)

print(f"\n{'='*60}")
print(f"  DONE: {success} generated, {failed} failed")
print(f"{'='*60}")
