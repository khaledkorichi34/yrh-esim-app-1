"""Arabic social posts for YRH eSIM (Maghreb diaspora focus), 1080x1350.
Writes social/YYYY-MM-DD.jpg + .json for the Make "Social daily post" scenario.
Run: python3 make_social_ar.py  (needs Pillow with raqm and the Tajawal fonts)
Prices are the store prices on the day the posts were made."""
from PIL import Image, ImageDraw, ImageFont
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('AR_FONTS', '/tmp/claude-0/fonts/gf/ofl/tajawal')
LAT = '/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf'
RAW = 'https://raw.githubusercontent.com/khaledkorichi34/yrh-esim-app-1/pinterest-assets/social/'
SHOP = 'https://yrh.ai/products/'
WA = '+34 642 377 474'

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


def ar(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, 'Tajawal-%s.ttf' % weight), int(size * SS),
                              layout_engine=ImageFont.Layout.RAQM)


def lat(weight, size):
    return ImageFont.truetype(LAT % weight, int(size * SS))


def s(v):
    return int(round(v * SS))


def t(d, xy, txt, f, fill, anchor='ra', rtl=True):
    kw = {'direction': 'rtl', 'language': 'ar'} if rtl else {}
    d.text((s(xy[0]), s(xy[1])), txt, font=f, fill=fill, anchor=anchor, **kw)


def tw(d, txt, f, rtl=True):
    kw = {'direction': 'rtl', 'language': 'ar'} if rtl else {}
    return d.textlength(txt, font=f, **kw) / SS


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
        d.ellipse([s(-r), s(-r + 140), s(r), s(r + 140)], outline=NAVY_SOFT, width=s(3))
    sim(d, W - 84, 84, 34)
    t(d, (W - 116, 86), 'YRH eSIM', lat('Bold', 34), WHITE, 'rm', rtl=False)
    t(d, (70, 88), 'إنترنت السفر', ar('Medium', 26), MUTED, 'lm')
    return img, d


def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if tw(d, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def footer(d):
    items = ['يصلك بالإيميل في دقائق', 'بدون تجوال', 'تحتفظ برقمك']
    f = ar('Medium', 27)
    gap = 44
    widths = [tw(d, x, f) for x in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = (W + total) / 2  # start from the right
    for i, (txt, w) in enumerate(zip(items, widths)):
        t(d, (x, 1236), txt, f, WHITE, 'rm')
        x -= w
        if i < len(items) - 1:
            cx = x - gap / 2
            d.ellipse([s(cx - 4), s(1236 - 4), s(cx + 4), s(1236 + 4)], fill=YELLOW)
            x -= gap
    t(d, (W / 2, 1296), 'إنترنت فقط (بدون مكالمات/SMS) · يتطلب هاتفًا يدعم eSIM وغير مقفل', ar('Regular', 22), MUTED, 'mm')


def offer(kicker, title, sub, code, plans):
    img, d = base()
    R = W - 72
    t(d, (R, 210), kicker, ar('Bold', 32), YELLOW, 'ra')
    f = ar('ExtraBold', 104)
    y = 262
    for ln in wrap(d, title, f, W - 150):
        t(d, (R, y), ln, f, WHITE, 'ra')
        y += 118
    y += 6
    for ln in wrap(d, sub, ar('Regular', 36), W - 150):
        t(d, (R, y), ln, ar('Regular', 36), MUTED, 'ra')
        y += 50
    x0, x1, y1 = 72, W - 72, 1160
    row_h = 104
    y0 = y1 - 40 - row_h * len(plans) - 150
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(36), fill=PAPER)
    t(d, (x1 - 50, y0 + 44), 'الوجهة', ar('Medium', 26), SLATE, 'ra')
    t(d, (x1 - 50, y0 + 70), code, lat('Bold', 76), NAVY, 'ra', rtl=False)
    t(d, (x0 + 50, y0 + 44), 'ابتداءً من', ar('Medium', 26), SLATE, 'la')
    t(d, (x0 + 50, y0 + 74), '€' + plans[0][2], lat('Bold', 66), NAVY, 'la', rtl=False)
    perf = y0 + 170
    xx = x0 + 40
    while xx < x1 - 40:
        d.line([(s(xx), s(perf)), (s(xx + 14), s(perf))], fill=LINE, width=s(3))
        xx += 26
    ry = perf + 20
    for i, (gb, days, price) in enumerate(plans):
        cy = ry + row_h * i + row_h / 2
        t(d, (x1 - 50, cy), gb, ar('Bold', 42), NAVY, 'rm')
        t(d, (x1 - 50 - tw(d, gb, ar('Bold', 42)) - 22, cy + 3), days, ar('Regular', 32), SLATE, 'rm')
        t(d, (x0 + 50, cy), '€' + price, lat('Bold', 40), NAVY, 'lm', rtl=False)
        if i < len(plans) - 1:
            d.line([(s(x0 + 50), s(cy + row_h / 2)), (s(x1 - 50), s(cy + row_h / 2))], fill=LINE, width=s(2))
    footer(d)
    return img


def tip(kicker, title, points):
    img, d = base()
    R = W - 72
    t(d, (R, 210), kicker, ar('Bold', 32), YELLOW, 'ra')
    f = ar('ExtraBold', 92)
    y = 262
    for ln in wrap(d, title, f, W - 150):
        t(d, (R, y), ln, f, WHITE, 'ra')
        y += 106
    y += 40
    x0, x1 = 72, W - 72
    box_h = min(190, (1170 - y - 20 * (len(points) - 1)) / len(points))
    for i, p in enumerate(points):
        d.rounded_rectangle([s(x0), s(y), s(x1), s(y + box_h)], radius=s(30), fill=PAPER)
        cy = y + box_h / 2
        d.ellipse([s(x1 - 128), s(cy - 42), s(x1 - 44), s(cy + 42)], fill=NAVY)
        t(d, (x1 - 86, cy + 4), str(i + 1), lat('Bold', 42), YELLOW, 'mm', rtl=False)
        pf = ar('Medium', 36)
        lines = wrap(d, p, pf, x1 - x0 - 200)
        ly = cy - (len(lines) - 1) * 24
        for ln in lines:
            t(d, (x1 - 160, ly), ln, pf, NAVY, 'rm')
            ly += 48
        y += box_h + 20
    footer(d)
    return img


TAGS_IG = '#eSIM #esim_travel #الجزائر #المغرب #تونس #إسبانيا #المغتربين #الجالية_الجزائرية #سفر #انترنت'
TAGS_FB = '#eSIM #الجالية #سفر #انترنت'


def caption(body, handle, tags_extra=''):
    link_fb = ('🛒 ' + SHOP + handle + '\n') if handle else '🛒 https://yrh.ai\n'
    body = body + '\n\n🎁 خصم 30% على أول شريحة بالكود AHLAN30 (حتى 31 أكتوبر)'
    ig = body + '\n\n🔗 الرابط في البايو · 💬 واتساب ' + WA + '\n\n' + (tags_extra + ' ' if tags_extra else '') + TAGS_IG
    fb = body + '\n\n' + link_fb + '💬 واتساب ' + WA + '\n\n' + (tags_extra + ' ' if tags_extra else '') + TAGS_FB
    return ig, fb


def plan_lines(plans):
    return '\n'.join('• %s · %s · €%s' % p for p in plans)


DZ = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '5.24'), ('5GB', '30 يومًا', '8.73')]
DZ_LONG = [('3GB', '30 يومًا', '5.57'), ('5GB', '30 يومًا', '8.73'), ('10GB', '30 يومًا', '15.33')]
MA = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '6.39'), ('5GB', '30 يومًا', '10.12')]
TN = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '5.12'), ('5GB', '30 يومًا', '8.53')]
ES = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '3.03'), ('10GB', '30 يومًا', '8.63')]
FR = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '3.43'), ('10GB', '30 يومًا', '9.48')]
IT = [('1GB', '7 أيام', '3.00'), ('3GB', '15 يومًا', '3.03'), ('10GB', '30 يومًا', '8.63')]


def build():
    posts = []

    def O(date, name, handle, kicker, title, sub, code, plans, intro):
        body = intro + '\n\n' + plan_lines(plans) + '\n\nيصلك بالإيميل في دقائق · تحتفظ برقمك · إنترنت فقط'
        ig, fb = caption(body, handle)
        posts.append((date, name, offer(kicker, title, sub, code, plans), ig, fb))

    def T(date, name, kicker, title, points, intro, handle=None):
        body = intro + '\n\n' + '\n'.join('%d. %s' % (i + 1, p) for i, p in enumerate(points))
        ig, fb = caption(body, handle)
        posts.append((date, name, tip(kicker, title, points), ig, fb))

    O('2026-10-13', 'Algeria', 'dz_package', 'زيارة الأهل في الجزائر؟', 'إنترنت الجزائر من لحظة الهبوط',
      'بدون طابور لشراء شريحة محلية في المطار', 'DZ', DZ,
      'نازل للبلاد؟ 🇩🇿 جهّز إنترنت الجزائر قبل ما تركب الطيارة: eSIM مسبقة الدفع، تشتغل أول ما تنزل، وتبقى على تواصل مع العائلة على الواتساب برقمك العادي.')
    T('2026-10-14', 'Check eSIM', 'قبل ما تشتري', 'هل هاتفك يدعم eSIM؟',
      ['اطلب الرمز \u200f*#06#\u200e — إذا ظهر رقم EID فهاتفك يدعم eSIM',
       'تأكد أن الهاتف غير مقفل على شركة اتصالات معيّنة',
       'أغلب هواتف iPhone من XS فما فوق وهواتف Samsung الحديثة تدعمه'],
      'قبل ما تشتري eSIM للسفر، تأكد في 30 ثانية أن هاتفك يدعمها 👇', 'dz_package')
    O('2026-10-15', 'Morocco', 'ma_package', 'مسافر للمغرب؟', 'إنترنت المغرب جاهز قبل السفر',
      'eSIM مسبقة الدفع بدون مفاجآت في الفاتورة', 'MA', MA,
      'رايح للمغرب 🇲🇦 في عطلة أو لزيارة العائلة؟ فعّل إنترنت المغرب قبل ما تسافر، ونسى قصة التجوال والفواتير.')
    T('2026-10-16', 'Install', 'نصيحة سفر', 'ثبّتها في الدار، فعّلها في المطار',
      ['اشترِ الباقة وستصلك رسالة فيها رمز QR',
       'امسح الرمز وأنت متصل بالـ Wi-Fi قبل السفر',
       'عند الهبوط: فعّل الخط وشغّل تجوال البيانات للـ eSIM فقط'],
      'أسهل طريقة باش يكون عندك إنترنت أول ما تنزل من الطيارة ✈️', 'dz_package')
    O('2026-10-17', 'Tunisia', 'tn_package', 'عطلة في تونس؟', 'إنترنت تونس بدون شريحة',
      'تشتغل من أول دقيقة في المطار', 'TN', TN,
      'مسافر لتونس 🇹🇳؟ eSIM مسبقة الدفع تخليك متصل من أول ما توصل: خرائط، واتساب، وتحويلات… بلا ما تدوّر على شريحة محلية.')
    O('2026-10-18', 'Spain', 'es_package', 'جايين يزوروك في إسبانيا؟', 'إنترنت إسبانيا لضيوفك',
      'هدية مفيدة لعائلتك القادمة من البلاد', 'ES', ES,
      'عندك عائلة جاية تزورك في إسبانيا 🇪🇸؟ بدل ما يدفعوا تجوال غالي، اشري لهم eSIM إسبانيا وابعثها لهم بالإيميل قبل ما يسافروا.')
    T('2026-10-19', 'WhatsApp', 'سؤال يتكرر كثيرًا', 'هل يبقى الواتساب برقمي القديم؟',
      ['نعم — الـ eSIM للإنترنت فقط، وحسابك في الواتساب يبقى على رقمك',
       'شريحتك الأصلية تبقى في الهاتف لاستقبال رسائل البنك',
       'تتصل وتكلّم العائلة عبر الواتساب كالمعتاد'],
      'أكثر سؤال يوصلنا 👇 الجواب: نعم، رقمك ما يتغيّرش.', 'dz_package')
    O('2026-10-20', 'France', 'fr_package', 'زيارة عائلية لفرنسا؟', 'إنترنت فرنسا من لحظة الوصول',
      'باقات مسبقة الدفع تبدأ من 3 يورو', 'FR', FR,
      'مسافر لفرنسا 🇫🇷 عند العائلة أو للخدمة؟ جهّز الإنترنت قبل السفر وتجنّب فواتير التجوال.')
    O('2026-10-21', 'Algeria long stay', 'dz_package', 'إقامة طويلة في البلاد؟', 'باقات الجزائر لمدة شهر كامل',
      'للعطل الطويلة وزيارات الصيف', 'DZ', DZ_LONG,
      'رايح للجزائر 🇩🇿 لمدة طويلة؟ هذه باقات 30 يومًا تكفيك للخرائط، الواتساب، ومكالمات الفيديو مع اللي بقاو هنا.')
    O('2026-10-22', 'Italy', 'it_package', 'سفرة إلى إيطاليا؟', 'إنترنت إيطاليا بسعر خفيف',
      'eSIM مسبقة الدفع تصلك بالإيميل', 'IT', IT,
      'مسافر لإيطاليا 🇮🇹؟ اشترِ eSIM قبل السفر وكون متصل من أول ما تنزل.')
    T('2026-10-23', 'How it works', 'كيف تشتغل؟', 'إنترنت السفر في 3 خطوات',
      ['اختر البلد والباقة المناسبة لك',
       'تصلك eSIM بالإيميل عادةً خلال دقائق',
       'امسح رمز QR واتصل بالإنترنت عند الوصول'],
      'بدون محل، بدون شريحة بلاستيكية، بدون انتظار 👇')
    O('2026-10-24', 'Morocco 30 days', 'ma_package', 'المغرب لمدة أطول؟', 'باقات المغرب حسب مدة إقامتك',
      'من أسبوع إلى شهر كامل', 'MA',
      [('1GB', '7 أيام', '3.00'), ('3GB', '30 يومًا', '6.74'), ('5GB', '30 يومًا', '10.12')],
      'سواء رايح للمغرب 🇲🇦 أسبوع ولا شهر، اختار الباقة اللي تناسب مدة إقامتك.')
    T('2026-10-25', 'Dual SIM', 'نصيحة مهمة', 'خلّي شريحتك الأصلية مفعّلة',
      ['استعمل الـ eSIM للبيانات فقط في إعدادات الهاتف',
       'أبقِ شريحتك الأصلية لاستقبال رسائل التحقق من البنك',
       'أوقف تجوال البيانات على الشريحة الأصلية لتجنّب الرسوم'],
      'باش تستقبل رموز البنك وما تدفعش تجوال في نفس الوقت 👇', 'dz_package')
    O('2026-10-26', 'Tunisia 30 days', 'tn_package', 'تونس هذا الشتاء؟', 'إنترنت تونس لعطلتك',
      'باقات مسبقة الدفع بدون مفاجآت', 'TN',
      [('3GB', '30 يومًا', '5.45'), ('5GB', '30 يومًا', '8.53'), ('10GB', '30 يومًا', '15.57')],
      'عطلة الشتاء في تونس 🇹🇳؟ اختار باقة 30 يومًا وابقَ متصل طول الإقامة.')
    return posts


def main(only=None):
    out = os.path.join(HERE, 'social')
    for date, name, img, ig, fb in build():
        if only and date not in only:
            continue
        img.resize((W, H), Image.LANCZOS).save(os.path.join(out, date + '-11.jpg'), quality=90)
        with open(os.path.join(out, date + '-11.json'), 'w', encoding='utf-8') as fh:
            json.dump({'date': date, 'name': name, 'image': RAW + date + '-11.jpg', 'ig': ig, 'fb': fb},
                      fh, ensure_ascii=False, indent=1)
        print(date, name)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
