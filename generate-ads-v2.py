"""
generate-ads-v2.py — Generate 7 research-informed Facebook ad images via Gemini.
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

MODEL = "gemini-3.1-flash-image-preview"

# Research-informed adjustments applied to all prompts:
# - Bold text overlays (most viewers watch without sound, text IS the hook)
# - Specific numbers and data points (credibility driver)
# - High contrast emotional split-screens (3x more clicks)
# - Price shock comparisons (top performing hook)
# - Genuine urgency over manufactured scarcity

ADS = [
    {
        "filename": "creative-1-comparison.jpg",
        "prompt": """Generate a dramatic photorealistic split-screen real estate advertisement.

Left half: A depressing tiny Sydney apartment interior. Dark cramped bedroom, peeling beige walls, single dirty window overlooking a grey concrete carpark, cheap furniture, sad claustrophobic atmosphere, muted grey desaturated tones. Bold white text overlay at bottom: "SYDNEY — AU$175,000" and smaller: "1 bed. No pool. Western Sydney."

Right half: A breathtaking luxury Bali villa at blue hour dusk. Glowing turquoise infinity pool reflecting palm trees in foreground, warm amber golden light pouring from every open window, lush tropical garden, stunning modern tropical architecture with clean lines. Bold white text overlay at bottom: "BALI — US$175,000" and smaller: "3 bed. 3 bath. Private pool. North Canggu."

Thin vertical gold dividing line in centre. Ultra sharp emotional contrast between misery and paradise. The difference should be shocking and immediate.

Luxury real estate advertising photography. Cinematic quality. Facebook ad landscape format 1200x628."""
    },
    {
        "filename": "creative-2-regulation.jpg",
        "prompt": """Generate a dark cinematic luxury warning advertisement image.

Deep navy and charcoal textured background. Subtle blurred silhouette of a luxury Bali villa at dusk in background with warm amber window glow and faint turquoise pool — atmospheric, not competing with text.

Large dramatic gold serif font centred: "MARCH 31, 2026"

Below in clean white sans-serif:
"Indonesia's SBG & SLF regulations take effect."

Below that in light grey elegant text:
"Every short-term rental villa in Bali now legally requires an SBG tourism licence AND an SLF building safety certificate to operate on Airbnb and Booking.com."

Below: "Villas without both face fines, forced closure and permanent delisting."

Bold white: "Only 25% of Bali villas comply."

Gold text: "Our villas are fully licensed. Our investors are fully protected."

Small red-gold stamp in corner: "VERIFIED LICENSED"

Bottom gold: "Don't buy unlicensed. The risk isn't worth it."

Premium serious sophisticated design. Luxury watch advertisement aesthetic. 1080x1080 square."""
    },
    {
        "filename": "creative-3-fifo.jpg",
        "prompt": """Generate a powerful emotional cinematic split-screen portrait photograph.

Left side: Close up of an exhausted rugged Australian male FIFO mining worker, mid 40s. Wearing dusty orange hi-vis safety vest and white hard hat. Dust and sweat on his weathered face, squinting in harsh outback midday sun. Red dirt mine site behind him with heavy yellow mining machinery, haul trucks. He looks drained, worn down, resigned. Hard dramatic shadows. Desaturated muted colour grading.

Right side: The same type of man (similar build, age, rugged face) completely transformed. Relaxed genuine smile, tanned and healthy. Wearing open linen shirt and navy board shorts. Holding a cold Bintang beer. Standing at the edge of a glowing turquoise Bali infinity pool at golden dusk. Palm trees swaying, warm villa lights behind him, sunset reflecting on water. Absolute paradise. Warm saturated tropical colours.

Thin gold vertical dividing line in centre.
Bold white text at bottom centre: "Same budget. Different life."
Smaller: "From US$170,000 — North Canggu, Bali"

Photorealistic, raw, emotionally powerful, cinematic quality. Facebook ad landscape 1200x628."""
    },
    {
        "filename": "creative-4-retirement.jpg",
        "prompt": """Generate beautiful warm emotional lifestyle photography for a luxury real estate ad.

A happy genuine Australian couple in their early 60s. The woman has short silver-blonde hair wearing a flowing cream linen dress. The man has grey hair wearing a casual light blue linen shirt. Both tanned, healthy, relaxed.

They're sitting close together on a luxurious Bali villa terrace at golden sunset. Beautiful infinity pool shimmering behind them catching the last orange and pink light. Tropical flowers in foreground — frangipani, bougainvillea. Cold white wine glasses on the rattan table beside them. They're laughing at something together, completely at peace and genuinely happy.

Lush manicured tropical garden surrounds the villa. Modern Balinese architecture visible. Warm amber and gold tones saturate the entire image. Cinematic shallow depth of field.

Bold text overlay at bottom: "Your super was supposed to be enough. In Bali, it still is."
Smaller: "3 bed villa from US$170,000 — North Canggu"

Aspirational, deeply emotional, luxury travel and retirement lifestyle photography. Facebook ad landscape 1200x628."""
    },
    {
        "filename": "creative-5-scarcity.jpg",
        "prompt": """Generate a perfectly minimal ultra-luxury static advertisement image.

Pure matte black background. Zero photography. Zero people. Only elegant typography and thin gold horizontal rule lines.

Centred layout with generous spacing:

Thin gold horizontal rule at top.

Large elegant gold Didot-style serif font:
"3 VILLAS. NORTH CANGGU."

Thin gold rule divider.

"FROM US$170,000"

Thin gold rule divider.

Smaller refined white text:
"28-Year Lease  ·  Private Pool  ·  3 Bed  ·  3 Bath"

Below that:
"SBG & SLF Licensed  ·  Legal Airbnb & Booking.com"

Thin gold rule divider.

In slightly urgent warm red-gold text:
"2 Already Reserved. 1 Remaining."

Thin gold rule at bottom.

Very small refined gold at bottom edge: "ENQUIRE: arjan@insituasia.com"

Feels exactly like a Cartier or Rolex print advertisement. Absolute premium luxury restraint. Perfect typography. Exquisite minimalism. 1080x1080 square."""
    },
    {
        "filename": "creative-6-digital-nomad.jpg",
        "prompt": """Generate stunning aspirational lifestyle editorial photography.

An attractive creative young woman, late 20s, effortlessly stylish. Wearing linen wide-leg pants, simple white crop top, minimal gold jewellery. Sitting cross-legged on a gorgeous Bali villa daybed beside a glistening infinity pool.

MacBook Pro open in front of her, AirPods in, iced matcha latte on the side table. She's completely absorbed in her work but visibly happy, calm, free. Soft genuine smile.

Morning golden light bathes the scene. Lush tropical garden surrounds the villa — palm trees, tropical plants, frangipani. Pool glistens in the warm light. Through the open-plan villa living area in background you can see hints of the Canggu neighbourhood beyond.

Bold text overlay at bottom: "Your office. Your pool. Your villa."
Smaller: "Own in North Canggu from US$175,000"

Bright warm tones. Editorial Condé Nast Traveller quality. Aspirational millennial remote work lifestyle. Facebook ad landscape 1200x628."""
    },
    {
        "filename": "creative-7-young-family.jpg",
        "prompt": """Generate deeply emotional warm family lifestyle photography.

A beautiful young Australian family — attractive couple mid 30s. Mother in a floral sundress, sun-kissed skin. Father in linen shorts and a casual t-shirt. Two young children aged approximately 3 and 6.

They are all playing joyfully in and around a stunning private Bali villa pool at late afternoon golden hour. The children are laughing and splashing in the shallow end. Parents are in the pool watching them with pure happiness and genuine love. Everyone is glowing with health and joy.

Tropical garden paradise surrounds the private compound — lush greenery, frangipani flowers, palm trees. Beautiful modern Balinese villa architecture with warm amber lights beginning to glow inside. The compound feels completely safe, private, enclosed.

Warm amber golden light bathes the entire scene. Cinematic shallow depth of field.

Bold text overlay at bottom: "The childhood you dreamed of giving them."
Second line: "Still possible. Just not in Australia."
Smaller: "3 bed villa from US$170K — North Canggu, Bali"

Photorealistic. Deep emotional resonance. Cinematic quality. Facebook ad landscape 1200x628."""
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

    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            print(f"  WARNING: Text response: {part.text[:500]}")
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
