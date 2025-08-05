from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

# Simple symptom severity mapping
symptom_db = {
    "chest pain": "emergency",
    "shortness of breath": "emergency",
    "fever": "doctor",
    "cough": "self-care",
    "headache": "self-care",
    "dizziness": "doctor",
    "loss of consciousness": "emergency"
}

# Extract symptoms from user input
def extract_symptoms(text):
    doc = nlp(text.lower())
    extracted = []

    for chunk in doc.noun_chunks:
        if chunk.text in symptom_db:
            extracted.append(chunk.text)
    
    # Also check token-level match
    for token in doc:
        if token.text in symptom_db and token.text not in extracted:
            extracted.append(token.text)
    
    return extracted

# Triage decision logic
def triage(symptoms):
    if not symptoms:
        return "⚠️ No known symptoms detected. Please describe in more detail."
    
    for symptom in symptoms:
        if symptom_db[symptom] == "emergency":
            return "🚨 Emergency – Seek medical help immediately!"
    
    for symptom in symptoms:
        if symptom_db[symptom] == "doctor":
            return "📋 See a doctor within 24-48 hours."
    
    return "💊 Self-care is recommended. Monitor your symptoms."

@app.route("/triage", methods=["POST"])
def triage_route():
    data = request.get_json()
    user_input = data.get("message", "")
    
    symptoms = extract_symptoms(user_input)
    decision = triage(symptoms)
    
    return jsonify({
        "input": user_input,
        "symptoms": symptoms,
        "decision": decision
    })

if __name__ == "__main__":
    app.run(debug=True)
