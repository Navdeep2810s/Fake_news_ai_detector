from utils import extract_pdf_text
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import database
import sqlite3

app = Flask(__name__)
CORS(app)

# Load trained model and vectorizer
model = joblib.load("model/model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")


@app.route("/")
def home():
    return jsonify({
        "message": "Fake News Detection API is Running 🚀"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "Healthy"
    })


@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    text = data["text"]

    text_vector = vectorizer.transform([text])

    prediction = model.predict(text_vector)[0]

    probability = model.predict_proba(text_vector)[0]

    confidence = max(probability) * 100

    result = "Real News" if prediction == 1 else "Fake News"
    conn = sqlite3.connect("database/predictions.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (news, prediction, confidence)
        VALUES (?, ?, ?)
        """,
        (
            text,
            result,
            confidence
        )
    )

    conn.commit()
    conn.close()

    explanation = (
        "The article appears to contain language patterns similar to reliable news sources."
        if prediction == 1
        else "The article contains language patterns commonly found in misleading or fake news."
    )

    return jsonify({
        "prediction": result,
        "confidence": round(confidence, 2),
        "model": "Logistic Regression",
        "explanation": explanation
    })
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename.endswith(".txt"):

        text = file.read().decode("utf-8")

    elif file.filename.endswith(".pdf"):

        text = extract_pdf_text(file)

    else:

        return jsonify({"error": "Only TXT and PDF files are allowed"}), 400

    text_vector = vectorizer.transform([text])

    prediction = model.predict(text_vector)[0]

    probability = model.predict_proba(text_vector)[0]

    confidence = max(probability) * 100

    result = "Real News" if prediction == 1 else "Fake News"
    
    import sqlite3

    conn = sqlite3.connect("database/predictions.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (news,prediction,confidence)

        VALUES(?,?,?)
        """,
    (
        text,
        result,
        confidence
    )
)

    conn.commit()

    conn.close()

    return jsonify({
        "prediction": result,
        "confidence": round(confidence, 2)
    })
@app.route("/dashboard", methods=["GET"])
def dashboard():

    conn = sqlite3.connect("database/predictions.db")
    cursor = conn.cursor()

    # Total predictions
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    # Real News count
    cursor.execute(
        "SELECT COUNT(*) FROM predictions WHERE prediction = ?",
        ("Real News",)
    )
    real_news = cursor.fetchone()[0]

    # Fake News count
    cursor.execute(
        "SELECT COUNT(*) FROM predictions WHERE prediction = ?",
        ("Fake News",)
    )
    fake_news = cursor.fetchone()[0]

    # Average confidence
    cursor.execute("SELECT AVG(confidence) FROM predictions")
    avg_confidence = cursor.fetchone()[0]

    if avg_confidence is None:
        avg_confidence = 0

    # Recent predictions
    cursor.execute("""
        SELECT prediction,
               confidence,
               created_at
        FROM predictions
        ORDER BY created_at DESC
        LIMIT 10
    """)

    recent_predictions = []

    for row in cursor.fetchall():

        recent_predictions.append({
            "prediction": row[0],
            "confidence": round(row[1], 2),
            "date": row[2]
        })

    conn.close()

    return jsonify({
        "total_predictions": total_predictions,
        "real_news": real_news,
        "fake_news": fake_news,
        "average_confidence": round(avg_confidence, 2),
        "recent_predictions": recent_predictions
    })
if __name__ == "__main__":
    app.run(debug=True)