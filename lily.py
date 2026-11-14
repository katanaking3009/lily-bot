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
    layout="centered"
)

# Ultra-transparent glass UI with buttons safely tucked on the side
st.markdown("""
<style>
  /* Make Streamlit main containers transparent so the 3D background shows through */
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
      background: transparent !important;
  }

  /* FIX: let clicks pass through Streamlit's page layers to the 3D iframe buttons */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="stHeader"] {
      pointer-events: none !important;
  }

  /* Pin ONLY the 3D VRM iframe to cover the full background */
  iframe[height="800"] {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 0 !important;