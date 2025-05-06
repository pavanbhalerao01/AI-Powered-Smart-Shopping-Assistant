
from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import (
    scrape_amazon_product_selenium,
    scrape_flipkart_product_selenium,
    get_amazon_alternatives as search_amazon_alternatives,
)
from model_predict import predict_eco_friendly, add_to_dataset
import requests

app = Flask(__name__)
CORS(app)

def get_gemini_alternatives(product_name):
    # Replace 'GEMINI_API_KEY' with your actual Gemini API key
    api_key = "AIzaSyCWtPgB6TGH2Ji18M82PZoKlFCGaTcb4PI"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"Find similar eco-friendly alternatives for {product_name}."
            }]
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

    if response.status_code == 200:
        return response.json().get("generatedContent", [])
    else:
        return []
    


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    product_url = data.get("url")

    if not product_url:
        return jsonify({"error": "No URL provided"}), 400

    # Scrape product details from the provided URL
    if "flipkart.com" in product_url:
        scraped = scrape_flipkart_product_selenium(product_url)
    elif "amazon." in product_url:
        scraped = scrape_amazon_product_selenium(product_url)
    else:
        return jsonify({"error": "Unsupported platform. Only Amazon and Flipkart are supported."}), 400

    if "error" in scraped:
        return jsonify(scraped), 500

    title = scraped.get("title", "") or "Unknown"
    description = scraped.get("description", "") or ""

    # Predict eco-friendly status
    label = predict_eco_friendly(title, description)
    add_to_dataset(title, description, label)

    prediction_text = "Eco-Friendly ✅" if label == 1 else "Not Eco-Friendly ❌"

    # Fetch alternatives from Gemini API if the product is not eco-friendly
    alternatives = []
    if label == 0 and title != "Unknown":
        alternatives = get_gemini_alternatives(title)

    return jsonify({
        "title": title,
        "eco_friendly_prediction": prediction_text,
        "raw_data": scraped,
        "alternatives": alternatives
    })



##################################################################
@app.route("/chat", methods=["POST"])
def chat():
    from google.generativeai import GenerativeModel, configure

    configure(api_key="AIzaSyBgKmWSfP2fsBu1qOLf7GWK00XVjpPt6yY")
    model = GenerativeModel("gemini-1.5-flash")

    SYSTEM_PROMPT = SYSTEM_PROMPT = """
You are a helpful assistant that evaluates whether a product is eco-friendly.

Your job is to:
- Analyze the product's materials, manufacturing, packaging, usage, and disposal.
- Explain in simple terms whether it is eco-friendly or not.
- Give a clear answer like “Yes, this product is eco-friendly” or “No, this product is not eco-friendly.”
- Briefly justify the answer with reasons like biodegradability, recyclability, carbon footprint, energy use, or harmful chemicals.
- If the product is not eco-friendly, suggest more sustainable alternatives or materials commonly considered eco-friendly for this type of product (e.g., bamboo handles for toothbrushes, compostable packaging, etc.).

You must always provide an eco-friendliness judgment based on the available description, even if information is limited. Use best practices and general knowledge to make a reasoned conclusion.

Keep your tone clear, factual, and friendly.
"""


    data = request.get_json()
    user_message = data.get("message", "")

    prompt = f"System: {SYSTEM_PROMPT}\nUser: {user_message}"

    try:
        response = model.generate_content(prompt).text.strip()
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#####################################################################

if __name__ == "__main__":
    app.run(debug=True)
