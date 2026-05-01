import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("diabetes_prediction_dataset.csv")


print("Columns in dataset:", df.columns)

# Initialize encoders
gender_encoder = LabelEncoder()
smoking_encoder = LabelEncoder()

# Encode categorical features
df['gender'] = gender_encoder.fit_transform(df['gender'])
df['smoking_history'] = smoking_encoder.fit_transform(df['smoking_history'])

# Save encoders together for easy loading
encoders = {'gender': gender_encoder, 'smoking_history': smoking_encoder}
joblib.dump(encoders, "encoders.pkl")

# Features and target
FEATURE_ORDER = [
    'gender', 'age', 'hypertension', 'heart_disease',
    'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level'
]

X = df[FEATURE_ORDER]
y = df["diabetes"]

# Balance dataset with SMOTE
smote = SMOTE(random_state=42)
X_bal, y_bal = smote.fit_resample(X, y)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X_bal, y_bal, test_size=0.2, random_state=42)

# Train RandomForest with tuned params
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=10,
    random_state=42
)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")
print(" Model and encoders saved successfully!")

# Evaluate
y_pred = model.predict(X_test)
print(f" Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Show original distribution
print("\nOriginal Class Distribution:\n", y.value_counts())

# Plot feature importance
importances = model.feature_importances_
sns.barplot(x=importances, y=FEATURE_ORDER)
plt.title("Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.show()
