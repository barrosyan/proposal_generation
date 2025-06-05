import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIGURAÇÃO STREAMLIT ==========
st.set_page_config(page_title="ELM Proposal Generator", layout="centered")

# ========== CONFIGURAÇÃO GEMINI ==========
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ========== CONFIGURAÇÃO GOOGLE SHEETS ==========
def connect_to_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    return client

def save_to_sheet(problem, currency, language, proposal):
    client = connect_to_sheets()
    sheet = client.open("EnterpriseLM_Proposals").sheet1
    sheet.append_row([problem, currency, language, proposal])


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

problem = st.text_area("1. Technical Problem Description", placeholder="Describe the problem you'd like us to help with...")
currency = st.selectbox("2. Desired Proposal Currency", ["BRL (R$)", "USD ($)", "EUR (€)", "GBP (£)"])
language = st.selectbox("3. Proposal Language", ["English", "Portuguese", "Spanish", "Italian"])

submit = st.button("🚀 Generate Proposal")

# ========== GERAÇÃO DA PROPOSTA ==========
if submit and problem.strip():
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

        # Salvar no Google Sheets
        save_to_sheet(problem, currency, language, proposal_text)

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
