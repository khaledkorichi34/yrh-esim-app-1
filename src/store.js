import { STORE_URL } from './config';

// Catalog and checkout from the yrh.ai WooCommerce store.
// The app shows exactly the plans and prices of the website: add a plan or change
// a price there and the app follows on its next refresh. No API key is needed.

// Two-letter code -> flag emoji. Regional plans (e.g. "eu-42") get a globe.
export function flagFor(code) {
  if (!code || !/^[a-z]{2}$/i.test(code)) return '🌍';
  const base = 0x1f1e6;
  const up = code.toUpperCase();
  return String.fromCodePoint(base + up.charCodeAt(0) - 65, base + up.charCodeAt(1) - 65);
}

// Product descriptions list specs as <li><strong>Hotspot:</strong> share your data...</li>
function readSpec(html, label) {
  if (!html) return null;
  const re = new RegExp('<strong>\\s*' + label + '\\s*:?\\s*</strong>\\s*:?\\s*([^<]+)', 'i');
  const m = html.match(re);
  return m ? m[1].replace(/&amp;/g, '&').replace(/&#8217;/g, "'").trim().replace(/\.$/, '') : null;
}

// Plan names look like "Spain 3GB 30Days", "Spain 2GB/Day 7Days",
// "Japan No-Throttling-Unlimited 7Days (KDDI)" or "Japan Unlimited-10Mbps 5Days (KDDI)".
export function parsePlan(title) {
  const daily = title.match(/(\d+(?:\.\d+)?)\s*(GB|MB)\s*\/\s*Day/i);
  const amount = daily || title.match(/(\d+(?:\.\d+)?)\s*(GB|MB)\b/i);
  const days = title.match(/(\d+)\s*Days?\b/i);
  let data = amount ? `${amount[1]} ${amount[2].toUpperCase()}` : null;
  let unlimited = null;
  if (!amount && /unlimited/i.test(title)) {
    const speed = title.match(/(\d+)\s*Mbps/i);
    unlimited = speed ? `${speed[1]} Mbps` : 'full';
  }
  return { data, unlimited, perDay: Boolean(daily), days: days ? parseInt(days[1], 10) : null };
}

async function getJson(path) {
  // Always ask the store, never a saved copy: prices must be the current ones.
  const res = await fetch(`${STORE_URL}/wp-json/wc/store/v1/${path}`, {
    cache: 'no-store',
    headers: { 'Cache-Control': 'no-cache', Accept: 'application/json' },
  });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const pages = parseInt(res.headers.get('X-WP-TotalPages') || '1', 10) || 1;
  return { items: await res.json(), pages };
}

// Reads every page of a Store API list: the first page tells how many there are,
// the rest are fetched together.
async function getAll(query) {
  const first = await getJson(`products?${query}&per_page=100&page=1`);
  const rest = [];
  for (let p = 2; p <= Math.min(first.pages, 40); p++) rest.push(getJson(`products?${query}&per_page=100&page=${p}`));
  const more = await Promise.all(rest);
  return first.items.concat(...more.map((r) => r.items));
}

const price = (prices) => {
  if (!prices || prices.price == null) return NaN;
  const minor = prices.currency_minor_unit == null ? 2 : prices.currency_minor_unit;
  return parseInt(prices.price, 10) / Math.pow(10, minor);
};

// Loads the whole catalog (about 240 destinations and 1,500 plans).
export async function fetchDestinations() {
  const [parents, variations] = await Promise.all([
    getAll('type=variable&_fields=id,name,sku,slug,description'),
    getAll('type=variation&_fields=id,parent,variation,prices,is_in_stock'),
  ]);

  const byParent = {};
  for (const v of variations) {
    if (v.is_in_stock === false) continue;
    const title = (v.variation || '').replace(/^[^:]*:\s*/, '').trim();
    const p = { id: v.id, parent: v.parent, title, price: price(v.prices), ...parsePlan(title) };
    if (Number.isNaN(p.price)) continue;
    (byParent[v.parent] = byParent[v.parent] || []).push(p);
  }

  return parents
    .map((p) => {
      const plans = (byParent[p.id] || []).sort((a, b) => a.price - b.price || (a.days || 0) - (b.days || 0));
      const code = (p.sku || p.slug || '').split('_')[0].toLowerCase();
      const hotspot = readSpec(p.description, 'Hotspot');
      const topUp = readSpec(p.description, 'Top-ups?');
      return {
        id: p.id,
        handle: p.slug,
        code,
        flag: flagFor(code),
        name: (p.name || '').replace(/\s*eSIM\s*$/i, '').trim(),
        plans,
        fromPrice: plans.length ? plans[0].price : null,
        hotspot: hotspot ? !/^no\b/i.test(hotspot) : null,
        topUp: topUp ? !/^no\b/i.test(topUp) : null,
        network: readSpec(p.description, 'Networks?'),
      };
    })
    .filter((d) => d.plans.length > 0);
}

// Opens the store checkout with only this plan in the cart.
export const checkoutUrl = (plan) =>
  `${STORE_URL}/checkout/?add-to-cart=${plan.parent}&variation_id=${plan.id}` +
  `&attribute_plan=${encodeURIComponent(plan.title)}&quantity=1`;
