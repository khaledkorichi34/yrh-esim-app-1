import React from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { C, T, dir } from '../theme';
import { t, daysLabel, formatPrice } from '../i18n';

// A plan drawn as a boarding pass: data and validity on the stub,
// a perforated tear line, then the price and the buy action.
export default function PlanTicket({ plan, lang, rtl, busy, onBuy }) {
  const d = dir(rtl);
  const data = plan.data ? (plan.perDay ? t(lang, 'perDay', { data: plan.data }) : plan.data) : plan.title;
  const days = daysLabel(lang, plan.days);
  const price = formatPrice(lang, plan.price);

  return (
    <View style={[styles.ticket, d.row]}>
      <View style={styles.stub}>
        <Text style={[styles.data, d.text]} numberOfLines={1} adjustsFontSizeToFit>
          {data}
        </Text>
        {days ? <Text style={[styles.days, d.text]}>{days}</Text> : null}
      </View>

      <View style={styles.tear} importantForAccessibility="no-hide-descendants">
        <View style={[styles.notch, styles.notchTop]} />
        {Array.from({ length: 7 }).map((_, i) => (
          <View key={i} style={styles.dash} />
        ))}
        <View style={[styles.notch, styles.notchBottom]} />
      </View>

      <View style={styles.side}>
        <Text style={styles.price}>{price}</Text>
        <Pressable
          onPress={onBuy}
          disabled={busy}
          accessibilityRole="button"
          accessibilityLabel={`${t(lang, 'buy')}: ${data}, ${days}, ${price}`}
          style={({ pressed }) => [styles.buy, pressed && styles.buyPressed]}
        >
          {busy ? <ActivityIndicator color={C.navy} /> : <Text style={styles.buyText}>{t(lang, 'buy')}</Text>}
        </Pressable>
      </View>
    </View>
  );
}

const NOTCH = 14;

const styles = StyleSheet.create({
  ticket: {
    backgroundColor: C.ticket,
    borderRadius: 14,
    marginBottom: 14,
    minHeight: 104,
    alignItems: 'stretch',
  },
  stub: { flex: 1, justifyContent: 'center', paddingHorizontal: 18, paddingVertical: 16 },
  data: { color: C.ink, fontSize: 28, lineHeight: 34, fontWeight: '800', letterSpacing: -0.5 },
  days: { ...T.body, color: C.slate, marginTop: 2 },
  tear: { width: NOTCH, alignItems: 'center', justifyContent: 'space-evenly', paddingVertical: 14 },
  dash: { width: 2, height: 6, borderRadius: 1, backgroundColor: C.line },
  notch: {
    position: 'absolute',
    width: NOTCH,
    height: NOTCH,
    borderRadius: NOTCH / 2,
    backgroundColor: C.paper,
  },
  notchTop: { top: -NOTCH / 2 },
  notchBottom: { bottom: -NOTCH / 2 },
  side: { width: 128, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 12, paddingVertical: 14 },
  price: { color: C.ink, fontSize: 19, fontWeight: '800', marginBottom: 10, fontVariant: ['tabular-nums'] },
  buy: {
    alignSelf: 'stretch',
    backgroundColor: C.yellow,
    borderRadius: 10,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buyPressed: { opacity: 0.75 },
  buyText: { color: C.navy, fontSize: 16, fontWeight: '800' },
});
