# شخصية الدكتور محمد للويب

هذه الحزمة تحتوي على نموذج GLB بهيكل بشري قابل للتحريك عبر Three.js، ونسخة ثانية معها مقطع idle جاهز، إضافة إلى مثال صفحة ويب يعمل محليًا.

## محتويات الحزمة

- `public/assets/doctor_mohammad_web_character_rigged.glb` — النسخة الأساسية الموصى بها للتحريك بالكود؛ تتضمن هيكلًا بشريًا و23 عظمة، بدون مقطع حركة مفروض.
- `public/assets/doctor_mohammad_web_character_idle.glb` — نسخة معها مقطع `idle` متكرر، للاختبار أو التشغيل الجاهز.
- `src/main.js` و`src/style.css` — مثال Three.js يتيح التبديل بين حركة عظام برمجية ومقطع idle.
- `index.html` و`package.json` — تشغيل المثال كصفحة Vite.

## تشغيل المثال

تحتاج Node.js. فك ضغط الحزمة، افتح الطرفية داخل المجلد، ثم نفّذ:

```bash
npm install
npm run dev
```

افتح عنوان Vite الذي يظهر في الطرفية. لا تفتح `index.html` مباشرة عبر `file://`؛ ملفات GLB يجب أن تُحمّل من خادم محلي أو موقع منشور.

## استخدام النموذج في مشروع Three.js

انسخ ملف `doctor_mohammad_web_character_rigged.glb` إلى مجلد الأصول العام لديك، ثم حمّله هكذا:

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
const gltf = await loader.loadAsync('/assets/doctor_mohammad_web_character_rigged.glb');
const character = gltf.scene;
scene.add(character);

// اتجاه وجه النموذج الأصلي هو +X. هذا التدوير يجعله يواجه كاميرا Three.js المعتادة عند +Z.
character.rotation.y = -Math.PI / 2;

// أسماء العظام بعد تحميل GLB في Three.js (النقطتان في أسماء Mixamo تُزال تلقائيًا):
const rightArm = character.getObjectByName('mixamorigRightArm');
const rightForeArm = character.getObjectByName('mixamorigRightForeArm');
const head = character.getObjectByName('mixamorigHead');

if (!rightArm || !rightForeArm) throw new Error('عظام الذراع غير موجودة');
```

مثال حركة برمجية بسيطة؛ خزّن وضعية البداية مرة واحدة ثم حدّث دوران العظام داخل حلقة الرسم:

```js
const armRest = rightArm.quaternion.clone();
const forearmRest = rightForeArm.quaternion.clone();
const armDelta = new THREE.Quaternion();
const forearmDelta = new THREE.Quaternion();

function animateCharacter(timeSeconds) {
  armDelta.setFromAxisAngle(new THREE.Vector3(1, 0, 0), 0.4 * Math.sin(timeSeconds * 1.6));
  forearmDelta.setFromAxisAngle(new THREE.Vector3(0, 0, 1), 0.3 * Math.sin(timeSeconds * 3.0));
  rightArm.quaternion.copy(armRest).multiply(armDelta);
  rightForeArm.quaternion.copy(forearmRest).multiply(forearmDelta);
}
```

إذا كان المطلوب تشغيل الحركة الجاهزة بدل كتابة حركة من الصفر، حمّل ملف `doctor_mohammad_web_character_idle.glb` وأنشئ `AnimationMixer`:

```js
const gltf = await loader.loadAsync('/assets/doctor_mohammad_web_character_idle.glb');
scene.add(gltf.scene);
const mixer = new THREE.AnimationMixer(gltf.scene);
const idle = gltf.animations.find((clip) => clip.name.toLowerCase() === 'idle');
const action = mixer.clipAction(idle);
action.setLoop(THREE.LoopRepeat, Infinity);
action.play();

// داخل حلقة الرسم:
mixer.update(deltaSeconds);
```

## ملاحظات عملية

- استخدم نسخة `rigged` إذا كان وكيلك سيصنع حركاته بالكود؛ واستخدم نسخة `idle` كمعاينة أو حركة افتراضية جاهزة. كلتا النسختين تتضمنان هيكلًا عظميًا، لذا يمكن قراءة العظام من نسخة idle أيضًا.
- أسماء العظام الشائعة في Three.js: `mixamorigHips`, `mixamorigSpine`, `mixamorigHead`, `mixamorigRightArm`, `mixamorigRightForeArm`, `mixamorigRightHand`، ونظائرها لليسار والساقين.
- اتجاه الواجهة الأصلي للنموذج +X؛ المثال يدوّر الجذر ليستقبل كاميرا عند +Z. احذف التدوير إذا كانت كاميرتك تنظر من +X، أو عدّله بما يناسب مشهدك.
- الملفان GLB بحجم بضعة ميغابايت لكل منهما. التحويل من الرسم إلى 3D يعطي تفسيرًا ثلاثي الأبعاد منمّقًا بأسلوب قريب من الرسم، وليس نسخة مطابقة لكل تفاصيل الصورة.
- هذه حزمة أصول ومثال ويب؛ لم تُدمج داخل مشروعك الحالي لأن ملفات المشروع لم تُرفق هنا.
