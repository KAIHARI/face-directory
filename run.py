"""Face Directory build pipeline.

Workflow that lets you prune unwanted faces between detection
and HTML generation, then publishes with one command:

    1. Drop a group photo into input/
    2. python run.py crop      # detect faces, write face_01.jpg .. face_NN.jpg
    3. (Optional) Manually delete any face_*.jpg you don't want in the directory
    4. python run.py build     # regenerate index.html from remaining files
    5. python run.py deploy    # git add + commit + push (or double-click deploy.bat)

Or, if you want every detected face without pruning:

    python run.py all          # crop + build in one shot

Subcommands:
    crop    Detect faces in newest input/ image, write face_*.jpg to root.
            Deletes existing face_*.jpg first for a clean slate.
    build   Run generate.py to embed current face_*.jpg files into index.html.
    all     Equivalent to: crop + build (skips the manual prune step).
    deploy  Stage all changes, commit with a dated message, and push.
            Available as deploy.bat for double-click convenience.
"""
import sys
import subprocess
from pathlib import Path

from crop_faces import crop_faces

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "input"
FACES_DIR = SCRIPT_DIR / "faces"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def find_input_image():
    """Return the most recently modified image in input/, or None."""
    if not INPUT_DIR.exists():
        return None
    candidates = [
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix in IMAGE_EXTENSIONS
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def clean_old_faces():
    """Delete all face_*.jpg files in the faces/ folder. Returns count removed."""
    if not FACES_DIR.exists():
        return 0
    removed = 0
    for p in FACES_DIR.glob("face_*.jpg"):
        p.unlink()
        removed += 1
    return removed


def count_face_files():
    if not FACES_DIR.exists():
        return 0
    return len(list(FACES_DIR.glob("face_*.jpg")))


def run_generate():
    """Invoke generate.py as a subprocess so its stdout is visible."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "generate.py")],
        cwd=str(SCRIPT_DIR),
    )
    return result.returncode == 0


def cmd_crop():
    """Detect faces and write fresh face_*.jpg files into faces/."""
    image_path = find_input_image()
    if image_path is None:
        print("ERROR: no image found in input/")
        print(f"Drop a group photo (jpg/png) into: {INPUT_DIR}")
        return 1

    print(f"Using input image: {image_path.name}")

    removed = clean_old_faces()
    print(f"Removed {removed} old face_*.jpg file(s) from faces/\n")

    FACES_DIR.mkdir(exist_ok=True)

    try:
        count = crop_faces(image_path, FACES_DIR)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    if count == 0:
        print("\nERROR: no faces detected in the image.")
        return 1

    print("\n" + "=" * 60)
    print(f"Crop complete: {count} face(s) saved to faces/face_01.jpg .. face_{count:02d}.jpg")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Open the folder: {FACES_DIR}")
    print("  2. Delete any face_*.jpg files you don't want in the directory")
    print("  3. Run: python run.py build")
    return 0


def cmd_build():
    """Regenerate index.html from existing face_*.jpg files."""
    count = count_face_files()
    if count == 0:
        print("ERROR: no face_*.jpg files found in the project root.")
        print("Run 'python run.py crop' first.")
        return 1

    print(f"Building index.html from {count} face file(s)...\n")
    if not run_generate():
        print("\nERROR: generate.py failed. index.html may be stale.")
        return 1

    print("\n" + "=" * 60)
    print(f"Build complete: index.html embeds {count} face(s)")
    print("=" * 60)
    print("\nNext steps (review first, then deploy):")
    print("  1. Open index.html in a browser to verify the directory")
    print("  2. When ready to publish: python run.py deploy")
    print("     (or double-click deploy.bat)")
    return 0


def cmd_all():
    """Crop + build in one shot, no manual prune step."""
    rc = cmd_crop()
    if rc != 0:
        return rc
    print()  # blank line between phases
    return cmd_build()


def _git(*args, capture=False):
    """Run a git command in the project root. Returns CompletedProcess."""
    return subprocess.run(
        ["git", *args],
        cwd=str(SCRIPT_DIR),
        capture_output=capture,
        text=capture,
    )


def cmd_deploy():
    """Stage, commit, and push to GitHub Pages."""
    from datetime import datetime

    # Verify we're in a git repo
    rc = _git("rev-parse", "--is-inside-work-tree", capture=True).returncode
    if rc != 0:
        print("ERROR: not a git repository")
        return 1

    # Show what's about to be deployed
    status = _git("status", "--short", capture=True)
    if not status.stdout.strip():
        print("Nothing to deploy — working tree is clean.")
        print("If you just made changes, run 'python run.py build' first.")
        return 0

    print("Changes to deploy:")
    print(status.stdout)

    # Stage everything
    print("Staging changes...")
    if _git("add", "-A").returncode != 0:
        print("ERROR: git add failed")
        return 1

    # Commit with date in the message (git records the full timestamp anyway)
    msg = f"Update directory {datetime.now().strftime('%Y-%m-%d')}"
    print(f"Committing: {msg}")
    if _git("commit", "-m", msg).returncode != 0:
        print("ERROR: git commit failed")
        return 1

    # Push
    print("\nPushing to GitHub...")
    if _git("push").returncode != 0:
        print("\nERROR: git push failed")
        print("Check your internet connection or run 'git push' manually.")
        return 1

    print("\n" + "=" * 60)
    print("Deployed! Site will redeploy on GitHub Pages in ~30 seconds.")
    print("URL: https://kaihari.github.io/face-directory/")
    print("=" * 60)
    return 0


COMMANDS = {
    "crop": cmd_crop,
    "build": cmd_build,
    "all": cmd_all,
    "deploy": cmd_deploy,
}


def main():
    print("=" * 60)
    print("Face Directory — build pipeline")
    print("=" * 60 + "\n")

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python run.py <command>")
        print()
        print("Commands:")
        print("  crop    Detect faces, write face_01.jpg .. face_NN.jpg")
        print("  build   Regenerate index.html from current face files")
        print("  all     Run crop + build together (no manual prune)")
        print("  deploy  Stage, commit, and push to GitHub Pages")
        print()
        print("Typical workflow:")
        print("  1. Drop group photo in input/")
        print("  2. python run.py crop")
        print("  3. Delete any unwanted face_*.jpg files")
        print("  4. python run.py build")
        print("  5. python run.py deploy   (or double-click deploy.bat)")
        sys.exit(1)

    sys.exit(COMMANDS[sys.argv[1]]())


if __name__ == "__main__":
    main()
