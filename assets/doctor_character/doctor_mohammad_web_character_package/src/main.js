import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import './style.css';

const stage = document.querySelector('#stage');
const status = document.querySelector('#status');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setClearColor(0xeaf3f1);
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeaf3f1);
scene.add(new THREE.HemisphereLight(0xffffff, 0x71857f, 2.1));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
keyLight.position.set(3, 6, 5);
scene.add(keyLight);

const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 100);
camera.position.set(0, 0.78, 3.0);
camera.lookAt(0, 0.72, 0);

const loader = new GLTFLoader();
const clock = new THREE.Clock();
let mode = 'code';
let mixer;
let idleAction;
let rigRoot;
let idleRoot;
let rightArm;
let rightForeArm;
let armRest;
let foreArmRest;

function resize() {
  const width = stage.clientWidth;
  const height = stage.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

async function loadCharacters() {
  try {
    const [rigged, idle] = await Promise.all([
      loader.loadAsync('/assets/doctor_mohammad_web_character_rigged.glb'),
      loader.loadAsync('/assets/doctor_mohammad_web_character_idle.glb'),
    ]);

    rigRoot = rigged.scene;
    idleRoot = idle.scene;
    // The model's forward direction is +X. Turn it toward the usual Three.js camera at +Z.
    rigRoot.rotation.y = -Math.PI / 2;
    idleRoot.rotation.y = -Math.PI / 2;
    rigRoot.scale.setScalar(1.35);
    idleRoot.scale.setScalar(1.35);
    scene.add(rigRoot, idleRoot);
    idleRoot.visible = false;

    // Three.js sanitizes the original Mixamo bone names by removing the colon.
    rightArm = rigRoot.getObjectByName('mixamorigRightArm');
    rightForeArm = rigRoot.getObjectByName('mixamorigRightForeArm');
    if (!rightArm || !rightForeArm) {
      throw new Error('Could not find expected Mixamo arm bones in the rigged GLB.');
    }
    armRest = rightArm.quaternion.clone();
    foreArmRest = rightForeArm.quaternion.clone();

    mixer = new THREE.AnimationMixer(idleRoot);
    const idleClip = idle.animations.find((clip) => clip.name.toLowerCase() === 'idle') ?? idle.animations[0];
    if (!idleClip) throw new Error('The idle GLB does not contain an animation clip.');
    idleAction = mixer.clipAction(idleClip);
    idleAction.setLoop(THREE.LoopRepeat, Infinity);
    status.textContent = `جاهز — idle (${idleClip.duration.toFixed(1)} ثانية)`;
  } catch (error) {
    console.error(error);
    status.textContent = 'تعذر تحميل النموذج؛ تحقق من مسارات ملفات GLB.';
  }
}

function setMode(nextMode) {
  mode = nextMode;
  if (!rigRoot || !idleRoot) return;
  rigRoot.visible = mode === 'code';
  idleRoot.visible = mode === 'idle';
  if (mode === 'idle') {
    idleAction.reset();
    idleAction.play();
  } else {
    idleAction.stop();
    rightArm.quaternion.copy(armRest);
    rightForeArm.quaternion.copy(foreArmRest);
  }
}

document.querySelector('#code-mode').addEventListener('click', () => setMode('code'));
document.querySelector('#idle-mode').addEventListener('click', () => setMode('idle'));

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  if (mode === 'idle' && mixer) {
    mixer.update(delta);
  } else if (mode === 'code' && rightArm && rightForeArm) {
    // Example procedural motion: animate the upper arm and forearm with sine waves.
    // Replace this with your own keyframes, input, or AI-generated animation logic.
    const armSwing = new THREE.Quaternion().setFromAxisAngle(
      new THREE.Vector3(1, 0, 0),
      0.4 * Math.sin(time * 1.6),
    );
    const elbowSwing = new THREE.Quaternion().setFromAxisAngle(
      new THREE.Vector3(0, 0, 1),
      0.3 * Math.sin(time * 3.0),
    );
    rightArm.quaternion.copy(armRest).multiply(armSwing);
    rightForeArm.quaternion.copy(foreArmRest).multiply(elbowSwing);
  }

  renderer.render(scene, camera);
}

loadCharacters();
animate();
