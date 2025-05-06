import joblib
import pandas as pd

# Load model and vectorizer
model = joblib.load("eco_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Path to dataset
DATASET_PATH = "D:/VS Code/Python/DV_CP/sample_product_dataset_updated.csv"

def predict_eco_friendly(title, description):
    input_text = f"{title} {description}"
    vectorized_input = vectorizer.transform([input_text])
    prediction = model.predict(vectorized_input)[0]
    return prediction  # 1 or 0

def add_to_dataset(title, description, label):
    new_row = {
        "title": title,
        "description": description,
        "label": label
    }
    try:
        df = pd.read_csv(DATASET_PATH)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([new_row])
    df.to_csv(DATASET_PATH, index=False)

# Test example
if __name__ == "__main__":
    title = "Bamboo Toothbrush"
    description = "A compostable toothbrush made from sustainable bamboo."
    result = predict_eco_friendly(title, description)
    print("Prediction:", "Eco-Friendly ✅" if result == 1 else "Not Eco-Friendly ❌")
    add_to_dataset(title, description, result)
