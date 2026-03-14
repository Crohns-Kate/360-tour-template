"""
fix-walkthrough-thumbs.py — Build walkthrough thumbnails from interior frame (t=4).
Uses the open-plan living/kitchen/pool shot — only a small top caption to mask.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(__file__).parent / "ad-creatives"

FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
WHITE = (255, 255, 255)
GOLD = (176, 141, 87)


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text_outline(draw, pos, text, font, fill=WHITE, ow=5):
    x, y = pos
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx*dx + dy*dy <= ow*ow:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def draw_centered(draw, y, text, font, fill=WHITE, w=1920, ow=5):
    tw, _ = text_size(draw, text, font)
    x = (w - tw) // 2
    draw_text_outline(draw, (x, y), text, font, fill, ow)


def add_bar(img, y, h, opacity=255):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([(0, y), (img.width, y + h)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img, ov)


def add_grad(img, y, h, opacity=240, direction="top"):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(h):
        r = (1 - i/h) if direction == "top" else (i/h)
        d.line([(0, y+i), (img.width, y+i)], fill=(0, 0, 0, int(opacity * r**0.6)))
    return Image.alpha_composite(img, ov)


# Load interior frame (t=4) — only small caption at top to mask
raw = Image.open(OUT_DIR / "thumb-wt-raw-t4.jpg")

# ═══ LANDSCAPE (1920x1080) ═══
print("  Walkthrough landscape...")
land = raw.resize((1920, 1080), Image.LANCZOS).convert("RGBA")
# Mask the top caption "From $170,000 — North Canggu, Bali" with fully opaque bar
land = add_bar(land, 0, 180, opacity=255)
# Heavy gradient top + solid bottom
land = add_grad(land, 0, 320, opacity=250, direction="top")
land = add_bar(land, land.height - 250, 250, opacity=250)

draw = ImageDraw.Draw(land)
w = land.width
f_huge = load_font(FONT_IMPACT, 100)
f_big = load_font(FONT_IMPACT, 72)
f_price = load_font(FONT_BOLD, 48)
f_spec = load_font(FONT_BOLD, 36)

draw_centered(draw, 25, "ONLY 3 AVAILABLE.", f_huge, WHITE, w)
draw_centered(draw, 145, "From $170,000", f_big, GOLD, w)

draw_centered(draw, land.height - 210, "3 bed  ·  3 bath  ·  Private pool", f_price, WHITE, w)
draw_centered(draw, land.height - 145, "28-year lease  ·  SBG & SLF licensed", f_spec, (220,220,220), w, ow=4)
draw_centered(draw, land.height - 90, "North Canggu, Bali", f_spec, GOLD, w, ow=4)

land.convert("RGB").save(OUT_DIR / "thumb-walkthrough-landscape.jpg", quality=92)
print("    Done")


# ═══ SQUARE (1080x1080) ═══
print("  Walkthrough square...")
rw, rh = raw.size
s = min(rw, rh)
left = (rw - s) // 2
sq = raw.crop((left, 0, left + s, rh)).resize((1080, 1080), Image.LANCZOS).convert("RGBA")
# Mask top caption with fully opaque bar
sq = add_bar(sq, 0, 200, opacity=255)
# Gradients
sq = add_grad(sq, 0, 320, opacity=245, direction="top")
sq = add_bar(sq, sq.height - 300, 300, opacity=250)

draw = ImageDraw.Draw(sq)
sw = sq.width
f_sq_huge = load_font(FONT_IMPACT, 78)
f_sq_big = load_font(FONT_IMPACT, 58)
f_sq_price = load_font(FONT_BOLD, 40)
f_sq_spec = load_font(FONT_BOLD, 30)

draw_centered(draw, 20, "ONLY 3", f_sq_huge, WHITE, sw)
draw_centered(draw, 105, "AVAILABLE.", f_sq_huge, WHITE, sw)
draw_centered(draw, 200, "From $170,000", f_sq_big, GOLD, sw)

draw_centered(draw, sq.height - 260, "3 bed · 3 bath · Private pool", f_sq_price, WHITE, sw)
draw_centered(draw, sq.height - 205, "28-year lease · Licensed", f_sq_spec, (220,220,220), sw, ow=4)
draw_centered(draw, sq.height - 130, "North Canggu, Bali", f_sq_spec, GOLD, sw, ow=4)

sq.convert("RGB").save(OUT_DIR / "thumb-walkthrough-square.jpg", quality=92)
print("    Done")


# ═══ VERTICAL (1080x1920) ═══
print("  Walkthrough vertical...")
target_w = int(rh * 9 / 16)
left = (rw - target_w) // 2
vt = raw.crop((left, 0, left + target_w, rh)).resize((1080, 1920), Image.LANCZOS).convert("RGBA")
# Mask top caption with fully opaque bar (larger for vertical crop)
vt = add_bar(vt, 0, 300, opacity=255)
# Gradients
vt = add_grad(vt, 0, 500, opacity=245, direction="top")
vt = add_bar(vt, vt.height - 500, 500, opacity=250)

draw = ImageDraw.Draw(vt)
vw = vt.width
f_v_huge = load_font(FONT_IMPACT, 92)
f_v_big = load_font(FONT_IMPACT, 70)
f_v_price = load_font(FONT_BOLD, 52)
f_v_spec = load_font(FONT_BOLD, 36)

draw_centered(draw, 50, "ONLY 3", f_v_huge, WHITE, vw)
draw_centered(draw, 155, "AVAILABLE.", f_v_huge, WHITE, vw)
draw_centered(draw, 280, "From $170,000", f_v_big, GOLD, vw)

draw_centered(draw, vt.height - 420, "3 bed · 3 bath", f_v_price, WHITE, vw)
draw_centered(draw, vt.height - 355, "Private pool", f_v_price, WHITE, vw)
draw_centered(draw, vt.height - 260, "28-year lease", f_v_spec, (220,220,220), vw, ow=4)
draw_centered(draw, vt.height - 215, "SBG & SLF licensed", f_v_spec, (220,220,220), vw, ow=4)
draw_centered(draw, vt.height - 120, "North Canggu, Bali", f_v_spec, GOLD, vw, ow=4)

vt.convert("RGB").save(OUT_DIR / "thumb-walkthrough-vertical.jpg", quality=92)
print("    Done")

# Cleanup temp frames
for f in ["thumb-wt-raw-t2.jpg", "thumb-wt-raw-t4.jpg", "thumb-wt-raw-t11.jpg"]:
    p = OUT_DIR / f
    if p.exists():
        p.unlink()

print("\n  All 3 walkthrough thumbnails rebuilt clean")
