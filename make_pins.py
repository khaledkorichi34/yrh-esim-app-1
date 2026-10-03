"""Draws the Pinterest pins for YRH eSIM (1000x1500).
Run: python3 make_pins.py  (needs Pillow and the Poppins fonts)
Prices are the store prices on the day the pins were made."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf'
SS = 2
W, H = 1000, 1500

NAVY = (16, 34, 51)
NAVY_SOFT = (27, 52, 74)
YELLOW = (255, 201, 60)
WHITE = (255, 255, 255)
PAPER = (238, 242, 245)
MUTED = (169, 188, 205)
SLATE = (85, 103, 122)
LINE = (208, 216, 224)


def font(weight, size):
    return ImageFont.truetype(F % weight, int(size * SS))


def s(v):
    return int(round(v * SS))


def text(d, xy, txt, f, fill, anchor='la', spacing=0):
    """Draws text; with spacing > 0 it letter-spaces (in 1x pixels)."""
    x, y = s(xy[0]), s(xy[1])
    if not spacing:
        d.text((x, y), txt, font=f, fill=fill, anchor=anchor)
        return
    widths = [d.textlength(ch, font=f) for ch in txt]
    total = sum(widths) + s(spacing) * (len(txt) - 1)
    if anchor[0] == 'r':
        x -= total
    elif anchor[0] == 'm':
        x -= total / 2
    for ch, w in zip(txt, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor='l' + anchor[1])
        x += w + s(spacing)


def sim(d, cx, cy, w, fill=YELLOW, chip=NAVY, bg=NAVY):
    cx, cy, w = s(cx), s(cy), s(w)
    h = w * 1.28
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    cut = w * 0.30
    d.rounded_rectangle([x0, y0, x1, y1], radius=w * 0.10, fill=fill)
    d.polygon([(x1 - cut, y0 - 2), (x1 + 2, y0 - 2), (x1 + 2, y0 + cut)], fill=bg)
    cw, ch = w * 0.46, w * 0.40
    ccy = cy + h * 0.10
    c0 = [cx - cw / 2, ccy - ch / 2, cx + cw / 2, ccy + ch / 2]
    d.rounded_rectangle(c0, radius=w * 0.05, fill=chip)
    lw = max(2, int(w * 0.03))
    d.line([(cx, c0[1]), (cx, c0[3])], fill=fill, width=lw)
    for f_ in (1 / 3, 2 / 3):
        y = c0[1] + ch * f_
        d.line([(c0[0], y), (cx - lw, y)], fill=fill, width=lw)
        d.line([(cx + lw, y), (c0[2], y)], fill=fill, width=lw)


def base():
    img = Image.new('RGB', (W * SS, H * SS), NAVY)
    d = ImageDraw.Draw(img)
    # flight-path arcs in the background
    for r in (520, 700, 880):
        d.ellipse([s(1000 - r), s(-r + 120), s(1000 + r), s(r + 120)], outline=NAVY_SOFT, width=s(3))
    # brand row
    sim(d, 92, 86, 34)
    text(d, (124, 88), 'YRH eSIM', font('Bold', 34), WHITE, 'lm')
    text(d, (930, 88), 'TRAVEL DATA', font('Medium', 20), MUTED, 'rm', spacing=4)
    return img, d


def footer(d, note):
    items = ['eSIM by email in minutes', 'No roaming bills', 'Keep your number']
    f = font('Medium', 25)
    gap, dot = 44, 8
    widths = [d.textlength(t, font=f) / SS for t in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = (W - total) / 2
    for i, (t, w) in enumerate(zip(items, widths)):
        text(d, (x, 1366), t, f, WHITE, 'lm')
        x += w
        if i < len(items) - 1:
            cx = x + gap / 2
            d.ellipse([s(cx - dot / 2), s(1366 - dot / 2), s(cx + dot / 2), s(1366 + dot / 2)], fill=YELLOW)
            x += gap
    text(d, (W / 2, 1436), note, font('Regular', 19), MUTED, 'mm')


def fit(d, txt, weight, max_size, min_size, max_w):
    size = max_size
    while size > min_size and d.textlength(txt, font=font(weight, size)) / SS > max_w:
        size -= 2
    return size


def ticket(d, x0, y0, x1, y1, perf_y):
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(36), fill=PAPER)
    r = 22
    for x in (x0, x1):
        d.ellipse([s(x - r), s(perf_y - r), s(x + r), s(perf_y + r)], fill=NAVY)
    x = x0 + r + 16
    while x < x1 - r - 16:
        d.line([(s(x), s(perf_y)), (s(x + 14), s(perf_y))], fill=LINE, width=s(3))
        x += 26


def destination_pin(code, name, lines, min_price, plans):
    img, d = base()
    text(d, (72, 236), 'eSIM FOR', font('Bold', 26), YELLOW, 'lm', spacing=6)
    y = 276
    if len(lines) == 1:
        size = fit(d, lines[0], 'Bold', 168, 96, 856)
    else:
        size = min(fit(d, ln, 'Bold', 120, 80, 856) for ln in lines)
    f = font('Bold', size)
    for ln in lines:
        text(d, (66, y), ln, f, WHITE, 'la')
        y += size * 1.08
    y += size * 0.30 + 10  # room for descenders on the last line
    text(d, (72, y), 'Mobile data from the moment you land.', font('Regular', 33), MUTED, 'la')

    x0, x1 = 70, 930
    y0, y1 = 660, 1290
    perf = 880
    ticket(d, x0, y0, x1, y1, perf)
    # ticket header: destination code and "from" price
    text(d, (x0 + 52, y0 + 44), 'DESTINATION', font('Medium', 19), SLATE, 'la', spacing=3)
    text(d, (x0 + 46, y0 + 62), code, font('Bold', 118), NAVY, 'la')
    text(d, (x1 - 52, y0 + 44), 'FROM', font('Medium', 19), SLATE, 'ra', spacing=3)
    pf = font('Bold', 78)
    ptxt = '€' + min_price
    pw = d.textlength(ptxt, font=pf) / SS
    d.rounded_rectangle([s(x1 - 52 - pw - 4), s(y0 + 152), s(x1 - 48), s(y0 + 176)], radius=s(6), fill=YELLOW)
    text(d, (x1 - 52, y0 + 76), ptxt, pf, NAVY, 'ra')
    # plans
    row_h = 118
    ry = perf + 36
    for i, (gb, days, price) in enumerate(plans):
        cy = ry + row_h * i + row_h / 2
        gf = font('Bold', 42)
        text(d, (x0 + 52, cy), gb, gf, NAVY, 'lm')
        gw = d.textlength(gb, font=gf) / SS
        text(d, (x0 + 52 + gw + 20, cy + 2), days, font('Regular', 30), SLATE, 'lm')
        text(d, (x1 - 52, cy), '€' + price, font('Bold', 42), NAVY, 'rm')
        if i < len(plans) - 1:
            d.line([(s(x0 + 52), s(cy + row_h / 2)), (s(x1 - 52), s(cy + row_h / 2))], fill=LINE, width=s(2))
    footer(d, 'Data only. Needs an unlocked, eSIM-compatible phone. Prices at time of posting.')
    return img


def steps_pin():
    img, d = base()
    text(d, (72, 236), 'HOW IT WORKS', font('Bold', 26), YELLOW, 'lm', spacing=6)
    f = font('Bold', 108)
    text(d, (66, 276), 'Travel data', f, WHITE, 'la')
    text(d, (66, 276 + 116), 'in 3 steps', f, WHITE, 'la')
    text(d, (72, 544), 'No shop, no plastic SIM, no waiting.', font('Regular', 33), MUTED, 'la')
    steps = [
        ('Choose', 'Pick your destination', 'and a data plan.'),
        ('Pay', 'Your eSIM arrives by email,', 'usually within minutes.'),
        ('Connect', 'Scan the QR code and go', 'online when you land.'),
    ]
    x0, x1 = 70, 930
    y = 660
    h = 196
    for i, (title, l1, l2) in enumerate(steps):
        d.rounded_rectangle([s(x0), s(y), s(x1), s(y + h)], radius=s(30), fill=PAPER)
        cy = y + h / 2
        d.ellipse([s(x0 + 40), s(cy - 46), s(x0 + 132), s(cy + 46)], fill=NAVY)
        text(d, (x0 + 86, cy + 2), str(i + 1), font('Bold', 46), YELLOW, 'mm')
        text(d, (x0 + 168, cy - 50), title, font('Bold', 40), NAVY, 'lm')
        text(d, (x0 + 168, cy + 2), l1, font('Regular', 28), SLATE, 'lm')
        text(d, (x0 + 168, cy + 40), l2, font('Regular', 28), SLATE, 'lm')
        y += h + 21
    footer(d, 'Data only. Needs an unlocked, eSIM-compatible phone. 200+ destinations.')
    return img


DESTS = [
    ('ES', 'spain', ['Spain'], '1.25', ('1.25', '3.97', '6.82')),
    ('TR', 'turkey', ['Turkey'], '0.85', ('1.09', '3.85', '5.22')),
    ('AE', 'uae', ['United Arab', 'Emirates'], '0.85', ('3.03', '12.40', '22.15')),
    ('US', 'usa', ['United', 'States'], '0.85', ('1.75', '5.50', '10.35')),
    ('FR', 'france', ['France'], '0.85', ('1.45', '4.45', '7.45')),
    ('IT', 'italy', ['Italy'], '1.25', ('1.25', '3.97', '6.82')),
    ('GB', 'uk', ['United', 'Kingdom'], '0.85', ('1.25', '3.97', '6.82')),
    ('JP', 'japan', ['Japan'], '0.85', ('1.45', '4.45', '7.45')),
]


def save(img, name):
    out = img.resize((W, H), Image.LANCZOS)
    path = os.path.join(HERE, name)
    out.save(path, 'PNG', optimize=True)
    print('wrote', name, os.path.getsize(path) // 1024, 'KB')


if __name__ == '__main__':
    save(steps_pin(), 'pin-how-it-works.png')
    for code, slug, lines, mn, (p1, p5, p10) in DESTS:
        plans = [('1 GB', '7 days', p1), ('5 GB', '30 days', p5), ('10 GB', '30 days', p10)]
        save(destination_pin(code, slug, lines, mn, plans), 'pin-%s.png' % slug)
