import json
import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv('.env')

# ========== CONFIGURAÇÃO STREAMLIT ==========
st.set_page_config(page_title="ELM Proposal Generator", layout="centered")

# ========== CONFIGURAÇÃO GEMINI ==========
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ========== CONFIGURAÇÃO GOOGLE SHEETS ==========
def connect_to_sheets():
    CREDENTIALS = {
          "type": "service_account",
          "project_id": "flask-appi",
          "private_key_id": "9ce0feaa601e15095d46927991a65b0901c4cc43",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDhpYaCSmzyzxui\nlSvkcKYGFTxi6pRAvc/tXiyccd/4CKE7F73xJuY725mVT2jZlRUg3Ok1E9XUZh6y\nucULuPIFfkzdG0LuhC7Aol8nPGiLAHOQ/JIQk7IllefXjZJ41VKxHM8v6orLC2vK\nkm5VKxl2qFIhkWNAk5OMFIHW1aNGiFV+a/4X1e9Fa35K6fva99XIQo+v1mETvOC/\nfWkGR9UYHRESaDABQiLP7KtNP/74qGeUjfx4ovZZJNlflBOA4HRMpdbaiBbHxEu8\ntAHBwQ0/SXGuTABPbQ/hNG/Qekb9jmod/pBWSrQZD/z/1Y/dOwwBaGWln+4sojwV\n1ZT2TqGZAgMBAAECggEADLoEQyGlfBsNnkw25InXTgKGnGGfU6N2WxdJAYM0CaOa\n9wqYw5rZDh6NpAE4PbAN4q5IV55dx2lXE+eBuJk0H/aGqUsvVDqPqdJpTCeOZ0Cd\nmVuAICqPDVWjdOHe6q0ayTMscFxp0EKS+s2VfCeT0RXJ7sC/eKtE0s1uoUpSt4M/\n3T4B8kmKyJID+34umK/Yj0bBkNYyMj0hdZIL14YMmVWStM2YaUaRNSH3ADlqAdUX\n7yxMQL3CkA5bKwWbxiuXeq/U+PyrQQsZgDhyuE1/j4sD7f9cl2sLoivtlQwzH8ns\n+teLb8I3x0iiHvSaEcMHc+C9cWAr12UBPQHo+gz/sQKBgQD3IppU/0VEjcJ5ZK3E\nT+UWpBk1ZFR+YzYsgHIY7K4+Ayj4nLp4+GwM4yly8UcUVCy5bW4fcEYOBtq7wKg+\n8K6cm6HLzCdHooZCAMduvymIo/22JXoUDuO69muKFgGKeXkYFkRPo2LRkA7OuoCx\nyccYP2ghaKZHZl5hY/TzYkUgpQKBgQDpvZjJaz+JuEY+BmHu5p/gg9qeFJROST15\nKr1eiREBV8xocxJyemusEtHBSr6byXW3mX/NWsdhxCet1eeBGY3FnnTLoOgHqB14\n5NAXIAjPZvdd64nUslRA6OA7MbnB8SNHxeVzSD/lwWvVNe3nB/7YbjV1GmVmz3DZ\n4s8zzq1W5QKBgQCq3FOTPEGpmdDAmOjCdvJN6vo6vbjlALatochAjzIQUaL772/E\nvwwFBPDdNQ8NcPzS3mNqfPcSL47+i75GdaRjRf5gpi7qCeWEsIExghy3CZoZWmPC\nhmDQHBpRh9Fc6YrdKlfkL3PcqxpxtuPPB1AM5Zmar312k8Hg13i85E4iuQKBgQC7\nL78f7uefXxfBrFLZg5AduPpnBowOddDpLDUjdBlOPgXQz/bB/xAjaZ7ZcQZctGW1\ndxRGXKC3xuMP7/HKDbDfxho6yM2I9DVGD9gl7N2hWxBXAr4KvBWFNfn87cGZc4eR\nfwZV4FJrqQ62XM386wZIRVpCQbVbNF1n4J+XGbjvkQKBgFqNH1CdDXEVSlOqolpV\n3eCtn6yKPZVU68PWqcPZ6YnF+RjSLnCTIHlYwPJ8okfGXkCzYUCdUojNIPvQ8hPx\nbhNeSmGk/G/tAsfoK1W79a4BfmivCse7AkhhI8s8eomfL/IcrVSO4LbZdk30XHu1\nZ0BIdYalVgjDGT6+JQEmTU8Z\n-----END PRIVATE KEY-----\n",
          "client_email": "automatize@flask-appi.iam.gserviceaccount.com",
          "client_id": "109404454649977700430",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/automatize%40flask-appi.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = json.loads(CREDENTIALS)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def save_to_sheet(name, email, company, role, problem, currency, language, proposal):
    client = connect_to_sheets()
    sheet = client.open("EnterpriseLM_Proposals").sheet1
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name, email, company, role,
        problem, currency, language, proposal
    ])

# ========== TEXTO INICIAL EXPLICATIVO ==========
st.title("🤖 ELM Proposal Generator (Beta)")
st.markdown("""
Welcome to the **Enterprise Learning Machines Proposal Generator**.

We're a small but highly specialized AI & Science team.  
To streamline our client intake process, this test version automatically generates a first-draft technical proposal from your problem description.

🔧 **Please note:** This is a **beta version**. Every submission will be reviewed manually before we contact you.

---

### 🧠 About Enterprise Learning Machines
We specialize in **Physics-Informed Machine Learning**, **Computer Vision**, and **AI Agents** for science and engineering problems.

We build:
- PINN pipelines and surrogates
- Scientific research automation
- AI agents with reasoning for complex tasks
- Geospatial ML solutions
""")

# ========== FORMULÁRIO ==========
st.header("📥 Provide Your Problem Details")

name = st.text_input("1. Your Full Name")
email = st.text_input("2. Email Address")
company = st.text_input("3. Company Name")
role = st.text_input("4. Your Role / Title")

problem = st.text_area("5. Technical Problem Description", placeholder="Describe the problem you'd like us to help with...")
currency = st.selectbox("6. Desired Proposal Currency", ["BRL (R$)", "USD ($)", "EUR (€)", "GBP (£)"])
language = st.selectbox("7. Proposal Language", ["English", "Portuguese", "Spanish", "Italian"])

submit = st.button("🚀 Generate Proposal")

# ========== GERAÇÃO DA PROPOSTA ==========
if submit:
    if not (name and email and problem):
        st.warning("⚠️ Please fill in at least your name, email and problem description.")
    else:
        with st.spinner("Generating proposal with Gemini..."):

            prompt = f"""
You are a proposal assistant for a scientific AI consulting firm.

Your goal is to create a detailed project proposal based on the user's problem description.

ONLY generate a proposal if the problem is in-scope for Enterprise Learning Machines, which specializes in:
- PINNs (Physics-Informed Neural Networks)
- LLM-based scientific automation
- AI agents for engineering tasks
- Computer vision for STEM
- Climate & geospatial modeling
- Surrogate modeling
- Custom pipelines for STEM problems

If the problem is clearly out of scope (e.g., social media apps, fintech, ecommerce), respond politely that it is outside our expertise and no proposal will be generated.

The proposal must include:
✅ Technical analysis of the challenge  
✅ Microtask breakdown  
✅ Estimated time and cost per microtask  
✅ Task difficulty level  
✅ Justification of the hourly rate (R$150/h base)  
✅ Total cost in selected currency  
✅ Mention of flexibility and openness to negotiation  
✅ One or two relevant real success cases  
✅ Translated to: {language}

Problem:
{problem}
Currency: {currency}
"""

            response = model.generate_content(prompt)
            proposal_text = response.text.strip()

            # Salvar tudo no Google Sheets
            save_to_sheet(name, email, company, role, problem, currency, language, proposal_text)

            # Exibir resultado
            st.success("✅ Proposal Generated Successfully!")
            st.markdown("---")
            st.subheader("📄 Proposal")
            st.markdown(proposal_text)

# ========== RODAPÉ ==========
st.markdown("""
---
📬 **Contact Us:** enterpriselearningmachines@gmail.com  
🌐 [Landing Page](https://enterpriselm.github.io/home)
""")
