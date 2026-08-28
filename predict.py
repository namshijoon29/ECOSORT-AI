from pathlib import Path
import json
import numpy as np
import tensorflow as tf

MODEL_PATH = Path("model/waste_classifier.keras")
CLASS_NAMES_PATH = Path("model/class_names.json")
IMAGE_FOLDER = Path("test_images")

IMAGE_SIZE = (160, 160)

# Load model
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

# Load class names
with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
    class_names = json.load(f)

print(f"Model loaded successfully")
print(f"Output classes: {len(class_names)}")

# Find images
extensions = {".jpg", ".jpeg", ".png", ".jfif", ".webp"}

image_files = [
    file for file in IMAGE_FOLDER.iterdir()
    if file.is_file() and file.suffix.lower() in extensions
]

if not image_files:
    print("No supported image found in test_images!")
    print("Supported formats:", ", ".join(sorted(extensions)))
    raise SystemExit(1)

# Predict each image
for image_path in image_files:

    print("\n" + "=" * 50)
    print(f"Image: {image_path.name}")

    image = tf.keras.utils.load_img(
        image_path,
        target_size=IMAGE_SIZE
    )

    image_array = tf.keras.utils.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))
    predicted_class = class_names[predicted_index]
    confidence = float(predictions[0][predicted_index]) * 100

    print(f"Prediction: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")