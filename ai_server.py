from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

MODEL_PATH = Path("model/waste_classifier.keras")
CLASS_NAMES_PATH = Path("model/class_names.json")

print("Loading EcoSort AI model...")

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
    class_names = json.load(f)

print("Model loaded successfully")
print(f"Output classes: {len(class_names)}")


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "EcoSort AI server is running",
        "classes": len(class_names)
    })


# --------------------------------------------------
# USER API
# --------------------------------------------------

users = []


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "User")
    email = data.get("email", "")

    user = {
        "id": len(users) + 1,
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat()
    }

    users.append(user)

    return jsonify({
        "success": True,
        "user": user
    }), 201


# --------------------------------------------------
# WASTE IMAGE PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({
            "error": "No image uploaded"
        }), 400

    file = request.files["image"]

    try:
        image = Image.open(file).convert("RGB")
        image = image.resize((160, 160))

        image_array = np.array(
            image,
            dtype=np.float32
        )

        image_array = np.expand_dims(
            image_array,
            axis=0
        )

        predictions = model.predict(
            image_array,
            verbose=0
        )[0]

        index = int(np.argmax(predictions))

        predicted_class = class_names[index]

        confidence = float(
            predictions[index] * 100
        )

        return jsonify({
            "success": True,
            "prediction": predicted_class,
            "confidence": round(confidence, 2)
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# --------------------------------------------------
# SERVER
# --------------------------------------------------

if __name__ == "__main__":

    print("Starting EcoSort AI server...")
    print("Open http://127.0.0.1:5000 in your browser")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )