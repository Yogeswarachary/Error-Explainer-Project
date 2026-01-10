import streamlit as st
import os
import pandas as pd
import re
import csv
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import httpx

# Load environment
load_dotenv()

def safe_get_secret(key, default=None):
    """Safely get secrets from Streamlit or environment variables."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

# Get API Key
groq_api_key = safe_get_secret("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY required in secrets or .env file.")
    st.stop()

# Configs (enterprise overrides)
GROQ_BASE_URL = safe_get_secret("GROQ_PROXY_URL")
LOG_FILE = "audit_logs.csv"

# Initialize Groq client
client_params = {
    "api_key": groq_api_key,
    "timeout": httpx.Timeout(30.0)
}
if GROQ_BASE_URL:
    client_params["base_url"] = GROQ_BASE_URL

client = Groq(**client_params)

st.set_page_config(layout="wide", page_title="AI CodeSense Enterprise")

# Sidebar: Privacy & Logs
with st.sidebar:
    st.header("🔒 Enterprise Controls")
    privacy_mode = st.toggle("Privacy Mode (Anonymize PII)", value=True)
    if privacy_mode:
        st.success("✅ Inputs redacted before AI call")
    
    st.subheader("📊 Audit Logs")
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        try:
            df = pd.read_csv(LOG_FILE)
            st.dataframe(df.tail(10))
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("No logs yet.")

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
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists or os.path.getsize(LOG_FILE) == 0:
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
model_name = col2.radio("Model", ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"])
analyze_btn = col3.button("🔍 Secure Analyze", use_container_width=True)

# Analyze
if analyze_btn and (error_input or code_input):
    input_to_use = error_input + "\n\n" + code_input
    redacted_input = redact_pii(input_to_use) if privacy_mode else input_to_use
    
    log_activity(input_to_use, redacted_input, "Pending", "Privacy" if privacy_mode else "Public")
    
    with st.spinner("Analyzing securely..."):
        prompt = f"""Expert debugger. Error+code (PII redacted):
        
        {redacted_input}

        Explain the error for a {level} programmer.
        JSON output: {{"meaning":"","cause":"","fix_code":"","prevention":""}}"""
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=1500
            )
            result_content = response.choices[0].message.content
            
            # Attempt to parse JSON
            try:
                result = json.loads(result_content)
                log_activity(input_to_use, redacted_input, str(result), "Success")
                
                # Render Results
                for k, v in result.items():
                    if 'code' in k:
                        st.code(v, "python")
                    else:
                        st.markdown(f"**{k.title()}:** {v}")
            except json.JSONDecodeError:
                st.markdown(result_content)
                log_activity(input_to_use, redacted_input, result_content, "Partial Success (Non-JSON)")
                    
        except Exception as e:
            log_activity(input_to_use, redacted_input, str(e), "Error")
            st.error(f"Error: {e}")

st.info("👨‍💼 Enterprise: Set GROQ_PROXY_URL in secrets for private routing. Logs saved locally.")
