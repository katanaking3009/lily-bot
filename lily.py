import streamlit as st
import os
import streamlit.components.v1 as components
from groq import Groq

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
# Configure layout to "wide" to support side-by-side columns
st.set_page_config(page_title="Lily-Hime AI 🌸", page_icon="🌸", layout="wide")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Please add your GROQ_API_KEY to your Streamlit App Secrets!")
    st.stop()

# Using official, active developer-tier model on Groq
MODEL_NAME = "qwen/qwen3.8-27b"
client = Groq(api_key=api_key)

# ==========================================
# 2. ANIME THEME INTERFACE CUSTOMIZATION
# ==========================================
st.markdown("""
    <style>
    /* Main Background color styling */
    .stApp {
        background-color: #FFFDF9; 
    }
    h1 {
        color: #FF4500 !important; /* Aesthetic Vibrant Orange */
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Custom Stylized Bubble for Manga Chat look */
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
# Split the layout window: 60% left for Chat, 40% right for Character Panel
chat_column, image_column = st.columns([0.6, 0.4])

with chat_column:
    st.title("🦊 Lily-Hime's Room 🌸")

    SYSTEM_PROMPT = (
        "Your name is Lily-Hime. You are a cheerful, sweet, and incredibly enthusiastic anime girl character. "
        "You speak using expressive cues, text emojis like (✿◠‿◠), and actions like *giggles*, *smiles*, or *waves*. "
        "You were built entirely by your master, katanaking! "
        "If anyone asks who made you or who your creator is, you must proudly and happily boast that katanaking created you!"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Konnichiwa! 🌸 I am Lily-Hime, your faithful companion. I am standing right here next to your chat! What shall we talk about today, Master katanaking? (✿◠‿◠)"}
        ]

    # Map state data loop elements down into graphic interface layouts
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
            
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f'<div class="anime-bubble">{message["content"]}</div>', unsafe_allow_html=True)

    # Capture interactive panel text submission actions
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
                
                lily_response = response.choices[0].message.content
                response_placeholder.markdown(f'<div class="anime-bubble">{lily_response}</div>', unsafe_allow_html=True)
                
            st.session_state.messages.append({"role": "assistant", "content": lily_response})
            
        except Exception as e:
            st.error(f"A magical shadow barrier broke our link: {e}")

# ==========================================
# 4. 3D PANEL WITH 6-SECOND ANIMATION TIMELINE
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
                    camera.position.set(0.0, 1.4, 2.5); // Start slightly further back for intro zoom

                    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                    renderer.setSize(container.clientWidth, 550);
                    // Mobile optimization: set to 1 instead of window.devicePixelRatio to prevent mobile GPU lag
                    renderer.setPixelRatio(1);
                    renderer.outputEncoding = THREE.sRGBEncoding;
                    container.appendChild(renderer.domElement);

                    const controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.target.set(0.0, 1.3, 0.0);
                    controls.enableZoom = false; // Keep fixed layout position
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
                                startTime = Date.now(); // Mark time animation timeline begins
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
                            
                            // Check out our intro time block context
                            let elapsedCutsceneTime = startTime ? (Date.now() - startTime) / 1000 : 0;

                            if (elapsedCutsceneTime < 6.0 && startTime !== null) {{
                                // 6-Second Cutscene Active Mode
                                // Camera pans in closer dynamically
                                camera.position.z = 2.5 - (elapsedCutsceneTime * 0.11);
                                
                                // Blend face states smoothly: Forced smile activation layout matrix
                                if (currentVrm.blendShapeProxy) {{
                                    currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Joy, 0.8);
                                    
                                    // Periodic artificial blinking sequence simulation
                                    if (Math.floor(elapsedCutsceneTime) % 3 === 0 && elapsedCutsceneTime % 1 < 0.2) {{
                                        currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 1.0);
                                    }} else {{
Use code with caution.currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 0.0);}}}}}} else {{// Background Idle Mode (Post 6-seconds)// Keep camera stationary at proper close framecamera.position.set(0.0, 1.4, 1.85);// Reset back to light default expressionsif (currentVrm.blendShapeProxy) {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Joy, 0.2);// Natural random baseline blinking layer matrix looplet blinkCycle = Math.sin(time * 3.5);if (blinkCycle > 0.96) {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 1.0);}} else {{currentVrm.blendShapeProxy.setValue(THREE.VRMBlendShapePresetName.Blink, 0.0);}}}}}}// Shared physics loop for continuous gentle breathing baseline layoutconst chest = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.Chest);if (chest) chest.rotation.z = Math.sin(time * 2.0) * 0.008;}}renderer.render(scene, camera);}}animate();}} catch(e) {{statusDiv.innerText = "💥 Crash: " + e.message;statusDiv.style.color = "red";}}}}let checkAttempts = 0;const scriptCheckLoop = setInterval(() => {{checkAttempts++;if (typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined' && typeof THREE.VRM !== 'undefined') {{clearInterval(scriptCheckLoop);start3DScene();}} else if (checkAttempts > 50) {{clearInterval(scriptCheckLoop);statusDiv.innerText = "❌ Network connection dropped. Please refresh the page.";statusDiv.style.color = "red";}}}}, 100);"""components.html(three_vrm_canvas, height=570
