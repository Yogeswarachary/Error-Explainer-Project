import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Load API key (from Streamlit secrets on Cloud or .env locally)
groq_api_key = (
    st.secrets.get("GROQ_API_KEY")
    if "GROQ_API_KEY" in st.secrets
    else os.getenv("GROQ_API_KEY")
)

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please set it in Streamlit Secrets or .env file.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=groq_api_key)

st.set_page_config(page_title="AI CodeSense", page_icon="💡", layout="centered")

st.title("💡 AI CodeSense — Explain Coding Errors in Plain English")
st.caption("Powered by Groq API | Created by Yogeswarachary")

# --- Helper Functions ---
def build_prompt(error, level):
    tone = {
        "Beginner": "Explain like teaching a school student using simple words and examples.",
        "Intermediate": "Use programming analogies and show quick fixes.",
        "Advanced": "Be concise and technical, focus on root causes."
    }[level]

    prompt = f"""
You are an AI coding assistant that explains programming errors in {level.lower()} terms.
{tone}

Error message:
```
{error}
```

Please answer with these sections:
1️⃣ Meaning (in simple English)
2️⃣ Why it happened
3️⃣ 1️⃣-line fix or code correction
4️⃣ Analogy (only if it helps)

Keep it friendly, short, and clear.
"""
    return prompt

def clear_text():
    st.session_state.error_text = ""

# --- Input Section ---
if "error_text" not in st.session_state:
    st.session_state.error_text = ""

st.text_area(
    "🧩 Paste your error message here:",
    key="error_text",
    height=200,
    placeholder="Type or paste your compiler/interpreter error here...",
)

# --- Settings Section ---
col1, col2 = st.columns(2)
with col1:
    level = st.selectbox("🧠 Explanation Level", ["Beginner", "Intermediate", "Advanced"])
with col2:
    mode = st.radio("⚙️ Model Mode", ["⚡ Fast (Llama-3.1-8B)", "🎯 Accurate (GPT-OSS-20B)"])

# --- Buttons Section ---
col1, col2 = st.columns([1, 1])  # Two equal columns

with col1:
    explain_btn = st.button("🔍 Explain Error", key="explain_btn", use_container_width=True)

with col2:
    # Use on_click to ensure state is cleared before next render
    clear_btn = st.button("🧹 Clear Text", key="clear_btn", use_container_width=True, on_click=clear_text)

# --- Logic & Output ---
if explain_btn:
    if not st.session_state.error_text.strip():
        st.warning("Please enter an error message first.")
    else:
        with st.spinner("Analyzing your error..."):
            prompt = build_prompt(st.session_state.error_text, level)
            model = "llama-3.1-8b-instant" if "Fast" in mode else "gpt-oss-20b"
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500,
                )
                result = response.choices[0].message.content
                st.markdown(result)
            except Exception as e:
                st.error(f"⚠️ API Error: {str(e)}")

st.divider()
st.info("💡 Tip: Try pasting errors from Python, C++, or JavaScript — AI CodeSense will decode them instantly!")
