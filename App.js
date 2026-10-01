import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, Pressable, BackHandler, I18nManager, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import { ShopifyCheckoutSheetProvider, ColorScheme } from '@shopify/checkout-sheet-kit';
import { C } from './src/theme';
import { t, deviceLang, isRTL } from './src/i18n';
import { fetchDestinations } from './src/shopify';
import Home from './src/screens/Home';
import Destination from './src/screens/Destination';
import Help from './src/screens/Help';

// Layout direction is handled per screen so the language can change without restarting the app.
try {
  I18nManager.allowRTL(false);
  I18nManager.forceRTL(false);
} catch (e) {}

function Root() {
  const insets = useSafeAreaInsets();
  const [lang, setLang] = useState(deviceLang());
  const [tab, setTab] = useState('dest');
  const [open, setOpen] = useState(null);
  const [destinations, setDestinations] = useState([]);
  const [status, setStatus] = useState('loading');
  const rtl = isRTL(lang);

  const load = useCallback(() => {
    setStatus('loading');
    fetchDestinations()
      .then((list) => {
        setDestinations(list);
        setStatus('ready');
      })
      .catch(() => setStatus('error'));
  }, []);

  useEffect(load, [load]);

  // Android back button: close the destination first, then the Help tab.
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (open) {
        setOpen(null);
        return true;
      }
      if (tab !== 'dest') {
        setTab('dest');
        return true;
      }
      return false;
    });
    return () => sub.remove();
  }, [open, tab]);

  let screen;
  if (open) {
    screen = <Destination dest={open} lang={lang} rtl={rtl} onBack={() => setOpen(null)} topInset={insets.top} />;
  } else if (tab === 'help') {
    screen = <Help lang={lang} rtl={rtl} topInset={insets.top} />;
  } else {
    screen = (
      <Home
        lang={lang}
        rtl={rtl}
        setLang={setLang}
        destinations={destinations}
        status={status}
        onRetry={load}
        onOpen={setOpen}
        topInset={insets.top}
      />
    );
  }

  const tabs = [
    { key: 'dest', label: t(lang, 'tabDest') },
    { key: 'help', label: t(lang, 'tabHelp') },
  ];
  const active = open ? 'dest' : tab;

  return (
    <View style={styles.app}>
      <StatusBar style={tab === 'help' && !open ? 'dark' : 'light'} />
      <View style={styles.screen}>{screen}</View>
      <View
        style={[styles.tabs, { paddingBottom: Math.max(insets.bottom, 8), flexDirection: rtl ? 'row-reverse' : 'row' }]}
        accessibilityRole="tablist"
      >
        {tabs.map((x) => (
          <Pressable
            key={x.key}
            onPress={() => {
              setOpen(null);
              setTab(x.key);
            }}
            accessibilityRole="tab"
            accessibilityState={{ selected: active === x.key }}
            style={styles.tab}
          >
            <View style={[styles.tabMark, active === x.key && styles.tabMarkOn]} />
            <Text style={[styles.tabText, active === x.key && styles.tabTextOn]}>{x.label}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

// In-app checkout sheet, coloured to match the app.
const checkoutConfig = {
  colorScheme: ColorScheme.light,
  preloading: true,
  colors: {
    android: {
      backgroundColor: C.paper,
      progressIndicator: C.navy,
      headerBackgroundColor: C.navy,
      headerTextColor: C.onNavy,
    },
    ios: { backgroundColor: C.paper, tintColor: C.navy },
  },
};

export default function App() {
  return (
    <SafeAreaProvider>
      <ShopifyCheckoutSheetProvider configuration={checkoutConfig}>
        <Root />
      </ShopifyCheckoutSheetProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: C.paper },
  screen: { flex: 1 },
  tabs: { backgroundColor: C.ticket, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: C.line, paddingTop: 6 },
  tab: { flex: 1, alignItems: 'center', justifyContent: 'center', minHeight: 48 },
  tabMark: { width: 24, height: 3, borderRadius: 2, marginBottom: 6, backgroundColor: 'transparent' },
  tabMarkOn: { backgroundColor: C.yellow },
  tabText: { fontSize: 14, fontWeight: '600', color: C.slate },
  tabTextOn: { color: C.navy, fontWeight: '800' },
});
