"""Read-only analysis for an image classification dataset.

This script never writes inside the dataset directory. It writes the optional
class-count chart to the current working directory unless --output is used.

Usage:
    py dataset_analysis.py
    py dataset_analysis.py --dataset datasets/images/images
    py dataset_analysis.py --output dataset_class_counts.png
"""

from __future__ import annotations

import argparse
import hashlib
import mimetypes
import sys
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff",
    ".jfif", ".avif",
}
SPLIT_NAMES = {"train", "training", "val", "valid", "validation", "test", "testing"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze an image dataset without changing it.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("datasets/images/images"),
        help="Dataset root folder (default: datasets/images/images)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset_class_counts.png"),
        help="Chart path outside the dataset (default: dataset_class_counts.png)",
    )
    return parser.parse_args()


def image_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]


def infer_classes(root: Path, files: list[Path]) -> tuple[dict[str, list[Path]], dict[str, Counter]]:
    """Infer classes for class-first and split-first layouts."""
    top_level_dirs = [path for path in root.iterdir() if path.is_dir()]
    has_split_dirs = any(path.name.lower() in SPLIT_NAMES for path in root.rglob("*") if path.is_dir())
    classes: dict[str, list[Path]] = defaultdict(list)
    split_counts: dict[str, Counter] = defaultdict(Counter)

    if has_split_dirs:
        for file_path in files:
            relative_parts = file_path.relative_to(root).parts
            split_index = next(
                (index for index, part in enumerate(relative_parts[:-1]) if part.lower() in SPLIT_NAMES),
                None,
            )
            if split_index is not None:
                split_name = relative_parts[split_index].lower()
                class_index = split_index + 1
                class_name = relative_parts[class_index] if class_index < len(relative_parts) - 1 else "unlabelled"
                classes[class_name].append(file_path)
                split_counts[class_name][split_name] += 1
                continue

            # Some datasets mix split and non-split folders. Keep those files visible.
            class_name = relative_parts[0] if relative_parts else "unlabelled"
            classes[class_name].append(file_path)
            split_counts[class_name]["unsplit"] += 1
    else:
        class_names = {path.name for path in top_level_dirs}
        for file_path in files:
            relative_parts = file_path.relative_to(root).parts
            class_name = relative_parts[0] if relative_parts and relative_parts[0] in class_names else "unlabelled"
            classes[class_name].append(file_path)
            split_counts[class_name]["unsplit"] += 1

    return dict(classes), dict(split_counts)


def validate_images(files: list[Path]) -> tuple[list[Path], str]:
    try:
        from PIL import Image
    except ImportError:
        return [], "Pillow is not installed; file validity was checked by extension only."

    invalid: list[Path] = []
    for file_path in files:
        try:
            with Image.open(file_path) as image:
                image.verify()
        except Exception:
            invalid.append(file_path)
    return invalid, "Pillow validation completed."


def find_duplicates(files: list[Path]) -> list[list[Path]]:
    hashes: dict[str, list[Path]] = defaultdict(list)
    for file_path in files:
        digest = hashlib.sha256()
        try:
            with file_path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            hashes[digest.hexdigest()].append(file_path)
        except OSError:
            continue
    return [paths for paths in hashes.values() if len(paths) > 1]


def make_chart(counts: Counter, output: Path) -> str:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return "Matplotlib is not installed; no chart was created."

    labels = list(counts.keys())
    values = list(counts.values())
    figure_height = max(5, len(labels) * 0.32)
    figure, axis = plt.subplots(figsize=(11, figure_height))
    axis.barh(labels[::-1], values[::-1], color="#6eaa7b")
    axis.set_title("Images per waste class")
    axis.set_xlabel("Number of images")
    axis.grid(axis="x", alpha=0.2)
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return f"Chart saved to: {output}"


def main() -> int:
    args = parse_args()
    root = args.dataset.expanduser().resolve()
    if not root.is_dir():
        print(f"Dataset folder not found: {root}", file=sys.stderr)
        return 1

    files = image_files(root)
    classes, split_counts = infer_classes(root, files)
    invalid_files, validation_note = validate_images(files)
    duplicate_groups = find_duplicates(files)
    extension_counts = Counter(file_path.suffix.lower() for file_path in files)
    class_counts = Counter({name: len(paths) for name, paths in classes.items()})
    split_names = sorted({split for counts in split_counts.values() for split in counts if split != "unsplit"})
    has_splits = bool(split_names)

    print("Dataset Analysis Report")
    print("=" * 24)
    print(f"Dataset: {root}")
    print(f"Total images: {len(files):,}")
    print(f"Number of classes: {len([name for name in classes if name != 'unlabelled'])}")
    print(f"Already split into train/validation/test folders: {'Yes' if has_splits else 'No'}")
    if has_splits:
        print(f"Detected split folders: {', '.join(split_names)}")
    else:
        print("Split note: classes contain nested folders, but no train/validation/test split was detected.")

    print("\nClass counts")
    print("------------")
    for class_name, count in sorted(class_counts.items(), key=lambda item: (-item[1], item[0].lower())):
        if class_name == "unlabelled":
            continue
        percentage = (count / len(files) * 100) if files else 0
        split_text = ", ".join(f"{name}: {value}" for name, value in sorted(split_counts[class_name].items()))
        print(f"Class: {class_name}")
        print(f"Number of images: {count:,}")
        print(f"Percentage: {percentage:.2f}%")
        print(f"Folders/splits: {split_text}")

    print("\nImage formats")
    print("--------------")
    for extension, count in sorted(extension_counts.items()):
        print(f"{extension}: {count:,}")

    print("\nQuality checks")
    print("--------------")
    print(f"Invalid or unreadable image files: {len(invalid_files):,}")
    print(f"Duplicate groups (same file content): {len(duplicate_groups):,}")
    print(validation_note)
    if invalid_files:
        print("First invalid files:")
        for file_path in invalid_files[:10]:
            print(f"  - {file_path.relative_to(root)}")
    if duplicate_groups:
        print("First duplicate groups:")
        for group in duplicate_groups[:5]:
            print("  - " + " | ".join(str(path.relative_to(root)) for path in group))

    labelled_classes = [name for name in classes if name != "unlabelled"]
    suitable = bool(files and len(labelled_classes) >= 2 and not invalid_files)
    print("\nSuitability")
    print("-----------")
    print("Suitable for image classification: " + ("Yes, with a train/validation/test split added before training." if suitable else "Needs cleanup before training."))
    if "unlabelled" in classes:
        print(f"Warning: {len(classes['unlabelled']):,} images could not be assigned to a class folder.")
    if duplicate_groups:
        print("Note: review duplicates before splitting so identical images do not leak across datasets.")

    output = args.output.expanduser().resolve()
    if output.parent == root or root in output.parents:
        print("Chart skipped: choose an output path outside the dataset folder.", file=sys.stderr)
    else:
        print(make_chart(class_counts, output))

    print("\nRecommended next step")
    print("---------------------")
    print("Create fixed train/validation/test splits, check class balance and duplicates, then train a transfer-learning image classifier. Do not train until the split is created and reviewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
