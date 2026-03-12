"""
generate-final-videos.py — Generate 3 x ~16-sec video ads in multiple formats.
- 2x 8-sec clips per video via Veo 3.1, stitched to ~16s
- Clean captions via ffmpeg (no burned-in text from AI)
- Outputs: 16:9 (landscape), 9:16 (Reels/Stories), 1:1 (Feed)

Facebook/Instagram ad specs:
  Feed: 1:1 (1080x1080) or 4:5 — max screen real estate
  Reels/Stories: 9:16 (1080x1920) — highest engagement
  In-stream: 16:9 (1920x1080)
  Duration: 15-60s feed, 15-90s Reels — our 16s is ideal
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


def gen_clip(prompt, out_path):
    """Generate a single 8-sec clip via Veo 3.1."""
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            person_generation="allow_all",
            number_of_videos=1,
            duration_seconds=8,
            aspect_ratio="16:9",
        ),
    )
    print("    Waiting for Veo 3.1...")
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        print("    Still generating...")

    for video in operation.result.generated_videos:
        video_data = client.files.download(file=video.video)
        with open(str(out_path), "wb") as f:
            f.write(video_data)
        print(f"    Saved: {out_path.name} ({out_path.stat().st_size // 1024}KB)")
        return True
    return False


def build_caption_filters(captions, canvas_w, canvas_h, x_offset=0, y_offset=0):
    """Build ffmpeg drawtext filters. Offsets allow adjusting for cropped canvases."""
    filters = []
    for cap in captions:
        text = cap["text"].replace("'", "'\\''").replace(":", "\\:")
        color = cap.get("color", "white")
        font = cap.get("font", "segoeuib.ttf")
        size = cap["size"]

        f = (
            f"drawtext=text='{text}'"
            f":fontsize={size}"
            f":fontcolor={color}"
            f":borderw=5"
            f":bordercolor=black@0.6"
            f":shadowcolor=black@0.4:shadowx=2:shadowy=2"
            f":fontfile='C\\:/Windows/Fonts/{font}'"
            f":x=(w-text_w)/2"
            f":y={cap['y']}"
            f":enable='between(t,{cap['start']},{cap['end']})'"
        )
        filters.append(f)
    return filters


def process_video(name, vid, index):
    """Generate clips, stitch, caption, and export in 3 formats."""
    clip_a = OUT_DIR / f"temp_clip_a_{index}.mp4"
    clip_b = OUT_DIR / f"temp_clip_b_{index}.mp4"
    concat_path = OUT_DIR / f"temp_concat_{index}.mp4"
    list_path = OUT_DIR / f"concat_list_{index}.txt"

    # Base filename without extension
    base = vid["final"].replace(".mp4", "")

    # Output paths for 3 formats
    out_landscape = OUT_DIR / f"{base}.mp4"           # 16:9
    out_vertical = OUT_DIR / f"{base}-vertical.mp4"   # 9:16
    out_square = OUT_DIR / f"{base}-square.mp4"       # 1:1

    print(f"\n{'='*60}")
    print(f"  VIDEO {index+1}: {name}")
    print(f"{'='*60}")

    # ── Generate clips ──
    print(f"\n  Clip A (first 8 sec):")
    gen_clip(vid["clip_a_prompt"], clip_a)

    print(f"\n  Waiting 15s (rate limit)...")
    time.sleep(15)

    print(f"\n  Clip B (last 8 sec):")
    gen_clip(vid["clip_b_prompt"], clip_b)

    # ── Stitch clips ──
    print(f"\n  Stitching clips...")
    with open(str(list_path), "w") as f:
        f.write(f"file '{clip_a.name}'\n")
        f.write(f"file '{clip_b.name}'\n")

    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_path), "-c", "copy",
        str(concat_path)
    ]
    result = subprocess.run(cmd_concat, capture_output=True, text=True, cwd=str(OUT_DIR))
    if result.returncode != 0:
        print(f"    Concat error: {result.stderr[-300:]}")
        return

    # ── 16:9 LANDSCAPE (1920x1080 or native) with captions ──
    print(f"\n  Creating 16:9 landscape version...")
    landscape_filters = build_caption_filters(vid["captions_landscape"], 1920, 1080)
    cmd = [
        "ffmpeg", "-y", "-i", str(concat_path),
        "-vf", ",".join(landscape_filters),
        "-codec:a", "copy", "-c:v", "libx264",
        "-preset", "fast", "-crf", "18",
        str(out_landscape)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr[-300:]}")
    else:
        size_mb = out_landscape.stat().st_size / (1024 * 1024)
        print(f"    Done: {out_landscape.name} ({size_mb:.1f}MB)")

    # ── 9:16 VERTICAL (1080x1920) — crop center of 16:9, then caption ──
    print(f"\n  Creating 9:16 vertical version (Reels/Stories)...")
    # Crop center portion of 16:9 to 9:16 ratio, then scale to 1080x1920
    vert_filters = ["crop=ih*9/16:ih:iw/2-ih*9/32:0", "scale=1080:1920"]
    vert_filters.extend(build_caption_filters(vid["captions_vertical"], 1080, 1920))
    cmd = [
        "ffmpeg", "-y", "-i", str(concat_path),
        "-vf", ",".join(vert_filters),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an",  # drop audio for vertical — most watch muted
        str(out_vertical)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr[-300:]}")
    else:
        size_mb = out_vertical.stat().st_size / (1024 * 1024)
        print(f"    Done: {out_vertical.name} ({size_mb:.1f}MB)")

    # ── 1:1 SQUARE (1080x1080) — crop center of 16:9, then caption ──
    print(f"\n  Creating 1:1 square version (Feed)...")
    sq_filters = ["crop=ih:ih:iw/2-ih/2:0", "scale=1080:1080"]
    sq_filters.extend(build_caption_filters(vid["captions_square"], 1080, 1080))
    cmd = [
        "ffmpeg", "-y", "-i", str(concat_path),
        "-vf", ",".join(sq_filters),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an",
        str(out_square)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr[-300:]}")
    else:
        size_mb = out_square.stat().st_size / (1024 * 1024)
        print(f"    Done: {out_square.name} ({size_mb:.1f}MB)")

    # ── Cleanup temp files ──
    for f in [clip_a, clip_b, concat_path, list_path]:
        if f.exists():
            f.unlink()


# ════════════════════════════════════════════════════════════
# VIDEO 1: COMPARISON  (Sydney cramped flat vs Bali villa)
# ════════════════════════════════════════════════════════════
COMPARISON = {
    "clip_a_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

Multiple slow tracking shots through a tiny, dark, cramped apartment. Grey walls, peeling paint, small dirty window overlooking a grey concrete carpark, cheap furniture, tiny depressing kitchen, claustrophobic bedroom barely fitting a bed. Fluorescent lighting. Show multiple angles — hallway, kitchen, bedroom — all equally grim and suffocating. Muted desaturated grey colour grading. Depressing atmosphere throughout.""",

    "clip_b_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

A breathtaking luxury tropical villa at blue-hour dusk. Camera glides smoothly through a stunning open-plan living area with warm amber lights, past a modern kitchen, through a spacious bedroom with garden views, then out through glass doors revealing a gorgeous glowing turquoise infinity pool surrounded by palm trees and tropical gardens. Deep blue twilight sky. Warm golden light from every fixture. Rich saturated warm colours. Paradise.""",

    "final": "video-ad-comparison.mp4",

    # 16:9 LANDSCAPE captions (1280x720 canvas)
    # Section 1: Sydney (0-7.5s) — headline + location + specs
    # Section 2: Bali (8.2-13.5s) — headline + location + specs
    # End card (14-16s) — tagline + price + location
    # KEY: No overlap between sections!
    "captions_landscape": [
        # ── Sydney section (clip A: 0–7.5s) ──
        {"text": "Same price. Different life.", "start": 0.3, "end": 7.5, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Sydney", "start": 0.5, "end": 7.5, "y": "h*0.50", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "1 bed. No pool. No garden.", "start": 1.0, "end": 7.5, "y": "h*0.61", "size": 30, "font": "segoeui.ttf", "color": "white@0.9"},
        # ── Bali section (clip B: 8–13.5s) ──
        {"text": "Same price. Different life.", "start": 8.2, "end": 13.5, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Bali", "start": 8.2, "end": 13.5, "y": "h*0.50", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed. 3 bath. Private pool. North Canggu.", "start": 8.7, "end": 13.5, "y": "h*0.61", "size": 30, "font": "segoeui.ttf", "color": "white@0.9"},
        # ── End card (14–16s) — clean gap, no overlap ──
        {"text": "Same price. Different life.", "start": 14, "end": 16, "y": "h*0.30", "size": 64, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 villas from $170,000", "start": 14, "end": 16, "y": "h*0.47", "size": 34, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.57", "size": 30, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    # 9:16 VERTICAL captions (1080x1920 canvas) — text in lower half
    "captions_vertical": [
        {"text": "Same price.", "start": 0.3, "end": 7.5, "y": "h*0.05", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 0.3, "end": 7.5, "y": "h*0.09", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Sydney", "start": 0.5, "end": 7.5, "y": "h*0.70", "size": 62, "font": "segoeuib.ttf", "color": "white"},
        {"text": "1 bed. No pool. No garden.", "start": 1.0, "end": 7.5, "y": "h*0.77", "size": 34, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same price.", "start": 8.2, "end": 13.5, "y": "h*0.05", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 8.2, "end": 13.5, "y": "h*0.09", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Bali", "start": 8.2, "end": 13.5, "y": "h*0.70", "size": 62, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed. 3 bath. Private pool.", "start": 8.7, "end": 13.5, "y": "h*0.77", "size": 34, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "North Canggu.", "start": 8.7, "end": 13.5, "y": "h*0.81", "size": 34, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same price.", "start": 14, "end": 16, "y": "h*0.33", "size": 72, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 14, "end": 16, "y": "h*0.38", "size": 72, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 villas from $170,000", "start": 14, "end": 16, "y": "h*0.50", "size": 40, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.55", "size": 36, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    # 1:1 SQUARE captions (1080x1080 canvas)
    "captions_square": [
        {"text": "Same price. Different life.", "start": 0.3, "end": 7.5, "y": "h*0.06", "size": 48, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Sydney", "start": 0.5, "end": 7.5, "y": "h*0.72", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "1 bed. No pool. No garden.", "start": 1.0, "end": 7.5, "y": "h*0.81", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same price. Different life.", "start": 8.2, "end": 13.5, "y": "h*0.06", "size": 48, "font": "segoeuib.ttf", "color": "white"},
        {"text": "$175,000 — Bali", "start": 8.2, "end": 13.5, "y": "h*0.72", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed. 3 bath. Private pool.", "start": 8.7, "end": 13.5, "y": "h*0.81", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same price. Different life.", "start": 14, "end": 16, "y": "h*0.28", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 villas from $170,000", "start": 14, "end": 16, "y": "h*0.48", "size": 32, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.56", "size": 28, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],
}

# ════════════════════════════════════════════════════════════
# VIDEO 2: FIFO  (Mine site vs villa life)
# ════════════════════════════════════════════════════════════
FIFO = {
    "clip_a_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

Multiple shots of an exhausted rugged male worker in dusty orange hi-vis safety vest and white hard hat at a remote Australian red-dirt mine site. Close-up of his tired dusty face squinting in harsh sun. Wide shot of barren outback with massive yellow haul trucks. Him walking wearily across red dirt. Heavy machinery. Isolation. Fatigue. Desaturated muted colours. Hard shadows.""",

    "clip_b_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

A relaxed happy man in his 40s at a luxury tropical villa at golden sunset. Multiple shots: walking barefoot along a glowing turquoise infinity pool, sitting on a comfortable daybed holding a cold beer and smiling genuinely, looking out over palm trees from a villa terrace, feet in the pool water. Warm golden sunset light. Villa glowing with amber lights. Rich warm saturated tropical colours. Freedom, peace, contentment.""",

    "final": "video-ad-fifo.mp4",

    "captions_landscape": [
        # ── Mine section (0–7.5s) ──
        {"text": "Same budget. Different life.", "start": 0.3, "end": 7.5, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks on.", "start": 0.5, "end": 7.5, "y": "h*0.50", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        # ── Villa section (8–13s) ──
        {"text": "Same budget. Different life.", "start": 8.2, "end": 13, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks off.", "start": 8.2, "end": 13, "y": "h*0.50", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "What are you doing with your time off?", "start": 9, "end": 13, "y": "h*0.61", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
        # ── End card (13.5–16s) ──
        {"text": "Same budget. Different life.", "start": 13.5, "end": 16, "y": "h*0.30", "size": 64, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed villa from $170,000", "start": 13.5, "end": 16, "y": "h*0.47", "size": 34, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 13.5, "end": 16, "y": "h*0.57", "size": 30, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    "captions_vertical": [
        {"text": "Same budget.", "start": 0.3, "end": 7.5, "y": "h*0.05", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 0.3, "end": 7.5, "y": "h*0.09", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks on.", "start": 0.5, "end": 7.5, "y": "h*0.70", "size": 64, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Same budget.", "start": 8.2, "end": 13, "y": "h*0.05", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 8.2, "end": 13, "y": "h*0.09", "size": 58, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks off.", "start": 8.2, "end": 13, "y": "h*0.70", "size": 64, "font": "segoeuib.ttf", "color": "white"},
        {"text": "What are you doing", "start": 9, "end": 13, "y": "h*0.77", "size": 34, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "with your time off?", "start": 9, "end": 13, "y": "h*0.81", "size": 34, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same budget.", "start": 13.5, "end": 16, "y": "h*0.33", "size": 72, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Different life.", "start": 13.5, "end": 16, "y": "h*0.38", "size": 72, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed villa from $170,000", "start": 13.5, "end": 16, "y": "h*0.50", "size": 40, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 13.5, "end": 16, "y": "h*0.55", "size": 36, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    "captions_square": [
        {"text": "Same budget. Different life.", "start": 0.3, "end": 7.5, "y": "h*0.06", "size": 48, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks on.", "start": 0.5, "end": 7.5, "y": "h*0.72", "size": 54, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Same budget. Different life.", "start": 8.2, "end": 13, "y": "h*0.06", "size": 48, "font": "segoeuib.ttf", "color": "white"},
        {"text": "2 weeks off.", "start": 8.2, "end": 13, "y": "h*0.72", "size": 54, "font": "segoeuib.ttf", "color": "white"},
        {"text": "What are you doing with your time off?", "start": 9, "end": 13, "y": "h*0.81", "size": 26, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Same budget. Different life.", "start": 13.5, "end": 16, "y": "h*0.28", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed villa from $170,000", "start": 13.5, "end": 16, "y": "h*0.48", "size": 32, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 13.5, "end": 16, "y": "h*0.56", "size": 28, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],
}

# ════════════════════════════════════════════════════════════
# VIDEO 3: WALKTHROUGH  (Villa interior → pool reveal)
# ════════════════════════════════════════════════════════════
WALKTHROUGH = {
    "clip_a_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

A smooth continuous gimbal shot entering a stunning modern tropical villa at dusk through an impressive entrance. The camera glides through a spacious elegant open-plan living area with warm amber recessed ceiling lights, designer furniture, past a sleek modern kitchen with under-cabinet lighting. Warm golden light from every fixture. The interior is luxurious, modern, spacious.""",

    "clip_b_prompt": """Generate a cinematic 8-second video. ABSOLUTELY NO TEXT, WORDS, NUMBERS, OR CAPTIONS ANYWHERE IN THE VIDEO.

Continuing a smooth gimbal walkthrough of a luxury tropical villa at dusk. Camera moves through a beautiful spacious bedroom with large windows showing tropical gardens, then through floor-to-ceiling glass doors for a grand reveal: a breathtaking private infinity pool glowing brilliant turquoise in the deep blue twilight. Lush tropical garden with palm trees and frangipani. Camera slowly pans across the pool taking in the full beauty. Warm villa lights reflect in the water. Deep navy blue sky. Magical atmosphere.""",

    "final": "video-ad-walkthrough.mp4",

    "captions_landscape": [
        # ── Price headline (0.5–6s) ──
        {"text": "From $170,000 — North Canggu, Bali", "start": 0.5, "end": 6, "y": "h*0.07", "size": 46, "font": "segoeuib.ttf", "color": "white"},
        # ── Specs mid-way (6–13.5s) ──
        {"text": "3 bed  ·  3 bath  ·  Private pool", "start": 6, "end": 13.5, "y": "h*0.50", "size": 48, "font": "segoeuib.ttf", "color": "white"},
        {"text": "28-year lease  ·  SBG & SLF licensed", "start": 7, "end": 13.5, "y": "h*0.61", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
        # ── End card (14–16s) ──
        {"text": "Only 3 available.", "start": 14, "end": 16, "y": "h*0.30", "size": 60, "font": "segoeuib.ttf", "color": "white"},
        {"text": "From $170,000 — North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.47", "size": 32, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    "captions_vertical": [
        {"text": "From $170,000", "start": 0.5, "end": 6, "y": "h*0.05", "size": 54, "font": "segoeuib.ttf", "color": "white"},
        {"text": "North Canggu, Bali", "start": 0.5, "end": 6, "y": "h*0.09", "size": 42, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "3 bed  ·  3 bath", "start": 6, "end": 13.5, "y": "h*0.70", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "Private pool", "start": 6, "end": 13.5, "y": "h*0.76", "size": 56, "font": "segoeuib.ttf", "color": "white"},
        {"text": "28-year lease  ·  SBG & SLF licensed", "start": 7, "end": 13.5, "y": "h*0.82", "size": 30, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Only 3 available.", "start": 14, "end": 16, "y": "h*0.35", "size": 68, "font": "segoeuib.ttf", "color": "white"},
        {"text": "From $170,000", "start": 14, "end": 16, "y": "h*0.50", "size": 40, "font": "segoeuib.ttf", "color": "#b08d57"},
        {"text": "North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.55", "size": 36, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],

    "captions_square": [
        {"text": "From $170,000 — North Canggu, Bali", "start": 0.5, "end": 6, "y": "h*0.06", "size": 38, "font": "segoeuib.ttf", "color": "white"},
        {"text": "3 bed  ·  3 bath  ·  Private pool", "start": 6, "end": 13.5, "y": "h*0.72", "size": 44, "font": "segoeuib.ttf", "color": "white"},
        {"text": "28-year lease  ·  SBG & SLF licensed", "start": 7, "end": 13.5, "y": "h*0.81", "size": 24, "font": "segoeui.ttf", "color": "white@0.9"},
        {"text": "Only 3 available.", "start": 14, "end": 16, "y": "h*0.30", "size": 54, "font": "segoeuib.ttf", "color": "white"},
        {"text": "From $170,000 — North Canggu, Bali", "start": 14, "end": 16, "y": "h*0.48", "size": 28, "font": "segoeuib.ttf", "color": "#b08d57"},
    ],
}


# ════════════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════════════
ALL_VIDEOS = [
    ("COMPARISON", COMPARISON),
    ("FIFO", FIFO),
    ("WALKTHROUGH", WALKTHROUGH),
]

for i, (name, vid) in enumerate(ALL_VIDEOS):
    try:
        process_video(name, vid, i)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        # Cleanup temp files on error
        for suffix in [f"temp_clip_a_{i}.mp4", f"temp_clip_b_{i}.mp4",
                       f"temp_concat_{i}.mp4", f"concat_list_{i}.txt"]:
            p = OUT_DIR / suffix
            if p.exists():
                p.unlink()

    if i < len(ALL_VIDEOS) - 1:
        print(f"\n  Waiting 15s before next video...")
        time.sleep(15)

print(f"\n{'='*60}")
print("  ALL DONE — 3 videos x 3 formats = 9 files")
print(f"{'='*60}")
print(f"\n  Output files in: {OUT_DIR}")
print("  Formats:")
print("    *-landscape.mp4  → 16:9 (in-stream ads)")
print("    *-vertical.mp4   → 9:16 (Reels, Stories)")
print("    *-square.mp4     → 1:1  (Feed ads)")
