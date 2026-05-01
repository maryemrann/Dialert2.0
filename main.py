import requests
import json
import os
import webbrowser
from pathlib import Path


# ── Input helpers ────────────────────────────────────────────────────────────

def read_float(prompt):
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Invalid input. Please enter a number.")


def read_binary(prompt):
    while True:
        val = input(prompt).strip()
        if val in ("0", "1"):
            return int(val)
        print("Invalid input. Please enter 0 or 1.")


def read_gender():
    while True:
        val = input("Enter gender (Male/Female/Other): ").strip().capitalize()
        if val in ("Male", "Female", "Other"):
            return val
        print("Invalid input. Please try again.")


# 🔥 FIXED SMOKING INPUT (MAIN FIX)
def read_smoking_status():
    options = [
        "formerly smoked",
        "never smoked",
        "smokes",
        "No Info"
    ]

    print("\nSmoking status options:")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")

    mapping = {
        "1": "formerly smoked",
        "2": "never smoked",
        "3": "smokes",
        "4": "No Info"
    }

    while True:
        val = input("Enter smoking status (1-4): ").strip()

        if val in mapping:
            return mapping[val]

        print("Invalid input. Please enter 1, 2, 3, or 4.")


# ── Recommendations ──────────────────────────────────────────────────────────

def get_recommendations(prediction, hypertension, heart_disease, bmi, glucose, hba1c):
    recs = []

    if prediction == 1:
        recs.append("Diabetes detected. Please consult a doctor.")
        recs.append("Follow a low sugar, high fiber diet.")
        recs.append("Exercise daily (30 minutes).")
        recs.append("Monitor glucose regularly.")
    else:
        recs.append("No diabetes detected. Keep healthy lifestyle.")

    if hypertension == 1:
        recs.append("Control blood pressure and reduce salt intake.")

    if heart_disease == 1:
        recs.append("Consult cardiologist regularly.")

    if bmi > 25:
        recs.append("Reduce weight through diet & exercise.")
    elif bmi < 18.5:
        recs.append("Maintain proper nutrition.")

    if glucose > 140:
        recs.append("High glucose detected. Reduce sugar intake.")

    if hba1c >= 6.5:
        recs.append("Diabetic HbA1c range. Strict control needed.")
    elif hba1c >= 5.7:
        recs.append("Prediabetic range. Take preventive steps.")

    return recs


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    try:
        gender = read_gender()
        age = read_float("Enter age: ")
        hypertension = read_binary("Enter hypertension (0 = No, 1 = Yes): ")
        heart_disease = read_binary("Enter heart disease (0 = No, 1 = Yes): ")
        smoking_status = read_smoking_status()
        bmi = read_float("Enter BMI: ")
        hba1c = read_float("Enter HbA1c Level: ")
        glucose = read_float("Enter Blood Glucose Level: ")

        payload = {
            "gender": gender,
            "age": age,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "smoking_history": smoking_status,
            "bmi": bmi,
            "HbA1c_level": hba1c,
            "blood_glucose_level": glucose
        }

        print("\n[Running prediction...]\n")

        response = requests.post("http://127.0.0.1:5001/predict", json=payload)

        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        result_json = response.json()
        prediction = result_json["prediction"]
        probability = result_json.get("probability", 100.0 if prediction == 1 else 0.0)

        label = "Diabetic" if prediction == 1 else "Non-Diabetic"
        print(f"Prediction: {label} ({probability:.2f}% risk)\n")

        recommendations = get_recommendations(
            prediction, hypertension, heart_disease, bmi, glucose, hba1c
        )

        for rec in recommendations:
            print("- " + rec)

        output = {
            "gender": gender,
            "age": age,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "smoking_status": smoking_status,
            "bmi": bmi,
            "hba1c": hba1c,
            "glucose": glucose,
            "prediction": prediction,
            "probability": round(probability, 2),
            "risk_level": label,
            "recommendations": recommendations
        }

        # Save result.txt next to this script
        script_dir = Path(__file__).parent
        result_txt = script_dir / "result.txt"
        with open(result_txt, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n[Result saved to {result_txt}]")

        # result.html lives in output/ subfolder — open it via a local Flask route
        # to avoid browser fetch() CORS restriction on file:// URLs
        html_path = script_dir / "output" / "result.html"
        if html_path.exists():
            webbrowser.open(f"http://127.0.0.1:5001/result")
        else:
            print("result.html not found in output/ folder.")

    except requests.exceptions.ConnectionError:
        print("\nERROR: API not running. Run: python api.py")

    except Exception as ex:
        print(f"An error occurred: {ex}")


if __name__ == "__main__":
    main()