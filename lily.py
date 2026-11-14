import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os
import re

st.set_page_config(
    page_title="Lily-Hime AI 🌸",
    page_icon="🌸",
    layout="wide"
)

st.markdown("""
<style>
.anime-bubble {
    background: rgba(255, 182, 193, 0.18);
    border-left: 4px solid #ff69b4;
    padding: 10px 14px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GROQ_API_KEY"]
    if not api_key or not api_key.startswith("gsk_"):
        st.error("⚠️ GROQ_API_KEY is missing or malformed.")
        st.stop()
except Exception:
    st.error("⚠️ GROQ_API_KEY not found in secrets.")
    st.stop()

MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

avatar_img = "character.png" if os.path.exists("character.png") else "🌸"

@st.cache_resource
def load_vrm_b64(vrm_path="lily_model.vrm"):
    if not os.path.exists(vrm_path):
        return ""
    with open(vrm_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def clean_for_speech(text):
    text = re.sub(r"\*.*?\*", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\s,.!?'-]", "", text)
    return " ".join(text.split())

def build_vrm_html(b64_vrm, last_reply=""):
    speech = clean_for_speech(last_reply).replace("\\", "").replace('"', "'")
    return """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: radial-gradient(circle at 50% 35%, #fff0f6 0%, #ffd6e7 100%);
      font-family: sans-serif;
    }
    canvas { width: 100vw; height: 100vh; display: block; }
    #status {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(255, 255, 255, 0.85);
      color: #d63384;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: bold;
    }
    .controls {
      position: absolute;
      bottom: 14px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      background: rgba(255, 255, 255, 0.85);
      padding: 7px 10px;
      border-radius: 24px;
      box-shadow: 0 4px 15px rgba(255, 105, 180, 0.25);
      z-index: 10;
    }
    .btn {
      border: 1px solid #ffb3d9;
      background: white;
      color: #c2185b;
      padding: 6px 10px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }
    .btn:active { background: #ff69b4; color: white; }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/",
        "@pixiv/three-vrm": "https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@3/lib/three-vrm.module.min.js"
      }
    }
  </script>
</head>
<body>
  <div id="status">🌸 Summoning Lily-Hime...</div>
  <div class="controls">
    <button class="btn" onclick="triggerAction('wave')">👋 Wave</button>
    <button class="btn" onclick="triggerAction('happy')">😊 Happy</button>
    <button class="btn" onclick="triggerAction('dance')">💃 Dance</button>
    <button class="btn" onclick="speakReply()">🔊 Voice</button>
  </div>
  <script type="module">
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

    const status = document.getElementById('status');
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.95;
    document.body.appendChild(renderer.domElement);

    const camera = new THREE.PerspectiveCamera(28.0, window.innerWidth / window.innerHeight, 0.1, 20.0);
    camera.position.set(0.0, 1.32, 2.05);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0.0, 1.22, 0.0);
    controls.enableDamping = true;
    controls.update();

    const scene = new THREE.Scene();
    const dirLight = new THREE.DirectionalLight(0xfff5f8, 1.35);
    dirLight.position.set(1.0, 1.5, 1.5);
    scene.add(dirLight);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));

    const b64 = '""" + b64_vrm + """';
    const lastReply = \"""" + speech + """\";

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blobUrl = URL.createObjectURL(new Blob([bytes], { type: "application/octet-stream" }));

    let currentVrm = null;
    let actionMode = "idle";
    let actionTimer = 0;
    let talkTimer = 0;

    window.triggerAction = (mode) => {
      actionMode = mode;
      actionTimer = 3.5;
    };

    window.speakReply = () => {
      const textToSay = lastReply || "Konnichiwa Master katanaking!";
      talkTimer = Math.min(7.0, Math.max(2.5, textToSay.length * 0.06));
      window.triggerAction("happy");

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(textToSay);
        utter.pitch = 1.4;
        utter.rate = 1.05;
        utter.onstart = () => { talkTimer = 12.0; };
        utter.onend = () => { talkTimer = 0.0; };
        utter.onerror = () => { talkTimer = 0.0; };
        window.speechSynthesis.speak(utter);
      }
    };

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      blobUrl,
      (gltf) => {
        const vrm = gltf.userData.vrm;
        VRMUtils.removeUnnecessaryVertices(gltf.scene);
        VRMUtils.rotateVRM0(vrm);
        vrm.scene.traverse((obj) => { obj.frustumCulled = false; });

        scene.add(vrm.scene);
        currentVrm = vrm;
        status.style.display = 'none';

        if (lastReply && lastReply.length > 0) {
          talkTimer = Math.min(6.0, Math.max(2.5, lastReply.length * 0.06));
          if (lastReply.toLowerCase().includes("konnichiwa")) {
            window.triggerAction("wave");
          } else {
            window.triggerAction("happy");
          }
        }
      },
      undefined,
      (err) => {
        status.textContent = "⚠️ Error loading VRM";
        console.error(err);
      }
    );

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const t = clock.getElapsedTime();

      if (currentVrm && currentVrm.humanoid) {
        const h = currentVrm.humanoid;
        const exp = currentVrm.expressionManager;

        const hips = h.getNormalizedBoneNode('hips');
        const spine = h.getNormalizedBoneNode('spine');
        const chest = h.getNormalizedBoneNode('chest');
        const head = h.getNormalizedBoneNode('head');
        const leftUpperArm = h.getNormalizedBoneNode('leftUpperArm');
        const rightUpperArm = h.getNormalizedBoneNode('rightUpperArm');
        const leftLowerArm = h.getNormalizedBoneNode('leftLowerArm');
        const rightLowerArm = h.getNormalizedBoneNode('rightLowerArm');

        if (actionTimer > 0) {
          actionTimer -= delta;
          if (actionTimer <= 0) actionMode = "idle";
        }
        if (talkTimer > 0) talkTimer -= delta;

        if (hips) {
          hips.position.y = Math.sin(t * 2.2) * 0.008;
          hips.rotation.z = Math.sin(t * 1.1) * 0.025;
        }
        if (spine) {
          spine.rotation.x = Math.sin(t * 2.0) * 0.025;
          spine.rotation.z = Math.cos(t * 1.1) * 0.02;
        }
        if (chest) chest.rotation.y = Math.sin(t * 0.9) * 0.04;
        if (head) {
          head.rotation.z = Math.sin(t * 1.3) * 0.045;
          head.rotation.x = Math.sin(t * 1.7) * 0.03;
          head.rotation.y = Math.sin(t * 0.7) * 0.06;
        }

        // Fixed arm rotation (try -1.22 / 1.22 or 0.0 if rig is already A-pose)
        if (leftUpperArm) {
          leftUpperArm.rotation.z = 1.15 + Math.sin(t * 2.0) * 0.03;
          leftUpperArm.rotation.x = 0.08;
        }
        if (leftLowerArm) {
          leftLowerArm.rotation.z = 0.15;
          leftLowerArm.rotation.y = 0.2;
        }
        if (rightUpperArm) {
          rightUpperArm.rotation.z = -1.15 - Math.sin(t * 2.0) * 0.03;
          rightUpperArm.rotation.x = 0.08;
        }
        if (rightLowerArm) {
          rightLowerArm.rotation.z = -0.15;
          rightLowerArm.rotation.y = -0.2;
        }

        if (actionMode === "wave" && rightUpperArm && rightLowerArm) {
          rightUpperArm.rotation.z = -0.35;
          rightUpperArm.rotation.x = 0.25;
          rightLowerArm.rotation.z = -1.0 + Math.sin(t * 10.0) * 0
