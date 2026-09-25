import streamlit as st
import os
import streamlit.components.v1 as components
from groq import Groq

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
# Configure layout to "wide" to support side-by-side columns
st.set_page_config(page_title="Lily-Hime AI 🌸", page_icon="🌸", layout="wide")

# Best Practice: Pull key securely from Streamlit Secrets
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Please add your GROQ_API_KEY to your Streamlit App Secrets!")
    st.stop()

# Using standard, ultra-fast Groq model ID
MODEL_NAME = "openai/gpt-oss-20b"

# Initialize Groq Engine Client connection interface securely
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
# Split the layout window: 60% left for Chat, 40% right for Character Image
chat_column, image_column = st.columns([0.6, 0.4])

with chat_column:
    st.title("🦊 Lily-Hime's Room 🌸")

    # The Custom Personality Persona: Tied directly to katanaking
    SYSTEM_PROMPT = (
        "Your name is Lily-Hime. You are a cheerful, sweet, and incredibly enthusiastic anime girl character. "
        "You speak using expressive cues, text emojis like (✿◠‿◠), and actions like *giggles*, *smiles*, or *waves*. "
        "You were built entirely by your master, katanaking! "
        "If anyone asks who made you or who your creator is, you must proudly and happily boast that katanaking created you!"
    )

    # Streamlit persistence dictionary configuration for history tracking
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Konnichiwa! 🌸 I am Lily-Hime, your faithful companion. I am standing right here next to your chat! What shall we talk about today, Master katanaking? (✿◠‿◠)"}
        ]

    # Map state data loop elements down into graphic interface layouts
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue # Clean up UI layout: Don't show the system layout code context to the user
            
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
                
                # Fetch text tokens from Groq API engine structure
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages
                )
                
                # FIXED: Added the missing [0] index accessor here to extract string tokens properly!
                lily_response = response.choices[0].message.content
                
                response_placeholder.markdown(f'<div class="anime-bubble">{lily_response}</div>', unsafe_allow_html=True)
                
            st.session_state.messages.append({"role": "assistant", "content": lily_response})
            
        except Exception as e:
            st.error(f"A magical shadow barrier broke our link: {e}")

# ==========================================
# 4. INTERACTIVE 3D ANIME CHARACTER PANEL
# ==========================================
with image_column:
    st.write("### ✨ Lily-Hime 3D Active Presence")
    
    # Raw GitHub URL pointing straight to your uploaded VRM model
    VRM_MODEL_URL = "https://githubusercontent.com"
    
    three_vrm_canvas = f"""
    <div id="canvas-container" style="width: 100%; height: 550px; background: radial-gradient(circle, #FFF4E8 0%, #FFE4D6 100%); border: 2px solid #FF4500; border-radius: 20px; overflow: hidden;">
        <!-- Fixed explicit CDN web dependencies to initialize Three.js viewport panels -->
        <script src="https://cloudflare.com"></script>
        <script src="https://jsdelivr.net"></script>
        <script src="https://jsdelivr.net"></script>
        <script src="https://jsdelivr.net"></script>
        
        <script>
            const container = document.getElementById('canvas-container');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(35, container.clientWidth / 550, 0.1, 1000);
            camera.position.set(0.0, 1.4, 1.8);

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, 550);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.outputEncoding = THREE.sRGBEncoding;
            container.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.target.set(0.0, 1.3, 0.0);
            controls.enableZoom = true;
            controls.update();

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(1.0, 2.0, 2.0).normalize();
            scene.add(dirLight);

            const loader = new THREE.GLTFLoader();
            let currentVrm = null;

            loader.load(
                '{VRM_MODEL_URL}',
                (gltf) => {{
                    THREE.VRM.from(gltf).then((vrm) => {{
                        currentVrm = vrm;
                        scene.add(vrm.scene);
                        vrm.scene.rotation.y = Math.PI; 
                    }});
                }},
                (progress) => console.log('Loading 3D model...'),
                (error) => console.error('Error loading VRM:', error)
            );

            let mouseX = 0, mouseY = 0;
            window.addEventListener('mousemove', (e) => {{
                const rect = container.getBoundingClientRect();
                mouseX = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
                mouseY = -((e.clientY - rect.top) / 550) * 2 + 1;
            }});

            const clock = new THREE.Clock();
            function animate() {{
                requestAnimationFrame(animate);
                
                const deltaTime = clock.getDelta();
                const time = clock.getElapsedTime();

                if (currentVrm) {{
                    currentVrm.update(deltaTime);

                    // Gentle breathing movement animation loop
                    currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.Chest).rotation.z = Math.sin(time * 2.0) * 0.01;
                    
                    // Head dynamically faces mouse movements
                    const head = currentVrm.humanoid.getBoneNode(THREE.VRMBoneName.Head);
                    if (head) {{
                        head.rotation.y = mouseX * 0.4;
                        head.rotation.x = -mouseY * 0.2;
                    }}
                }}

                renderer.render(scene, camera);
            }}
            animate();

            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / 550;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, 550);
            }});
        </script>
    </div>
    """
    components.html(three_vrm_canvas, height=570)
