"""
generate-videos-clean.py — Generate video ads WITHOUT text, then overlay captions with ffmpeg.
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

VIDEOS = [
    {
        "filename": "video-raw-comparison.mp4",
        "final": "video-ad-comparison.mp4",
        "prompt": """Generate a cinematic 8-second real estate advertisement video. NO TEXT OR CAPTIONS IN THE VIDEO.

First 4 seconds: Slow tracking shot through a tiny, dark, cramped apartment interior. Grey walls, small dirty window looking out at a grey concrete carpark, cheap old furniture, depressing fluorescent lighting. Claustrophobic, suffocating atmosphere. Muted desaturated colours.

Then a dramatic hard cut at the 4-second mark to:

Last 4 seconds: A breathtaking luxury tropical villa at blue-hour dusk. The camera glides smoothly through an open-plan living area with warm amber lights out toward a stunning glowing turquoise infinity pool surrounded by palm trees and lush tropical gardens. Deep blue twilight sky. Warm golden light from the villa. Complete paradise. Rich saturated warm colours.

The contrast between the two halves should be shocking and visceral. Cinematic camera movement throughout. Professional real estate videography quality. Dramatic lighting. NO TEXT, NO WORDS, NO CAPTIONS anywhere in the video.""",
        "captions": [
            {"text": "AU$175,000 — Sydney", "start": 0, "end": 3.8, "y": "h-80", "size": 42},
            {"text": "1 bed. No pool.", "start": 0.5, "end": 3.8, "y": "h-45", "size": 24},
            {"text": "US$175,000 — Bali", "start": 4.2, "end": 7, "y": "h-80", "size": 42},
            {"text": "3 bed. 3 bath. Private pool.", "start": 4.7, "end": 7, "y": "h-45", "size": 24},
            {"text": "Same price. Different life.", "start": 7, "end": 8, "y": "h/2-20", "size": 48},
            {"text": "North Canggu, Bali", "start": 7, "end": 8, "y": "h/2+25", "size": 28},
        ]
    },
    {
        "filename": "video-raw-fifo.mp4",
        "final": "video-ad-fifo.mp4",
        "prompt": """Generate a cinematic 8-second advertisement video. NO TEXT OR CAPTIONS IN THE VIDEO.

First 4 seconds: Close-up portrait of an exhausted rugged male worker in dusty orange hi-vis safety vest and white hard hat at a remote red-dirt mine site. Harsh midday Australian outback sun. He wipes sweat from his face. Heavy mining machinery in the background. He looks tired, worn down. Desaturated muted colour grading. Hard shadows.

Dramatic hard cut at 4 seconds to:

Last 4 seconds: A man of similar build, completely relaxed and transformed, walking barefoot along the edge of a glowing turquoise infinity pool at a luxury tropical villa during golden sunset. He is smiling genuinely, wearing an open linen shirt and board shorts, holding a cold beer. Palm trees sway gently. Warm villa lights glow in the background. Absolute paradise. Rich warm saturated colours.

The emotional transformation should be immediate and powerful. Cinematic quality. Smooth camera movement. Professional colour grading. NO TEXT, NO WORDS, NO CAPTIONS anywhere in the video.""",
        "captions": [
            {"text": "2 weeks on.", "start": 0.3, "end": 3.8, "y": "h-70", "size": 42},
            {"text": "2 weeks off.", "start": 4.2, "end": 7, "y": "h-70", "size": 42},
            {"text": "Same budget. Different life.", "start": 7, "end": 8, "y": "h/2-20", "size": 44},
            {"text": "From US$170K — North Canggu", "start": 7, "end": 8, "y": "h/2+25", "size": 26},
        ]
    },
    {
        "filename": "video-raw-walkthrough.mp4",
        "final": "video-ad-walkthrough.mp4",
        "prompt": """Generate a cinematic 8-second luxury villa walkthrough video at blue-hour dusk. NO TEXT OR CAPTIONS IN THE VIDEO.

A single continuous smooth gimbal shot gliding through a stunning modern tropical villa. The camera enters through the front door, moves through an elegant open-plan living area with warm amber recessed ceiling lights and designer furniture, past a sleek modern kitchen with under-cabinet lighting, then out through large floor-to-ceiling glass doors that open onto a breathtaking private infinity pool glowing turquoise in the deep blue twilight.

Lush tropical garden with palm trees and frangipani flowers surrounds the pool. Deep navy blue dusk sky above. Warm amber and golden light pours from every fixture inside the villa. The pool water reflects the twilight and villa lights.

Smooth continuous camera movement throughout like a professional Steadicam shot. Luxury real estate videography quality. Warm cinematic colour grading. The reveal of the pool at the end should feel magical. NO TEXT, NO WORDS, NO CAPTIONS anywhere in the video.""",
        "captions": [
            {"text": "3 bed · 3 bath · Private pool", "start": 5, "end": 7.5, "y": "h-70", "size": 36},
            {"text": "From US$170,000 — North Canggu, Bali", "start": 5, "end": 7.5, "y": "h-35", "size": 24},
        ]
    },
]


def generate_video(vid):
    raw_path = OUT_DIR / vid["filename"]
    final_path = OUT_DIR / vid["final"]

    print(f"\n{'='*60}")
    print(f"  Generating: {vid['filename']}")
    print(f"{'='*60}")

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
        size_mb = raw_path.stat().st_size / (1024 * 1024)
        print(f"  Raw video saved: {vid['filename']} ({size_mb:.1f}MB)")

    # Now overlay captions with ffmpeg
    print(f"  Adding captions with ffmpeg...")
    add_captions(raw_path, final_path, vid["captions"])

    # Clean up raw
    raw_path.unlink()
    print(f"  Final: {vid['final']}")


def add_captions(input_path, output_path, captions):
    """Overlay text captions using ffmpeg drawtext filter."""
    # Build drawtext filter chain
    filters = []
    for cap in captions:
        text = cap["text"].replace("'", "'\\''").replace(":", "\\:")
        y_expr = cap["y"]
        size = cap["size"]
        start = cap["start"]
        end = cap["end"]

        f = (
            f"drawtext=text='{text}'"
            f":fontsize={size}"
            f":fontcolor=white"
            f":borderw=3"
            f":bordercolor=black@0.7"
            f":fontfile='C\\:/Windows/Fonts/segoeui.ttf'"
            f":x=(w-text_w)/2"
            f":y={y_expr}"
            f":enable='between(t,{start},{end})'"
        )
        filters.append(f)

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", filter_str,
        "-codec:a", "copy",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr[-500:]}")
    else:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Captioned video: {output_path.name} ({size_mb:.1f}MB)")


# Run all
for i, vid in enumerate(VIDEOS):
    try:
        generate_video(vid)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

    if i < len(VIDEOS) - 1:
        print("\n  Waiting 15s before next...")
        time.sleep(15)

print(f"\n{'='*60}")
print("  ALL DONE!")
print(f"{'='*60}")
