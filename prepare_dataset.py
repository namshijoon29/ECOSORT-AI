"""Create reproducible train/validation/test copies of an image dataset.

The source dataset is never changed: files are validated, hashed, and copied.
The script refuses to use an existing output directory to prevent accidental
overwrites.

Usage:
    py prepare_dataset.py
    py prepare_dataset.py --dataset datasets/images/images
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff",
    ".jfif", ".avif",
}
SPLITS = (("train", 0.70), ("validation", 0.15), ("test", 0.15))
RANDOM_SEED = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare safe, reproducible dataset splits.")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/images/images"), help="Original dataset root")
    parser.add_argument("--output", type=Path, default=Path("dataset_split"), help="New output folder")
    parser.add_argument("--chart", type=Path, default=Path("dataset_split_class_distribution.png"), help="Chart path")
    return parser.parse_args()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_valid_image(path: Path) -> bool:
    if Image is None:
        return True
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def discover_dataset(root: Path) -> tuple[list[str], dict[str, list[Path]], list[Path]]:
    class_dirs = sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name.lower())
    classes = [path.name for path in class_dirs]
    supported: dict[str, list[Path]] = {class_name: [] for class_name in classes}
    unsupported: list[Path] = []
    for class_dir in class_dirs:
        for path in class_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                supported[class_dir.name].append(path)
            else:
                unsupported.append(path)
    return classes, supported, unsupported


def build_duplicate_groups(files: list[Path]) -> list[list[Path]]:
    hashed: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        try:
            hashed[digest_file(path)].append(path)
        except OSError:
            continue
    return [group for group in hashed.values() if len(group) > 1]


def split_paths(paths: list[Path]) -> dict[str, list[Path]]:
    """Use a fixed seed and stable order, with rounded per-class targets."""
    ordered = sorted(paths, key=lambda path: path.as_posix().lower())
    # A local deterministic ranking avoids dependence on Python's hash randomization.
    ranked = sorted(
        ordered,
        key=lambda path: hashlib.sha256(f"{RANDOM_SEED}:{path.as_posix()}".encode("utf-8")).hexdigest(),
    )
    total = len(ranked)
    train_count = round(total * 0.70)
    validation_count = round(total * 0.15)
    return {
        "train": ranked[:train_count],
        "validation": ranked[train_count:train_count + validation_count],
        "test": ranked[train_count + validation_count:],
    }


def safe_output_name(source: Path, class_name: str) -> str:
    # Include nested source folders so repeated names such as default/Image_1.png
    # and real_world/Image_1.png can never overwrite one another.
    parts = list(source.parts)
    class_index = max((index for index, part in enumerate(parts) if part == class_name), default=len(parts) - 1)
    relative_parts = parts[class_index + 1:]
    return "__".join(relative_parts) if relative_parts else source.name


def create_chart(counts: Counter, output: Path) -> str:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return "Matplotlib is not installed; the split was created without a chart."
    labels = list(counts.keys())
    values = list(counts.values())
    figure, axis = plt.subplots(figsize=(11, max(5, len(labels) * 0.32)))
    axis.barh(labels[::-1], values[::-1], color="#6eaa7b")
    axis.set_title("Prepared dataset: images per class")
    axis.set_xlabel("Number of source images")
    axis.grid(axis="x", alpha=0.2)
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return f"Chart saved to: {output}"


def main() -> int:
    args = parse_args()
    source = args.dataset.expanduser().resolve()
    output = args.output.expanduser().resolve()
    chart = args.chart.expanduser().resolve()

    if not source.is_dir():
        print(f"Dataset folder not found: {source}", file=sys.stderr)
        return 1
    if output.exists():
        print(f"Refusing to overwrite existing output folder: {output}", file=sys.stderr)
        print("Choose another --output path or move the previous generated split yourself.", file=sys.stderr)
        return 1
    if source == output or source in output.parents:
        print("Output must be outside the original dataset folder.", file=sys.stderr)
        return 1
    if chart == source or source in chart.parents:
        print("Chart must be outside the original dataset folder.", file=sys.stderr)
        return 1

    classes, paths_by_class, unsupported = discover_dataset(source)
    all_supported = [path for paths in paths_by_class.values() for path in paths]
    invalid = [] if Image is None else [path for path in all_supported if not is_valid_image(path)]
    invalid_set = set(invalid)
    valid_by_class = {name: [path for path in paths if path not in invalid_set] for name, paths in paths_by_class.items()}
    duplicates = build_duplicate_groups([path for paths in valid_by_class.values() for path in paths])

    output.mkdir(parents=True)
    split_counts: dict[str, Counter] = {split: Counter() for split, _ in SPLITS}
    source_counts = Counter({name: len(paths) for name, paths in valid_by_class.items()})
    try:
        for class_name in classes:
            class_split = split_paths(valid_by_class[class_name])
            for split_name, split_paths_for_class in class_split.items():
                destination = output / split_name / class_name
                destination.mkdir(parents=True, exist_ok=True)
                for source_path in split_paths_for_class:
                    shutil.copy2(source_path, destination / safe_output_name(source_path, class_name))
                    split_counts[split_name][class_name] += 1
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise

    print("Prepared Dataset Report")
    print("=" * 24)
    print(f"Source dataset: {source}")
    print(f"Output folder: {output}")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Total source images: {len(all_supported):,}")
    print(f"Valid images copied: {sum(source_counts.values()):,}")
    print(f"Number of classes: {len(classes)}")
    print(f"Unsupported files: {len(unsupported):,}")
    print(f"Corrupted/unreadable images: {len(invalid):,}")
    print(f"Duplicate groups detected: {len(duplicates):,}")
    if Image is None:
        print("Warning: Pillow is not installed, so corrupted-image validation was skipped.")
    if duplicates:
        print("Warning: duplicates were detected. Review them before training to avoid data leakage.")

    print("\nClass and split counts")
    print("----------------------")
    for class_name in classes:
        print(
            f"{class_name}: total={source_counts[class_name]:,}, "
            f"train={split_counts['train'][class_name]:,}, "
            f"validation={split_counts['validation'][class_name]:,}, "
            f"test={split_counts['test'][class_name]:,}"
        )

    print("\nTotals")
    print("------")
    for split_name, _ in SPLITS:
        print(f"{split_name}: {sum(split_counts[split_name].values()):,}")
    print(create_chart(source_counts, chart))
    print("\nModel training has not been started.")
    print("Next step: review the split report and duplicate warnings, then train a transfer-learning classifier.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
