import React, { useMemo, useState } from 'react';
import { View, Text, TextInput, FlatList, Pressable, ScrollView, ActivityIndicator, StyleSheet } from 'react-native';
import { C, T, dir } from '../theme';
import { t, formatPrice, countryName, fold, LANGS } from '../i18n';
import { POPULAR } from '../config';

export default function Home({ lang, rtl, setLang, destinations, status, onRetry, onOpen, topInset }) {
  const [q, setQ] = useState('');
  const d = dir(rtl);

  // Display name in the chosen language, sorted for that language.
  const list = useMemo(() => {
    const named = destinations.map((x) => ({ ...x, label: countryName(lang, x.code, x.name) }));
    return named.sort((a, b) => a.label.localeCompare(b.label, lang));
  }, [destinations, lang]);

  const popular = useMemo(
    () => POPULAR.map((code) => list.find((x) => x.code === code)).filter(Boolean),
    [list]
  );

  const query = fold(q.trim());
  const results = query
    ? list.filter((x) => fold(x.label).includes(query) || fold(x.name).includes(query) || x.code === query)
    : list;

  const header = (
    <View>
      <View style={[styles.hero, { paddingTop: topInset + 16 }]}>
        <View style={[styles.topRow, d.row]}>
          <Text style={styles.brand}>YRH eSIM</Text>
          <View style={[styles.langs, d.row]} accessibilityRole="radiogroup" accessibilityLabel={t(lang, 'language')}>
            {LANGS.map((l) => (
              <Pressable
                key={l.code}
                onPress={() => setLang(l.code)}
                accessibilityRole="radio"
                accessibilityState={{ selected: l.code === lang }}
                hitSlop={6}
                style={[styles.lang, l.code === lang && styles.langOn]}
              >
                <Text style={[styles.langText, l.code === lang && styles.langTextOn]}>{l.label}</Text>
              </Pressable>
            ))}
          </View>
        </View>
        <Text style={[styles.tagline, d.text]}>{t(lang, 'tagline')}</Text>
        <TextInput
          value={q}
          onChangeText={setQ}
          placeholder={t(lang, 'search')}
          placeholderTextColor={C.slate}
          style={[styles.search, d.text]}
          autoCorrect={false}
          returnKeyType="search"
          clearButtonMode="while-editing"
          accessibilityLabel={t(lang, 'search')}
        />
      </View>

      {!query && popular.length > 0 ? (
        <View style={styles.block}>
          <Text style={[styles.section, d.text]}>{t(lang, 'popular')}</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={[styles.chips, d.row]}
          >
            {popular.map((x) => (
              <Pressable
                key={x.id}
                onPress={() => onOpen(x)}
                accessibilityRole="button"
                style={({ pressed }) => [styles.chip, pressed && styles.pressed]}
              >
                <Text style={styles.chipFlag}>{x.flag}</Text>
                <Text style={styles.chipName} numberOfLines={1}>
                  {x.label}
                </Text>
                <Text style={styles.chipPrice}>{t(lang, 'from', { price: formatPrice(lang, x.fromPrice) })}</Text>
              </Pressable>
            ))}
          </ScrollView>
        </View>
      ) : null}

      {status === 'ready' && results.length > 0 ? (
        <Text style={[styles.section, styles.listTitle, d.text]}>{t(lang, 'all')}</Text>
      ) : null}
    </View>
  );

  let empty = null;
  if (status === 'loading') {
    empty = (
      <View style={styles.state}>
        <ActivityIndicator color={C.navy} size="large" />
        <Text style={styles.stateText}>{t(lang, 'loading')}</Text>
      </View>
    );
  } else if (status === 'error') {
    empty = (
      <View style={styles.state}>
        <Text style={[styles.stateText, { textAlign: 'center' }]}>{t(lang, 'loadError')}</Text>
        <Pressable onPress={onRetry} accessibilityRole="button" style={styles.retry}>
          <Text style={styles.retryText}>{t(lang, 'retry')}</Text>
        </Pressable>
      </View>
    );
  } else if (query) {
    empty = (
      <View style={styles.state}>
        <Text style={[styles.stateText, { textAlign: 'center' }]}>{t(lang, 'noResults', { q: q.trim() })}</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={status === 'ready' ? results : []}
      keyExtractor={(x) => String(x.id)}
      ListHeaderComponent={header}
      ListEmptyComponent={empty}
      keyboardShouldPersistTaps="handled"
      keyboardDismissMode="on-drag"
      contentContainerStyle={styles.content}
      initialNumToRender={20}
      renderItem={({ item }) => (
        <Pressable
          onPress={() => onOpen(item)}
          accessibilityRole="button"
          style={({ pressed }) => [styles.row, d.row, pressed && styles.pressed]}
        >
          <Text style={styles.rowFlag}>{item.flag}</Text>
          <Text style={[styles.rowName, d.text]} numberOfLines={1}>
            {item.label}
          </Text>
          <Text style={styles.rowPrice}>{t(lang, 'from', { price: formatPrice(lang, item.fromPrice) })}</Text>
        </Pressable>
      )}
    />
  );
}

const styles = StyleSheet.create({
  content: { paddingBottom: 24 },
  hero: { backgroundColor: C.navy, paddingHorizontal: 20, paddingBottom: 22 },
  topRow: { alignItems: 'center', justifyContent: 'space-between' },
  brand: { color: C.onNavy, fontSize: 18, fontWeight: '800', letterSpacing: 0.3 },
  langs: { gap: 4 },
  lang: { minWidth: 36, height: 32, borderRadius: 8, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 6 },
  langOn: { backgroundColor: C.navySoft },
  langText: { color: C.onNavyMuted, fontSize: 14, fontWeight: '700' },
  langTextOn: { color: C.onNavy },
  tagline: { ...T.hero, color: C.onNavy, marginTop: 22, marginBottom: 18 },
  search: {
    backgroundColor: C.ticket,
    borderRadius: 12,
    minHeight: 52,
    paddingHorizontal: 16,
    fontSize: 16,
    color: C.ink,
  },
  block: { paddingTop: 22 },
  section: { ...T.section, color: C.ink, paddingHorizontal: 20, marginBottom: 12 },
  listTitle: { marginTop: 24 },
  chips: { paddingHorizontal: 20, gap: 10 },
  chip: { width: 128, backgroundColor: C.ticket, borderRadius: 14, padding: 14 },
  chipFlag: { fontSize: 30, marginBottom: 8 },
  chipName: { ...T.body, color: C.ink, fontWeight: '700' },
  chipPrice: { ...T.small, color: C.slate, marginTop: 2 },
  row: {
    alignItems: 'center',
    paddingHorizontal: 20,
    minHeight: 58,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: C.line,
    backgroundColor: C.paper,
    gap: 12,
  },
  rowFlag: { fontSize: 24 },
  rowName: { ...T.body, color: C.ink, fontWeight: '600', flex: 1 },
  rowPrice: { ...T.small, color: C.slate },
  pressed: { opacity: 0.6 },
  state: { alignItems: 'center', paddingHorizontal: 32, paddingVertical: 48, gap: 16 },
  stateText: { ...T.body, color: C.slate },
  retry: { backgroundColor: C.navy, borderRadius: 10, paddingHorizontal: 22, minHeight: 44, justifyContent: 'center' },
  retryText: { color: C.onNavy, fontWeight: '700', fontSize: 15 },
});
