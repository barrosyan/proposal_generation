import os
import json
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

app = Flask(__name__)

# === CONFIGURAR GEMINI ===
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# === CONFIGURAR GOOGLE SHEETS ===
def connect_to_sheets():
    creds_dict = json.loads(os.getenv("GOOGLE_CREDS"))
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

def save_to_sheet(name, email, company, role, problem, currency, language, proposal):
    client = connect_to_sheets()
    sheet = client.open("EnterpriseLM_Proposals").sheet1
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name, email, company, role,
        problem, currency, language, proposal
    ])

# === FRONTEND HTML ===
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ELM Proposal Generator</title>
    <style>
        body { font-family: Arial; background: #f4f4f4; padding: 20px; }
        #form { background: white; padding: 20px; border-radius: 10px; width: 500px; margin: auto; }
        input, textarea, select, button { width: 100%; margin-top: 10px; padding: 10px; }
        #output { margin-top: 30px; white-space: pre-wrap; background: #eef; padding: 15px; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="form">
        <h2>🤖 ELM Proposal Generator (Beta)</h2>
        <input id="name" placeholder="Full Name">
        <input id="email" placeholder="Email">
        <input id="company" placeholder="Company">
        <input id="role" placeholder="Your Role">
        <textarea id="problem" placeholder="Describe your technical problem..."></textarea>
        <select id="currency">
            <option>BRL (R$)</option>
            <option>USD ($)</option>
            <option>EUR (€)</option>
            <option>GBP (£)</option>
        </select>
        <select id="language">
            <option>English</option>
            <option>Portuguese</option>
            <option>Spanish</option>
            <option>Italian</option>
        </select>
        <button onclick="send()">🚀 Generate Proposal</button>
        <div id="output"></div>
    </div>
    <script>
        async function send() {
            const data = {
                name: document.getElementById("name").value,
                email: document.getElementById("email").value,
                company: document.getElementById("company").value,
                role: document.getElementById("role").value,
                problem: document.getElementById("problem").value,
                currency: document.getElementById("currency").value,
                language: document.getElementById("language").value,
            };
            const res = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            const result = await res.json();
            document.getElementById("output").innerText = result.proposal || result.error;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    company = data.get("company", "")
    role = data.get("role", "")
    problem = data.get("problem", "")
    currency = data.get("currency", "USD ($)")
    language = data.get("language", "English")

    if not (name and email and problem):
        return jsonify({"error": "Please provide at least name, email, and problem."}), 400

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

    try:
        response = model.generate_content(prompt)
        proposal_text = response.text.strip()
        save_to_sheet(name, email, company, role, problem, currency, language, proposal_text)
        return jsonify({"proposal": proposal_text})
    except Exception as e:
        return jsonify({"error": f"Failed to generate proposal: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)