// Installation guide and FAQ shown inside the app, in the four app languages.

export const GUIDE = {
  en: {
    before: [
      'Make sure your phone supports eSIM and is carrier-unlocked.',
      'Connect to Wi-Fi during installation.',
      'Open the email we sent after your purchase. It contains your install link.',
    ],
    iphone: [
      'Open the install link from the email on your iPhone, or go to Settings → Mobile Service (or Cellular) → Add eSIM.',
      'Choose Use QR Code and follow the steps on screen.',
      'Name the new line, for example Travel.',
      'When you arrive, set it as your data line and turn on Data Roaming for that line.',
    ],
    android: [
      'Open the install link from the email, or go to Settings → Connections → SIM manager → Add eSIM (Samsung), or Settings → Network & internet → SIMs → Add (Pixel).',
      'Scan the QR code or follow the install link.',
      'When you arrive, turn on the eSIM, choose it for mobile data and turn on Data Roaming for it.',
    ],
    help: "If something doesn't work, reply to your eSIM email with your order number and phone model, or email support from the Help tab.",
  },
  ar: {
    before: [
      'تأكد أن هاتفك يدعم eSIM وأنه غير مقفل على شبكة معينة.',
      'اتصل بشبكة Wi-Fi أثناء التثبيت.',
      'افتح الإيميل الذي أرسلناه بعد الشراء، ففيه رابط التثبيت.',
    ],
    iphone: [
      'افتح رابط التثبيت من الإيميل على هاتفك، أو اذهب إلى الإعدادات ← الخدمة الخلوية ← إضافة eSIM.',
      'اختر استخدام رمز QR واتبع الخطوات على الشاشة.',
      'سمِّ الخط الجديد، مثلاً: سفر.',
      'عند وصولك، اجعله خط البيانات وفعّل تجوال البيانات لهذا الخط.',
    ],
    android: [
      'افتح رابط التثبيت من الإيميل، أو اذهب إلى الإعدادات ← الاتصالات ← مدير SIM ← إضافة eSIM (سامسونج)، أو الإعدادات ← الشبكة والإنترنت ← شرائح SIM ← إضافة (بكسل).',
      'امسح رمز QR أو اتبع رابط التثبيت.',
      'عند وصولك، شغّل الـ eSIM واخترها لبيانات الجوال وفعّل تجوال البيانات لها.',
    ],
    help: 'إن لم يعمل شيء، فرد على إيميل الـ eSIM مع رقم طلبك ونوع هاتفك، أو راسل الدعم من تبويب المساعدة.',
  },
  fr: {
    before: [
      'Vérifiez que votre téléphone est compatible eSIM et débloqué.',
      "Connectez-vous au Wi-Fi pendant l'installation.",
      "Ouvrez l'e-mail envoyé après votre achat : il contient votre lien d'installation.",
    ],
    iphone: [
      "Ouvrez le lien d'installation de l'e-mail sur votre iPhone, ou allez dans Réglages → Service mobile (ou Données cellulaires) → Ajouter une eSIM.",
      "Choisissez Utiliser un code QR et suivez les étapes à l'écran.",
      'Nommez la nouvelle ligne, par exemple Voyage.',
      "À l'arrivée, définissez-la comme ligne de données et activez l'itinérance des données pour cette ligne.",
    ],
    android: [
      "Ouvrez le lien d'installation de l'e-mail, ou allez dans Paramètres → Connexions → Gestionnaire de SIM → Ajouter une eSIM (Samsung), ou Paramètres → Réseau et Internet → SIM → Ajouter (Pixel).",
      "Scannez le code QR ou suivez le lien d'installation.",
      "À l'arrivée, activez l'eSIM, choisissez-la pour les données mobiles et activez l'itinérance des données.",
    ],
    help: "Si quelque chose ne fonctionne pas, répondez à l'e-mail de votre eSIM avec votre numéro de commande et le modèle de votre téléphone, ou écrivez au support depuis l'onglet Aide.",
  },
  es: {
    before: [
      'Asegúrate de que tu teléfono admite eSIM y está liberado.',
      'Conéctate a una red Wi-Fi durante la instalación.',
      'Abre el correo que enviamos tras tu compra: contiene tu enlace de instalación.',
    ],
    iphone: [
      'Abre el enlace de instalación del correo en tu iPhone, o ve a Ajustes → Servicio móvil (o Datos móviles) → Añadir eSIM.',
      'Elige Usar código QR y sigue los pasos en pantalla.',
      'Ponle un nombre a la nueva línea, por ejemplo Viaje.',
      'Al llegar, selecciónala como línea de datos y activa la itinerancia de datos para esa línea.',
    ],
    android: [
      'Abre el enlace de instalación del correo, o ve a Ajustes → Conexiones → Administrador de SIM → Añadir eSIM (Samsung), o Ajustes → Redes e Internet → SIM → Añadir (Pixel).',
      'Escanea el código QR o sigue el enlace de instalación.',
      'Al llegar, activa la eSIM, elígela para los datos móviles y activa la itinerancia de datos.',
    ],
    help: 'Si algo no funciona, responde al correo de tu eSIM con tu número de pedido y el modelo de tu teléfono, o escribe a soporte desde la pestaña Ayuda.',
  },
};

export const FAQ = {
  en: [
    { q: 'When will I receive my eSIM?', a: "After your payment is confirmed, your eSIM is prepared automatically and sent to the email address you used at checkout, usually within a few minutes. Check your spam folder if you don't see it." },
    { q: "I didn't receive my eSIM email", a: "Wait a few minutes and check your spam folder. If it still hasn't arrived, email support with your order number and the email address you used at checkout." },
    { q: 'How do I install my eSIM?', a: 'Open the email on your phone and tap the install button, then follow the steps. The installation guide in the Help tab covers iPhone and Android.' },
    { q: 'Is my phone compatible?', a: "Your phone must support eSIM and be carrier-unlocked. Most recent iPhone, Samsung Galaxy and Google Pixel models do. Check your phone's settings or the manufacturer's website if you're not sure." },
    { q: 'Can I keep my normal number?', a: 'Yes. On dual-SIM phones your main SIM stays active for calls and texts while the eSIM provides mobile data.' },
    { q: 'Do plans include calls or SMS?', a: 'Plans are data only. You can call and message with apps such as WhatsApp.' },
    { q: 'Can I share my connection (hotspot)?', a: 'It depends on the destination. Each destination page shows whether hotspot is available.' },
    { q: 'Can I top up my eSIM?', a: 'It depends on the destination. Each destination page shows whether top-up is available.' },
  ],
  ar: [
    { q: 'متى أستلم الـ eSIM؟', a: 'بعد تأكيد الدفع تُجهَّز الـ eSIM تلقائياً وتُرسل إلى الإيميل الذي استخدمته عند الدفع، عادةً خلال دقائق. تحقق من مجلد الرسائل غير المرغوبة إن لم تجدها.' },
    { q: 'لم يصلني إيميل الـ eSIM', a: 'انتظر بضع دقائق وتحقق من مجلد الرسائل غير المرغوبة. إن لم يصل بعد ذلك فراسل الدعم مع رقم طلبك والإيميل الذي استخدمته عند الدفع.' },
    { q: 'كيف أثبّت الـ eSIM؟', a: 'افتح الإيميل على هاتفك واضغط زر التثبيت ثم اتبع الخطوات. دليل التثبيت في تبويب المساعدة يشرح الطريقة لآيفون وأندرويد.' },
    { q: 'هل هاتفي متوافق؟', a: 'يجب أن يدعم هاتفك eSIM وألا يكون مقفلاً على شبكة. تدعمه معظم هواتف آيفون وسامسونج جالاكسي وجوجل بكسل الحديثة. تحقق من إعدادات هاتفك أو موقع الشركة المصنّعة إن لم تكن متأكداً.' },
    { q: 'هل أحتفظ برقمي الأساسي؟', a: 'نعم. في الهواتف ثنائية الشريحة تبقى شريحتك الأساسية فعّالة للمكالمات والرسائل بينما تؤمّن الـ eSIM بيانات الجوال.' },
    { q: 'هل تشمل الباقات مكالمات أو رسائل SMS؟', a: 'الباقات بيانات فقط. يمكنك الاتصال والمراسلة عبر تطبيقات مثل واتساب.' },
    { q: 'هل أستطيع مشاركة الإنترنت (Hotspot)؟', a: 'يعتمد ذلك على الوجهة. صفحة كل وجهة تبيّن إن كانت مشاركة الإنترنت متاحة.' },
    { q: 'هل أستطيع شحن الـ eSIM مرة أخرى؟', a: 'يعتمد ذلك على الوجهة. صفحة كل وجهة تبيّن إن كان الشحن الإضافي متاحاً.' },
  ],
  fr: [
    { q: 'Quand vais-je recevoir mon eSIM ?', a: "Une fois votre paiement confirmé, votre eSIM est préparée automatiquement et envoyée à l'adresse e-mail utilisée lors du paiement, généralement en quelques minutes. Vérifiez vos spams si vous ne la voyez pas." },
    { q: "Je n'ai pas reçu l'e-mail de mon eSIM", a: "Patientez quelques minutes et vérifiez vos spams. S'il n'est toujours pas arrivé, écrivez au support avec votre numéro de commande et l'adresse e-mail utilisée lors du paiement." },
    { q: 'Comment installer mon eSIM ?', a: "Ouvrez l'e-mail sur votre téléphone, appuyez sur le bouton d'installation et suivez les étapes. Le guide d'installation de l'onglet Aide couvre iPhone et Android." },
    { q: 'Mon téléphone est-il compatible ?', a: "Votre téléphone doit être compatible eSIM et débloqué. C'est le cas de la plupart des iPhone, Samsung Galaxy et Google Pixel récents. En cas de doute, vérifiez les réglages de votre téléphone ou le site du fabricant." },
    { q: 'Puis-je garder mon numéro habituel ?', a: "Oui. Sur les téléphones double SIM, votre SIM principale reste active pour les appels et SMS pendant que l'eSIM fournit les données mobiles." },
    { q: 'Les forfaits incluent-ils appels ou SMS ?', a: 'Les forfaits sont uniquement des données. Vous pouvez appeler et écrire avec des applis comme WhatsApp.' },
    { q: 'Puis-je partager ma connexion ?', a: 'Cela dépend de la destination. La page de chaque destination indique si le partage de connexion est disponible.' },
    { q: 'Puis-je recharger mon eSIM ?', a: 'Cela dépend de la destination. La page de chaque destination indique si la recharge est disponible.' },
  ],
  es: [
    { q: '¿Cuándo recibiré mi eSIM?', a: 'Una vez confirmado el pago, tu eSIM se prepara automáticamente y se envía al correo que usaste al pagar, normalmente en pocos minutos. Revisa la carpeta de spam si no la ves.' },
    { q: 'No he recibido el correo de mi eSIM', a: 'Espera unos minutos y revisa la carpeta de spam. Si sigue sin llegar, escribe a soporte con tu número de pedido y el correo que usaste al pagar.' },
    { q: '¿Cómo instalo mi eSIM?', a: 'Abre el correo en tu teléfono, pulsa el botón de instalación y sigue los pasos. La guía de instalación de la pestaña Ayuda explica iPhone y Android.' },
    { q: '¿Es compatible mi teléfono?', a: 'Tu teléfono debe admitir eSIM y estar liberado. La mayoría de los iPhone, Samsung Galaxy y Google Pixel recientes lo admiten. Si no estás seguro, revisa los ajustes de tu teléfono o la web del fabricante.' },
    { q: '¿Puedo conservar mi número habitual?', a: 'Sí. En teléfonos con doble SIM, tu SIM principal sigue activa para llamadas y mensajes mientras la eSIM ofrece los datos móviles.' },
    { q: '¿Incluyen los planes llamadas o SMS?', a: 'Los planes son solo de datos. Puedes llamar y escribir con apps como WhatsApp.' },
    { q: '¿Puedo compartir mi conexión?', a: 'Depende del destino. La página de cada destino indica si se puede compartir la conexión.' },
    { q: '¿Puedo recargar mi eSIM?', a: 'Depende del destino. La página de cada destino indica si hay recarga disponible.' },
  ],
};
