import React, { useState } from 'react';
import { View, Text, ScrollView, Pressable, StyleSheet } from 'react-native';
import { C, T, dir } from '../theme';
import { t } from '../i18n';
import { GUIDE, FAQ } from '../content';

function Header({ title, lang, rtl, onBack, topInset }) {
  const d = dir(rtl);
  return (
    <View style={[styles.head, { paddingTop: topInset + 8 }]}>
      <Pressable onPress={onBack} accessibilityRole="button" hitSlop={10} style={[styles.back, d.row]}>
        <Text style={styles.backText}>{rtl ? '›' : '‹'}</Text>
        <Text style={styles.backText}>{t(lang, 'back')}</Text>
      </Pressable>
      <Text style={[styles.title, d.text]} accessibilityRole="header">
        {title}
      </Text>
    </View>
  );
}

export function Guide({ lang, rtl, onBack, topInset }) {
  const d = dir(rtl);
  const g = GUIDE[lang] || GUIDE.en;

  const steps = (items) =>
    items.map((text, i) => (
      <View key={i} style={[styles.step, d.row]}>
        <Text style={styles.num}>{i + 1}</Text>
        <Text style={[styles.stepText, d.text]}>{text}</Text>
      </View>
    ));

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Header title={t(lang, 'guide')} lang={lang} rtl={rtl} onBack={onBack} topInset={topInset} />
      <View style={styles.body}>
        <Text style={[styles.section, d.text]}>{t(lang, 'guideBefore')}</Text>
        {g.before.map((text, i) => (
          <View key={i} style={[styles.bullet, d.row]}>
            <View style={styles.dot} />
            <Text style={[styles.stepText, d.text]}>{text}</Text>
          </View>
        ))}

        <Text style={[styles.section, styles.gap, d.text]}>iPhone</Text>
        {steps(g.iphone)}

        <Text style={[styles.section, styles.gap, d.text]}>{t(lang, 'guideAndroid')}</Text>
        {steps(g.android)}

        <View style={styles.helpCard}>
          <Text style={[styles.helpTitle, d.text]}>{t(lang, 'guideHelp')}</Text>
          <Text style={[styles.helpText, d.text]}>{g.help}</Text>
        </View>
      </View>
    </ScrollView>
  );
}

export function Faq({ lang, rtl, onBack, topInset }) {
  const d = dir(rtl);
  const items = FAQ[lang] || FAQ.en;
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Header title={t(lang, 'faq')} lang={lang} rtl={rtl} onBack={onBack} topInset={topInset} />
      <View style={styles.body}>
        <View style={styles.list}>
          {items.map((item, i) => {
            const isOpen = openIndex === i;
            return (
              <View key={i} style={i > 0 && styles.divider}>
                <Pressable
                  onPress={() => setOpenIndex(isOpen ? null : i)}
                  accessibilityRole="button"
                  accessibilityState={{ expanded: isOpen }}
                  style={({ pressed }) => [styles.question, d.row, pressed && styles.pressed]}
                >
                  <Text style={[styles.questionText, d.text]}>{item.q}</Text>
                  <Text style={styles.toggle}>{isOpen ? '−' : '+'}</Text>
                </Pressable>
                {isOpen ? <Text style={[styles.answer, d.text]}>{item.a}</Text> : null}
              </View>
            );
          })}
        </View>
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
  title: { ...T.title, fontSize: 26, lineHeight: 32, color: C.onNavy, marginTop: 8 },
  body: { paddingHorizontal: 20, paddingTop: 22 },
  section: { ...T.section, color: C.ink, marginBottom: 14 },
  gap: { marginTop: 22 },
  step: { gap: 14, alignItems: 'flex-start', marginBottom: 16 },
  num: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: C.navy,
    color: C.yellow,
    textAlign: 'center',
    lineHeight: 30,
    fontWeight: '800',
    fontSize: 14,
    overflow: 'hidden',
  },
  stepText: { ...T.body, color: C.ink, flex: 1, paddingTop: 4 },
  bullet: { gap: 14, alignItems: 'flex-start', marginBottom: 12 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: C.yellow, marginTop: 11, marginHorizontal: 11 },
  helpCard: { backgroundColor: C.ticket, borderRadius: 14, padding: 18, marginTop: 14 },
  helpTitle: { ...T.section, color: C.ink, marginBottom: 6 },
  helpText: { ...T.body, color: C.slate },
  list: { backgroundColor: C.ticket, borderRadius: 14, overflow: 'hidden' },
  divider: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: C.line },
  question: { alignItems: 'center', justifyContent: 'space-between', minHeight: 58, paddingHorizontal: 18, paddingVertical: 14, gap: 12 },
  questionText: { ...T.body, color: C.ink, fontWeight: '700', flex: 1 },
  toggle: { color: C.slate, fontSize: 22, width: 20, textAlign: 'center' },
  answer: { ...T.body, color: C.slate, paddingHorizontal: 18, paddingBottom: 16 },
  pressed: { backgroundColor: C.paper },
});
