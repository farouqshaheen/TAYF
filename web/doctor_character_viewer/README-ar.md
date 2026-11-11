# عارض شخصية المشرف لطيف

هذا المكوّن يعرض حركة `idle` من الحزمة `doctor_mohammad_web_character_package.zip` داخل لوحة Streamlit. ملف GLB موجود في `static/doctor_character/assets/doctor_mohammad_web_character_idle.glb` ويُقدّم محلياً عبر إعداد `enableStaticServing` في `.streamlit/config.toml`.

## التشغيل اليومي

يكفي تشغيل التطبيق كالمعتاد:

```bash
python -m streamlit run app.py
```

لا يحتاج تشغيل Streamlit إلى Node.js؛ ملفات Three.js المبنية وملف GLB موجودة ضمن المشروع. يمكن إخفاء المجسم من مفتاح «إظهار المجسم ثلاثي الأبعاد» لتقليل استهلاك الجهاز.

## إعادة بناء العارض

إذا عُدّل `src/main.js` أو `src/style.css`، أعد بناء الحزمة من هذا المجلد:

```bash
npm ci
npm run build
```

يكتب Vite الملفات النهائية إلى `static/doctor_character/`. احتفظ بملف GLB الموجود داخل مجلد `assets`؛ خيار `emptyOutDir: false` يمنع حذفه أثناء البناء.

## التفاعل

تعمل حركة `idle` تلقائياً. يمكن سحب المجسم لتدويره، وتمرير عجلة الفأرة للتقريب أو الإبعاد. يحترم الدوران التلقائي إعداد `prefers-reduced-motion` في المتصفح.
