# تطبيق YRH eSIM لأندرويد

تطبيق Expo (React Native) يعرض وجهات متجرك وباقاتها، والدفع يتم داخل التطبيق نفسه عبر نافذة دفع Shopify المدمجة (Checkout Sheet Kit). بعد الدفع يتولى سيناريو Make الحالي شراء الـ eSIM من eSIM Access وإرسال رابط التثبيت بالإيميل.

## كيف يرتبط التطبيق بـ eSIM Access

```
التطبيق ← كتالوج المتجر العام (بلا مفاتيح)
التطبيق ← "اشترِ" ← نافذة دفع Shopify داخل التطبيق
Shopify (Order payment) ← Make ← eSIM Access ← إيميل الزبون
```

مفتاح eSIM Access لا يوضع داخل التطبيق أبداً. أي شخص يستطيع فك ملف التطبيق وقراءة المفاتيح، فيشتري eSIM من رصيدك. لذلك يبقى المفتاح في Make فقط، والتطبيق لا يحمل أي مفتاح سري.

## محتوى المشروع

- `App.js`: التنقل بين الشاشات، وزر الرجوع في أندرويد.
- `src/screens/Home.js`: البحث، والوجهات المطلوبة، وكل الوجهات.
- `src/screens/Destination.js`: باقات الوجهة والشراء.
- `src/screens/Help.js`: طريقة العمل، ودليل التثبيت، والدعم.
- `src/i18n.js`: العربية (من اليمين لليسار) والإنجليزية والفرنسية والإسبانية.
- `src/config.js`: رابط المتجر وإيميل الدعم ورقم واتساب.
- `store/`: أيقونة 512، وصورة العرض 1024×500، ونصوص المتجر بأربع لغات.

## 1) جرّب التطبيق على هاتفك (يلزم كمبيوتر)

1. ثبّت Node.js LTS من nodejs.org.
2. فك ضغط المجلد، وافتح الطرفية فيه، ثم:
   ```
   npm install
   npx expo install --fix
   npx expo start
   ```
3. ثبّت تطبيق **Expo Go** على هاتفك وامسح رمز QR الظاهر.

## 2) ابنِ ملف التطبيق

1. أنشئ حساباً مجانياً على expo.dev.
2. في نفس المجلد:
   ```
   npm install -g eas-cli
   eas login
   eas init
   eas build -p android --profile preview
   ```
   تحصل على **APK** تثبّته على هاتفك مباشرة لتجربة الشراء وأخذ لقطات الشاشة.
3. للنشر على Google Play:
   ```
   eas build -p android --profile production
   ```
   تحصل على ملف **AAB** ترفعه إلى Play Console.

إن ظهر تحذير يخص إصدار Expo فشغّل: `npx expo install expo@latest` ثم `npx expo install --fix`. أحدث إصدار يضمن توافق التطبيق مع مستوى أندرويد الذي تطلبه Google.

## 3) النشر على Google Play

1. سجّل في play.google.com/console (رسوم 25 دولاراً مرة واحدة وتوثيق الهوية).
2. **Create app** باسم **YRH eSIM: Travel Data**، واختر App وFree.
3. **Store listing:** انسخ النصوص من `store/listing.md`، وارفع `store/play-icon-512.png` و`store/feature-graphic-1024x500.png`، ثم لقطتي شاشة على الأقل من الهاتف.
4. **Privacy policy:** `https://07eqi1-zk.myshopify.com/pages/app-privacy`
5. **Data safety:**
   - الدفع يتم داخل التطبيق، فصرّح بأن التطبيق يجمع: الاسم، والبريد الإلكتروني، ومعلومات الدفع، وسجل المشتريات. الغرض: App functionality. البيانات تُرسل مشفّرة وتعالجها Shopify.
   - راجع هذه الأجوبة قبل الإرسال، فأنت المسؤول عن دقتها.
6. **Content rating:** املأ الاستبيان (لا عنف ولا محتوى للبالغين ولا مقامرة). **Target audience:** 18+.
7. **Testing:** الحسابات الشخصية الجديدة يُطلب منها غالباً اختبار مغلق مع 12 مختبِراً لمدة 14 يوماً قبل النشر العام. Play Console يبيّن لك ذلك.
8. ارفع ملف AAB في **Production** (أو Closed testing أولاً) ثم **Send for review**.

## الدفع وسياسة Google Play

باقات eSIM خدمة اتصالات تُستهلك خارج التطبيق، ولذلك تبيعها تطبيقات eSIM عادةً عبر دفعها الخاص لا عبر Google Play Billing. هذا ليس ضماناً: راجع صفحة Payments policy في Play Console قبل الإرسال. إن طلبت Google غير ذلك فأخبرني.

## قبل النشر، تحقق من

- [ ] اشترِ باقة رخيصة من التطبيق بنفسك وتأكد من وصول الإيميل.
- [ ] غيّر `SUPPORT_EMAIL` و`SUPPORT_WHATSAPP` في `src/config.js` إن أردت.
- [ ] اسم المتجر في Shopify ما زال "My Store" ويظهر في صفحة الدفع وإيميلات Shopify. غيّره من Settings ← General.
- [ ] انشر لغات المتجر (Settings ← Languages) إن أردت أن تكون صفحة الدفع بلغة الزبون.

## إعادة رسم الأيقونات

```
python3 store/make_graphics.py
```
