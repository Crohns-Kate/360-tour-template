"""
generate-video-ad.py — Generate a short-form video ad using Google Veo 3.1
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

client = genai.Client(api_key=API_KEY)
OUT_DIR = Path(__file__).parent / "ad-creatives"

# Research-informed: 14-15 sec sweet spot, hook in first 3 sec,
# bold visual contrast, movement/disruption, specific numbers

VIDEO_PROMPT = """Generate a cinematic 8-second real estate advertisement video.

The video opens with a slow tracking shot through a tiny, dark, cramped Sydney apartment — grey walls, small dirty window, depressing fluorescent lighting, cheap furniture. The mood is suffocating and grim. Bold white text appears on screen: "AU$175,000 — Sydney"

Then a dramatic hard cut — sudden transition to a breathtaking luxury Bali villa at blue-hour dusk. The camera glides smoothly through an open-plan living area out toward a glowing turquoise infinity pool surrounded by palm trees and tropical gardens. Warm amber lights glow from the villa. The mood completely transforms to paradise. Bold white text: "US$175,000 — Bali"

Final frame: elegant gold text on dark background: "Same price. Different life. North Canggu, Bali."

Style: Cinematic real estate videography. Smooth camera movement. High contrast between the two locations. Dramatic lighting. Professional colour grading. Luxury advertising quality. The emotional contrast should be shocking and immediate."""

print("Generating video with Veo 3.1...")
print("This may take 1-3 minutes...\n")

try:
    # Try Veo 3.1 first, fall back to Veo 3.0, then Veo 2.0
    models_to_try = [
        "veo-3.1-fast-generate-preview",
        "veo-3.0-fast-generate-001",
        "veo-2.0-generate-001",
    ]

    operation = None
    model_used = None

    for model in models_to_try:
        try:
            print(f"Trying model: {model}")
            operation = client.models.generate_videos(
                model=model,
                prompt=VIDEO_PROMPT,
                config=types.GenerateVideosConfig(
                    person_generation="allow_all",
                    number_of_videos=1,
                    duration_seconds=8,
                    aspect_ratio="16:9",
                ),
            )
            model_used = model
            print(f"  Request accepted by {model}!")
            break
        except Exception as e:
            print(f"  {model} failed: {e}")
            continue

    if not operation:
        print("ERROR: All video models failed.")
        exit(1)

    # Poll for completion
    print(f"\nUsing model: {model_used}")
    print("Waiting for video generation...")

    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        print("  Still generating...")

    print("\nGeneration complete!")

    # Save the video
    for i, video in enumerate(operation.result.generated_videos):
        fname = f"video-ad-comparison.mp4"
        out_path = OUT_DIR / fname
        video_data = client.files.download(file=video.video)

        # video_data is a file-like object, write it
        with open(str(out_path), "wb") as f:
            f.write(video_data)

        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"\nSaved: {fname} ({size_mb:.1f}MB)")
        print(f"Path: {out_path}")

    print("\nDone!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
