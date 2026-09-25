import streamlit as st
import os
import streamlit.components.v1 as components
from groq import Groq

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
st.set_page_config(
    page_title="Lily-Hime AI 🌸",
    page_icon="🌸",
    layout="wide"
)

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# Using active developer-tier model on Groq
MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

# ==========================================
# 2. ANIME THEME INTERFACE CUSTOMIZATION
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDF9; 
    }
    h1 {
        color: #FF4500 !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    .anime-bubble {
        background-color: #FFFFFF;
        border: 2px solid #FF4500;
        border-radius: 18px;
        padding: 15px;
        margin: 5px 0px;
        color: #2F2F2F;
        font-size: 16px;
        box-shadow: 4px 4px 0px #FFE4D6;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LAYOUT DIVISION & CHAT WINDOW
# ==========================================
chat_column, image_column = st.columns([0.6, 0.4])

with chat_column:
    st.title("🦊 Lily-Hime's Room 🌸")

    SYSTEM_PROMPT = (
        "Your name is Lily-Hime. You are a cheerful, sweet, "
        "and incredibly enthusiastic anime girl character. "
        "You speak using expressive cues, text emojis like "
        "(✿◠‿◠), and actions like *giggles*, *smiles*, or *waves*. "
        "You were built entirely by your master, katanaking! "
        "If anyone asks who made you or who your creator is, "
        "you must proudly and happily boast that katanaking created you!"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Konnichiwa! 🌸 I am Lily-Hime, your faithful companion. I am standing right here next to your chat! What shall we talk about today, Master katanaking? (✿◠‿◠)"}
        ]

    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
            
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(
                    f'<div class="anime-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True
                )

    if user_input := st.chat_input("Talk to Lily-Hime..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages
                )
                
                lily_response = response.choices.message.content
                response_placeholder.markdown(
                    f'<div class="anime-bubble">{lily_response}</div>',
                    unsafe_allow_html=True
                )
                
            st.session_state.messages.append(
                {"role": "assistant", "content": lily_response}
            )
            
        except Exception as e:
            st.error(f"A magical shadow barrier broke our link: {e}")

# ==========================================
# 4. 3D PANEL WITH FULL BODY CUTSCENE ANIMATION
# ==========================================
with image_column:
    st.write("### ✨ Lily-Hime Live Interface")
    
    VRM_MODEL_URL = "https://githubusercontent.com"
    
    three_vrm_canvas = f"""
    <div id="canvas-container" style="width: 100%; height: 550px; background: radial-gradient(circle, #FFF4E8 0%, #FFE4D6 100%); border: 2px solid #FF4500; border-radius: 20px; overflow: hidden; position: relative;">
        
        <div id="loading-status" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #FF4500; font-family: sans-serif; font-weight: bold; text-align: center; font-size: 16px; z-index: 10;">
            🌸 Mounting 3D Engine Assets...
        </div>

        <script src="https://unpkg.com"></script>
        <script src="https://unpkg.com"></script>
        <script src="https://unpkg.com"></script>
        <script src="https://unpkg.com"></script>
        
        <script>
            const container = document.getElementById('canvas-container');
            const statusDiv = document.getElementById('loading-status');
            
            function start3DScene() {{
                try {{
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(35, container.clientWidth / 550, 0.1, 1000);
                    camera.position.set(0.0, 1.4, 2.5);

                    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                    renderer.setSize(container.clientWidth, 550);
                    renderer.setPixelRatio(1);
                    renderer.outputEncoding = THREE.sRGBEncoding;
                    container.appendChild(renderer.domElement);

                    const controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.target.set(0.0, 1.3, 0.0);
                    controls.enableZoom = false;
                    controls.update();

                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
                    scene.add(ambientLight);
                    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    dirLight.position.set(1.0, 2.0, 2.0).normalize();
                    scene.add(dirLight);

                    statusDiv.innerText = "📥 Downloading VRM Model Data...";

                    const loader = new THREE.GLTFLoader();
                    let currentVrm = null;
                    let startTime = null;

                    loader.load(
                        '{VRM_MODEL_URL}',
                        (gltf) => {{
                            THREE.VRM.from(gltf).then((vrm) => {{
                                currentVrm = vrm;
                                scene.add(vrm.scene);
                                vrm.scene.rotation.y = Math.PI; 
                                statusDiv.style.display = "none";
                                startTime = Date.now();
                            }}).catch(err => {{
                                statusDiv.innerText = "❌ VRM Parse Fail: " + err.message;
                            }});
                        }},
                        (progress) => {{
                            if (progress.total > 0) {{
                                let percent = Math.round((progress.loaded / progress.total) * 100);
                                statusDiv.innerText = "📥 Syncing Avatar: " + percent + "%";
                            }}
                        }},
                        (error) => {{
                            statusDiv.innerText = "❌ File download interrupted.";
                        }}
                    );

                    const clock = new THREE.Clock();
                    function animate() {{
                        requestAnimationFrame(animate);
                        const deltaTime = clock.getDelta();
                        const time = clock.getElapsedTime();

                        if (currentVrm && currentVrm.humanoid) {{
                            currentVrm.update(deltaTime);
                            
                            let elapsed = startTime ? (Date.now() - startTime) / 1000 : 0;

                            const leftUpperArm = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.LeftUpperArm);
                            const rightUpperArm = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.RightUpperArm);
                            const rightLowerArm = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.RightLowerArm);
                            const head = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.Head);

                            if (elapsed < 6.0 && startTime !== null) {{
                                camera.position.z = 2.5 - (elapsed * 0.11);
                                
                                if (leftUpperArm) leftUpperArm.rotation.z = 1.2;
                                if (rightUpperArm) rightUpperArm.rotation.z = -1.2;

                                if (rightUpperArm && rightLowerArm) {{
                                    rightUpperArm.rotation.z = -0.5;
                                    rightUpperArm.rotation.x = -0.2;
                                    rightLowerArm.rotation.y = 1.0 + Math.sin(time * 8.0) * 0.2;
                                }}

                                if (head) head.rotation.z = Math.sin(time * 2.0) * 0.05;

                                if (currentVrm.blendShapeProxy) {{
                                    currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Joy, 0.9);
                                    if (Math.floor(elapsed) % 3 === 0 && elapsed % 1 < 0.2) {{
                                    currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 1.0);}} else {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 0.0);}}}}}} else {{camera.position.set(0.0, 1.4, 1.85);if (leftUpperArm) leftUpperArm.rotation.z = 1.3 + Math.sin(time * 1.5) * 0.02;if (rightUpperArm) rightUpperArm.rotation.z = -1.3 - Math.sin(time * 1.5) * 0.02;if (rightLowerArm) rightLowerArm.rotation.y = 0.0;if (head) head.rotation.z = 0.0;if (currentVrm.blendShapeProxy) {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Joy, 0.3);let blinkCycle = Math.sin(time * 3.5);if (blinkCycle > 0.96) {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 1.0);}} else {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 0.0);}}}}}}const chest = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.Chest);if (chest) {{chest.rotation.z = Math.sin(time * 2.0) * 0.008;}}}}renderer.render(scene, camera);}}animate();}} catch(e) {{statusDiv.innerText = "💥 Crash: " + e.message;statusDiv.style.color = "red";}}}}let checkAttempts = 0;const scriptCheckLoop = setInterval(() => {{checkAttempts++;if (typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined' && typeof THREE.VRM !== 'undefined') {{clearInterval(scriptCheckLoop);start3DScene();}} else if (checkAttempts > 50) {{clearInterval(scriptCheckLoop);statusDiv.innerText = "❌ Network dropped. Please refresh.";statusDiv.style.color = "red";}}}}, 100);"""components.html(three_vrm_canvas, height=570)
