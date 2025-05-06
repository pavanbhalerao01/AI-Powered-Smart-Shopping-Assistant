import React, { useState } from "react";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { sender: "bot", text: "Hello, I’m here to listen. What would you like to talk about today?" }
  ]);

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Error analyzing product.");
    }

    setLoading(false);
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatHistory((prev) => [...prev, { sender: "user", text: userMessage }]);
    setChatInput("");

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      if (data.reply) {
        setChatHistory((prev) => [...prev, { sender: "bot", text: data.reply }]);
      } else {
        setChatHistory((prev) => [...prev, { sender: "bot", text: "Sorry, I couldn't understand that." }]);
      }
    } catch (error) {
      setChatHistory((prev) => [...prev, { sender: "bot", text: "Error contacting the assistant." }]);
    }
  };

  return (
    <div className="container">
      <h1 className="title">Eco-Friendly Product Analyzer 🌱</h1>

      <input
        className="input"
        type="text"
        placeholder="Paste Amazon or Flipkart product URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <button className="button" onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Product"}
      </button>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <h2>{result.title}</h2>
          <p><strong>Eco-Friendly Prediction:</strong> {result.eco_friendly_prediction}</p>
          <p><strong>Price:</strong> ₹{result.raw_data?.price ?? "N/A"}</p>
          <p><strong>Manufacturer:</strong> {result.raw_data?.manufacturer ?? "N/A"}</p>
          <p><strong>Description:</strong> {result.raw_data?.description ?? "N/A"}</p>

          {result.alternatives && result.alternatives.length > 0 ? (
            <div className="alternatives">
              <h3>♻️ Suggested Eco-Friendly Alternatives</h3>
              <div className="alternatives-grid">
                {result.alternatives.map((alt, index) => (
                  <div className="alt-item" key={index}>
                    <a href={alt.url} target="_blank" rel="noopener noreferrer">
                      <strong>{alt.title}</strong>
                    </a>
                    <p>Price: ₹{alt.price}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            result.eco_friendly_prediction === "Not Eco-Friendly ❌"
          )}
        </div>
      )}

      {/* Gemini Chat Interface */}
      <div className="chat-box">
        <h2>🗨️ Gemini Assistant</h2>
        <div className="chat-history">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.sender}`}>
              <strong>{msg.sender === "bot" ? "Bot" : "You"}:</strong> {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input-group">
          <input
            type="text"
            className="input"
            placeholder="Describe the product here..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
          />
          <button className="button" onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
