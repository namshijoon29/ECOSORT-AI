"""Train a waste image classifier with TensorFlow/Keras transfer learning.

Expected input layout:
    dataset_split/
        train/<class_name>/*.png
        validation/<class_name>/*.png
        test/<class_name>/*.png

The original dataset and dataset_split are read only. Generated files are saved
under model/.

Usage:
    python train_model.py
    python train_model.py --epochs 10 --batch-size 32
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

IMAGE_SIZE = (160, 160)
DEFAULT_BATCH_SIZE = 32
DEFAULT_EPOCHS = 10
SEED = 42
AUTOTUNE = tf.data.AUTOTUNE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the EcoSort waste classifier.")
    parser.add_argument("--dataset", type=Path, default=Path("dataset_split"), help="Prepared split folder")
    parser.add_argument("--output", type=Path, default=Path("model"), help="Folder for model artifacts")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS, help="Maximum training epochs")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Images per training batch")
    return parser.parse_args()


def load_split(path: Path, class_names: list[str] | None = None, shuffle: bool = False):
    return tf.keras.utils.image_dataset_from_directory(
        path,
        labels="inferred",
        label_mode="int",
        class_names=class_names,
        image_size=IMAGE_SIZE,
        batch_size=DEFAULT_BATCH_SIZE,
        shuffle=shuffle,
        seed=SEED,
    )


def create_model(number_of_classes: int) -> tf.keras.Model:
    data_augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="image")
    augmented = data_augmentation(inputs)
    scaled = tf.keras.applications.mobilenet_v2.preprocess_input(augmented)
    features = base_model(scaled, training=False)
    features = tf.keras.layers.GlobalAveragePooling2D()(features)
    features = tf.keras.layers.Dropout(0.2)(features)
    outputs = tf.keras.layers.Dense(number_of_classes, activation="softmax", name="class_probabilities")(features)
    model = tf.keras.Model(inputs, outputs, name="ecosort_mobilenetv2")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_training_graphs(history: tf.keras.callbacks.History, output: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib is not installed; training graphs were not created.")
        return

    epochs = range(1, len(history.history["accuracy"]) + 1)
    figure, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(epochs, history.history["accuracy"], label="Training accuracy")
    axes[0].plot(epochs, history.history["val_accuracy"], label="Validation accuracy")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()
    axes[0].grid(alpha=0.2)
    axes[1].plot(epochs, history.history["loss"], label="Training loss")
    axes[1].plot(epochs, history.history["val_loss"], label="Validation loss")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()
    axes[1].grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(output / "training_curves.png", dpi=160)
    plt.close(figure)
    print(f"Training graphs saved to: {output / 'training_curves.png'}")


def save_confusion_matrix(model: tf.keras.Model, test_data, class_names: list[str], output: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
    except ImportError:
        print("scikit-learn or Matplotlib is not installed; confusion matrix was not created.")
        return

    true_labels: list[int] = []
    predicted_labels: list[int] = []
    for images, labels in test_data:
        probabilities = model.predict(images, verbose=0)
        true_labels.extend(labels.numpy().tolist())
        predicted_labels.extend(np.argmax(probabilities, axis=1).tolist())

    matrix = confusion_matrix(true_labels, predicted_labels, labels=list(range(len(class_names))))
    figure_size = max(10, len(class_names) * 0.42)
    figure, axis = plt.subplots(figsize=(figure_size, figure_size))
    ConfusionMatrixDisplay(matrix, display_labels=class_names).plot(
        ax=axis, xticks_rotation=90, cmap="Greens", colorbar=False
    )
    axis.set_title("EcoSort test confusion matrix")
    figure.tight_layout()
    figure.savefig(output / "confusion_matrix.png", dpi=160)
    plt.close(figure)
    print(f"Confusion matrix saved to: {output / 'confusion_matrix.png'}")


def main() -> int:
    args = parse_args()
    dataset_root = args.dataset.expanduser().resolve()
    output = args.output.expanduser().resolve()
    train_path = dataset_root / "train"
    validation_path = dataset_root / "validation"
    test_path = dataset_root / "test"

    missing = [path for path in (train_path, validation_path, test_path) if not path.is_dir()]
    if missing:
        print("Missing prepared dataset folders:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        print("Run prepare_dataset.py first, then run this script again.", file=sys.stderr)
        return 1

    class_names = sorted(path.name for path in train_path.iterdir() if path.is_dir())
    if len(class_names) < 2:
        print("At least two class folders are required in dataset_split/train.", file=sys.stderr)
        return 1
    validation_classes = {path.name for path in validation_path.iterdir() if path.is_dir()}
    test_classes = {path.name for path in test_path.iterdir() if path.is_dir()}
    if set(class_names) != validation_classes or set(class_names) != test_classes:
        print("Train, validation, and test folders must contain the same class names.", file=sys.stderr)
        return 1

    output.mkdir(parents=True, exist_ok=True)
    with (output / "class_names.json").open("w", encoding="utf-8") as file:
        json.dump(class_names, file, ensure_ascii=True, indent=2)

    print("EcoSort model training")
    print("=" * 24)
    print(f"Classes: {len(class_names)}")
    print(f"Image size: {IMAGE_SIZE[0]} x {IMAGE_SIZE[1]}")
    print(f"Batch size: {args.batch_size}")
    print(f"Maximum epochs: {args.epochs}")
    print("Model: MobileNetV2 with ImageNet transfer learning")

    train_data = tf.keras.utils.image_dataset_from_directory(
        train_path, labels="inferred", label_mode="int", class_names=class_names,
        image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=True, seed=SEED,
    ).prefetch(AUTOTUNE)
    validation_data = tf.keras.utils.image_dataset_from_directory(
        validation_path, labels="inferred", label_mode="int", class_names=class_names,
        image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=False,
    ).prefetch(AUTOTUNE)
    test_data = tf.keras.utils.image_dataset_from_directory(
        test_path, labels="inferred", label_mode="int", class_names=class_names,
        image_size=IMAGE_SIZE, batch_size=args.batch_size, shuffle=False,
    ).prefetch(AUTOTUNE)

    model = create_model(len(class_names))
    model.summary()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(output / "best_model.keras", monitor="val_accuracy", save_best_only=True),
    ]
    history = model.fit(train_data, validation_data=validation_data, epochs=args.epochs, callbacks=callbacks)
    test_loss, test_accuracy = model.evaluate(test_data, verbose=1)
    model.save(output / "waste_classifier.keras")
    save_training_graphs(history, output)
    save_confusion_matrix(model, test_data, class_names, output)

    final_training_accuracy = history.history["accuracy"][-1]
    final_validation_accuracy = history.history["val_accuracy"][-1]
    print("\nFinal metrics")
    print("-------------")
    print(f"Training accuracy: {final_training_accuracy:.4f}")
    print(f"Validation accuracy: {final_validation_accuracy:.4f}")
    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Test loss: {test_loss:.4f}")
    print(f"Model saved to: {output / 'waste_classifier.keras'}")
    print(f"Labels saved to: {output / 'class_names.json'}")
    print("Training complete. Flask integration has not been created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
