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
          "private_key_id": "166d8a063d10b55b503f6d35cfc2956f9ab7a206",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDDJ31Vk4v0p60N\nxrxd0Ehrl5e/9n6voiWnQStou+/8e/iNrV7PPqlNDBvb1x4npd0SmYNQBzHM9iNO\nZBwC7PonY2hqzDRMk6qR5qZimMd2/yN27q9CtDefDy6gEaya760SgTWe2znbPcxC\n4huzV72A+fFc8KGsIRO8kemcTJMv4I0wfg4X2fDLPsLzZBGXIc8kkjMs/oipuZD+\nZsxx+TNSQ9XhbtU2s6TYeC2cuBgyA5fXrWKd5aTwCxLXg4AMEz5ZY47pMtjNAp+p\nsn5Vt712DWUXalqwEL9BfeEo7leSOQTMzW8ZYTCyy+5o1X7jHKW2PJ9USErkFM7L\nJJ2GgQQXAgMBAAECggEACdIY6o+MQXmWqdTQceAjZNayGkTrRydfwbTz3Edo4knS\nzj5lQQSkPG5ZkIyYxeIA6Ai1pPdXuDrCuBUtm7AVPpowDP/NufTMZp82zEtn7kMU\no82LIE41Zlm7PO7mwr1A9mduLVpW5QONHeiHAFVwAeeSD91EJYdcmOa23Ni1p3kM\nzCHbrP7mXqKfDmPxMHe7YGNbmYrFRgjN3jZOdAcc2u968XPuFmSO5xtjcyxgSwfN\nxfRe5w7nmIyI67h1hGuQhElXwDEF1sv1shAugpTupjCaFWPa0TlcTFA7tzEe54qO\nTMp4YNqE5GIhpPH9qhWozYIb+sEbMMsKY7sImHlAEQKBgQD0QyhQY9yx097ieVbZ\nWifsVBnBnN2/Wc5BwX4QhiEE2vemuDhxyUzqxHE+gbj1GbZHtCe3xUzfZeC36TcY\n7qBNmgT7GaUUf0VAe243bmdxKZHvIhAL2phe0jpHLcqIRbLzQHhhSWldV5cZdMUn\nhmr7S08MRJpGAE6ju6AlxzpClQKBgQDMiDgaoQEtJi6IX7zVx9lzpi/KI21qFYpx\nn6G8NLA3ADK7vbb3qW5jeif1RYwkOksTxFhsow1PcLHs/0SzHfxqUQAvZysu+K5G\nVvNZeUmuoyrd+T0bDafDgbJx0SidaegyM1EVAZO2QVss5ODJ7W92UdzZAo4K878X\nIRrgHEfM+wKBgHc51JKwu8edCBz5Zzf+dqA3SL8lh2NgPXoBLTx5i+Jn0xvwrbR0\nsnOhYTlGbnZMj5meSQi9aFFe0/pQ/pDP4TUfqbC7CsXffXkFBn5OCHXG+bGEqdpv\nX5JhAQs/Qa2Uf82WOWwbPi/OkjVdtuIdDVkNoE73qWnjun7XFUt7XGelAoGBAILx\n+ylhRwWG2mfJE3ay2k8maJY7lENEwzv3fW6nNOIhqFl2Hnv0542cmZR4ED7pa0Oe\ngxYaVd00Q1V+IJekbQQME9hFbupFoB28cVQpSLkcEcfHWA3H8k5C7OHdjOkq8tOg\n8xpFxjH7KcpWRmxBLQlNY90zu4jbgM3oDfLJaFadAoGBANN97lOEInWrGef5k5e1\nVuslVd94Rf8TozkV2Cdmm1A0myRJevyPrFIfFZhJD6K1xQd4etZn20zx5Cafe8cA\nAgFEAXW6EZZUhSufiOSl3/qjPosQuSxo11fJkMa4qdMPSndvz5FNl+SvnY6NlvGY\ny7jzy1IkBBZ2YoXcWLHienMM\n-----END PRIVATE KEY-----\n",
          "client_email": "automatize@flask-appi.iam.gserviceaccount.com",
          "client_id": "109404454649977700430",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/automatize%40flask-appi.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }


    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, scope)
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
