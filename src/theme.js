// Departure-board palette: airline navy, paper, and one signal yellow for prices and the buy action.
export const C = {
  navy: '#102233',
  navySoft: '#1E3A52',
  paper: '#EEF2F5',
  ticket: '#FFFFFF',
  yellow: '#FFC93C',
  ink: '#102233',
  slate: '#55677A',
  line: '#D5DDE5',
  onNavy: '#FFFFFF',
  onNavyMuted: '#A9BCCD',
  danger: '#B42318',
};

export const T = {
  hero: { fontSize: 30, lineHeight: 36, fontWeight: '800', letterSpacing: -0.5 },
  title: { fontSize: 22, lineHeight: 28, fontWeight: '800' },
  section: { fontSize: 17, lineHeight: 22, fontWeight: '700' },
  body: { fontSize: 15, lineHeight: 22 },
  small: { fontSize: 13, lineHeight: 18 },
};

// Row direction and text alignment for right-to-left languages.
export const dir = (rtl) => ({
  row: { flexDirection: rtl ? 'row-reverse' : 'row' },
  text: { textAlign: rtl ? 'right' : 'left', writingDirection: rtl ? 'rtl' : 'ltr' },
});
