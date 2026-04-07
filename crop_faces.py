"""Face detection and cropping using YuNet.

Reads a group photo, detects faces, and writes individually cropped
face_01.jpg, face_02.jpg, ... to an output directory. Sorted left-to-right
by x-coordinate so the numbering matches the visual order in the photo.

Adapted from the original crop_faces.py in the `team roster tool` project.
The only changes from the original are:
  - IMAGE_PATH and OUTPUT_DIR are function parameters instead of globals
  - Model path resolves relative to this script's own location
  - Callable as a function from run.py (`crop_faces(image_path, output_dir)`)
    and still runnable standalone (`python crop_faces.py photo.jpg [out_dir]`)

Tunable constants kept at module level to match the original script.
"""
import sys
import os
from pathlib import Path

import cv2

# ── Tunables (match the original team roster tool script exactly) ──
PADDING_RATIO = 0.55          # extra context around each detected face
SCORE_THRESHOLD = 0.5         # detector score threshold
NMS_THRESHOLD = 0.3           # non-maximum suppression threshold
CONFIDENCE_CUTOFF = 0.7       # skip detections below this final confidence
JPEG_QUALITY = 95

# Model file sits next to this script
SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_PATH = SCRIPT_DIR / "face_detection_yunet_2023mar.onnx"


def crop_faces(image_path, output_dir):
    """Detect faces in `image_path` and write crops to `output_dir`.

    Returns the number of faces successfully written.
    Raises FileNotFoundError if the image can't be read.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}\n"
            f"Copy face_detection_yunet_2023mar.onnx next to crop_faces.py"
        )

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not load {image_path}")

    h, w, _ = img.shape
    print(f"Image size: {w}x{h}")

    detector = cv2.FaceDetectorYN.create(
        str(MODEL_PATH), "", (w, h),
        score_threshold=SCORE_THRESHOLD,
        nms_threshold=NMS_THRESHOLD,
    )
    _, faces = detector.detect(img)

    if faces is None:
        print("No faces detected.")
        return 0

    print(f"Detected {faces.shape[0]} faces")

    # Sort faces left-to-right by x coordinate — gives stable visual numbering
    faces_sorted = faces[faces[:, 0].argsort()]

    count = 0
    for face in faces_sorted:
        x, y, fw, fh = face[:4].astype(int)
        confidence = face[-1]

        if confidence < CONFIDENCE_CUTOFF:
            print(
                f"  Skipping detection at ({x},{y}) "
                f"confidence={confidence:.2f} (below threshold)"
            )
            continue

        count += 1
        pad_w = int(fw * PADDING_RATIO)
        pad_h = int(fh * PADDING_RATIO)

        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w, x + fw + pad_w)
        y2 = min(h, y + fh + pad_h)

        cropped = img[y1:y2, x1:x2]
        output_path = output_dir / f"face_{count:02d}.jpg"
        cv2.imwrite(str(output_path), cropped, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        print(
            f"  Face {count:02d}: ({x1},{y1})-({x2},{y2}) "
            f"confidence={confidence:.2f} -> {output_path.name}"
        )

    print(f"\nDone! {count} faces saved to {output_dir}/")
    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python crop_faces.py <image_path> [output_dir]")
        print("  output_dir defaults to ./faces/")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(SCRIPT_DIR / "faces")

    count = crop_faces(image_path, output_dir)
    sys.exit(0 if count > 0 else 1)


if __name__ == "__main__":
    main()
