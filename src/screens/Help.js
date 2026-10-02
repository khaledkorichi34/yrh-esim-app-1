import React from 'react';
import { View, Text, ScrollView, Pressable, Linking, StyleSheet } from 'react-native';
import { C, T, dir } from '../theme';
import { t } from '../i18n';
import { SUPPORT_EMAIL, SUPPORT_WHATSAPP } from '../config';

export default function Help({ lang, rtl, topInset, onOpenPage }) {
  const d = dir(rtl);

  const actions = [
    { label: t(lang, 'guide'), onPress: () => onOpenPage('guide') },
    { label: t(lang, 'faq'), onPress: () => onOpenPage('faq') },
    SUPPORT_EMAIL && { label: t(lang, 'email'), onPress: () => Linking.openURL(`mailto:${SUPPORT_EMAIL}`).catch(() => {}) },
    SUPPORT_WHATSAPP && {
      label: t(lang, 'whatsapp'),
      onPress: () => Linking.openURL(`https://wa.me/${SUPPORT_WHATSAPP}`).catch(() => {}),
    },
  ].filter(Boolean);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={[styles.content, { paddingTop: topInset + 24 }]}>
      <Text style={[styles.title, d.text]} accessibilityRole="header">
        {t(lang, 'howTitle')}
      </Text>

      {['step1', 'step2', 'step3'].map((k, i) => (
        <View key={k} style={[styles.step, d.row]}>
          <Text style={styles.num}>{i + 1}</Text>
          <Text style={[styles.stepText, d.text]}>{t(lang, k)}</Text>
        </View>
      ))}

      <Text style={[styles.compat, d.text]}>{t(lang, 'compat')}</Text>

      <View style={styles.actions}>
        {actions.map((a) => (
          <Pressable
            key={a.label}
            onPress={a.onPress}
            accessibilityRole="button"
            style={({ pressed }) => [styles.action, d.row, pressed && styles.pressed]}
          >
            <Text style={[styles.actionText, d.text]}>{a.label}</Text>
            <Text style={styles.chev}>{rtl ? '‹' : '›'}</Text>
          </Pressable>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.paper },
  content: { paddingHorizontal: 20, paddingBottom: 32 },
  title: { ...T.title, color: C.ink, marginBottom: 20 },
  step: { gap: 14, alignItems: 'flex-start', marginBottom: 18 },
  num: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: C.navy,
    color: C.yellow,
    textAlign: 'center',
    lineHeight: 32,
    fontWeight: '800',
    fontSize: 15,
    overflow: 'hidden',
  },
  stepText: { ...T.body, color: C.ink, flex: 1, paddingTop: 5 },
  compat: { ...T.small, color: C.slate, marginTop: 4, marginBottom: 24 },
  actions: { backgroundColor: C.ticket, borderRadius: 14, overflow: 'hidden' },
  action: {
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 56,
    paddingHorizontal: 18,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: C.line,
  },
  actionText: { ...T.body, color: C.ink, fontWeight: '600', flex: 1 },
  chev: { color: C.slate, fontSize: 22 },
  pressed: { backgroundColor: C.paper },
});
