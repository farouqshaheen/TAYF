"""
طيف — TAYF
المجسم التفاعلي ثلاثي الأبعاد لدكتور محمد رسمي (Three.js WebGL Component)
تحميل وتشغيل ملف GLB المتحرك بنمط الـ Cyberpunk مع فقاعة حوار ذكية
"""
import base64
import os

def get_doctor_3d_html(speech_text: str = "أهلاً بك في مختبر طيف الجنائي! افحص الترددات واكتشف مين عطل الاتصال اليوم.", height: int = 420) -> str:
    """
    تولد عنصر HTML5 مدمج بـ Three.js لتحميل مجسم الدكتور ثلاثي الأبعاد مع حركة Idle حية وتفاعل بالماوس
    """
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "doctor_idle.glb")
    
    # تحويل ملف الـ GLB إلى Base64 لتضمينه داخل الـ Component بدون الحاجة لإنشاء سيرفر محلي منفصل
    with open(model_path, "rb") as f:
        glb_base64 = base64.b64encode(f.read()).decode("utf-8")

    html_code = f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500;700;900&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background: transparent;
            font-family: 'Tajawal', sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
        }}
        
        .char-wrapper {{
            position: relative;
            width: 100%;
            max-width: 550px;
            height: {height}px;
            background: radial-gradient(circle at 50% 60%, rgba(0, 240, 255, 0.08) 0%, rgba(5, 11, 20, 0.95) 75%);
            border: 1.5px solid rgba(0, 240, 255, 0.4);
            border-radius: 14px;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.2), inset 0 0 20px rgba(0, 0, 0, 0.8);
            overflow: hidden;
        }}
        
        /* شارة المشرف الأمني */
        .supervisor-tag {{
            position: absolute;
            top: 12px;
            right: 14px;
            background: rgba(13, 21, 39, 0.85);
            border: 1px solid #00f0ff;
            color: #00f0ff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            z-index: 10;
            backdrop-filter: blur(4px);
        }}
        
        .live-dot {{
            width: 8px;
            height: 8px;
            background: #00e676;
            border-radius: 50%;
            box-shadow: 0 0 8px #00e676;
        }}
        
        /* فقاعة حوار الدكتور */
        .speech-bubble {{
            position: absolute;
            bottom: 12px;
            left: 14px;
            right: 14px;
            background: rgba(11, 17, 30, 0.92);
            border: 1px solid rgba(0, 240, 255, 0.35);
            border-radius: 10px;
            padding: 10px 14px;
            color: #e2e8f0;
            font-size: 0.92rem;
            line-height: 1.45;
            text-align: right;
            direction: rtl;
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }}
        
        .speech-bubble strong {{
            color: #ffd600;
        }}
        
        /* مؤشر التحميل */
        #loader {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #00f0ff;
            font-weight: 700;
            font-size: 0.95rem;
            z-index: 5;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        
        .spinner {{
            width: 32px;
            height: 32px;
            border: 3px solid rgba(0, 240, 255, 0.2);
            border-top-color: #00f0ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        canvas {{
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;
        }}
        canvas:active {{
            cursor: grabbing;
        }}
    </style>
    <!-- Three.js + GLTFLoader + OrbitControls عبر CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>

    <div class="char-wrapper">
        <div class="supervisor-tag">
            <div class="live-dot"></div>
            <span>د. محمد رسمي موسى | المشرف الأكاديمي</span>
        </div>
        
        <div id="loader">
            <div class="spinner"></div>
            <span>جاري استدعاء المشرف 3D...</span>
        </div>

        <div class="speech-bubble">
            <strong>د. محمد:</strong> "{speech_text}"
        </div>

        <div id="sceneContainer" style="width:100%; height:100%;"></div>
    </div>

    <script>
        const container = document.getElementById('sceneContainer');
        const loaderElem = document.getElementById('loader');

        // 1. المشهد والكاميرا والريندر
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 100);
        camera.position.set(0, 1.45, 2.7);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        // التحكم بالماوس (OrbitControls)
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 1.25, 0); // تركيز الكاميرا على الصدر والرأس
        controls.minDistance = 1.6;
        controls.maxDistance = 3.6;
        controls.maxPolarAngle = Math.PI / 2 + 0.1;

        // 2. الإضاءة السيبرانية الفخمة
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
        scene.add(ambientLight);

        // ضوء رئيسي من الأمام
        const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
        dirLight.position.set(2, 4, 3);
        scene.add(dirLight);

        // إضاءة سيان نيون من اليمين (Cyber Cyan Rim Light)
        const cyanLight = new THREE.PointLight(0x00f0ff, 2.5, 8);
        cyanLight.position.set(-2, 1.8, 1);
        scene.add(cyanLight);

        // إضاءة أرجوانية خفيفة من الخلف للحواف
        const magentaLight = new THREE.PointLight(0xff007f, 1.5, 8);
        magentaLight.position.set(2, 1.2, -1.5);
        scene.add(magentaLight);

        // 3. قاعدة رادار تحت أقدام الدكتور
        const ringGeo = new THREE.RingGeometry(0.5, 0.75, 32);
        const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.3 }});
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.rotation.x = -Math.PI / 2;
        ringMesh.position.y = 0.01;
        scene.add(ringMesh);

        // 4. فك تشفير الـ GLB Base64 وتحميله
        const base64Data = "{glb_base64}";
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}
        const byteArray = new Uint8Array(byteNumbers);
        const glbBlob = new Blob([byteArray], {{ type: 'model/gltf-binary' }});
        const blobUrl = URL.createObjectURL(glbBlob);

        let mixer;
        const loader = new THREE.GLTFLoader();

        loader.load(blobUrl, (gltf) => {{
            loaderElem.style.display = 'none';
            const model = gltf.scene;

            // توجيه النموذج للأمام وتعديل موضعه
            model.rotation.y = -Math.PI / 2;
            model.position.set(0, 0, 0);
            scene.add(model);

            // تشغيل حركة الـ Idle الجاهزة
            if (gltf.animations && gltf.animations.length > 0) {{
                mixer = new THREE.AnimationMixer(model);
                const idleClip = gltf.animations.find(c => c.name.toLowerCase().includes('idle')) || gltf.animations[0];
                const action = mixer.clipAction(idleClip);
                action.setLoop(THREE.LoopRepeat, Infinity);
                action.play();
            }}

            URL.revokeObjectURL(blobUrl);
        }}, undefined, (err) => {{
            console.error('Error loading 3D model:', err);
            loaderElem.innerHTML = '<span style="color:#ff1744">فشل تحميل المجسم 3D</span>';
        }});

        // حلقة الرسم الحركية
        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const delta = clock.getDelta();

            if (mixer) mixer.update(delta);
            controls.update();

            // دوران خفيف لقاعدة الرادار
            ringMesh.rotation.z += 0.01;

            renderer.render(scene, camera);
        }}
        animate();

        // تجاوب الحجم عند تغيير حجم الشاشة
        window.addEventListener('resize', () => {{
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }});
    </script>
    </body>
    </html>
    """
    return html_code

