import { SHOP_URL } from './config';

// Two-letter code -> flag emoji. Regional plans (e.g. "aukus-3") get a globe.
export function flagFor(code) {
  if (!code || !/^[a-z]{2}$/i.test(code)) return '🌍';
  const base = 0x1f1e6;
  const up = code.toUpperCase();
  return String.fromCodePoint(base + up.charCodeAt(0) - 65, base + up.charCodeAt(1) - 65);
}

// Product descriptions carry specs like <li data-spec="hotspot"><strong>Hotspot:</strong> Yes</li>
function readSpec(html, key) {
  if (!html) return null;
  const re = new RegExp('data-(?:feature|spec)="' + key + '"[^>]*>[\\s\\S]*?</strong>\\s*([^<]+)', 'i');
  const m = html.match(re);
  return m ? m[1].trim() : null;
}

// Plan titles look like "Spain 3GB 30Days" or "Spain 2GB/Day 7Days".
export function parsePlan(title) {
  const daily = title.match(/(\d+(?:\.\d+)?)\s*(GB|MB)\s*\/\s*Day/i);
  const amount = daily || title.match(/(\d+(?:\.\d+)?)\s*(GB|MB)/i);
  const days = title.match(/(\d+)\s*Days?\b/i);
  return {
    data: amount ? `${amount[1]} ${amount[2].toUpperCase()}` : null,
    perDay: Boolean(daily),
    days: days ? parseInt(days[1], 10) : null,
  };
}

const yes = (v) => (v ? /^yes/i.test(v) : null);

export function toDestination(p) {
  const code = (p.handle || '').split('_')[0].toLowerCase();
  const plans = (p.variants || [])
    .filter((v) => v.available !== false)
    .map((v) => ({ id: v.id, title: v.title, price: parseFloat(v.price), ...parsePlan(v.title) }))
    .filter((v) => !Number.isNaN(v.price))
    .sort((a, b) => a.price - b.price || (a.days || 0) - (b.days || 0));
  return {
    id: p.id,
    handle: p.handle,
    code,
    flag: flagFor(code),
    name: p.title.replace(/\s*eSIM\s*$/i, '').trim(),
    plans,
    fromPrice: plans.length ? plans[0].price : null,
    hotspot: yes(readSpec(p.body_html, 'hotspot')),
    topUp: yes(readSpec(p.body_html, 'top-up')),
    network: readSpec(p.body_html, 'networks'),
  };
}

// Loads the public catalog (about 250 destinations). No API key needed.
export async function fetchDestinations() {
  const all = [];
  for (let page = 1; page <= 5; page++) {
    const res = await fetch(`${SHOP_URL}/products.json?limit=250&page=${page}`);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const json = await res.json();
    const items = json.products || [];
    all.push(...items);
    if (items.length < 250) break;
  }
  return all
    .filter((p) => p.product_type === 'eSIM' || /esim/i.test(p.title))
    .map(toDestination)
    .filter((d) => d.plans.length > 0);
}

// Shopify cart link: opens checkout with this one plan in the cart.
export const checkoutUrl = (variantId) => `${SHOP_URL}/cart/${variantId}:1`;

export const pageUrl = (handle) => `${SHOP_URL}/pages/${handle}`;
