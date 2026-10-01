import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Pressable, StyleSheet } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { useShopifyCheckoutSheet } from '@shopify/checkout-sheet-kit';
import { C, T, dir } from '../theme';
import { t, countryName } from '../i18n';
import { checkoutUrl } from '../shopify';
import PlanTicket from '../components/PlanTicket';

export default function Destination({ dest, lang, rtl, onBack, topInset }) {
  const d = dir(rtl);
  const checkout = useShopifyCheckoutSheet();
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState(null); // 'paid' | 'sent' | 'error'
  const [paidEmail, setPaidEmail] = useState(null);

  // Checkout runs in a sheet inside the app. These events tell us how it ended.
  useEffect(() => {
    const subs = [
      checkout.addEventListener('completed', (event) => {
        setPaidEmail((event && event.orderDetails && event.orderDetails.email) || null);
        setNotice('paid');
      }),
      checkout.addEventListener('error', () => setNotice('error')),
      checkout.addEventListener('close', () => setBusyId(null)),
    ];
    return () => subs.forEach((s) => s && s.remove && s.remove());
  }, [checkout]);

  async function buy(plan) {
    setBusyId(plan.id);
    setNotice(null);
    const url = checkoutUrl(plan.id);
    try {
      // Payment happens here, inside the app. After payment the store's
      // automation orders the eSIM and emails the install link.
      checkout.present(url);
      setTimeout(() => setBusyId(null), 1500);
    } catch (e) {
      // If the in-app sheet is unavailable on this phone, fall back to a browser tab.
      try {
        await WebBrowser.openBrowserAsync(url, { toolbarColor: C.navy, controlsColor: C.yellow, showTitle: true });
        setNotice('sent');
      } catch (e2) {
        setNotice('error');
      } finally {
        setBusyId(null);
      }
    }
  }

  const facts = [
    dest.hotspot != null && { k: t(lang, 'hotspot'), v: t(lang, dest.hotspot ? 'yes' : 'no') },
    dest.topUp != null && { k: t(lang, 'topUp'), v: t(lang, dest.topUp ? 'yes' : 'no') },
    dest.network && { k: t(lang, 'network'), v: dest.network.replace(/^[A-Z]{2}\s*-\s*/, '') },
  ].filter(Boolean);

  const showCard = notice === 'paid' || notice === 'sent';
  const cardTitle = notice === 'paid' ? t(lang, 'paidTitle') : t(lang, 'sentTitle');
  const cardText =
    notice === 'paid'
      ? paidEmail
        ? t(lang, 'paidTextEmail', { email: paidEmail })
        : t(lang, 'paidText')
      : t(lang, 'sentText');

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={[styles.head, { paddingTop: topInset + 8 }]}>
        <Pressable onPress={onBack} accessibilityRole="button" hitSlop={10} style={[styles.back, d.row]}>
          <Text style={styles.backText}>{rtl ? '›' : '‹'}</Text>
          <Text style={styles.backText}>{t(lang, 'back')}</Text>
        </Pressable>
        <View style={[styles.titleRow, d.row]}>
          <Text style={styles.flag}>{dest.flag}</Text>
          <Text style={[styles.title, d.text]} accessibilityRole="header">
            {countryName(lang, dest.code, dest.name)}
          </Text>
        </View>
        {facts.length > 0 ? (
          <View style={[styles.facts, d.row]}>
            {facts.map((f) => (
              <View key={f.k} style={styles.fact}>
                <Text style={[styles.factKey, d.text]}>{f.k}</Text>
                <Text style={[styles.factVal, d.text]} numberOfLines={1}>
                  {f.v}
                </Text>
              </View>
            ))}
          </View>
        ) : null}
      </View>

      <View style={styles.body}>
        {showCard ? (
          <View style={styles.sent} accessibilityLiveRegion="polite">
            <Text style={[styles.sentTitle, d.text]}>{cardTitle}</Text>
            <Text style={[styles.sentText, d.text]}>{cardText}</Text>
            <Pressable onPress={() => setNotice(null)} accessibilityRole="button" style={[styles.sentOk, rtl && styles.sentOkRtl]}>
              <Text style={styles.sentOkText}>{t(lang, 'ok')}</Text>
            </Pressable>
          </View>
        ) : null}
        {notice === 'error' ? (
          <Text style={[styles.error, d.text]} accessibilityLiveRegion="polite">
            {t(lang, 'checkoutError')}
          </Text>
        ) : null}

        <Text style={[styles.section, d.text]}>{t(lang, 'choosePlan')}</Text>
        {dest.plans.map((p) => (
          <PlanTicket
            key={p.id}
            plan={p}
            lang={lang}
            rtl={rtl}
            busy={busyId === p.id}
            onBuy={() => buy(p)}
          />
        ))}
        <Text style={[styles.note, d.text]}>{t(lang, 'dataOnly')}</Text>
        <Text style={[styles.note, d.text]}>{t(lang, 'compat')}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.paper },
  content: { paddingBottom: 32 },
  head: { backgroundColor: C.navy, paddingHorizontal: 20, paddingBottom: 22 },
  back: { alignItems: 'center', gap: 6, minHeight: 44, alignSelf: 'flex-start' },
  backText: { color: C.onNavy, fontSize: 16, fontWeight: '600' },
  titleRow: { alignItems: 'center', gap: 12, marginTop: 8 },
  flag: { fontSize: 40 },
  title: { ...T.title, fontSize: 28, lineHeight: 34, color: C.onNavy, flexShrink: 1 },
  facts: { marginTop: 18, gap: 20, flexWrap: 'wrap' },
  fact: { maxWidth: 160 },
  factKey: { ...T.small, color: C.onNavyMuted },
  factVal: { ...T.body, color: C.onNavy, fontWeight: '700' },
  body: { paddingHorizontal: 16, paddingTop: 20 },
  section: { ...T.section, color: C.ink, marginBottom: 14, paddingHorizontal: 4 },
  note: { ...T.small, color: C.slate, paddingHorizontal: 4, marginTop: 6 },
  sent: { backgroundColor: C.navy, borderRadius: 14, padding: 18, marginBottom: 20 },
  sentTitle: { ...T.section, color: C.yellow, marginBottom: 6 },
  sentText: { ...T.body, color: C.onNavy },
  sentOk: { alignSelf: 'flex-start', marginTop: 12, minHeight: 40, justifyContent: 'center', paddingHorizontal: 4 },
  sentOkRtl: { alignSelf: 'flex-end' },
  sentOkText: { color: C.yellow, fontSize: 15, fontWeight: '800' },
  error: { ...T.body, color: C.danger, marginBottom: 16, paddingHorizontal: 4 },
});
