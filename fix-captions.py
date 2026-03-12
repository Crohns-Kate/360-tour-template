"""
fix-captions.py — Re-generate the 3 videos without text via Veo, then overlay
larger, better-positioned captions via ffmpeg.
"""

import os
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
OUT_DIR = Path(__file__).parent / "ad-creatives"
MODEL = "veo-3.1-fast-generate-preview"

# Video resolution is 1280x720
# Font sizes scaled for 720p: headlines ~56-64px, subtext ~32-36px
# Position from bottom: main text ~100px up, subtext ~55px up

VIDEOS = [
    {
        "raw": "video-raw-comparison.mp4",
        "final": "video-ad-comparison.mp4",
        "prompt": """Generate a cinematic 8-second real estate advertisement video. NO TEXT OR CAPTIONS IN THE VIDEO.

First 4 seconds: Slow tracking shot through a tiny, dark, cramped apartment interior. Grey walls, small dirty window looking out at a grey concrete carpark, cheap old furniture, depressing fluorescent lighting. Claustrophobic, suffocating atmosphere. Muted desaturated colours.

Then a dramatic hard cut at the 4-second mark to:

Last 4 seconds: A breathtaking luxury tropical villa at blue-hour dusk. The camera glides smoothly through an open-plan living area with warm amber lights out toward a stunning glowing turquoise infinity pool surrounded by palm trees and lush tropical gardens. Deep blue twilight sky. Warm golden light from the villa. Complete paradise. Rich saturated warm colours.

The contrast between the two halves should be shocking. Cinematic quality. NO TEXT anywhere.""",
        "captions": [
            # Sydney section (first 4 sec)
            {"text": "AU$175,000", "start": 0.3, "end": 3.8, "y": "h-120", "size": 64, "color": "white"},
            {"text": "1 bed. No pool. Western Sydney.", "start": 0.3, "end": 3.8, "y": "h-60", "size": 32, "color": "white@0.9"},
            # Bali section (last 4 sec)
            {"text": "US$175,000", "start": 4.2, "end": 7, "y": "h-120", "size": 64, "color": "white"},
            {"text": "3 bed. 3 bath. Private pool. North Canggu.", "start": 4.2, "end": 7, "y": "h-60", "size": 32, "color": "white@0.9"},
            # End card
            {"text": "Same price. Different life.", "start": 7, "end": 8, "y": "h/2-30", "size": 64, "color": "white"},
            {"text": "North Canggu, Bali", "start": 7, "end": 8, "y": "h/2+30", "size": 36, "color": "#b08d57"},
        ]
    },
    {
        "raw": "video-raw-fifo.mp4",
        "final": "video-ad-fifo.mp4",
        "prompt": """Generate a cinematic 8-second advertisement video. NO TEXT OR CAPTIONS IN THE VIDEO.

First 4 seconds: Close-up portrait of an exhausted rugged male worker in dusty orange hi-vis safety vest and white hard hat at a remote red-dirt mine site. Harsh midday Australian outback sun. He wipes sweat from his face. Heavy mining machinery in the background. Desaturated muted colours.

Dramatic hard cut at 4 seconds to:

Last 4 seconds: A man of similar build, completely relaxed, walking barefoot along the edge of a glowing turquoise infinity pool at a luxury tropical villa during golden sunset. Smiling, wearing linen shirt and board shorts, holding a cold beer. Palm trees, warm villa lights. Rich warm colours.

Cinematic quality. NO TEXT anywhere.""",
        "captions": [
            {"text": "2 weeks on.", "start": 0.5, "end": 3.8, "y": "h-100", "size": 64, "color": "white"},
            {"text": "2 weeks off.", "start": 4.2, "end": 7, "y": "h-100", "size": 64, "color": "white"},
            {"text": "Same budget. Different life.", "start": 7, "end": 8, "y": "h/2-30", "size": 60, "color": "white"},
            {"text": "From US$170K — North Canggu", "start": 7, "end": 8, "y": "h/2+30", "size": 34, "color": "#b08d57"},
        ]
    },
    {
        "raw": "video-raw-walkthrough.mp4",
        "final": "video-ad-walkthrough.mp4",
        "prompt": """Generate a cinematic 8-second luxury villa walkthrough video at blue-hour dusk. NO TEXT OR CAPTIONS.

A single continuous smooth gimbal shot gliding through a stunning modern tropical villa. The camera enters through the front door, moves through an elegant open-plan living area with warm amber recessed lights, past a modern kitchen, then out through large glass doors revealing a breathtaking private infinity pool glowing turquoise in the twilight. Lush tropical garden with palm trees. Deep navy blue sky. Warm golden light from the villa.

Smooth continuous camera movement. Luxury real estate videography. NO TEXT anywhere.""",
        "captions": [
            {"text": "3 bed  ·  3 bath  ·  Private pool", "start": 5, "end": 7.5, "y": "h-110", "size": 52, "color": "white"},
            {"text": "From US$170,000 — North Canggu, Bali", "start": 5, "end": 7.5, "y": "h-55", "size": 32, "color": "#b08d57"},
        ]
    },
]


def generate_and_caption(vid):
    raw_path = OUT_DIR / vid["raw"]
    final_path = OUT_DIR / vid["final"]

    print(f"\n{'='*60}")
    print(f"  Generating: {vid['raw']}")
    print(f"{'='*60}")

    # Generate with Veo
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=vid["prompt"],
        config=types.GenerateVideosConfig(
            person_generation="allow_all",
            number_of_videos=1,
            duration_seconds=8,
            aspect_ratio="16:9",
        ),
    )

    print("  Waiting for Veo 3.1...")
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        print("  Still generating...")

    for video in operation.result.generated_videos:
        video_data = client.files.download(file=video.video)
        with open(str(raw_path), "wb") as f:
            f.write(video_data)
        print(f"  Raw saved: {raw_path.stat().st_size // 1024}KB")

    # Overlay captions
    print("  Adding captions...")
    filters = []
    for cap in vid["captions"]:
        text = cap["text"].replace("'", "'\\''").replace(":", "\\:")
        color = cap.get("color", "white")

        f = (
            f"drawtext=text='{text}'"
            f":fontsize={cap['size']}"
            f":fontcolor={color}"
            f":borderw=4"
            f":bordercolor=black@0.6"
            f":fontfile='C\\:/Windows/Fonts/segoeuib.ttf'"
            f":x=(w-text_w)/2"
            f":y={cap['y']}"
            f":enable='between(t,{cap['start']},{cap['end']})'"
        )
        filters.append(f)

    cmd = [
        "ffmpeg", "-y", "-i", str(raw_path),
        "-vf", ",".join(filters),
        "-codec:a", "copy", "-c:v", "libx264",
        "-preset", "fast", "-crf", "18",
        str(final_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr[-300:]}")
    else:
        size_mb = final_path.stat().st_size / (1024 * 1024)
        print(f"  Final: {vid['final']} ({size_mb:.1f}MB)")

    # Cleanup raw
    if raw_path.exists():
        raw_path.unlink()


for i, vid in enumerate(VIDEOS):
    try:
        generate_and_caption(vid)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

    if i < len(VIDEOS) - 1:
        print("\n  Waiting 15s...")
        time.sleep(15)

print(f"\n{'='*60}")
print("  ALL DONE!")
print(f"{'='*60}")
