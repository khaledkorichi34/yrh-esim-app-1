"""Prepares today's Pinterest pins for YRH eSIM.

Each run:
  1. reads the public catalog of the store (current plans and prices),
  2. picks the next destinations that have no pin yet (PER_DAY of them),
  3. draws one 1000x1500 pin per destination with today's prices,
  4. writes days/<date>.json, which the Make scenario "Pinterest daily pins"
     reads later the same day and publishes.

Nothing here talks to Pinterest and there are no secrets in this script.

Run by .github/workflows/pinterest-daily.yml. To try it on a computer:
  python3 daily.py --out /tmp/assets --fonts /path/to/poppins --catalog-file products.json
"""
import argparse
import datetime
import itertools
import json
import os
import re
import urllib.request
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

SHOP_URL = 'https://07eqi1-zk.myshopify.com'
ASSETS_URL = 'https://raw.githubusercontent.com/khaledkorichi34/yrh-esim-app-1/pinterest-assets'
BOARD_ID = '887631476498021166'  # "Travel eSIM - Stay Connected Abroad"
PER_DAY = 5
TIMEZONE = 'Europe/Madrid'

# Published by hand before this script existed.
ALREADY_PUBLISHED = ['es_package', 'tr_package', 'jp_package', 'us_package',
                     'ae_package', 'fr_package', 'it_package', 'gb_package']

# Destinations people travel to most go first; everything else follows A to Z.
PRIORITY = [
    'th', 'de', 'gr', 'pt', 'eu-42', 'sa', 'eg', 'ma', 'id', 'kr',
    'cn', 'sg', 'my', 'vn', 'au', 'ca', 'mx', 'nl', 'ch', 'at',
    'hr', 'ie', 'in', 'ph', 'br', 'qa', 'hk', 'tw', 'be', 'cz',
    'pl', 'se', 'no', 'dk', 'hu', 'is', 'nz', 'za', 'ke', 'tz',
    'lk', 'mv', 'jo', 'cy', 'mt', 'ar', 'cl', 'pe', 'co', 'do',
    'cr', 'gl-120', 'usca-2', 'sea-8', 'me-13', 'kw', 'bh', 'om', 'tn', 'dz',
]

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

FONT_DIR = '.'


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, 'Poppins-%s.ttf' % weight), int(size * SS))


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
    for r in (520, 700, 880):  # flight-path arcs in the background
        d.ellipse([s(1000 - r), s(-r + 120), s(1000 + r), s(r + 120)], outline=NAVY_SOFT, width=s(3))
    sim(d, 92, 86, 34)
    text(d, (124, 88), 'YRH eSIM', font('Bold', 34), WHITE, 'lm')
    text(d, (930, 88), 'TRAVEL DATA', font('Medium', 20), MUTED, 'rm', spacing=4)
    return img, d


def footer(d, note):
    items = ['eSIM by email in minutes', 'No roaming bills', 'Keep your number']
    f = font('Medium', 25)
    gap, dot = 44, 8
    widths = [d.textlength(t, font=f) / SS for t in items]
    x = (W - (sum(widths) + gap * (len(items) - 1))) / 2
    for i, (t, w) in enumerate(zip(items, widths)):
        text(d, (x, 1366), t, f, WHITE, 'lm')
        x += w
        if i < len(items) - 1:
            cx = x + gap / 2
            d.ellipse([s(cx - dot / 2), s(1366 - dot / 2), s(cx + dot / 2), s(1366 + dot / 2)], fill=YELLOW)
            x += gap
    text(d, (W / 2, 1436), note, font('Regular', 19), MUTED, 'mm')


def ticket(d, x0, y0, x1, y1, perf_y):
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(36), fill=PAPER)
    r = 22
    for x in (x0, x1):
        d.ellipse([s(x - r), s(perf_y - r), s(x + r), s(perf_y + r)], fill=NAVY)
    x = x0 + r + 16
    while x < x1 - r - 16:
        d.line([(s(x), s(perf_y)), (s(x + 14), s(perf_y))], fill=LINE, width=s(3))
        x += 26


def headline_layout(d, name, max_w=856, max_h=300, max_size=168, min_size=54):
    """Splits the name over 1 to 3 lines and returns (lines, size) with the largest type that fits."""
    words = name.split()
    best = None
    for n in range(1, min(3, len(words)) + 1):
        for cuts in itertools.combinations(range(1, len(words)), n - 1):
            bounds = [0, *cuts, len(words)]
            lines = [' '.join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
            size = min(max_size, int(max_h / (n * 1.08 + 0.30)))
            while size > min_size and max(d.textlength(ln, font=font('Bold', size)) / SS for ln in lines) > max_w:
                size -= 2
            if best is None or size > best[1]:
                best = (lines, size)
    return best


def fit_size(d, txt, weight, max_size, min_size, max_w):
    size = max_size
    while size > min_size and d.textlength(txt, font=font(weight, size)) / SS > max_w:
        size -= 2
    return size


def draw_pin(dest):
    img, d = base()
    text(d, (72, 236), 'eSIM FOR', font('Bold', 26), YELLOW, 'lm', spacing=6)
    lines, size = headline_layout(d, dest['name'])
    f = font('Bold', size)
    y = 276
    for ln in lines:
        text(d, (66, y), ln, f, WHITE, 'la')
        y += size * 1.08
    y += size * 0.30 + 10  # room for descenders on the last line
    text(d, (72, y), 'Mobile data from the moment you land.', font('Regular', 33), MUTED, 'la')

    x0, x1 = 70, 930
    y0, y1 = 660, 1290
    perf = 880
    ticket(d, x0, y0, x1, y1, perf)

    # right: lowest price
    text(d, (x1 - 52, y0 + 44), 'FROM', font('Medium', 19), SLATE, 'ra', spacing=3)
    pf = font('Bold', 78)
    ptxt = '€' + dest['min_price']
    pw = d.textlength(ptxt, font=pf) / SS
    d.rounded_rectangle([s(x1 - 52 - pw - 4), s(y0 + 152), s(x1 - 48), s(y0 + 176)], radius=s(6), fill=YELLOW)
    text(d, (x1 - 52, y0 + 76), ptxt, pf, NAVY, 'ra')

    # left: country code, or number of places covered for regional plans
    left_w = (x1 - x0) - 104 - pw - 40
    if dest['regional']:
        text(d, (x0 + 52, y0 + 44), 'COVERAGE', font('Medium', 19), SLATE, 'la', spacing=3)
        big = str(dest['areas'])
        bf = font('Bold', 118)
        text(d, (x0 + 46, y0 + 62), big, bf, NAVY, 'la')
        bw = d.textlength(big, font=bf) / SS
        text(d, (x0 + 46 + bw + 16, y0 + 150), 'places', font('Regular', 34), SLATE, 'ls')
    else:
        text(d, (x0 + 52, y0 + 44), 'DESTINATION', font('Medium', 19), SLATE, 'la', spacing=3)
        code_size = fit_size(d, dest['code'], 'Bold', 118, 60, left_w)
        text(d, (x0 + 46, y0 + 62), dest['code'], font('Bold', code_size), NAVY, 'la')

    plans = dest['plans']
    area_top = perf + 36
    row_h = (y1 - 20 - area_top) / max(len(plans), 1)
    row_h = min(row_h, 150)
    for i, p in enumerate(plans):
        cy = area_top + row_h * i + row_h / 2
        gf = font('Bold', 42)
        text(d, (x0 + 52, cy), p['size'], gf, NAVY, 'lm')
        gw = d.textlength(p['size'], font=gf) / SS
        text(d, (x0 + 52 + gw + 20, cy + 2), p['days'], font('Regular', 30), SLATE, 'lm')
        text(d, (x1 - 52, cy), '€' + p['price'], font('Bold', 42), NAVY, 'rm')
        if i < len(plans) - 1:
            d.line([(s(x0 + 52), s(cy + row_h / 2)), (s(x1 - 52), s(cy + row_h / 2))], fill=LINE, width=s(2))
    footer(d, 'Data only. Needs an unlocked, eSIM-compatible phone. Prices at time of posting.')
    return img.resize((W, H), Image.LANCZOS)


# ---------- catalog ----------

def fetch_catalog():
    products = []
    for page in range(1, 6):
        req = urllib.request.Request(
            '%s/products.json?limit=250&page=%d' % (SHOP_URL, page),
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 14) YRH-eSIM'})
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)['products']
        if not batch:
            break
        products += batch
    return products


def clean_name(title):
    name = re.sub(r'\s*eSIM$', '', title).strip()
    name = re.sub(r'(?<=\S)\(', ' (', name)
    # Regional plans carry a count in the title ("Europe (35 areas)", "Global139"). The pin shows the
    # count taken from the product's own list of supported places, so drop the one in the name.
    name = re.sub(r'\s*\(\s*\d+\+?\s*(areas|countries)\s*\)', '', name)
    name = re.sub(r'-?\d+$', '', name)
    return re.sub(r'\s+', ' ', name).strip()


def size_label(gb):
    if gb < 1:
        return '%d MB' % round(gb * 1000)
    return ('%g GB' % gb)


def parse_plans(product):
    """Standard plans of a product as dicts, from SKUs like ES_1_7 (country, GB, days)."""
    plans = []
    for v in product['variants']:
        if not v.get('available', True):
            continue
        m = re.fullmatch(r'[A-Za-z0-9-]+_(\d+(?:\.\d+)?)_(\d+)', v.get('sku') or '')
        if not m:
            continue
        gb, days = float(m.group(1)), int(m.group(2))
        plans.append({'gb': gb, 'ndays': days, 'price': v['price'], 'value': float(v['price']),
                      'size': size_label(gb), 'days': '%d day%s' % (days, '' if days == 1 else 's')})
    return plans


def pick_plans(plans):
    """Three plans to show: a small, a medium and a large one. Prefers 1 GB/7 d, 5 GB/30 d, 10 GB/30 d."""
    chosen = []

    def take(gb, days=None):
        cands = [p for p in plans if p['gb'] == gb and (days is None or p['ndays'] == days) and p not in chosen]
        if cands:
            chosen.append(min(cands, key=lambda p: p['value']))
            return True
        return False

    take(1, 7) or take(1)
    take(5, 30) or take(5) or take(3, 30) or take(3)
    take(10, 30) or take(10) or take(20, 30) or take(20)
    rest = sorted((p for p in plans if p not in chosen), key=lambda p: (p['gb'] < 1, p['value']))
    while len(chosen) < 3 and rest:
        chosen.append(rest.pop(0))
    return sorted(chosen, key=lambda p: (p['gb'], p['ndays']))


def supported_count(product):
    m = re.search(r'Supported Countries:</strong>\s*([^<]+)', product.get('body_html') or '')
    if not m:
        return None
    return len([c for c in m.group(1).split(',') if c.strip()])


def to_destination(product):
    handle = product['handle']
    key = handle[:-len('_package')] if handle.endswith('_package') else handle
    plans = parse_plans(product)
    if not plans:
        return None
    regional = not re.fullmatch(r'[a-z]{2}', key)
    areas = None
    if regional:
        areas = supported_count(product)
        if not areas or areas < 2:
            m = re.search(r'-(\d+)$', key)
            areas = int(m.group(1)) if m else None
        if not areas:
            return None
    all_prices = [(float(v['price']), v['price']) for v in product['variants'] if v.get('available', True)]
    return {
        'handle': handle, 'key': key, 'name': clean_name(product['title']),
        'code': key.upper(), 'regional': regional, 'areas': areas,
        'min_price': min(all_prices)[1], 'plans': pick_plans(plans),
    }


def ordered_handles(dests):
    by_key = {d['key']: d for d in dests}
    first = [by_key[k]['handle'] for k in PRIORITY if k in by_key]
    rest = sorted((d for d in dests if d['handle'] not in first), key=lambda d: d['name'].lower())
    return first + [d['handle'] for d in rest]


# ---------- pin text ----------

# Pinterest search reads the title and the first sentence most, so both lead with
# the words people type: "<country> eSIM", "SIM card for <country>", "travel data".
OPENERS = [
    'Looking for a SIM card for {name}? This prepaid {name} eSIM gives you mobile data without roaming fees.',
    '{name} eSIM for tourists: prepaid travel data that works from the moment you land.',
    'Travel data for {name} without a physical SIM: get a prepaid {name} eSIM before you fly.',
    'Need internet in {name}? A prepaid travel eSIM keeps maps, rides and messages working.',
]
REGION_OPENER = ('Regional eSIM for {name}: one prepaid travel data plan that works in {areas} places, '
                 'so you do not need a new SIM card in each country.')
CLOSER = (' Delivered by email in minutes, installed with a QR code, and your own number stays active.'
          ' Data only; needs an unlocked, eSIM-compatible phone.')
COMMON_TAGS = ['#esim', '#travelesim', '#traveltips', '#travelhacks', '#internationaltravel']


def pin_payload(dest, index, image_url):
    plans = ', '.join('%s for %s €%s' % (p['size'], p['days'], p['price']) for p in dest['plans'])
    alt_plans = ', '.join('%s for %s at %s euros' % (p['size'], p['days'], p['price']) for p in dest['plans'])
    name = dest['name']
    if dest['regional']:
        where = 'your whole trip' if name == 'Global' else name
        opener = REGION_OPENER.format(name=where, areas=dest['areas'])
        label = 'Global eSIM' if name == 'Global' else 'Regional eSIM for %s' % name
        title = '%s (%d places): Prepaid Travel Data from €%s' % (label, dest['areas'], dest['min_price'])
        tags = COMMON_TAGS + ['#backpacking', '#roaming']
    else:
        opener = OPENERS[index % len(OPENERS)].format(name=name)
        title = '%s eSIM: Prepaid Travel Data Plans from €%s' % (name, dest['min_price'])
        slug = re.sub(r'[^a-z]', '', name.lower())
        tags = ['#%stravel' % slug, '#%s' % slug] + COMMON_TAGS
    description = '%s Plans: %s.%s %s' % (opener, plans, CLOSER, ' '.join(tags))
    return {
        'board_id': BOARD_ID,
        'title': title[:100],
        'description': description[:800],
        'link': '%s/products/%s' % (SHOP_URL, dest['handle']),
        'alt_text': ('%s eSIM data plans: %s.' % (name, alt_plans))[:500],
        'media_source': {'source_type': 'image_url', 'url': image_url},
    }


# ---------- Facebook / Instagram ----------

# One post a day: the first destination of the day's pins, as a 4:5 JPEG
# (Instagram does not take the 2:3 pin) with captions for each network.

def flag(dest):
    if dest['regional'] or not re.fullmatch(r'[A-Z]{2}', dest['code']):
        return '🌍'
    return ''.join(chr(0x1F1E6 + ord(c) - 65) for c in dest['code'])


def social_captions(dest, index):
    name = dest['name']
    plan_lines = '\n'.join('• %s · %s · €%s' % (p['size'], p['days'], p['price']) for p in dest['plans'])
    if dest['regional']:
        where = 'your whole trip' if name == 'Global' else name
        opener = REGION_OPENER.format(name=where, areas=dest['areas'])
        head = '%s eSIM %s %d places, from €%s' % (name, flag(dest), dest['areas'], dest['min_price'])
        ig_tags = ['#esim', '#travelesim', '#esimtravel', '#backpacking', '#traveltips', '#travelhacks',
                   '#internationaltravel', '#digitalnomad', '#roaming', '#worldtravel']
        fb_tags = ['#esim', '#travelesim', '#backpacking', '#roaming']
    else:
        opener = OPENERS[index % len(OPENERS)].format(name=name)
        head = '%s eSIM %s from €%s – prepaid travel data' % (name, flag(dest), dest['min_price'])
        slug = re.sub(r'[^a-z]', '', name.lower())
        ig_tags = ['#%stravel' % slug, '#%s' % slug, '#esim', '#travelesim', '#esimtravel', '#traveltips',
                   '#travelhacks', '#internationaltravel', '#digitalnomad', '#roaming']
        fb_tags = ['#%stravel' % slug, '#esim', '#travelesim', '#traveltips']
    body = '%s\n\n%s\n\n%s\n\neSIM by email in minutes · Keep your number · Data only' % (head, opener, plan_lines)
    link = '%s/products/%s' % (SHOP_URL, dest['handle'])
    ig = '%s\n\n🔗 Link in bio · 💬 WhatsApp +34 642 377 474\n\n%s' % (body, ' '.join(ig_tags))
    fb = '%s\n\n🛒 %s\n💬 WhatsApp +34 642 377 474\n\n%s' % (body, link, ' '.join(fb_tags))
    return ig, fb


def write_social(out, date, dest):
    from PIL import Image
    pin = Image.open(os.path.join(out, 'pins', date, dest['key'] + '.png')).convert('RGB')
    img = Image.new('RGB', (1080, 1350), NAVY)
    img.paste(pin.resize((900, 1350), Image.LANCZOS), (90, 0))
    os.makedirs(os.path.join(out, 'social'), exist_ok=True)
    img.save(os.path.join(out, 'social', date + '.jpg'), 'JPEG', quality=90)
    index = int(datetime.date.fromisoformat(date).toordinal())
    ig, fb = social_captions(dest, index)
    with open(os.path.join(out, 'social', date + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'date': date, 'name': dest['name'],
                   'image': '%s/social/%s.jpg' % (ASSETS_URL, date), 'ig': ig, 'fb': fb},
                  f, ensure_ascii=False, indent=1)
    print('Social post for', date, ':', dest['name'])


# ---------- main ----------

def main():
    global FONT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='checkout of the pinterest-assets branch')
    ap.add_argument('--fonts', default='.', help='folder with Poppins-Bold/Medium/Regular.ttf')
    ap.add_argument('--catalog-file', help='saved products.json, instead of reading the store')
    ap.add_argument('--date', help='YYYY-MM-DD, default is today in Madrid')
    ap.add_argument('--per-day', type=int, default=PER_DAY)
    ap.add_argument('--redo', metavar='NAME', help='draw again, with current prices, every destination that '
                    'already has a pin; saved as days/redo-NAME.json for publishing by hand')
    args = ap.parse_args()
    FONT_DIR = args.fonts

    date = args.date or datetime.datetime.now(ZoneInfo(TIMEZONE)).strftime('%Y-%m-%d')
    if args.redo and not re.fullmatch(r'[A-Za-z0-9-]+', args.redo):
        raise SystemExit('--redo NAME may only contain letters, digits and dashes')
    batch = 'redo-' + args.redo if args.redo else date
    day_file = os.path.join(args.out, 'days', batch + '.json')
    state_file = os.path.join(args.out, 'state.json')
    pins_ready = os.path.exists(day_file)
    social_ready = os.path.exists(os.path.join(args.out, 'social', date + '.json'))
    if pins_ready and (args.redo or social_ready):
        print('Pins for', batch, 'are already prepared. Nothing to do.')
        return

    state = {'queued': list(ALREADY_PUBLISHED), 'days': {}}
    if os.path.exists(state_file):
        state = json.load(open(state_file, encoding='utf-8'))

    if args.catalog_file:
        products = json.load(open(args.catalog_file, encoding='utf-8'))['products']
    else:
        products = fetch_catalog()
    dests = [d for d in (to_destination(p) for p in products) if d]
    by_handle = {d['handle']: d for d in dests}
    if pins_ready:
        # Pins were made earlier today; only the Facebook/Instagram post is missing.
        first = [h for h in state['days'].get(date, []) if h in by_handle][:1]
        if first:
            write_social(args.out, date, by_handle[first[0]])
        return
    if args.redo:
        today = [h for h in state['queued'] if h in by_handle]
        print('Drawing again the %d destinations that already have a pin' % len(today))
    else:
        todo = [h for h in ordered_handles(dests) if h not in state['queued']]
        today = todo[:args.per_day]
        print('%d destinations in the store, %d still without a pin, preparing %d' % (len(dests), len(todo), len(today)))
    if not today:
        print('Nothing to prepare.')
        return

    pin_dir = os.path.join(args.out, 'pins', batch)
    os.makedirs(pin_dir, exist_ok=True)
    os.makedirs(os.path.dirname(day_file), exist_ok=True)
    payloads = []
    for handle in today:
        dest = by_handle[handle]
        draw_pin(dest).save(os.path.join(pin_dir, dest['key'] + '.png'), 'PNG', optimize=True)
        url = '%s/pins/%s/%s.png' % (ASSETS_URL, batch, dest['key'])
        index = len(payloads) if args.redo else len(state['queued']) + len(payloads)
        payloads.append(pin_payload(dest, index, url))
        print(' ', dest['name'], 'from', dest['min_price'], [(p['size'], p['days'], p['price']) for p in dest['plans']])

    # Each pin is stored as the exact JSON body for the Pinterest API, so Make can send it as is.
    with open(day_file, 'w', encoding='utf-8') as f:
        json.dump({'date': batch, 'pins': [json.dumps(p, ensure_ascii=False) for p in payloads]},
                  f, ensure_ascii=False, indent=1)
    if args.redo:
        return  # the daily queue is unchanged
    state['queued'] += today
    state['days'][date] = today
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    write_social(args.out, date, by_handle[today[0]])


if __name__ == '__main__':
    main()
