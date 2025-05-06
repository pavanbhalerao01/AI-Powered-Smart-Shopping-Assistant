import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib


df = pd.read_csv("D:/Downloads/sample_product_dataset_updated.csv")


df["combined"] = df["title"].fillna("") + " " + df["description"].fillna("")


vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["combined"])
y = df["label"]


model = LogisticRegression()
model.fit(X, y)

# Save model and vectorizer
joblib.dump(model, "eco_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Model and vectorizer saved successfully.")
