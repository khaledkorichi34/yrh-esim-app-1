#!/usr/bin/env python3
"""Render a YRH eSIM vertical Short (1080x1920, 30 fps) from a spec JSON + voice WAV + music.

usage: render.py spec.json voice.wav music.mp3 out.mp4
"""
import json, math, os, random, subprocess, sys, re, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

BG = (11, 15, 26)
INK = (244, 246, 250)
MUTED = (150, 160, 180)
CARD = (22, 28, 44)


# ---------- helpers ----------
def ease(t):  # ease-out cubic, clamped
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Typo:
    def __init__(self, spec):
        self.lang = spec.get("lang", "en")
        self.rtl = spec.get("rtl", False)
        self.bold = spec["font_bold"]
        self.reg = spec.get("font_regular", spec["font_bold"])
        self.var_bold = spec.get("font_bold_var")  # e.g. "Bold" for variable fonts
        self.index = spec.get("font_index", 0)
        self.cache = {}

    def font(self, size, bold=True):
        key = (size, bold)
        if key not in self.cache:
            path = self.bold if bold else self.reg
            f = ImageFont.truetype(path, size, index=self.index, layout_engine=ImageFont.Layout.RAQM)
            try:
                if self.var_bold and bold:
                    f.set_variation_by_name(self.var_bold)
                elif self.var_bold:
                    f.set_variation_by_name("Regular")
            except Exception:
                pass
            self.cache[key] = f
        return self.cache[key]

    def kw(self):
        return {"direction": "rtl", "language": self.lang} if self.rtl else {"language": self.lang}

    def width(self, txt, f):
        return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f, **self.kw())

    def wrap(self, txt, f, maxw):
        if not txt:
            return []
        txt = txt.replace("YRH eSIM", "YRH\u00a0eSIM")
        words = txt.split(" ")
        if len(words) == 1 or self.lang in ("ja", "zh", "ko") and " " not in txt:
            # CJK: break by characters
            lines, cur = [], ""
            for ch in txt:
                if self.width(cur + ch, f) > maxw and cur:
                    lines.append(cur); cur = ch
                else:
                    cur += ch
            return lines + ([cur] if cur else [])
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.width(t, f) > maxw and cur:
                lines.append(cur); cur = w
            else:
                cur = t
        return lines + ([cur] if cur else [])

    def fit(self, txt, maxw, size, minsize, bold=True, maxlines=3):
        s = size
        while s > minsize:
            f = self.font(s, bold)
            lines = self.wrap(txt, f, maxw)
            if len(lines) <= maxlines and all(self.width(l, f) <= maxw for l in lines):
                return f, lines
            s -= 4
        f = self.font(minsize, bold)
        return f, self.wrap(txt, f, maxw)


def draw_text_block(img, typo, lines, f, cx, top, color, alpha=1.0, dy=0, gap=1.18):
    if alpha <= 0:
        return top
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lh = int(f.size * gap)
    y = top
    for ln in lines:
        d.text((cx, y + dy + lh / 2), ln, font=f, fill=color + (int(255 * alpha),), anchor="mm", **typo.kw())
        y += lh
    img.alpha_composite(layer)
    return y


EMOJI_FONT = None


def emoji_img(ch, size):
    global EMOJI_FONT
    if EMOJI_FONT is None:
        EMOJI_FONT = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=EMOJI_FONT, embedded_color=True, anchor="mm")
    bb = im.getbbox() or (0, 0, 160, 160)
    im = im.crop(bb)
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


# ---------- static layers ----------
def make_background(accent):
    bg = Image.new("RGBA", (W, H), BG + (255,))
    return bg


def glow(accent, r, a):
    import numpy as np
    S = r * 2
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    al = (np.clip(1 - d, 0, 1) ** 2.2 * a).astype("uint8")
    im = Image.new("RGBA", (S, S), accent + (0,))
    im.putalpha(Image.fromarray(al, "L"))
    return im


def vignette():
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    al = (np.clip(d - 0.55, 0, 1) / 0.45) ** 1.6 * 170
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v.putalpha(Image.fromarray(np.clip(al, 0, 255).astype("uint8"), "L"))
    return v


def grains(n=4):
    out = []
    rnd = random.Random(3)
    for _ in range(n):
        g = Image.effect_noise((W // 2, H // 2), 40).resize((W, H))
        ga = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        ga.putalpha(Image.eval(g, lambda p: max(0, (p - 128)) // 14))
        out.append(ga)
    return out


# ---------- scene painters ----------
class Ctx:
    def __init__(self, spec):
        self.spec = spec
        self.typo = Typo(spec)
        self.accent = hexrgb(spec.get("accent", "#0066FF"))
        self.accent2 = hexrgb(spec.get("accent2", "#00D2FF"))
        self.bg = make_background(self.accent)
        self.glow_big = glow(self.accent, 620, 110)
        self.glow_small = glow(self.accent2, 420, 55)
        self.vig = vignette()
        self.grain = grains()
        self.brand_f = ImageFont.truetype(os.path.join(FONTS, "Inter-ExtraBold.otf"), 40)

    def base(self, t_global, frame):
        img = self.bg.copy()
        # two slowly drifting glows
        x = int(W * 0.15 + 160 * math.sin(t_global * 0.35))
        y = int(H * 0.22 + 120 * math.cos(t_global * 0.27))
        img.alpha_composite(self.glow_big, (x - 620, y - 620))
        x2 = int(W * 0.85 + 140 * math.cos(t_global * 0.31))
        y2 = int(H * 0.78 + 100 * math.sin(t_global * 0.23))
        img.alpha_composite(self.glow_small, (x2 - 420, y2 - 420))
        return img

    def finish(self, img, frame):
        img.alpha_composite(self.vig)
        img.alpha_composite(self.grain[frame % len(self.grain)])
        # brand bug top
        d = ImageDraw.Draw(img)
        d.text((W // 2, 120), "YRH eSIM", font=self.brand_f, fill=INK + (200,), anchor="mm")
        d.rounded_rectangle([W // 2 - 26, 150, W // 2 + 26, 156], radius=3, fill=self.accent + (230,))
        return img


def p_hook(c, img, t, dur, sc):
    T = c.typo
    a = ease(t / 0.35)
    flag = c.spec.get("hook_emoji")
    if flag:
        e = emoji_img(flag, int(190 + 20 * ease(t / 0.5)))
        ea = e.copy(); ea.putalpha(Image.eval(e.getchannel("A"), lambda p: int(p * a)))
        img.alpha_composite(ea, (W // 2 - e.width // 2, 640 - e.height // 2 + int(40 * (1 - a))))
    f, lines = T.fit(sc["headline"], W - 140, 132, 72, maxlines=3)
    y = draw_text_block(img, T, lines, f, W // 2, 820, INK, a, int(60 * (1 - a)))
    if sc.get("sub"):
        a2 = ease((t - 0.35) / 0.35)
        f2, l2 = T.fit(sc["sub"], W - 180, 70, 44, maxlines=2)
        # accent pill behind sub
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        lh = int(f2.size * 1.18)
        bw = max(T.width(l, f2) for l in l2) + 80
        top = y + 40
        d.rounded_rectangle([W // 2 - bw / 2, top, W // 2 + bw / 2, top + lh * len(l2) + 40], radius=40,
                            fill=c.accent + (int(235 * a2),))
        img.alpha_composite(lay)
        draw_text_block(img, T, l2, f2, W // 2, top + 20, (255, 255, 255), a2, int(30 * (1 - a2)))


def p_problem(c, img, t, dur, sc):
    T = c.typo
    a = ease(t / 0.35)
    # receipt / bill card with red total
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, top = W // 2, 470
    shake = int(10 * math.sin(t * 40) * max(0, 1 - t / 0.6)) if t > 0.3 else 0
    bw, bh = 560, 520
    x0 = cx - bw // 2 + shake
    d.rounded_rectangle([x0, top + int(80 * (1 - a)), x0 + bw, top + bh + int(80 * (1 - a))], radius=36,
                        fill=(245, 246, 250, int(255 * a)))
    yy = top + 70 + int(80 * (1 - a))
    for i, wdt in enumerate([380, 300, 420, 260]):
        d.rounded_rectangle([x0 + 60, yy + i * 70, x0 + 60 + wdt, yy + i * 70 + 22], radius=11,
                            fill=(200, 205, 215, int(255 * a)))
    d.line([x0 + 50, yy + 300, x0 + bw - 50, yy + 300], fill=(210, 212, 220, int(255 * a)), width=4)
    # big red "!!!"
    r = ease((t - 0.3) / 0.3)
    d.rounded_rectangle([x0 + 60, yy + 330, x0 + bw - 60, yy + 420], radius=24, fill=(230, 57, 70, int(255 * r)))
    d.text((cx + shake, yy + 375), "$ $ $ !", font=c.brand_f.font_variant(size=60), fill=(255, 255, 255, int(255 * r)),
           anchor="mm")
    img.alpha_composite(lay)
    f, lines = T.fit(sc["headline"], W - 140, 112, 64, maxlines=2)
    y = draw_text_block(img, T, lines, f, W // 2, 1120, INK, a, int(50 * (1 - a)))
    if sc.get("sub"):
        a2 = ease((t - 0.3) / 0.4)
        f2, l2 = T.fit(sc["sub"], W - 180, 60, 40, bold=False, maxlines=2)
        draw_text_block(img, T, l2, f2, W // 2, y + 30, MUTED, a2)


def p_offers(c, img, t, dur, sc):
    T = c.typo
    a = ease(t / 0.3)
    f, lines = T.fit(sc["headline"], W - 140, 96, 60, maxlines=2)
    y = draw_text_block(img, T, lines, f, W // 2, 300, INK, a, int(40 * (1 - a)))
    offers = c.spec["offers"]
    n = len(offers)
    top = max(y + 50, 560)
    ch, gap = 300, 40
    step = min(0.9, (dur - 1.0) / max(1, n))
    for i, o in enumerate(offers):
        ai = ease((t - 0.25 - i * step) / 0.35)
        if ai <= 0:
            continue
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        y0 = top + i * (ch + gap) + int(70 * (1 - ai))
        x0, x1 = 70, W - 70
        d.rounded_rectangle([x0, y0, x1, y0 + ch], radius=40, fill=CARD + (int(250 * ai),),
                            outline=c.accent + (int(160 * ai),), width=3)
        img.alpha_composite(lay)
        # emoji
        e = emoji_img(o["emoji"], 120)
        ea = e.copy(); ea.putalpha(Image.eval(e.getchannel("A"), lambda p: int(p * ai)))
        ex = (x1 - 60 - e.width) if T.rtl else (x0 + 60)
        img.alpha_composite(ea, (ex, y0 + 50))
        # label + plan
        lf, ll = T.fit(o["label"], 470, 64, 40, maxlines=1)
        pf = T.font(42, bold=False)
        d = ImageDraw.Draw(img)
        lx = (x1 - 220) if T.rtl else (x0 + 220)
        anchor = "rm" if T.rtl else "lm"
        d.text((lx, y0 + 105), ll[0], font=lf, fill=INK + (int(255 * ai),), anchor=anchor, **T.kw())
        d.text((lx, y0 + 180), o["plan"], font=pf, fill=MUTED + (int(255 * ai),), anchor=anchor,
               **({} if True else T.kw()))
        # price (always LTR digits)
        pfnt = ImageFont.truetype(os.path.join(FONTS, "Inter-ExtraBold.otf"), 88)
        px = (x0 + 60) if T.rtl else (x1 - 60)
        d.text((px, y0 + ch / 2 + 10), o["price"], font=pfnt, fill=c.accent2 + (int(255 * ai),),
               anchor=("lm" if T.rtl else "rm"))
        if o.get("from"):
            ff = T.font(34, bold=False)
            d.text((px, y0 + 70), o["from"], font=ff, fill=MUTED + (int(255 * ai),),
                   anchor=("lm" if T.rtl else "rm"), **T.kw())
    # footnote
    fa = ease((t - 1.0) / 0.5)
    note = c.spec.get("price_note", "")
    if note:
        nf = T.font(32, bold=False)
        ImageDraw.Draw(img).text((W // 2, 1720), note, font=nf, fill=MUTED + (int(200 * fa),), anchor="mm", **T.kw())


def p_benefits(c, img, t, dur, sc):
    T = c.typo
    a = ease(t / 0.3)
    f, lines = T.fit(sc["headline"], W - 140, 96, 60, maxlines=2)
    y = draw_text_block(img, T, lines, f, W // 2, 300, INK, a, int(40 * (1 - a)))
    # phone with QR
    pa = ease((t - 0.1) / 0.45)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pw, ph = 330, 600
    px = W // 2 - pw // 2
    py = max(y + 40, 520) + int(80 * (1 - pa))
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=54, fill=(30, 36, 54, int(255 * pa)),
                        outline=(80, 90, 115, int(255 * pa)), width=6)
    d.rounded_rectangle([px + 18, py + 18, px + pw - 18, py + ph - 18], radius=40, fill=(245, 246, 250, int(255 * pa)))
    # QR pattern
    rnd = random.Random(7)
    q0x, q0y, cell = px + 55, py + 110, 20
    for i in range(11):
        for j in range(11):
            corner = (i < 3 and j < 3) or (i < 3 and j > 7) or (i > 7 and j < 3)
            if corner:
                on = not (i in (1, 9) and j in (1, 9)) and not ((i == 1 or i == 9) and (j == 1 or j == 9))
                on = (i in (0, 2, 8, 10) or j in (0, 2, 8, 10) or (i in (1, 9) and j in (1, 9)))
            else:
                on = rnd.random() < 0.5
            if on:
                d.rectangle([q0x + j * cell, q0y + i * cell, q0x + j * cell + cell - 2, q0y + i * cell + cell - 2],
                            fill=(15, 23, 42, int(255 * pa)))
    # scan line
    sl = q0y + int((math.sin(t * 3) * 0.5 + 0.5) * 11 * cell)
    d.rectangle([q0x - 10, sl, q0x + 11 * cell + 10, sl + 6], fill=c.accent + (int(200 * pa),))
    # signal arcs on phone
    cxp, cyp = px + pw // 2, py + ph - 120
    for k in range(3):
        ak = ease((t - 0.6 - k * 0.15) / 0.3) * pa
        r = 30 + k * 26
        d.arc([cxp - r, cyp - r, cxp + r, cyp + r], 225, 315, fill=c.accent + (int(255 * ak),), width=10)
    img.alpha_composite(lay)
    # bullets
    bullets = c.spec.get("bullets", [])
    by = py + ph + 50 - int(80 * (1 - pa))
    bf = T.font(52)
    cols = 2
    cw = (W - 140) // cols
    for i, b in enumerate(bullets[:4]):
        ab = ease((t - 0.7 - i * 0.35) / 0.3)
        if ab <= 0:
            continue
        r_, col = divmod(i, cols)
        if T.rtl:
            col = cols - 1 - col
        cx = 70 + col * cw + cw // 2
        cy = by + r_ * 110 + int(20 * (1 - ab))
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([cx - cw // 2 + 10, cy, cx + cw // 2 - 10, cy + 90], radius=45,
                            fill=CARD + (int(240 * ab),))
        tw = T.width("✓ " + b, bf)
        d.text((cx, cy + 45), b, font=T.fit(b, cw - 110, 46, 30, maxlines=1)[0], fill=INK + (int(255 * ab),),
               anchor="mm", **T.kw())
        img.alpha_composite(lay)


def p_cta(c, img, t, dur, sc):
    T = c.typo
    a = ease(t / 0.35)
    f, lines = T.fit(sc["headline"], W - 140, 110, 64, maxlines=2)
    y = draw_text_block(img, T, lines, f, W // 2, 600, INK, a, int(40 * (1 - a)))
    # big domain
    da = ease((t - 0.2) / 0.4)
    df = ImageFont.truetype(os.path.join(FONTS, "Inter-ExtraBold.otf"), 150)
    d = ImageDraw.Draw(img)
    s = 0.92 + 0.08 * da
    d.text((W // 2, y + 170), "yrh.ai", font=df.font_variant(size=int(150 * s)), fill=c.accent2 + (int(255 * da),),
           anchor="mm")
    # button
    ba = ease((t - 0.5) / 0.4)
    pulse = 1 + 0.03 * math.sin(max(0, t - 0.9) * 6)
    bw, bh = int(760 * pulse), int(150 * pulse)
    by = y + 340
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle([W // 2 - bw // 2, by, W // 2 + bw // 2, by + bh], radius=bh // 2,
                         fill=c.accent + (int(255 * ba),))
    tri = 34
    tx = (W // 2 + bw // 2 - 90) if T.rtl else (W // 2 - bw // 2 + 70)
    ty = by + bh // 2
    pts = [(tx, ty - tri), (tx, ty + tri), (tx + tri * 1.6, ty)] if not T.rtl else \
        [(tx + tri * 1.6, ty - tri), (tx + tri * 1.6, ty + tri), (tx, ty)]
    dd.polygon(pts, fill=(255, 255, 255, int(255 * ba)))
    img.alpha_composite(lay)
    bf, bl = T.fit(c.spec.get("cta_button", "Google Play"), bw - 220, 54, 34, maxlines=1)
    ImageDraw.Draw(img).text((W // 2 + (-30 if T.rtl else 30), by + bh // 2), bl[0], font=bf,
                             fill=(255, 255, 255, int(255 * ba)), anchor="mm", **T.kw())
    if sc.get("sub"):
        a2 = ease((t - 0.9) / 0.4)
        f2, l2 = T.fit(sc["sub"], W - 180, 54, 36, bold=False, maxlines=2)
        draw_text_block(img, T, l2, f2, W // 2, by + bh + 60, MUTED, a2)


PAINTERS = {"hook": p_hook, "problem": p_problem, "offers": p_offers, "benefits": p_benefits, "cta": p_cta}


# ---------- timing from voice ----------
def audio_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def scene_bounds(voice, scenes):
    """Split the voice track into len(scenes) parts at its longest pauses."""
    total = audio_dur(voice)
    r = subprocess.run(["ffmpeg", "-i", voice, "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    gaps = [(e - s, (s + e) / 2) for s, e in zip(starts, ends) if 0.4 < s and e < total - 0.3]
    n = len(scenes)
    # proportional guess by text length as fallback / tie-breaker
    lens = [max(1, len(s["voice"])) for s in scenes]
    acc, guess = 0, []
    for L in lens[:-1]:
        acc += L
        guess.append(total * acc / sum(lens))
    cuts = []
    if len(gaps) >= n - 1:
        # the n-1 longest pauses are the scene breaks (the voice is read with a long pause between lines)
        cuts = sorted(m for _, m in sorted(gaps, key=lambda g: -g[0])[: n - 1])
    else:
        cuts = guess
    return total, cuts


def main():
    spec_path, voice, music, out = sys.argv[1:5]
    spec = json.load(open(spec_path, encoding="utf-8"))
    c = Ctx(spec)
    scenes = spec["scenes"]
    lead = 0.35  # silence before the voice starts
    total, cuts = scene_bounds(voice, scenes)
    tail = 1.4
    edges = [0.0] + [lead + x for x in cuts] + [lead + total + tail]
    tmp = tempfile.mkdtemp(prefix="yrh_")
    parts = []
    frame0 = 0
    for i, sc in enumerate(scenes):
        t0, t1 = edges[i], edges[i + 1]
        nfr = int(round(t1 * FPS)) - int(round(t0 * FPS))
        dur = nfr / FPS
        part = os.path.join(tmp, f"s{i}.mp4")
        tmpname = os.path.join(tmp, f"s{i}.tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "23", "-pix_fmt", "yuv420p", tmpname], stdin=subprocess.PIPE)
        for k in range(nfr):
            t = k / FPS
            tg = t0 + t
            img = c.base(tg, frame0 + k)
            PAINTERS[sc["id"]](c, img, t, dur, sc)
            # quick fade-in at scene start (except first)
            img = c.finish(img, frame0 + k)
            if i > 0 and t < 0.12:
                img = Image.blend(c.bg, img, t / 0.12)
            p.stdin.write(img.convert("RGB").tobytes())
        p.stdin.close()
        if p.wait() != 0:
            sys.exit("ffmpeg failed on scene %d" % i)
        os.rename(tmpname, part)
        parts.append(part)
        frame0 += nfr
        print(f"scene {sc['id']}: {dur:.2f}s", flush=True)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(tmp, "silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    silent], check=True)
    vid_dur = frame0 / FPS
    # mix: voice (delayed by lead) + music ducked to ~14%, music fades out at end
    fc = (f"[1:a]adelay={int(lead * 1000)}:all=1,volume=1.6,apad[v];"
          f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{vid_dur:.2f},volume=0.14,"
          f"afade=t=in:d=0.4,afade=t=out:st={vid_dur - 1.2:.2f}:d=1.2[m];"
          f"[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{vid_dur:.2f},"
          f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    tmpout = out[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", voice, "-i", music,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", tmpout], check=True)
    os.rename(tmpout, out)
    shutil.rmtree(tmp, ignore_errors=True)
    print("done", out, f"{vid_dur:.2f}s")


if __name__ == "__main__":
    main()
