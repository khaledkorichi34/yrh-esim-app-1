#!/usr/bin/env python3
"""Daily job helper for YRH eSIM Shorts. See RUNBOOK.md.

  prepare.py next                         -> create jobs/<date>-<cc>/plan.json, print what to fetch
  prepare.py prices <job> <key> <file>    -> store a product's variations JSON (from WP API)
  prepare.py prompt <job>                 -> print the Gemini script prompt (real prices filled in)
  prepare.py review <job> <script.json>   -> print the Fable review prompt
  prepare.py spec <job> <script.json>     -> validate script, write spec.json + meta.json, print TTS text
  prepare.py done <job> <videoId>         -> record publish in state.json
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "countries.json"), encoding="utf-8"))
STATE = os.path.join(HERE, "state.json")
MUSIC = ["music/house1.mp3", "music/house2.mp3", "music/house3.mp3"]


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"day": 0, "history": []}


def jdir(job):
    return os.path.join(HERE, "jobs", job)


def plan_size(opt):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB)\s*(\d+)\s*Days?", opt, re.I)
    if not m:
        return None
    gb = float(m.group(1)) / (1024 if m.group(2).upper() == "MB" else 1)
    return gb, int(m.group(3))


def fmt_plan(gb, days):
    g = f"{int(gb)}GB" if gb == int(gb) else f"{gb:g}GB"
    return f"{g} · {days} days"


def pick(variations):
    rows = []
    for v in variations:
        opt = v["attributes"][0]["option"] if v.get("attributes") else ""
        ps = plan_size(opt)
        if not ps or not v.get("price"):
            continue
        rows.append({"gb": ps[0], "days": ps[1], "price": float(v["price"]), "option": opt})
    if not rows:
        raise SystemExit("no usable variations")
    cheapest = min(rows, key=lambda r: r["price"])
    # card plan: cheapest plan with >=5GB valid >=30 days, else 3GB+, else cheapest
    card = None
    for mingb in (5, 3):
        c = [r for r in rows if r["gb"] >= mingb and r["days"] >= 30]
        if c:
            card = min(c, key=lambda r: r["price"]); break
    card = card or cheapest
    return {"cheapest": cheapest, "card": card}


def cmd_next():
    st = load_state()
    d = st["day"]
    n = len(CFG["countries"])
    c = CFG["countries"][d % n]
    pool = c["pools"][(d // n) % len(c["pools"])]
    today = datetime.date.today().isoformat()
    job = f"{today}-{c['code']}"
    os.makedirs(jdir(job), exist_ok=True)
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(c["tz"])
    now = datetime.datetime.now(datetime.timezone.utc)
    local = now.astimezone(tz)
    target = local.replace(hour=18, minute=30, second=0, microsecond=0)
    if target - local < datetime.timedelta(minutes=50):
        target += datetime.timedelta(days=1)
    publish_at = target.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    plan = {"job": job, "date": today, "publish_at": publish_at, "day": d, "country": c, "pool": pool,
            "music": MUSIC[d % len(MUSIC)], "dest": {k: CFG["dest"][k] for k in pool}}
    json.dump(plan, open(os.path.join(jdir(job), "plan.json"), "w"), ensure_ascii=False, indent=1)
    print("JOB", job, "| publish_at", publish_at, "(18:30 in", c["tz"] + ")")
    for k in pool:
        print("FETCH", k, CFG["dest"][k]["slug"])


def cmd_prices(job, key, path):
    raw = open(path, encoding="utf-8").read().strip()
    data = json.loads(raw)
    if isinstance(data, dict) and "body" in data:
        data = json.loads(data["body"])
    p = pick(data)
    plan = json.load(open(os.path.join(jdir(job), "plan.json")))
    plan.setdefault("prices", {})[key] = p
    json.dump(plan, open(os.path.join(jdir(job), "plan.json"), "w"), ensure_ascii=False, indent=1)
    print(key, "cheapest", p["cheapest"]["option"], p["cheapest"]["price"], "| card", p["card"]["option"], p["card"]["price"])


def cur(plan):
    return plan["country"].get("currency")


def amount(plan, usd):
    """Price as shown to this audience: local currency if the country has one set, else USD."""
    c = cur(plan)
    return f"{usd * c['rate']:.2f}" if c else f"{usd:.2f}"


def money(plan, usd):
    c = cur(plan)
    return f"{amount(plan, usd)} {c['word']}" if c else f"${usd:.2f}"


def price_lines(plan):
    out = []
    for k in plan["pool"]:
        p = plan["prices"][k]
        en = plan["dest"][k]["en"]
        ch, cd = p["cheapest"], p["card"]
        out.append(f"- {k} = {en}: {fmt_plan(ch['gb'], ch['days'])} = {money(plan, ch['price'])} ; "
                   f"{fmt_plan(cd['gb'], cd['days'])} = {money(plan, cd['price'])}")
    return "\n".join(out)


def currency_rule(plan):
    c = cur(plan)
    if not c:
        return "Prices are in US dollars."
    return (f"Show and say prices ONLY in {c['name']} ({c['word']}), never in dollars. In voice lines you may round "
            f"up as 'less than N {c['word']}' (N = next whole number above the price).")


def human_date(plan):
    d = datetime.date.fromisoformat(plan["date"])
    return d.strftime("%-d %b %Y")


def cmd_prompt(job):
    plan = json.load(open(os.path.join(jdir(job), "plan.json")))
    c = plan["country"]
    keys = plan["pool"]
    print(f"""Write a 26-30 second YouTube Short script for YRH eSIM (travel data eSIMs, website yrh.ai, Android app "YRH eSIM" on Google Play).
Audience: residents of {c['name']} who travel abroad. Language: {c['language']}. Natural, warm, energetic, like a friend giving a travel tip; never stiff or formal.
Featured destinations and REAL prices (use exactly; never invent other numbers, plans or currencies):
{price_lines(plan)}
{currency_rule(plan)}
True facts you may use: QR code arrives by email right after purchase; install in minutes (Wi-Fi needed to install); works on local 4G/5G networks; hotspot included; top up anytime; data only (no phone number); phone must be unlocked and eSIM-compatible; "works or your money back" with WhatsApp support.
Never claim: unlimited data, cheapest in the world, named carriers' roaming prices, user counts, discounts.
Every spoken price must be said together with its data amount. Write numbers in voice lines as words, the way a native speaker says them.
Make this video feel different from a generic ad: open with a hook built on the FIRST destination ({plan['dest'][keys[0]]['en']}) and its cheapest price, and add one genuinely useful travel tip for that destination in the problem line.
Scenes (each voice line 4-10 words):
1 hook (0-3s): destination question + price shock with its data amount
2 problem: roaming bills / SIM-shop queues / a practical tip
3 offers: name the destinations; say at most one price aloud
4 steps: how to order on the website: go to yrh.ai, choose your destination and plan, pay, scan the QR code from the email
5 cta: download our app from our website yrh.ai (the "Get the app" button at the top of the site)
Return ONLY JSON:
{{"scenes":[{{"id":"hook|problem|offers|steps|cta","voice":"...","headline":"max 5 words on screen","sub":"max 6 words or empty"}}],
"offer_labels":{{{', '.join(f'"{k}":"destination name in the target language"' for k in keys)}}},
"steps":["4 short on-screen steps, max 5 words each; step 1 must contain yrh.ai"],
"cta_button":"'Download the app at yrh.ai' in the target language, short",
"price_note":"one short footnote line in the target language: prices from yrh.ai on {human_date(plan)}{'' if not cur(plan) else ', shown in ' + cur(plan)['name'] + ' at ' + str(cur(plan)['rate']) + ' per dollar, paid in USD on the site'}",
"title":"SEO title in the target language, max 70 chars: start with the exact phrase people search (e.g. 'eSIM <first destination>' in the target language), then the cheapest price with its data amount, then '| YRH eSIM'; max 1 emoji",
"description":"4-6 lines in the target language: hook line, the prices list with plan sizes, the 4 ordering steps, 'download the YRH eSIM app from yrh.ai', the line 'Prices checked on yrh.ai, {human_date(plan)}' translated, then 3-5 hashtags in the target language and English (no #Shorts, it is added). The first line must contain the main search phrase. Do not put URLs in it, they are added automatically",
"tags":"10-15 comma-separated search phrases people type, in the target language and English: 'esim <destination>', '<destination> sim card', 'internet in <destination>', 'roaming', 'travel esim', 'YRH eSIM'",
"tts_style":"one English sentence for the voice actor: tone, pace, accent"}}
Headlines and subs must not contain prices with plan sizes split apart; if a sub shows a price it must also show its data amount.""")


def cmd_review(job, script_path):
    plan = json.load(open(os.path.join(jdir(job), "plan.json")))
    c = plan["country"]
    script = open(script_path, encoding="utf-8").read().strip()
    print(f"""Review and correct this YouTube Short script JSON for YRH eSIM, aimed at residents of {c['name']} travelling abroad, language: {c['language']}.
Allowed facts and prices, nothing else:
{price_lines(plan)}
{currency_rule(plan)}
Check and fix:
1. Every price matches the list and is tied to its data amount and validity. Remove any number not in the list.
2. Language is natural and native for {c['name']} (spelling, grammar, idiom). No machine-translation feel.
3. Hook is specific and strong in the first 3 seconds. Each voice line 4-10 words; total voice 22-28 seconds.
4. Numbers in voice lines are written as words a TTS reads naturally.
5. No false or risky claims (unlimited, cheapest, guaranteed coverage everywhere, competitor prices).
6. offer_labels are destination names only. Title <= 70 chars. Description contains https://yrh.ai and the price-check date line.
Return ONLY the corrected JSON, same structure, no commentary.

{script}""")


def strip_fences(t):
    t = t.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    return t


def cmd_spec(job, script_path):
    plan = json.load(open(os.path.join(jdir(job), "plan.json")))
    s = json.loads(strip_fences(open(script_path, encoding="utf-8").read()))
    c = plan["country"]
    font = dict(CFG["fonts"][c["font"]])
    ids = [x["id"] for x in s["scenes"]]
    assert ids == ["hook", "problem", "offers", "steps", "cta"], ids
    allowed = set()
    for k in plan["pool"]:
        for which in ("cheapest", "card"):
            allowed.add(amount(plan, plan['prices'][k][which]['price']))
    # on-screen prices must be real
    for sc in s["scenes"]:
        for fld in ("headline", "sub"):
            for num in re.findall(r"\d+[.,]\d{2}", sc.get(fld, "")):
                if num.replace(",", ".") not in allowed:
                    raise SystemExit(f"price {num} in {sc['id']}.{fld} is not a real price")
    first = plan["pool"][0]
    offers = []
    for k in plan["pool"]:
        cd = plan["prices"][k]["card"]
        offers.append({"emoji": plan["dest"][k]["emoji"], "label": s["offer_labels"][k],
                       "plan": fmt_plan(cd["gb"], cd["days"]),
                       **({"price": amount(plan, cd["price"]), "unit": cur(plan)["word"]} if cur(plan)
                          else {"price": f"${cd['price']:.2f}"})})
    spec = {"lang": c["lang"], "rtl": font.pop("rtl", False), **font,
            "accent": c["accent"], "accent2": c["accent2"], "hook_emoji": plan["dest"][first]["emoji"],
            "cta_button": s["cta_button"], "offers": offers, "steps": s["steps"][:4],
            "price_note": s.get("price_note") or f"yrh.ai · {human_date(plan)}", "scenes": s["scenes"],
            **({"bill_text": "! ! !"} if cur(plan) else {})}
    json.dump(spec, open(os.path.join(jdir(job), "spec.json"), "w"), ensure_ascii=False, indent=1)
    title = s["title"][:95]
    utm = f"utm_source=youtube&utm_medium=shorts&utm_campaign={plan['job']}"
    links = []
    for k in plan["pool"]:
        cd = plan["prices"][k]["card"]
        links.append(f"{plan['dest'][k]['emoji']} {s['offer_labels'][k]} {fmt_plan(cd['gb'], cd['days'])} {money(plan, cd['price'])}: "
                     f"https://yrh.ai/product/{plan['dest'][k]['slug']}/?{utm}")
    first_line = s["description"].split("\n")[0]
    rest = "\n".join(s["description"].split("\n")[1:])
    desc = (f"{first_line}\n👉 https://yrh.ai/product/{plan['dest'][first]['slug']}/?{utm}\n\n" + "\n".join(links)
            + f"\n\n{rest}\n\n📲 YRH eSIM app: https://yrh.ai/?{utm} (Get the app)\n#Shorts")
    meta = {"title": title, "description": desc, "tags": s["tags"],
            "voice": c["voice"], "music": plan["music"], "publish_at": plan["publish_at"]}
    json.dump(meta, open(os.path.join(jdir(job), "meta.json"), "w"), ensure_ascii=False, indent=1)
    lines = "\n\n".join(sc["voice"] for sc in s["scenes"])
    tts = (f"{s.get('tts_style', '')} Speak in {c['language']}. Leave a clear one-second pause between each line. "
           f"Say the brand as 'Y R H eSIM' and the website as 'Y R H dot A I'.\n\n{lines}")
    open(os.path.join(jdir(job), "tts.txt"), "w", encoding="utf-8").write(tts)
    print(tts)


def cmd_done(job, vid):
    st = load_state()
    st["history"].append({"job": job, "videoId": vid, "at": datetime.datetime.utcnow().isoformat() + "Z"})
    st["day"] += 1
    json.dump(st, open(STATE, "w"), indent=1)
    print("next day index", st["day"])


if __name__ == "__main__":
    a = sys.argv[1:]
    {"next": lambda: cmd_next(), "prices": lambda: cmd_prices(*a[1:4]), "prompt": lambda: cmd_prompt(a[1]),
     "review": lambda: cmd_review(a[1], a[2]), "spec": lambda: cmd_spec(a[1], a[2]),
     "done": lambda: cmd_done(a[1], a[2])}[a[0]]()
