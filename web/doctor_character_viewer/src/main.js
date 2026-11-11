import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import './style.css';

const stage = document.querySelector('#stage');
const loading = document.querySelector('#loading');
const status = document.querySelector('#status');
const errorPanel = document.querySelector('#error');

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.setClearColor(0x0b1520, 1);
stage.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1520);
scene.add(new THREE.HemisphereLight(0xd8fbff, 0x152333, 2.1));

const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
keyLight.position.set(2.5, 4, 3.5);
scene.add(keyLight);
const rimLight = new THREE.PointLight(0x52e0d1, 16, 8);
rimLight.position.set(-2.4, 1.8, -1.5);
scene.add(rimLight);

const camera = new THREE.PerspectiveCamera(30, 1, 0.05, 100);
camera.position.set(0, 1.05, 3.35);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.92, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = false;
controls.minDistance = 2.15;
controls.maxDistance = 5.2;
controls.minPolarAngle = 0.5;
controls.maxPolarAngle = 1.55;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
controls.autoRotate = !reducedMotion;
controls.autoRotateSpeed = 0.45;

const floor = new THREE.GridHelper(8, 24, 0x315266, 0x1d3041);
floor.position.y = 0.012;
floor.material.transparent = true;
floor.material.opacity = 0.25;
scene.add(floor);

const platform = new THREE.Mesh(
  new THREE.RingGeometry(0.48, 0.52, 72),
  new THREE.MeshBasicMaterial({ color: 0x52e0d1, transparent: true, opacity: 0.58, side: THREE.DoubleSide }),
);
platform.rotation.x = -Math.PI / 2;
platform.position.y = 0.018;
scene.add(platform);

function resize() {
  const width = Math.max(stage.clientWidth, 1);
  const height = Math.max(stage.clientHeight, 1);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
const observer = new ResizeObserver(resize);
observer.observe(stage);
resize();

const clock = new THREE.Clock();
let mixer = null;
let loaded = false;
const loader = new GLTFLoader();
const modelUrl = new URL('./assets/doctor_mohammad_web_character_idle.glb', document.baseURI).href;

loader.load(
  modelUrl,
  (gltf) => {
    const character = gltf.scene;
    // The supplied asset faces +X; rotate toward the default +Z camera.
    character.rotation.y = -Math.PI / 2;
    scene.add(character);

    const originalBounds = new THREE.Box3().setFromObject(character);
    const originalSize = originalBounds.getSize(new THREE.Vector3());
    const center = originalBounds.getCenter(new THREE.Vector3());
    const targetHeight = 1.85;
    const scale = targetHeight / Math.max(originalSize.y, 0.01);
    character.scale.setScalar(scale);
    character.position.x = -center.x * scale;
    character.position.z = -center.z * scale;
    character.position.y = -originalBounds.min.y * scale;

    const idleClip = gltf.animations.find((clip) => clip.name.toLowerCase() === 'idle') ?? gltf.animations[0];
    if (idleClip) {
      mixer = new THREE.AnimationMixer(character);
      const idleAction = mixer.clipAction(idleClip);
      idleAction.setLoop(THREE.LoopRepeat, Infinity);
      idleAction.play();
      status.textContent = 'حركة هادئة · اسحب للتدوير';
    } else {
      status.textContent = 'اسحب للتدوير · لا توجد حركة مرفقة';
    }
    loading.hidden = true;
    loaded = true;
  },
  (event) => {
    if (event.total > 0) {
      const percent = Math.round((event.loaded / event.total) * 100);
      loading.textContent = `جارٍ تحميل المجسم… ${percent}%`;
    }
  },
  (error) => {
    console.error('Doctor model failed to load:', error);
    loading.hidden = true;
    errorPanel.hidden = false;
    status.textContent = 'لم يتم تحميل النموذج';
  },
);

function renderFrame() {
  const delta = Math.min(clock.getDelta(), 0.05);
  if (mixer && loaded && !reducedMotion) mixer.update(delta);
  controls.update();
  renderer.render(scene, camera);
}

let stageVisible = true;
function syncAnimationLoop() {
  const shouldRender = stageVisible && document.visibilityState === 'visible';
  renderer.setAnimationLoop(shouldRender ? renderFrame : null);
}

const visibilityObserver = new IntersectionObserver(([entry]) => {
  stageVisible = entry.isIntersecting;
  syncAnimationLoop();
});
visibilityObserver.observe(stage);
document.addEventListener('visibilitychange', syncAnimationLoop);
syncAnimationLoop();
