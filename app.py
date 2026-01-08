import streamlit as st
import os
import re
import csv
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import httpx

# Load environment
load_dotenv()

groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
if not groq_api_key:
    st.error("❌ GROQ_API_KEY required in secrets.")
    st.stop()

# Configs (enterprise overrides)
GROQ_BASE_URL = st.secrets.get("GROQ_PROXY_URL", "https://api.groq.com/openai/v1")  # Private proxy
LOG_FILE = "audit_logs.csv"

client = Groq(
    api_key=groq_api_key,
    base_url=GROQ_BASE_URL,
    timeout=httpx.Timeout(30.0)
)

st.set_page_config(layout="wide", page_title="AI CodeSense Enterprise")

# Sidebar: Privacy & Logs
with st.sidebar:
    st.header("🔒 Enterprise Controls")
    privacy_mode = st.toggle("Privacy Mode (Anonymize PII)", value=True)
    if privacy_mode:
        st.success("✅ Inputs redacted before AI call")
    st.subheader("📊 Audit Logs")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)  # Requires pandas in requirements
        st.dataframe(df.tail(10))

st.title("💼 AI CodeSense Enterprise — Secure Code Fixing")
st.caption("🔒 Confidential Mode | Proxy-Ready | Audit-Logged")

# PII Redactor (regex for code-safe anonymization)
def redact_pii(text):
    patterns = {
        r'api[_-]?key["\']?\s*[=:]\s*["\']?[a-zA-Z0-9_-]{20,}': '[API_KEY]',
        r'(https?://[^\s]+|www\.[^\s]+)': '[URL]',
        r'\b[A-Z][a-z]+(?:[A-Z][a-z]+){2,}\b': '[COMPANY]',  # CamelCase companies
        r'@\w+\.\w+': '[EMAIL]',
        r'[A-Z]{3}\d{4,}': '[DB_FIELD]',  # e.g., ACC1234
        r'(?:user|customer)_?id["\']?\s*[=:]\s*["\']?\d+': '[USER_ID]',
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b': '[PHONE]'
    }
    for pattern, replacement in patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def log_activity(user_input, redacted, response, mode):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if os.path.getsize(LOG_FILE) == 0:
            writer.writerow(['Timestamp', 'Input Length', 'PII Detected', 'Mode', 'Response Preview'])
        writer.writerow([datetime.now().isoformat(), len(user_input), 'Yes' if user_input != redacted else 'No', mode, response[:100]])

# Inputs
col1, col2 = st.columns(2)
error_input = col1.text_area("❌ Error:", height=150, key="error")
code_input = col2.text_area("📄 Code:", height=150, key="code")

# Preview Redaction
if privacy_mode:
    redacted_error = redact_pii(error_input)
    redacted_code = redact_pii(code_input)
    with st.expander("👁️ Preview Redacted Input (sent to AI)"):
        st.code(redacted_error + "\n\n" + redacted_code)

# Settings & Buttons
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
model = col2.radio("Model", ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"])
analyze_btn = col3.button("🔍 Secure Analyze", use_container_width=True)

# Analyze
if analyze_btn and (error_input or code_input):
    input_to_use = error_input + "\n\n" + code_input
    redacted_input = redact_pii(input_to_use) if privacy_mode else input_to_use
    
    log_activity(input_to_use, redacted_input, "Pending", "Privacy" if privacy_mode else "Public")
    
    with st.spinner("Analyzing securely..."):
        prompt = f"""Expert debugger. Error+code (PII redacted):


JSON output: {{"meaning":"","cause":"","fix_code":"","prevention":""}}"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=1500
            )
            result = json.loads(response.choices[0].message.content)
            
            log_activity(input_to_use, redacted_input, str(result), "Success")
            
            # Render Results
            for k, v in result.items():
                if 'code' in k:
                    st.code(v, "python")
                else:
                    st.markdown(f"**{k.title()}:** {v}")
                    
        except Exception as e:
            log_activity(input_to_use, redacted_input, str(e), "Error")
            st.error(f"Error: {e}")

st.info("👨‍💼 Enterprise: Set GROQ_PROXY_URL in secrets for private routing. Logs saved locally.")
