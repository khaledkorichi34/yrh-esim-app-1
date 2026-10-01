import { getLocales } from 'expo-localization';
import { CURRENCY } from './config';

export const LANGS = [
  { code: 'en', label: 'EN' },
  { code: 'ar', label: 'ع' },
  { code: 'fr', label: 'FR' },
  { code: 'es', label: 'ES' },
];

const S = {
  en: {
    tagline: 'Mobile data for your trip, ready in minutes.',
    search: 'Where are you going?',
    popular: 'Popular destinations',
    all: 'All destinations',
    from: 'from {price}',
    loading: 'Loading destinations…',
    loadError: "Couldn't load destinations. Check your internet connection and try again.",
    retry: 'Try again',
    noResults: 'No destination matches “{q}”. Try another spelling or the name in English.',
    back: 'Back',
    choosePlan: 'Choose a plan',
    buy: 'Buy',
    perDay: '{data} per day',
    hotspot: 'Hotspot',
    topUp: 'Top-up',
    yes: 'Yes',
    no: 'No',
    network: 'Network',
    dataOnly: 'Data only. Calls and messages work through apps like WhatsApp.',
    sentTitle: 'After you pay',
    sentText: "Your eSIM install link arrives by email within a few minutes. Check your spam folder if you don't see it.",
    paidTitle: 'Payment received',
    paidText: 'Your eSIM install link is on its way by email. It usually arrives within a few minutes.',
    paidTextEmail: 'Your eSIM install link is on its way to {email}. It usually arrives within a few minutes.',
    ok: 'OK',
    checkoutError: "Couldn't open checkout. Check your connection and try again.",
    tabDest: 'Destinations',
    tabHelp: 'Help',
    howTitle: 'How it works',
    step1: 'Choose a destination and a data plan.',
    step2: 'Pay securely. Your eSIM arrives by email within minutes.',
    step3: 'Open the email on your phone, tap install, and turn on the eSIM when you land.',
    compat: 'Your phone must support eSIM and be carrier-unlocked.',
    guide: 'Installation guide',
    faq: 'Support and FAQ',
    email: 'Email support',
    whatsapp: 'WhatsApp support',
    language: 'Language',
  },
  ar: {
    tagline: 'إنترنت الجوال لرحلتك، جاهز خلال دقائق.',
    search: 'إلى أين تسافر؟',
    popular: 'وجهات مطلوبة',
    all: 'كل الوجهات',
    from: 'ابتداءً من {price}',
    loading: 'جارٍ تحميل الوجهات…',
    loadError: 'تعذّر تحميل الوجهات. تحقق من اتصالك بالإنترنت وحاول مرة أخرى.',
    retry: 'حاول مرة أخرى',
    noResults: 'لا توجد وجهة تطابق «{q}». جرّب كتابة أخرى أو الاسم بالإنجليزية.',
    back: 'رجوع',
    choosePlan: 'اختر باقة',
    buy: 'اشترِ',
    perDay: '{data} يومياً',
    hotspot: 'مشاركة الإنترنت',
    topUp: 'الشحن الإضافي',
    yes: 'نعم',
    no: 'لا',
    network: 'الشبكة',
    dataOnly: 'بيانات فقط. المكالمات والرسائل تعمل عبر تطبيقات مثل واتساب.',
    sentTitle: 'بعد الدفع',
    sentText: 'يصلك رابط تثبيت الـ eSIM بالإيميل خلال دقائق. تحقق من مجلد الرسائل غير المرغوبة إن لم تجده.',
    paidTitle: 'تم استلام الدفع',
    paidText: 'رابط تثبيت الـ eSIM في طريقه إليك بالإيميل. يصل عادةً خلال دقائق.',
    paidTextEmail: 'رابط تثبيت الـ eSIM في طريقه إلى {email}. يصل عادةً خلال دقائق.',
    ok: 'حسناً',
    checkoutError: 'تعذّر فتح صفحة الدفع. تحقق من اتصالك وحاول مرة أخرى.',
    tabDest: 'الوجهات',
    tabHelp: 'المساعدة',
    howTitle: 'كيف تعمل',
    step1: 'اختر وجهتك وباقة البيانات.',
    step2: 'ادفع بأمان، وتصلك الـ eSIM بالإيميل خلال دقائق.',
    step3: 'افتح الإيميل على هاتفك، اضغط تثبيت، وفعّل الـ eSIM عند وصولك.',
    compat: 'يجب أن يدعم هاتفك eSIM وألا يكون مقفلاً على شبكة.',
    guide: 'دليل التثبيت',
    faq: 'الدعم والأسئلة الشائعة',
    email: 'راسل الدعم بالإيميل',
    whatsapp: 'الدعم عبر واتساب',
    language: 'اللغة',
  },
  fr: {
    tagline: 'Des données mobiles pour votre voyage, prêtes en quelques minutes.',
    search: 'Où partez-vous ?',
    popular: 'Destinations populaires',
    all: 'Toutes les destinations',
    from: 'dès {price}',
    loading: 'Chargement des destinations…',
    loadError: 'Impossible de charger les destinations. Vérifiez votre connexion et réessayez.',
    retry: 'Réessayer',
    noResults: 'Aucune destination ne correspond à « {q} ». Essayez une autre orthographe ou le nom en anglais.',
    back: 'Retour',
    choosePlan: 'Choisissez un forfait',
    buy: 'Acheter',
    perDay: '{data} par jour',
    hotspot: 'Partage de connexion',
    topUp: 'Recharge',
    yes: 'Oui',
    no: 'Non',
    network: 'Réseau',
    dataOnly: 'Données uniquement. Appels et messages via des applis comme WhatsApp.',
    sentTitle: 'Après le paiement',
    sentText: "Le lien d'installation de votre eSIM arrive par e-mail en quelques minutes. Vérifiez vos spams si vous ne le voyez pas.",
    paidTitle: 'Paiement reçu',
    paidText: "Le lien d'installation de votre eSIM arrive par e-mail, généralement en quelques minutes.",
    paidTextEmail: "Le lien d'installation de votre eSIM est envoyé à {email}. Il arrive généralement en quelques minutes.",
    ok: 'OK',
    checkoutError: 'Impossible d’ouvrir le paiement. Vérifiez votre connexion et réessayez.',
    tabDest: 'Destinations',
    tabHelp: 'Aide',
    howTitle: 'Comment ça marche',
    step1: 'Choisissez une destination et un forfait de données.',
    step2: 'Payez en toute sécurité. Votre eSIM arrive par e-mail en quelques minutes.',
    step3: "Ouvrez l'e-mail sur votre téléphone, appuyez sur installer et activez l'eSIM à l'arrivée.",
    compat: 'Votre téléphone doit être compatible eSIM et débloqué.',
    guide: "Guide d'installation",
    faq: 'Support et FAQ',
    email: 'Écrire au support',
    whatsapp: 'Support WhatsApp',
    language: 'Langue',
  },
  es: {
    tagline: 'Datos móviles para tu viaje, listos en minutos.',
    search: '¿A dónde viajas?',
    popular: 'Destinos populares',
    all: 'Todos los destinos',
    from: 'desde {price}',
    loading: 'Cargando destinos…',
    loadError: 'No se pudieron cargar los destinos. Revisa tu conexión e inténtalo de nuevo.',
    retry: 'Reintentar',
    noResults: 'Ningún destino coincide con «{q}». Prueba otra forma de escribirlo o el nombre en inglés.',
    back: 'Atrás',
    choosePlan: 'Elige un plan',
    buy: 'Comprar',
    perDay: '{data} al día',
    hotspot: 'Compartir conexión',
    topUp: 'Recarga',
    yes: 'Sí',
    no: 'No',
    network: 'Red',
    dataOnly: 'Solo datos. Llamadas y mensajes con apps como WhatsApp.',
    sentTitle: 'Después de pagar',
    sentText: 'El enlace de instalación de tu eSIM llega por correo en pocos minutos. Revisa la carpeta de spam si no lo ves.',
    paidTitle: 'Pago recibido',
    paidText: 'El enlace de instalación de tu eSIM va en camino por correo. Suele llegar en pocos minutos.',
    paidTextEmail: 'El enlace de instalación de tu eSIM va en camino a {email}. Suele llegar en pocos minutos.',
    ok: 'Entendido',
    checkoutError: 'No se pudo abrir el pago. Revisa tu conexión e inténtalo de nuevo.',
    tabDest: 'Destinos',
    tabHelp: 'Ayuda',
    howTitle: 'Cómo funciona',
    step1: 'Elige un destino y un plan de datos.',
    step2: 'Paga de forma segura. Tu eSIM llega por correo en minutos.',
    step3: 'Abre el correo en tu teléfono, pulsa instalar y activa la eSIM al llegar.',
    compat: 'Tu teléfono debe admitir eSIM y estar liberado.',
    guide: 'Guía de instalación',
    faq: 'Soporte y preguntas frecuentes',
    email: 'Escribir a soporte',
    whatsapp: 'Soporte por WhatsApp',
    language: 'Idioma',
  },
};

export function deviceLang() {
  try {
    const code = getLocales()[0]?.languageCode;
    return S[code] ? code : 'en';
  } catch (e) {
    return 'en';
  }
}

export function t(lang, key, vars) {
  let s = (S[lang] && S[lang][key]) || S.en[key] || key;
  if (vars) Object.keys(vars).forEach((k) => (s = s.replace('{' + k + '}', vars[k])));
  return s;
}

export const isRTL = (lang) => lang === 'ar';

export function daysLabel(lang, n) {
  if (n == null) return '';
  if (lang === 'ar') {
    if (n === 1) return 'يوم واحد';
    if (n === 2) return 'يومان';
    if (n <= 10) return `${n} أيام`;
    return `${n} يوماً`;
  }
  if (lang === 'fr') return n === 1 ? '1 jour' : `${n} jours`;
  if (lang === 'es') return n === 1 ? '1 día' : `${n} días`;
  return n === 1 ? '1 day' : `${n} days`;
}

const priceFmt = {};
export function formatPrice(lang, n) {
  if (n == null) return '';
  try {
    const loc = lang === 'ar' ? 'ar-u-nu-latn' : lang;
    if (!priceFmt[loc]) priceFmt[loc] = new Intl.NumberFormat(loc, { style: 'currency', currency: CURRENCY });
    return priceFmt[loc].format(n);
  } catch (e) {
    return '€' + n.toFixed(2);
  }
}

// Country names in the chosen language when the phone supports it; otherwise the store name.
const regionNames = {};
export function countryName(lang, code, fallback) {
  if (lang === 'en' || !code || !/^[a-z]{2}$/i.test(code)) return fallback;
  try {
    if (!regionNames[lang]) regionNames[lang] = new Intl.DisplayNames([lang], { type: 'region' });
    const name = regionNames[lang].of(code.toUpperCase());
    return name && name.toUpperCase() !== code.toUpperCase() ? name : fallback;
  } catch (e) {
    return fallback;
  }
}

// Lowercase and strip accents so "turquia" finds "Turquía".
export function fold(s) {
  const lower = (s || '').toLowerCase();
  try {
    return lower.normalize('NFD').replace(/[̀-ͯ]/g, '');
  } catch (e) {
    return lower;
  }
}
