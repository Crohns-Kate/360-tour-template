"""
recaption-final.py — Take the 467b973 videos (one old caption layer at h-120 to h-35),
mask the old caption zone with a gradient, then overlay new captions higher.
"""

import subprocess
from pathlib import Path

OUT_DIR = Path(__file__).parent / "ad-creatives"

VIDEOS = [
    {
        "input": "video-ad-comparison.mp4",
        "output": "video-ad-comparison-fixed.mp4",
        "captions": [
            # Top headline — visible from first second
            {"text": "Same price. Different life.", "start": 0.3, "end": 6.5, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
            # Sydney section (first half)
            {"text": "$175,000 — Sydney", "start": 0.5, "end": 3.8, "y": "h*0.45", "size": 56, "font": "segoeuib.ttf", "color": "white"},
            {"text": "1 bed. No pool. No garden.", "start": 0.8, "end": 3.8, "y": "h*0.56", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
            # Bali section (second half) — ends cleanly before end card
            {"text": "$175,000 — Bali", "start": 4.2, "end": 6.5, "y": "h*0.45", "size": 56, "font": "segoeuib.ttf", "color": "white"},
            {"text": "3 bed. 3 bath. Private pool. North Canggu.", "start": 4.5, "end": 6.5, "y": "h*0.56", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
            # End card — clean, no overlap with above
            {"text": "Same price. Different life.", "start": 6.8, "end": 8, "y": "h*0.30", "size": 62, "font": "segoeuib.ttf", "color": "white"},
            {"text": "3 villas from $170,000", "start": 6.8, "end": 8, "y": "h*0.46", "size": 32, "font": "segoeuib.ttf", "color": "#b08d57"},
            {"text": "North Canggu, Bali", "start": 6.8, "end": 8, "y": "h*0.55", "size": 28, "font": "segoeuib.ttf", "color": "#b08d57"},
        ]
    },
    {
        "input": "video-ad-fifo.mp4",
        "output": "video-ad-fifo-fixed.mp4",
        "captions": [
            # Top headline from first second
            {"text": "Same budget. Different life.", "start": 0.3, "end": 6.5, "y": "h*0.07", "size": 52, "font": "segoeuib.ttf", "color": "white"},
            # Mine section
            {"text": "2 weeks on.", "start": 0.5, "end": 3.8, "y": "h*0.45", "size": 58, "font": "segoeuib.ttf", "color": "white"},
            # Bali section
            {"text": "2 weeks off.", "start": 4.2, "end": 6.5, "y": "h*0.45", "size": 58, "font": "segoeuib.ttf", "color": "white"},
            {"text": "What are you doing with yours?", "start": 4.5, "end": 6.5, "y": "h*0.56", "size": 28, "font": "segoeui.ttf", "color": "white@0.9"},
            # End card
            {"text": "Same budget. Different life.", "start": 6.8, "end": 8, "y": "h*0.30", "size": 62, "font": "segoeuib.ttf", "color": "white"},
            {"text": "3 bed villa from $170,000", "start": 6.8, "end": 8, "y": "h*0.46", "size": 32, "font": "segoeuib.ttf", "color": "#b08d57"},
            {"text": "North Canggu, Bali", "start": 6.8, "end": 8, "y": "h*0.55", "size": 28, "font": "segoeuib.ttf", "color": "#b08d57"},
        ]
    },
    {
        "input": "video-ad-walkthrough.mp4",
        "output": "video-ad-walkthrough-fixed.mp4",
        "captions": [
            # Price headline from first second
            {"text": "From $170,000 — North Canggu, Bali", "start": 0.5, "end": 5, "y": "h*0.07", "size": 46, "font": "segoeuib.ttf", "color": "white"},
            # Specs appear mid-way
            {"text": "3 bed  ·  3 bath  ·  Private pool", "start": 4, "end": 6.5, "y": "h*0.45", "size": 46, "font": "segoeuib.ttf", "color": "white"},
            {"text": "28-year lease  ·  SBG & SLF licensed", "start": 4.5, "end": 6.5, "y": "h*0.56", "size": 26, "font": "segoeui.ttf", "color": "white@0.9"},
            # End card
            {"text": "Only 3 available.", "start": 6.8, "end": 8, "y": "h*0.30", "size": 58, "font": "segoeuib.ttf", "color": "white"},
            {"text": "From $170,000 — North Canggu, Bali", "start": 6.8, "end": 8, "y": "h*0.46", "size": 30, "font": "segoeuib.ttf", "color": "#b08d57"},
        ]
    },
]

for vid in VIDEOS:
    input_path = OUT_DIR / vid["input"]
    output_path = OUT_DIR / vid["output"]

    print(f"\n  Processing: {vid['input']}")

    filters = []

    # Mask the old caption zone (h-120 to h, i.e. bottom ~17%)
    # Use a gradient-style black box to cover old burned-in captions
    filters.append(
        "drawbox=x=0:y=ih-130:w=iw:h=130:color=black@0.95:t=fill"
    )

    # Also mask old top caption area if any (top 60px)
    filters.append(
        "drawbox=x=0:y=0:w=iw:h=60:color=black@0.95:t=fill"
    )

    for cap in vid["captions"]:
        text = cap["text"].replace("'", "'\\''").replace(":", "\\:")
        color = cap.get("color", "white")
        font = cap.get("font", "segoeuib.ttf")

        f = (
            f"drawtext=text='{text}'"
            f":fontsize={cap['size']}"
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

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", ",".join(filters),
        "-codec:a", "copy", "-c:v", "libx264",
        "-preset", "fast", "-crf", "18",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr[-300:]}")
    else:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"    Done: {vid['output']} ({size_mb:.1f}MB)")

# Replace originals
print("\n  Replacing originals...")
for vid in VIDEOS:
    old = OUT_DIR / vid["input"]
    new = OUT_DIR / vid["output"]
    if new.exists():
        old.unlink()
        new.rename(old)
        print(f"    {vid['input']} updated")

print("\n  ALL DONE")
