<div align="center">
  <img src="https://github.com/user-attachments/assets/PLACEHOLDER_FOR_YOUR_LOGO" alt="DiAlert Logo" width="120" />
  <h1>DiAlert 🩺</h1>
  <p><strong>AI-Powered Diabetes Risk Assessment & Prediction System</strong></p>
</div>

<br>

DiAlert is an advanced, machine learning-driven web application designed to assess a patient's risk of developing diabetes based on clinical biomarkers. It features a modern, intuitive UI and instantly provides predictions alongside personalized health recommendations.

## ✨ Features

- **🧠 Machine Learning Prediction**: Uses a fine-tuned Random Forest Classifier (over 95% accuracy) to evaluate clinical data.
- **🧬 Comprehensive Biomarkers**: Analyzes essential metrics including BMI, HbA1c, Blood Glucose, age, hypertension, heart disease, and smoking history.
- **🖥️ Modern Web Interface**: Clean, dark-mode hero landing page and scan form built with HTML/CSS and styled for maximum readability.
- **💾 Patient History & Database**: Automatically saves every scan securely to a local SQLite database (`dialert_patients.db`).
- **📋 Personalized Recommendations**: Generates tailored actionable advice (e.g., diet change, doctor consultation) based on the specific risk profile.
- **⚡ Instant Results**: API-driven architecture using Flask to return real-time feedback.

## 🛠️ Tech Stack

- **Backend framework**: Python, Flask
- **Machine Learning**: Scikit-learn, Pandas, Joblib, imbalanced-learn
- **Database**: SQLite
- **Frontend**: Vanilla HTML / CSS

---

## 🚀 Getting Started

Follow these steps to run the DiAlert web application locally on your machine.

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/dialert.git
cd dialert
```

### 2. Set up a virtual environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the Flask web server:
```bash
python api.py
```
*The application should automatically open in your default browser. If it doesn't, navigate to `http://127.0.0.1:5001/` manually.*

---

## 📂 Project Structure

```
.
├── api.py                            # Main Flask backend server and API endpoints
├── train_model.py                    # Script to retrain or update the ML model
├── diabetes_prediction_dataset.csv   # The historical dataset used for ML training
├── model.pkl                         # The exported trained scikit-learn model
├── encoders.pkl                      # Encoded variables for mapping categorical strings
├── requirements.txt                  # List of Python dependencies
├── dialert_patients.db               # SQLite database mapping previous predictions
├── static/                           # Directory for static web assets (CSS/JS)
└── templates/
    ├── index.html                    # The Hero Landing Page UI
    ├── scan.html                     # Input form for new patients
    └── result.html                   # Graphic display of the prediction results
```

---

## 📊 Retraining the Model
If you'd like to tweak the algorithmic data or add new entries to `diabetes_prediction_dataset.csv`:
```bash
python train_model.py
```
This automatically updates `model.pkl` and `encoders.pkl` with your new training metrics using SMOTE balancing.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
