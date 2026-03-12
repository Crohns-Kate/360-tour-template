"""
generate-video-ads-batch.py — Generate additional video ads using Veo 3.1
"""

import os
import time
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
        "filename": "video-ad-fifo.mp4",
        "prompt": """Generate a cinematic 8-second real estate advertisement video.

Opens on a close-up of an exhausted FIFO mining worker in orange hi-vis and hard hat, wiping sweat from his dusty face at a remote Australian mine site. Red dirt, harsh sun, heavy machinery rumbling. He looks drained. Bold text appears: "2 weeks on."

Hard dramatic cut to: the same style of man, now completely relaxed, walking barefoot along the edge of a stunning turquoise infinity pool at a luxury Bali villa at golden sunset. He's smiling, holding a cold beer, wearing board shorts and an open linen shirt. Palm trees sway, warm villa lights glow behind him. Paradise. Bold text: "2 weeks off."

Final frame fades in: "Same budget. Different life. From US$170K — North Canggu, Bali"

Cinematic quality. Dramatic emotional contrast. Smooth camera movement. Professional colour grading. The transformation should feel visceral and immediate."""
    },
    {
        "filename": "video-ad-walkthrough.mp4",
        "prompt": """Generate a cinematic 8-second luxury villa walkthrough video at blue-hour dusk.

The camera glides smoothly through a stunning modern Bali villa. Starting from the entrance, moving through an open-plan living area with warm amber interior lights, past a modern kitchen, then out through large glass doors to reveal a breathtaking private infinity pool glowing turquoise in the twilight. Lush tropical garden with palm trees and frangipani surrounds the pool. Deep blue dusk sky above.

The camera movement is smooth, cinematic, and continuous — like a single take from a gimbal. Warm amber light pours from recessed ceiling fixtures and wall sconces. The mood is luxury, serenity, tropical paradise.

Small elegant text appears at the end: "3 bed · 3 bath · Private pool · From US$170,000"

Professional real estate videography quality. Warm colour grading. Luxury advertising aesthetic. Smooth gliding camera movement throughout."""
    },
]

for i, vid in enumerate(VIDEOS):
    print(f"\n{'='*60}")
    print(f"  Generating: {vid['filename']}")
    print(f"{'='*60}")

    try:
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

        print("  Waiting for generation...")
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("  Still generating...")

        for video in operation.result.generated_videos:
            out_path = OUT_DIR / vid["filename"]
            video_data = client.files.download(file=video.video)
            with open(str(out_path), "wb") as f:
                f.write(video_data)
            size_mb = out_path.stat().st_size / (1024 * 1024)
            print(f"  Saved: {vid['filename']} ({size_mb:.1f}MB)")

    except Exception as e:
        print(f"  ERROR: {e}")

    if i < len(VIDEOS) - 1:
        print("  Waiting 15s before next...")
        time.sleep(15)

print("\nAll done!")
