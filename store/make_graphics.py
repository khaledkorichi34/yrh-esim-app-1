"""Draws the app icon, adaptive icon, splash, Play Store icon and feature graphic.
Run: python3 store/make_graphics.py  (needs Pillow)"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
NAVY = (16, 34, 51, 255)
NAVY_SOFT = (30, 58, 82, 255)
YELLOW = (255, 201, 60, 255)
WHITE = (255, 255, 255, 255)
PAPER = (238, 242, 245, 255)
SLATE = (85, 103, 122, 255)
SS = 4  # supersampling for smooth edges

BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'


def font(path, size):
    return ImageFont.truetype(path, size * SS)


def sim(draw, cx, cy, w, fill=YELLOW, chip=NAVY):
    """SIM card with a cut corner and a chip, centred on (cx, cy), width w (already scaled)."""
    h = w * 1.28
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    r = w * 0.10
    cut = w * 0.30
    # body: rounded rectangle, then knock out the top-right corner as a diagonal
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)
    draw.polygon([(x1 - cut, y0 - 2), (x1 + 2, y0 - 2), (x1 + 2, y0 + cut)], fill=(0, 0, 0, 0))
    # chip
    cw, ch = w * 0.46, w * 0.40
    ccx, ccy = cx, cy + h * 0.10
    c0 = [ccx - cw / 2, ccy - ch / 2, ccx + cw / 2, ccy + ch / 2]
    draw.rounded_rectangle(c0, radius=w * 0.05, fill=chip)
    lw = max(2, int(w * 0.025))
    gap = fill
    draw.line([(ccx, c0[1]), (ccx, c0[3])], fill=gap, width=lw)
    for f in (1 / 3, 2 / 3):
        y = c0[1] + ch * f
        draw.line([(c0[0], y), (ccx - lw, y)], fill=gap, width=lw)
        draw.line([(ccx + lw, y), (c0[2], y)], fill=gap, width=lw)


def sim_layer(size, w_frac, bg=None):
    S = size * SS
    img = Image.new('RGBA', (S, S), bg or (0, 0, 0, 0))
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sim(ImageDraw.Draw(layer), S / 2, S / 2, S * w_frac)
    img.alpha_composite(layer)
    return img.resize((size, size), Image.LANCZOS)


def save(img, name):
    path = os.path.join(ASSETS, name) if not name.startswith('store/') else os.path.join(HERE, name[6:])
    img.save(path)
    print('wrote', os.path.relpath(path, os.path.join(HERE, '..')), img.size)


# App icon (full bleed navy) and Play Store icon (512, Play rounds the corners itself)
save(sim_layer(1024, 0.42, NAVY), 'icon.png')
save(sim_layer(512, 0.42, NAVY), 'store/play-icon-512.png')
# Adaptive icon foreground: transparent, artwork inside the safe zone
save(sim_layer(1024, 0.30), 'adaptive-icon.png')
# Splash artwork (shown on navy)
save(sim_layer(1024, 0.26), 'splash.png')

# Feature graphic 1024x500: brand on the left, a boarding-pass plan on the right
W, H = 1024, 500
S = SS
fg = Image.new('RGBA', (W * S, H * S), NAVY)
d = ImageDraw.Draw(fg)
d.text((64 * S, 150 * S), 'YRH eSIM', font=font(BOLD, 58), fill=WHITE)
d.text((66 * S, 236 * S), 'Mobile data for your trip,', font=font(REG, 30), fill=(169, 188, 205, 255))
d.text((66 * S, 278 * S), 'ready in minutes.', font=font(REG, 30), fill=(169, 188, 205, 255))
d.text((66 * S, 344 * S), '200+ countries', font=font(BOLD, 26), fill=YELLOW)

# ticket
tx0, ty0, tx1, ty1 = 560 * S, 120 * S, 960 * S, 380 * S
d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=22 * S, fill=WHITE)
tear = 790 * S
notch = 14 * S
d.ellipse([tear - notch, ty0 - notch, tear + notch, ty0 + notch], fill=NAVY)
d.ellipse([tear - notch, ty1 - notch, tear + notch, ty1 + notch], fill=NAVY)
y = ty0 + 30 * S
while y < ty1 - 30 * S:
    d.rounded_rectangle([tear - 2 * S, y, tear + 2 * S, y + 12 * S], radius=2 * S, fill=(213, 221, 229, 255))
    y += 22 * S
d.text((tx0 + 34 * S, ty0 + 52 * S), 'Spain', font=font(REG, 24), fill=SLATE)
d.text((tx0 + 32 * S, ty0 + 88 * S), '3 GB', font=font(BOLD, 64), fill=NAVY)
d.text((tx0 + 34 * S, ty0 + 178 * S), '30 days', font=font(REG, 26), fill=SLATE)
d.rounded_rectangle([tear + 26 * S, ty0 + 102 * S, tx1 - 26 * S, ty0 + 158 * S], radius=12 * S, fill=YELLOW)
bf = font(BOLD, 24)
bw = d.textlength('Buy', font=bf)
d.text(((tear + tx1) / 2 - bw / 2, ty0 + 112 * S), 'Buy', font=bf, fill=NAVY)
save(fg.resize((W, H), Image.LANCZOS).convert('RGB'), 'store/feature-graphic-1024x500.png')
