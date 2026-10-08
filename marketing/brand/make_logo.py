"""Draws the YRH eSIM logo files. Run: python3 marketing/brand/make_logo.py /path/to/poppins-fonts"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = sys.argv[1] if len(sys.argv) > 1 else '.'
NAVY = (16, 34, 51, 255)
YELLOW = (255, 201, 60, 255)
WHITE = (255, 255, 255, 255)
SS = 4


def sim(d, cx, cy, w, fill, chip, knock):
    """SIM card with a cut corner and a chip, centred on (cx, cy)."""
    h = w * 1.28
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    cut = w * 0.30
    d.rounded_rectangle([x0, y0, x1, y1], radius=w * 0.10, fill=fill)
    d.polygon([(x1 - cut, y0 - 2), (x1 + 2, y0 - 2), (x1 + 2, y0 + cut)], fill=knock)
    cw, ch = w * 0.46, w * 0.40
    ccy = cy + h * 0.10
    c0 = [cx - cw / 2, ccy - ch / 2, cx + cw / 2, ccy + ch / 2]
    d.rounded_rectangle(c0, radius=w * 0.05, fill=chip)
    lw = max(2, int(w * 0.03))
    d.line([(cx, c0[1]), (cx, c0[3])], fill=fill, width=lw)
    for f in (1 / 3, 2 / 3):
        y = c0[1] + ch * f
        d.line([(c0[0], y), (cx - lw, y)], fill=fill, width=lw)
        d.line([(cx + lw, y), (c0[2], y)], fill=fill, width=lw)


def profile(size=1080):
    """Square for profile pictures. The mark stays inside the circle that Instagram cuts out."""
    S = size * SS
    img = Image.new('RGBA', (S, S), NAVY)
    sim(ImageDraw.Draw(img), S / 2, S / 2, S * 0.34, YELLOW, NAVY, NAVY)
    return img.resize((size, size), Image.LANCZOS).convert('RGB')


def wordmark(text_color, background=None, chip=NAVY, height=360):
    """Mark and name side by side."""
    H = height * SS
    f = ImageFont.truetype(os.path.join(FONTS, 'Poppins-Bold.ttf'), int(H * 0.44))
    probe = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    tw = probe.textlength('YRH eSIM', font=f)
    mark_w = H * 0.40
    pad = H * 0.22
    gap = H * 0.16
    W = int(pad + mark_w + gap + tw + pad)
    bg = background or (0, 0, 0, 0)
    img = Image.new('RGBA', (W, H), bg)
    d = ImageDraw.Draw(img)
    sim(d, pad + mark_w / 2, H / 2, mark_w, YELLOW, chip, bg)
    d.text((pad + mark_w + gap, H / 2), 'YRH eSIM', font=f, fill=text_color, anchor='lm')
    return img.resize((W // SS, height), Image.LANCZOS)


def save(img, name):
    img.save(os.path.join(HERE, name))
    print('wrote', name, img.size)


save(profile(), 'yrh-esim-logo-profile.png')
save(wordmark(WHITE, NAVY), 'yrh-esim-logo-on-navy.png')
save(wordmark(NAVY), 'yrh-esim-logo-transparent.png')
