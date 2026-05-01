from flask import Flask, request, jsonify, send_from_directory, render_template
import joblib
import pandas as pd
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "dialert_patients.db"

model = joblib.load(BASE_DIR / "model.pkl")
encoders = joblib.load(BASE_DIR / "encoders.pkl")

FEATURE_ORDER = [
    'gender', 'age', 'hypertension', 'heart_disease',
    'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level'
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            gender TEXT,
            age REAL,
            hypertension INTEGER,
            heart_disease INTEGER,
            smoking_history TEXT,
            bmi REAL,
            hba1c REAL,
            blood_glucose_level REAL,
            prediction INTEGER,
            probability REAL,
            risk_level TEXT,
            recommendations TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def fix_smoking(value):
    value = str(value).lower().strip()
    mapping = {
        "smokes": "smokes", "smoker": "smokes", "current": "smokes",
        "never smoked": "never smoked", "never": "never smoked",
        "formerly smoked": "formerly smoked", "former": "formerly smoked",
        "no info": "No Info", "unknown": "No Info"
    }
    return mapping.get(value, "No Info")

def get_recommendations(prediction, hypertension, heart_disease, bmi, glucose, hba1c):
    recs = []
    if prediction == 1:
        recs.append("Diabetes detected. Please consult a doctor immediately.")
        recs.append("Follow a low sugar, high fiber diet.")
        recs.append("Exercise daily for at least 30 minutes.")
        recs.append("Monitor blood glucose regularly.")
    else:
        recs.append("No diabetes detected. Keep up a healthy lifestyle!")
    if hypertension == 1:
        recs.append("Control blood pressure and reduce salt intake.")
    if heart_disease == 1:
        recs.append("Consult a cardiologist regularly.")
    if bmi > 25:
        recs.append("Reduce weight through balanced diet & exercise.")
    elif bmi < 18.5:
        recs.append("Maintain proper nutrition to reach a healthy weight.")
    if glucose > 140:
        recs.append("High glucose detected. Significantly reduce sugar intake.")
    if hba1c >= 6.5:
        recs.append("Diabetic HbA1c range. Strict glucose control is needed.")
    elif hba1c >= 5.7:
        recs.append("Prediabetic HbA1c range. Take preventive steps now.")
    return recs

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/logo')
def logo():
    output_dir = BASE_DIR / "output"
    return send_from_directory(str(output_dir), "3re_Logo-removebg-preview.png")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if "smoking_history" in data:
        data["smoking_history"] = fix_smoking(data["smoking_history"])

    input_df = pd.DataFrame([data], columns=FEATURE_ORDER)

    for column in input_df.select_dtypes(include='object').columns:
        if column in encoders:
            try:
                input_df[column] = encoders[column].transform(input_df[column])
            except Exception:
                input_df[column] = encoders[column].transform(["No Info"])

    prediction = model.predict(input_df)[0]
    try:
        proba = model.predict_proba(input_df)[0]
        probability = round(float(proba[1]) * 100, 2)
    except AttributeError:
        probability = 100.0 if prediction == 1 else 0.0

    hypertension = data.get('hypertension', 0)
    heart_disease = data.get('heart_disease', 0)
    bmi = data.get('bmi', 0)
    hba1c = data.get('HbA1c_level', 0)
    glucose = data.get('blood_glucose_level', 0)
    label = "Diabetic" if int(prediction) == 1 else "Non-Diabetic"

    recommendations = get_recommendations(
        int(prediction), hypertension, heart_disease, bmi, glucose, hba1c
    )

    output = {
        "patient_name": data.get("patient_name", "Anonymous"),
        "gender": data.get("gender"),
        "age": data.get("age"),
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "smoking_status": data.get("smoking_history"),
        "bmi": bmi,
        "hba1c": hba1c,
        "glucose": glucose,
        "prediction": int(prediction),
        "probability": probability,
        "risk_level": label,
        "recommendations": recommendations
    }

    result_txt = BASE_DIR / "result.txt"
    with open(result_txt, "w") as f:
        json.dump(output, f, indent=2)

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO patients (
                patient_name, gender, age, hypertension, heart_disease,
                smoking_history, bmi, hba1c, blood_glucose_level,
                prediction, probability, risk_level, recommendations, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            output["patient_name"], output["gender"], output["age"],
            output["hypertension"], output["heart_disease"],
            output["smoking_status"], output["bmi"], output["hba1c"],
            output["glucose"], output["prediction"], output["probability"],
            output["risk_level"], json.dumps(output["recommendations"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

    return jsonify({'prediction': int(prediction), 'probability': probability})

@app.route('/result-data')
def result_data():
    result_file = BASE_DIR / "result.txt"
    if not result_file.exists():
        return jsonify({"error": "No result yet"}), 404
    with open(result_file, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM patients ORDER BY created_at DESC LIMIT 50")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
