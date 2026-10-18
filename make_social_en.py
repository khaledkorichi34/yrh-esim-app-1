"""English social posts for YRH eSIM (replaces the remaining Arabic posts from Oct 18 22:00).
Same 1080x1350 look as the Arabic set, left-to-right, Poppins.
Files: social/YYYY-MM-DD-HH.jpg/.json (read by the Make "Social daily post" scenario).
Run: python3 make_social_en.py"""
from PIL import Image, ImageDraw, ImageFont
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf'
RAW = 'https://raw.githubusercontent.com/khaledkorichi34/yrh-esim-app-1/pinterest-assets/social/'
SHOP = 'https://yrh.ai/products/'
WA = '+34 642 377 474'
OFFER = '🎁 30% off your first eSIM with code AHLAN30 (until Oct 31)'

SS = 2
W, H = 1080, 1350
NAVY = (16, 34, 51)
NAVY_SOFT = (27, 52, 74)
YELLOW = (255, 201, 60)
WHITE = (255, 255, 255)
PAPER = (238, 242, 245)
MUTED = (169, 188, 205)
SLATE = (85, 103, 122)
LINE = (208, 216, 224)


def f(weight, size):
    return ImageFont.truetype(F % weight, int(size * SS))


def s(v):
    return int(round(v * SS))


def t(d, xy, txt, fnt, fill, anchor='la'):
    d.text((s(xy[0]), s(xy[1])), txt, font=fnt, fill=fill, anchor=anchor)


def tw(d, txt, fnt):
    return d.textlength(txt, font=fnt) / SS


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if tw(d, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def sim(d, cx, cy, w):
    cx, cy, w = s(cx), s(cy), s(w)
    h = w * 1.28
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    cut = w * 0.30
    d.rounded_rectangle([x0, y0, x1, y1], radius=w * 0.10, fill=YELLOW)
    d.polygon([(x1 - cut, y0 - 2), (x1 + 2, y0 - 2), (x1 + 2, y0 + cut)], fill=NAVY)
    cw, ch = w * 0.46, w * 0.40
    ccy = cy + h * 0.10
    d.rounded_rectangle([cx - cw / 2, ccy - ch / 2, cx + cw / 2, ccy + ch / 2], radius=w * 0.05, fill=NAVY)


def base():
    img = Image.new('RGB', (W * SS, H * SS), NAVY)
    d = ImageDraw.Draw(img)
    for r in (520, 720, 920):
        d.ellipse([s(W - r), s(-r + 140), s(W + r), s(r + 140)], outline=NAVY_SOFT, width=s(3))
    sim(d, 84, 84, 34)
    t(d, (116, 86), 'YRH eSIM', f('Bold', 34), WHITE, 'lm')
    t(d, (W - 70, 88), 'TRAVEL DATA', f('Medium', 22), MUTED, 'rm')
    return img, d


def footer(d):
    items = ['eSIM by email in minutes', 'No roaming bills', 'Keep your number']
    fnt = f('Medium', 25)
    gap = 44
    widths = [tw(d, x, fnt) for x in items]
    x = (W - sum(widths) - gap * (len(items) - 1)) / 2
    for i, (txt, w) in enumerate(zip(items, widths)):
        t(d, (x, 1236), txt, fnt, WHITE, 'lm')
        x += w
        if i < len(items) - 1:
            cx = x + gap / 2
            d.ellipse([s(cx - 4), s(1232), s(cx + 4), s(1240)], fill=YELLOW)
            x += gap
    t(d, (W / 2, 1296), 'Data only (no calls/SMS). Needs an unlocked, eSIM-compatible phone.', f('Regular', 21), MUTED, 'mm')


def offer(kicker, title, sub, code, plans):
    img, d = base()
    L = 72
    t(d, (L, 210), kicker.upper(), f('Bold', 26), YELLOW)
    fnt = f('Bold', 92)
    y = 252
    for ln in wrap(d, title, fnt, W - 150):
        t(d, (L - 4, y), ln, fnt, WHITE)
        y += 104
    y += 34
    for ln in wrap(d, sub, f('Regular', 34), W - 150):
        t(d, (L, y), ln, f('Regular', 34), MUTED)
        y += 48
    x0, x1, y1 = 72, W - 72, 1160
    row_h = 104
    y0 = y1 - 40 - row_h * len(plans) - 150
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(36), fill=PAPER)
    t(d, (x0 + 50, y0 + 44), 'DESTINATION', f('Medium', 20), SLATE)
    t(d, (x0 + 46, y0 + 66), code, f('Bold', 76), NAVY)
    t(d, (x1 - 50, y0 + 44), 'FROM', f('Medium', 20), SLATE, 'ra')
    t(d, (x1 - 50, y0 + 74), '€' + plans[0][2], f('Bold', 66), NAVY, 'ra')
    perf = y0 + 170
    xx = x0 + 40
    while xx < x1 - 40:
        d.line([(s(xx), s(perf)), (s(xx + 14), s(perf))], fill=LINE, width=s(3))
        xx += 26
    ry = perf + 20
    for i, (gb, days, price) in enumerate(plans):
        cy = ry + row_h * i + row_h / 2
        t(d, (x0 + 50, cy), gb, f('Bold', 42), NAVY, 'lm')
        t(d, (x0 + 50 + tw(d, gb, f('Bold', 42)) + 22, cy + 3), days, f('Regular', 30), SLATE, 'lm')
        t(d, (x1 - 50, cy), '€' + price, f('Bold', 40), NAVY, 'rm')
        if i < len(plans) - 1:
            d.line([(s(x0 + 50), s(cy + row_h / 2)), (s(x1 - 50), s(cy + row_h / 2))], fill=LINE, width=s(2))
    footer(d)
    return img


def tip(kicker, title, points):
    img, d = base()
    L = 72
    t(d, (L, 210), kicker.upper(), f('Bold', 26), YELLOW)
    fnt = f('Bold', 80)
    y = 252
    for ln in wrap(d, title, fnt, W - 150):
        t(d, (L - 4, y), ln, fnt, WHITE)
        y += 92
    y += 46
    x0, x1 = 72, W - 72
    box_h = min(190, (1170 - y - 20 * (len(points) - 1)) / len(points))
    for i, p in enumerate(points):
        d.rounded_rectangle([s(x0), s(y), s(x1), s(y + box_h)], radius=s(30), fill=PAPER)
        cy = y + box_h / 2
        d.ellipse([s(x0 + 44), s(cy - 42), s(x0 + 128), s(cy + 42)], fill=NAVY)
        t(d, (x0 + 86, cy + 2), str(i + 1), f('Bold', 42), YELLOW, 'mm')
        pf = f('Medium', 32)
        lines = wrap(d, p, pf, x1 - x0 - 200)
        ly = cy - (len(lines) - 1) * 22
        for ln in lines:
            t(d, (x0 + 160, ly), ln, pf, NAVY, 'lm')
            ly += 44
        y += box_h + 20
    footer(d)
    return img


TAGS_IG = '#eSIM #travelesim #esimtravel #traveltips #Algeria #Morocco #Tunisia #Spain #roaming #travelhacks'
TAGS_FB = '#eSIM #travelesim #traveltips #roaming'


def caption(body, handle):
    body = body + '\n\n' + OFFER
    link = SHOP + handle if handle else 'https://yrh.ai'
    ig = body + '\n\n🔗 Link in bio · 💬 WhatsApp ' + WA + '\n\n' + TAGS_IG
    fb = body + '\n\n🛒 ' + link + '\n💬 WhatsApp ' + WA + '\n\n' + TAGS_FB
    return ig, fb


def save(stem, name, img, body, handle=None):
    ig, fb = caption(body, handle)
    out = os.path.join(HERE, 'social')
    img.resize((W, H), Image.LANCZOS).save(os.path.join(out, stem + '.jpg'), quality=90)
    with open(os.path.join(out, stem + '.json'), 'w', encoding='utf-8') as fh:
        json.dump({'date': stem[:10], 'name': name, 'image': RAW + stem + '.jpg', 'ig': ig, 'fb': fb},
                  fh, ensure_ascii=False, indent=1)
    print(stem, name)


def plan_lines(plans):
    return '\n'.join('• %s · %s · €%s' % p for p in plans)


def O(stem, name, handle, kicker, title, sub, code, plans, intro):
    body = intro + '\n\n' + plan_lines(plans) + '\n\neSIM by email in minutes · Keep your number · Data only'
    save(stem, name, offer(kicker, title, sub, code, plans), body, handle)


def T(stem, name, kicker, title, points, intro, handle=None, numbered=True):
    mark = (lambda i: '%d. ' % (i + 1)) if numbered else (lambda i: '• ')
    body = intro + '\n\n' + '\n'.join(mark(i) + p for i, p in enumerate(points))
    save(stem, name, tip(kicker, title, points), body, handle)


def promo(stem, name, handle, title, sub, code, plans, intro):
    off = [(gb, d, '%.2f' % (float(p) * 0.7)) for gb, d, p in plans]
    lines = '\n'.join('• %s · %s · €%s → about €%s with AHLAN30' % (gb, d, p, o[2]) for (gb, d, p), o in zip(plans, off))
    body = intro + '\n\n' + lines + '\n\nDiscounted prices are approximate and shown at checkout with the code.'
    save(stem, name, offer('30% off with code AHLAN30', title, sub, code, off), body, handle)


DAYS7, DAYS15, DAYS30 = '7 days', '15 days', '30 days'
DZ_LONG = [('3GB', DAYS30, '5.57'), ('5GB', DAYS30, '8.73'), ('10GB', DAYS30, '15.33')]
FR = [('1GB', DAYS7, '3.00'), ('3GB', DAYS15, '3.43'), ('10GB', DAYS30, '9.48')]
IT = [('1GB', DAYS7, '3.00'), ('3GB', DAYS15, '3.03'), ('10GB', DAYS30, '8.63')]
MA30 = [('1GB', DAYS7, '3.00'), ('3GB', DAYS30, '6.74'), ('5GB', DAYS30, '10.12')]
TN30 = [('3GB', DAYS30, '5.45'), ('5GB', DAYS30, '8.53'), ('10GB', DAYS30, '15.57')]
ES = [('1GB', DAYS7, '3.00'), ('3GB', DAYS15, '3.03'), ('10GB', DAYS30, '8.63')]


def build():
    # Oct 18, 22:00
    T('2026-10-18-22', 'Android install', 'For Android users', 'Install an eSIM on Android',
      ['Settings > Connections > SIM manager', 'Add eSIM > scan the QR code from your email',
       'When you land, set it as your mobile data line'],
      'Samsung or another Android phone? Here is how 👇', 'dz_package')
    # Oct 19
    T('2026-10-19-09', 'Question', 'Question of the day', 'When is your next trip?',
      ['This month', 'Over the winter holidays', 'Next summer'],
      'Quick question 👇 When are you travelling next? Reply with the number in the comments.')
    T('2026-10-19-11', 'WhatsApp', 'Most asked question', 'Will WhatsApp keep my number?',
      ['Yes. The eSIM is for data only, WhatsApp stays on your number',
       'Your main SIM stays in the phone for bank codes',
       'Call and message family on WhatsApp as usual'],
      'The question we get the most 👇 Your number does not change.', 'dz_package', numbered=False)
    T('2026-10-19-15', 'Buy early', 'Travel tip', 'Buy your eSIM a few days before',
      ['Most plans start counting when you first connect abroad',
       'Installing early avoids airport Wi-Fi trouble', 'Check the activation window on the plan page'],
      'A tip so you are not stuck at the airport 👇', 'dz_package', numbered=False)
    promo('2026-10-19-19', 'Promo Italy', 'it_package', 'Italy, 30% off', 'On your first eSIM from us', 'IT', IT,
          'Travelling to Italy 🇮🇹? Your first eSIM is 30% off with code AHLAN30.')
    T('2026-10-19-22', 'Contact', 'Talk to us', 'Questions? We are here',
      ['WhatsApp ' + WA, 'Reply to any email from our store', 'Visit yrh.ai'],
      'Any question before you buy? Message us 👇', 'dz_package', numbered=False)
    # Oct 20 - 26, 11:00
    O('2026-10-20-11', 'France', 'fr_package', 'Visiting France?', 'France data from the moment you land',
      'Prepaid plans from €3', 'FR', FR, 'Travelling to France 🇫🇷 for family or work? Set up your data before you fly and skip roaming bills.')
    O('2026-10-21-11', 'Algeria long stay', 'dz_package', 'Long stay back home?', 'Algeria plans for a whole month',
      'For long holidays and summer visits', 'DZ', DZ_LONG,
      'Going to Algeria 🇩🇿 for a while? 30-day plans for maps, WhatsApp and video calls with the family.')
    O('2026-10-22-11', 'Italy', 'it_package', 'Trip to Italy?', 'Italy data at a light price',
      'Prepaid eSIM, sent by email', 'IT', IT, 'Travelling to Italy 🇮🇹? Get your eSIM before you fly and be online when you land.')
    T('2026-10-23-11', 'How it works', 'How it works', 'Travel data in 3 steps',
      ['Pick your destination and a data plan', 'Your eSIM arrives by email, usually within minutes',
       'Scan the QR code and go online when you land'],
      'No shop, no plastic SIM, no waiting 👇')
    O('2026-10-24-11', 'Morocco 30 days', 'ma_package', 'Longer stay in Morocco?', 'Morocco plans for your stay',
      'From one week to a full month', 'MA', MA30, 'One week or one month in Morocco 🇲🇦? Pick the plan that fits your stay.')
    T('2026-10-25-11', 'Dual SIM', 'Important tip', 'Keep your main SIM switched on',
      ['Use the eSIM for mobile data only', 'Keep your main SIM to receive bank verification codes',
       'Turn off data roaming on your main SIM to avoid charges'],
      'Get your bank codes without paying for roaming 👇', 'dz_package')
    O('2026-10-26-11', 'Tunisia 30 days', 'tn_package', 'Tunisia this winter?', 'Tunisia data for your holiday',
      'Prepaid plans, no surprises', 'TN', TN30, 'Winter holiday in Tunisia 🇹🇳? Pick a 30-day plan and stay online the whole trip.')


if __name__ == '__main__':
    build()
