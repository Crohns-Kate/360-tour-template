"""
add-scroll-stoppers.py — Add large, bold, scroll-stopping headline banners
to all 7 static ad creatives. Masks old AI-burned-in text first.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(__file__).parent / "ad-creatives"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"

GOLD = (176, 141, 87)
WHITE = (255, 255, 255)


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text_with_outline(draw, pos, text, font, fill=WHITE, outline_color=(0,0,0), outline_width=4):
    """Draw text with thick outline for max readability over any background."""
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx*dx + dy*dy <= outline_width*outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill)


def draw_centered(draw, y, text, font, fill=WHITE, img_width=1424, outline=True, outline_width=4):
    """Draw centered text with outline."""
    tw, _ = text_size(draw, text, font)
    x = (img_width - tw) // 2
    if outline:
        draw_text_with_outline(draw, (x, y), text, font, fill, outline_width=outline_width)
    else:
        draw.text((x, y), text, font=font, fill=fill)


def add_gradient_bar(img, y_start, height, opacity=220, direction="top"):
    """Add a gradient dark bar for text readability."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(height):
        if direction == "top":
            # Strongest at top, fading down
            ratio = 1 - (i / height)
        else:
            # Strongest at bottom, fading up
            ratio = i / height
        alpha = int(opacity * ratio ** 0.6)
        d.line([(0, y_start + i), (img.width, y_start + i)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def add_solid_bar(img, y_start, height, color=(0,0,0), opacity=255):
    """Add a fully opaque bar."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([(0, y_start), (img.width, y_start + height)], fill=(*color, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


# ════════════════════════════════════════════
# CREATIVE 1: COMPARISON (1424x752)
# Old burned-in text: bottom ~180px ("SYDNEY — AU$175,000" etc)
# ════════════════════════════════════════════
def process_creative_1():
    print("  Creative 1: Comparison...")
    img = Image.open(OUT_DIR / "creative-1-comparison.jpg").convert("RGBA")
    w, h = img.size

    # MASK old bottom text with fully opaque black bar
    img = add_solid_bar(img, h - 220, 220, opacity=255)
    # Top gradient for headline
    img = add_gradient_bar(img, 0, 150, opacity=230, direction="top")

    draw = ImageDraw.Draw(img)

    # TOP: Scroll-stopping headline
    font_big = load_font(FONT_IMPACT, 72)
    font_sub = load_font(FONT_BOLD, 32)
    draw_centered(draw, 14, "SAME PRICE. DIFFERENT LIFE.", font_big, WHITE, w)
    draw_centered(draw, 96, "What does $175,000 actually buy you?", font_sub, GOLD, w, outline_width=3)

    # BOTTOM LEFT: Sydney
    font_price = load_font(FONT_BOLD, 50)
    font_detail = load_font(FONT_REGULAR, 26)
    lx = 60
    draw_text_with_outline(draw, (lx, h - 170), "$175,000 — Sydney", font_price, WHITE)
    draw_text_with_outline(draw, (lx, h - 110), "1 bed. No pool. No garden.", font_detail, (220,220,220), outline_width=3)

    # BOTTOM RIGHT: Bali
    rx = w // 2 + 60
    draw_text_with_outline(draw, (rx, h - 170), "$175,000 — Bali", font_price, WHITE)
    draw_text_with_outline(draw, (rx, h - 110), "3 bed. 3 bath. Private pool.", font_detail, (220,220,220), outline_width=3)
    draw_text_with_outline(draw, (rx, h - 77), "North Canggu.", font_detail, GOLD, outline_width=3)

    img.convert("RGB").save(OUT_DIR / "creative-1-comparison.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 2: REGULATION (1024x1024)
# Already text-heavy on dark bg — just add urgency banner
# ════════════════════════════════════════════
def process_creative_2():
    print("  Creative 2: Regulation...")
    img = Image.open(OUT_DIR / "creative-2-regulation.jpg").convert("RGBA")
    w = img.width

    # Red urgency bar at top
    img = add_solid_bar(img, 0, 65, color=(180, 25, 25), opacity=240)

    draw = ImageDraw.Draw(img)
    font_urgency = load_font(FONT_IMPACT, 38)
    draw_centered(draw, 12, "DEADLINE: MARCH 31 — 18 DAYS LEFT", font_urgency, WHITE, w, outline=False)

    img.convert("RGB").save(OUT_DIR / "creative-2-regulation.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 3: FIFO (1424x752)
# Old burned-in text: bottom ~130px
# ════════════════════════════════════════════
def process_creative_3():
    print("  Creative 3: FIFO...")
    img = Image.open(OUT_DIR / "creative-3-fifo.jpg").convert("RGBA")
    w, h = img.size

    # MASK old bottom text — fully opaque
    img = add_solid_bar(img, h - 185, 185, opacity=255)
    # Top gradient
    img = add_gradient_bar(img, 0, 160, opacity=240, direction="top")

    draw = ImageDraw.Draw(img)

    # TOP: Scroll-stopper
    font_big = load_font(FONT_IMPACT, 68)
    font_sub = load_font(FONT_BOLD, 30)
    draw_centered(draw, 14, "2 WEEKS ON. 2 WEEKS OFF.", font_big, WHITE, w)
    draw_centered(draw, 92, "What are you doing with yours?", font_sub, GOLD, w, outline_width=3)

    # BOTTOM
    font_main = load_font(FONT_BOLD, 48)
    font_price = load_font(FONT_BOLD, 28)
    draw_centered(draw, h - 140, "Same budget. Different life.", font_main, WHITE, w)
    draw_centered(draw, h - 80, "3 bed villa from $170,000 — North Canggu, Bali", font_price, GOLD, w, outline_width=3)

    img.convert("RGB").save(OUT_DIR / "creative-3-fifo.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 4: RETIREMENT (1424x752)
# Old burned-in text: bottom ~140px
# ════════════════════════════════════════════
def process_creative_4():
    print("  Creative 4: Retirement...")
    img = Image.open(OUT_DIR / "creative-4-retirement.jpg").convert("RGBA")
    w, h = img.size

    # MASK old bottom text — fully opaque, extends higher
    img = add_solid_bar(img, h - 200, 200, opacity=255)
    # Top gradient
    img = add_gradient_bar(img, 0, 150, opacity=230, direction="top")

    draw = ImageDraw.Draw(img)

    # TOP
    font_big = load_font(FONT_IMPACT, 54)
    font_sub = load_font(FONT_BOLD, 30)
    draw_centered(draw, 14, "YOUR SUPER WAS SUPPOSED TO BE ENOUGH.", font_big, WHITE, w)
    draw_centered(draw, 78, "In Bali, it still is.", font_sub, GOLD, w, outline_width=3)

    # BOTTOM
    font_main = load_font(FONT_BOLD, 46)
    font_detail = load_font(FONT_BOLD, 26)
    draw_centered(draw, h - 150, "3 bed villa from $170,000", font_main, WHITE, w)
    draw_centered(draw, h - 95, "Private pool  ·  28-year lease  ·  North Canggu", font_detail, GOLD, w, outline_width=3)

    img.convert("RGB").save(OUT_DIR / "creative-4-retirement.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 5: SCARCITY (1024x1024)
# Already text on black — add urgency bar
# ════════════════════════════════════════════
def process_creative_5():
    print("  Creative 5: Scarcity...")
    img = Image.open(OUT_DIR / "creative-5-scarcity.jpg").convert("RGBA")
    w = img.width

    img = add_solid_bar(img, 0, 58, color=(180, 25, 25), opacity=235)

    draw = ImageDraw.Draw(img)
    font_urgency = load_font(FONT_IMPACT, 32)
    draw_centered(draw, 12, "ONLY 1 LEFT — ENQUIRE NOW", font_urgency, WHITE, w, outline=False)

    img.convert("RGB").save(OUT_DIR / "creative-5-scarcity.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 6: DIGITAL NOMAD (1424x752)
# Old burned-in text: bottom ~110px and some large text center-bottom
# ════════════════════════════════════════════
def process_creative_6():
    print("  Creative 6: Digital Nomad...")
    img = Image.open(OUT_DIR / "creative-6-digital-nomad.jpg").convert("RGBA")
    w, h = img.size

    # MASK old bottom text — fully opaque, bigger area
    img = add_solid_bar(img, h - 200, 200, opacity=255)
    # Top gradient
    img = add_gradient_bar(img, 0, 150, opacity=235, direction="top")

    draw = ImageDraw.Draw(img)

    # TOP
    font_big = load_font(FONT_IMPACT, 62)
    font_sub = load_font(FONT_BOLD, 28)
    draw_centered(draw, 12, "YOUR OFFICE. YOUR POOL. YOUR VILLA.", font_big, WHITE, w)
    draw_centered(draw, 84, "Stop renting someone else's dream.", font_sub, GOLD, w, outline_width=3)

    # BOTTOM
    font_main = load_font(FONT_BOLD, 42)
    font_detail = load_font(FONT_BOLD, 24)
    draw_centered(draw, h - 150, "Own in North Canggu from $170,000", font_main, WHITE, w)
    draw_centered(draw, h - 100, "28-year lease  ·  Licensed for Airbnb  ·  14 min to beach", font_detail, GOLD, w, outline_width=3)

    img.convert("RGB").save(OUT_DIR / "creative-6-digital-nomad.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
# CREATIVE 7: YOUNG FAMILY (1424x752)
# Old burned-in text: center-bottom ~200px
# ════════════════════════════════════════════
def process_creative_7():
    print("  Creative 7: Young Family...")
    img = Image.open(OUT_DIR / "creative-7-young-family.jpg").convert("RGBA")
    w, h = img.size

    # MASK old bottom text — fully opaque, extends higher
    img = add_solid_bar(img, h - 250, 250, opacity=255)
    # Top gradient
    img = add_gradient_bar(img, 0, 165, opacity=235, direction="top")

    draw = ImageDraw.Draw(img)

    # TOP
    font_big = load_font(FONT_IMPACT, 52)
    font_sub = load_font(FONT_BOLD, 30)
    draw_centered(draw, 10, "THE CHILDHOOD YOU DREAMED", font_big, WHITE, w)
    draw_centered(draw, 68, "OF GIVING THEM.", font_big, WHITE, w)
    draw_centered(draw, 125, "Still possible. Just not in Australia.", font_sub, GOLD, w, outline_width=3)

    # BOTTOM
    font_main = load_font(FONT_BOLD, 46)
    font_detail = load_font(FONT_BOLD, 26)
    draw_centered(draw, h - 185, "3 bed villa from $170,000", font_main, WHITE, w)
    draw_centered(draw, h - 130, "Private pool  ·  International school nearby", font_detail, GOLD, w, outline_width=3)
    draw_centered(draw, h - 96, "North Canggu, Bali", font_detail, GOLD, w, outline_width=3)

    img.convert("RGB").save(OUT_DIR / "creative-7-young-family.jpg", quality=92)
    print("    Done")


# ════════════════════════════════════════════
print("\n  Adding scroll-stopping captions...")
process_creative_1()
process_creative_2()
process_creative_3()
process_creative_4()
process_creative_5()
process_creative_6()
process_creative_7()
print("\n  ALL DONE — 7 creatives with scroll-stopping headlines")
