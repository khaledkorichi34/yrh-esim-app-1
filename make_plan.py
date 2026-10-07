"""Finds plans that are pointless next to another plan of the same destination:
same or lower price elsewhere for at least as much data and at least as many days."""
import json, re, sys, collections
cat_dir, out = sys.argv[1], sys.argv[2]
products = []
for p in (1, 2, 3):
    d = json.load(open('%s/products-%d.json' % (cat_dir, p)))
    products += d.get('products', [])
print('products', len(products), 'variants', sum(len(p['variants']) for p in products))
items, backup, stats = [], [], collections.Counter()
unparsed = []
for pr in products:
    vs = []
    for v in pr['variants']:
        m = re.fullmatch(r'[A-Za-z0-9-]+_(\d+(?:\.\d+)?)_(\d+)', v['sku'] or '')
        if not m:
            unparsed.append(v['sku']); continue
        vs.append({'id': v['id'], 'sku': v['sku'], 'title': v['title'], 'price': float(v['price']), 'gb': float(m.group(1)), 'days': int(m.group(2))})
    drop = []
    for a in vs:
        for b in vs:
            if b is a: continue
            better_or_equal = b['price'] <= a['price'] and b['gb'] >= a['gb'] and b['days'] >= a['days']
            strictly = b['price'] < a['price'] or b['gb'] > a['gb'] or b['days'] > a['days']
            # identical offers: keep the one with the lower id
            if better_or_equal and (strictly or b['id'] < a['id']):
                drop.append(a); break
    assert len(drop) < len(pr['variants']), pr['handle']
    if drop:
        items.append({'p': pr['id'], 'v': ','.join('"gid://shopify/ProductVariant/%d"' % a['id'] for a in drop)})
        for a in drop:
            backup.append({'handle': pr['handle'], 'sku': a['sku'], 'title': a['title'], 'price': '%.2f' % a['price']})
            stats['%.2f' % a['price']] += 1
print('unparsed skus (never touched):', unparsed)
print('products affected', len(items), 'variants to remove', len(backup))
print('by price', dict(stats.most_common(8)))
json.dump({'items': items}, open(out + '/remove.json', 'w'))
json.dump(backup, open(out + '/removed-plans-backup.json', 'w'), indent=0)
for h in ('dz_package', 'th_package', 'es_package', 'tr_package', 'bi-2_package'):
    pr = next(p for p in products if p['handle'] == h)
    gone = {b['sku'] for b in backup if b['handle'] == h}
    print(h, '| keep:', [(v['sku'], v['price']) for v in pr['variants'] if v['sku'] not in gone], '| remove:', sorted(gone))
