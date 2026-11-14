import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import os
import re
import json

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
    speech = clean_for_speech(last_reply)
    safe_speech_json = json.dumps(speech)
    
    html_template = """<!DOCTYPE html>
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

    const b64 = "__VRM
