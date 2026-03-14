"""
make-thumbnails.py — Create proper video thumbnails in all 3 aspect ratios.
- Comparison + FIFO: crop from static creatives (already have scroll-stopping text)
- Walkthrough: build from pool frame with big impact headline
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(__file__).parent / "ad-creatives"

FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

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


def draw_text_with_outline(draw, pos, text, font, fill=WHITE, outline_width=4):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx*dx + dy*dy <= outline_width*outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def draw_centered(draw, y, text, font, fill=WHITE, img_width=1920, outline_width=4):
    tw, _ = text_size(draw, text, font)
    x = (img_width - tw) // 2
    draw_text_with_outline(draw, (x, y), text, font, fill, outline_width)


def add_solid_bar(img, y_start, height, opacity=255):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([(0, y_start), (img.width, y_start + height)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def add_gradient_bar(img, y_start, height, opacity=230, direction="top"):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(height):
        if direction == "top":
            ratio = 1 - (i / height)
        else:
            ratio = i / height
        alpha = int(opacity * ratio ** 0.6)
        d.line([(0, y_start + i), (img.width, y_start + i)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def crop_to_square(img):
    """Center crop to 1:1."""
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    return img.crop((left, top, left + s, top + s)).resize((1080, 1080), Image.LANCZOS)


def crop_to_vertical(img):
    """Center crop to 9:16."""
    w, h = img.size
    target_w = int(h * 9 / 16)
    if target_w > w:
        target_h = int(w * 16 / 9)
        top = (h - target_h) // 2
        cropped = img.crop((0, top, w, top + target_h))
    else:
        left = (w - target_w) // 2
        cropped = img.crop((left, 0, left + target_w, h))
    return cropped.resize((1080, 1920), Image.LANCZOS)


def crop_to_landscape(img):
    """Center crop to 16:9."""
    w, h = img.size
    target_h = int(w * 9 / 16)
    if target_h > h:
        target_w = int(h * 16 / 9)
        left = (w - target_w) // 2
        cropped = img.crop((left, 0, left + target_w, h))
    else:
        top = (h - target_h) // 2
        cropped = img.crop((0, top, w, top + target_h))
    return cropped.resize((1920, 1080), Image.LANCZOS)


# ════════════════════════════════════════════
# COMPARISON — use static creative, crop to 3 sizes
# ════════════════════════════════════════════
print("  Comparison thumbnails...")
comp = Image.open(OUT_DIR / "creative-1-comparison.jpg")
crop_to_landscape(comp).save(OUT_DIR / "thumb-comparison-landscape.jpg", quality=92)
crop_to_square(comp).save(OUT_DIR / "thumb-comparison-square.jpg", quality=92)
# For vertical, the split-screen won't work well cropped — use Bali half
# Crop right half of original, then make vertical
w, h = comp.size
bali_half = comp.crop((w // 2, 0, w, h))
bali_vert = crop_to_vertical(bali_half)
# Add text overlay to vertical
bali_vert = bali_vert.convert("RGBA")
bali_vert = add_gradient_bar(bali_vert, 0, 400, opacity=220, direction="top")
bali_vert = add_solid_bar(bali_vert, bali_vert.height - 450, 450, opacity=240)
draw = ImageDraw.Draw(bali_vert)
vw = bali_vert.width
font_big = load_font(FONT_IMPACT, 82)
font_sub = load_font(FONT_BOLD, 42)
font_price = load_font(FONT_BOLD, 56)
font_detail = load_font(FONT_BOLD, 32)
draw_centered(draw, 40, "SAME PRICE.", font_big, WHITE, vw)
draw_centered(draw, 135, "DIFFERENT LIFE.", font_big, WHITE, vw)
draw_centered(draw, 240, "What does $175,000 buy you?", font_sub, GOLD, vw, outline_width=3)
draw_centered(draw, bali_vert.height - 380, "$175,000 — Bali", font_price, WHITE, vw)
draw_centered(draw, bali_vert.height - 310, "3 bed. 3 bath. Private pool.", font_detail, (220,220,220), vw, outline_width=3)
draw_centered(draw, bali_vert.height - 265, "North Canggu.", font_detail, GOLD, vw, outline_width=3)
draw_centered(draw, bali_vert.height - 150, "Only 3 available.", font_sub, WHITE, vw, outline_width=3)
draw_centered(draw, bali_vert.height - 95, "From $170,000", font_detail, GOLD, vw, outline_width=3)
bali_vert.convert("RGB").save(OUT_DIR / "thumb-comparison-vertical.jpg", quality=92)
print("    Done — 3 sizes")


# ════════════════════════════════════════════
# FIFO — use static creative, crop to 3 sizes
# ════════════════════════════════════════════
print("  FIFO thumbnails...")
fifo = Image.open(OUT_DIR / "creative-3-fifo.jpg")
crop_to_landscape(fifo).save(OUT_DIR / "thumb-fifo-landscape.jpg", quality=92)
crop_to_square(fifo).save(OUT_DIR / "thumb-fifo-square.jpg", quality=92)
# Vertical — use villa/pool half
w, h = fifo.size
villa_half = fifo.crop((w // 2, 0, w, h))
villa_vert = crop_to_vertical(villa_half)
villa_vert = villa_vert.convert("RGBA")
villa_vert = add_gradient_bar(villa_vert, 0, 400, opacity=220, direction="top")
villa_vert = add_solid_bar(villa_vert, villa_vert.height - 400, 400, opacity=240)
draw = ImageDraw.Draw(villa_vert)
vw = villa_vert.width
draw_centered(draw, 40, "2 WEEKS ON.", font_big, WHITE, vw)
draw_centered(draw, 135, "2 WEEKS OFF.", font_big, WHITE, vw)
draw_centered(draw, 240, "What are you doing with yours?", font_sub, GOLD, vw, outline_width=3)
draw_centered(draw, villa_vert.height - 330, "Same budget.", font_price, WHITE, vw)
draw_centered(draw, villa_vert.height - 260, "Different life.", font_price, WHITE, vw)
draw_centered(draw, villa_vert.height - 150, "3 bed villa from $170,000", font_detail, GOLD, vw, outline_width=3)
draw_centered(draw, villa_vert.height - 105, "North Canggu, Bali", font_detail, GOLD, vw, outline_width=3)
villa_vert.convert("RGB").save(OUT_DIR / "thumb-fifo-vertical.jpg", quality=92)
print("    Done — 3 sizes")


# ════════════════════════════════════════════
# WALKTHROUGH — build from pool frame with big impact text
# ════════════════════════════════════════════
print("  Walkthrough thumbnails...")
# Use the extracted pool frame as base
pool = Image.open(OUT_DIR / "thumb-walkthrough-landscape.jpg")
pool = pool.resize((1920, 1080), Image.LANCZOS).convert("RGBA")

# Add heavy gradients top + bottom
pool = add_gradient_bar(pool, 0, 300, opacity=240, direction="top")
pool = add_solid_bar(pool, pool.height - 280, 280, opacity=245)

draw = ImageDraw.Draw(pool)
pw = pool.width
font_huge = load_font(FONT_IMPACT, 96)
font_big2 = load_font(FONT_IMPACT, 72)
font_sub2 = load_font(FONT_BOLD, 38)
font_price2 = load_font(FONT_BOLD, 48)
font_detail2 = load_font(FONT_BOLD, 32)

# TOP — scroll-stopping headline
draw_centered(draw, 30, "ONLY 3 AVAILABLE.", font_huge, WHITE, pw)
draw_centered(draw, 145, "From $170,000", font_big2, GOLD, pw)

# BOTTOM — specs
draw_centered(draw, pool.height - 240, "3 bed  ·  3 bath  ·  Private pool", font_price2, WHITE, pw)
draw_centered(draw, pool.height - 175, "28-year lease  ·  SBG & SLF licensed", font_detail2, (220,220,220), pw, outline_width=3)
draw_centered(draw, pool.height - 110, "North Canggu, Bali", font_sub2, GOLD, pw, outline_width=3)

pool_rgb = pool.convert("RGB")
pool_rgb.save(OUT_DIR / "thumb-walkthrough-landscape.jpg", quality=92)

# Square version
crop_to_square(pool_rgb).save(OUT_DIR / "thumb-walkthrough-square-temp.jpg", quality=92)
# Re-do square with proper text since crop loses some
sq = Image.open(OUT_DIR / "thumb-walkthrough-landscape.jpg")
sq_img = crop_to_square(sq).convert("RGBA")
sq_img = add_gradient_bar(sq_img, 0, 250, opacity=230, direction="top")
sq_img = add_solid_bar(sq_img, sq_img.height - 280, 280, opacity=240)
draw = ImageDraw.Draw(sq_img)
sw = sq_img.width
font_sq_big = load_font(FONT_IMPACT, 72)
font_sq_sub = load_font(FONT_BOLD, 34)
font_sq_price = load_font(FONT_BOLD, 40)
font_sq_det = load_font(FONT_BOLD, 28)
draw_centered(draw, 20, "ONLY 3", font_sq_big, WHITE, sw)
draw_centered(draw, 98, "AVAILABLE.", font_sq_big, WHITE, sw)
draw_centered(draw, 180, "From $170,000", font_sq_sub, GOLD, sw, outline_width=3)
draw_centered(draw, sq_img.height - 240, "3 bed · 3 bath · Private pool", font_sq_price, WHITE, sw)
draw_centered(draw, sq_img.height - 185, "28-year lease · Licensed", font_sq_det, (220,220,220), sw, outline_width=3)
draw_centered(draw, sq_img.height - 120, "North Canggu, Bali", font_sq_sub, GOLD, sw, outline_width=3)
sq_img.convert("RGB").save(OUT_DIR / "thumb-walkthrough-square.jpg", quality=92)

# Vertical version — pool frame cropped to 9:16 with text
pool_base = Image.open(OUT_DIR / "thumb-walkthrough-landscape.jpg")
vert = crop_to_vertical(pool_base).convert("RGBA")
vert = add_gradient_bar(vert, 0, 500, opacity=235, direction="top")
vert = add_solid_bar(vert, vert.height - 500, 500, opacity=240)
draw = ImageDraw.Draw(vert)
vw = vert.width
font_v_huge = load_font(FONT_IMPACT, 90)
font_v_big = load_font(FONT_IMPACT, 68)
font_v_sub = load_font(FONT_BOLD, 42)
font_v_price = load_font(FONT_BOLD, 50)
font_v_det = load_font(FONT_BOLD, 34)
draw_centered(draw, 50, "ONLY 3", font_v_huge, WHITE, vw)
draw_centered(draw, 155, "AVAILABLE.", font_v_huge, WHITE, vw)
draw_centered(draw, 280, "From $170,000", font_v_big, GOLD, vw)
draw_centered(draw, vert.height - 420, "3 bed · 3 bath", font_v_price, WHITE, vw)
draw_centered(draw, vert.height - 355, "Private pool", font_v_price, WHITE, vw)
draw_centered(draw, vert.height - 260, "28-year lease", font_v_det, (220,220,220), vw, outline_width=3)
draw_centered(draw, vert.height - 215, "SBG & SLF licensed", font_v_det, (220,220,220), vw, outline_width=3)
draw_centered(draw, vert.height - 120, "North Canggu, Bali", font_v_sub, GOLD, vw, outline_width=3)
vert.convert("RGB").save(OUT_DIR / "thumb-walkthrough-vertical.jpg", quality=92)

# Cleanup temp
temp = OUT_DIR / "thumb-walkthrough-square-temp.jpg"
if temp.exists():
    temp.unlink()

print("    Done — 3 sizes")

print("\n  ALL DONE — 9 thumbnails ready")
print("  Files:")
print("    thumb-comparison-landscape.jpg / -square.jpg / -vertical.jpg")
print("    thumb-fifo-landscape.jpg / -square.jpg / -vertical.jpg")
print("    thumb-walkthrough-landscape.jpg / -square.jpg / -vertical.jpg")
