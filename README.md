## Error-Explainer-Project (AI CodeSense Enterprise)
- Hi, I am Yogeswarachary Modepalli. I am learning Data Science course. In the part of course, when I was doing coding I'll always get syntax errors, logic errors and many more errors.
- When I see the error, I'll always unable to understand, because the thown error is not exactly human reable format. So I've decided to do one simple project that help coding learners and developers
that can explain the errors to learners (who practicing the code) in a simple and plain english in the 2 to 3 statements.
- For this I've found free api service tier from Groq, which is providing multiple llm models for different kinds of purposes like text to speech, logical thinking, reasoning and many other purposes.
- I choose Groq, because it have lightening speed with more access for the API call compare with the any other GPT tools Free tier api service.
- By using the Groq API, Streamlit I've created a simple project that explain coding errors and provide solutions.

## What is the special about this project
- Secure AI-powered code error debugging with enterprise-grade privacy controls, PII redaction, proxy routing, and audit logging.
#### 🚀 Features
- 🔍 Smart Error Analysis - Explains syntax, logic, and runtime errors in plain English
- 🔒 Confidential Mode - Auto-redacts API keys, emails, company names before AI processing
- 📱 Multi-Level Explanations - Beginner/Intermediate/Advanced tailored responses
- 💻 Copy-Paste Fixes - Structured JSON output with ready-to-use corrected code
- 📊 Enterprise Audit Trail - Local CSV logging for compliance (GDPR/SOC2 ready)
- 🌐 Private Proxy Support - Route through corporate VPC/firewall
- ⚡ Blazing Fast - Groq LPU inference (<1s responses)

#### Quickstart
1. Deploy on Streamlit Cloud (2 minutes)
   1. Fork this repo
   2. Deploy → Streamlit Cloud
   3. Add secrets: GROQ_API_KEY (from console.groq.com)
   4. Optional: GROQ_PROXY_URL for private routing

2. Local Development
  > pip install -r requirements.txt
  > streamlit run app.py

#### 📊 Usage Demo
text
❌ Error: "IndexError: list index out of range"
📄 Code: for i in range(10): print(data[i+1])

#### ✅ AI Output:
meaning: "Trying to access list position that doesn't exist"
fix_code: `for i in range(len(data)-1): print(data[i])`
prevention: "Always use len() or enumerate() for safe indexing"

####🔒 Enterprise Security

| Feature        | Status                              |
| -------------- | ----------------------------------- |
| PII Redaction  | ✅ Regex (API keys, emails, domains) |
| Proxy Routing  | ✅ VPC/Private Connect               |
| Audit Logging  | ✅ Local CSV (downloadable)          |
| Data Residency | ✅ No cloud storage                  |

#### 🤝 Contributing
1.Fork the repo
2. Create feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add some AmazingFeature')
4. Push (git push origin feature/AmazingFeature)
5. Open Pull Request

#### 👨‍💻 Author
Yogeswarachary - Data Science & AI Developer
