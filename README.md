# Face Directory

A self-contained pipeline that turns a group photo into a polished, mobile-friendly **Name + Position** labeling form, hosted on GitHub Pages.

**Live site:** https://kaihari.github.io/face-directory/

---

## Quick start (the 5-step workflow)

You just want to publish a new staff directory. Do this:

1. **Drop a group photo** into `input/` (jpg or png)
2. **`python run.py crop`** — detects faces, writes `faces/face_01.jpg` ... `faces/face_NN.jpg`
3. **Open `faces/`** and manually delete any face files you don't want (background people, misdetections, etc.)
4. **`python run.py build`** — regenerates `index.html` with the remaining faces
5. **Double-click `deploy.bat`** — commits and pushes to GitHub Pages (or run `python run.py deploy`)

The site redeploys automatically in ~30 seconds. Share the live URL with whoever is filling it out.

> If you want to skip the prune step (use every detected face), substitute steps 2-4 with `python run.py all`.

---

## What each file does

| File | Purpose |
|---|---|
| `run.py` | The orchestrator. Single entry point for all subcommands. |
| `crop_faces.py` | Face detection (YuNet via OpenCV). Reads an image, writes cropped faces. |
| `generate.py` | Reads `faces/face_*.jpg`, embeds them as base64 into a self-contained `index.html`. |
| `index.html` | The deployed site. **Generated** — never hand-edit; re-run `build` instead. |
| `deploy.bat` | Double-clickable shim that runs `python run.py deploy`. |
| `face_detection_yunet_2023mar.onnx` | YuNet model file (~228 KB). Required by `crop_faces.py`. |
| `input/` | Where you drop the next group photo. Photos here are gitignored. |
| `faces/` | Where cropped face files live. Tracked in git. |
| `.gitignore` | Excludes raw input photos, `.claude/`, Python cache. |

---

## Subcommand reference

```
python run.py crop      # detect faces in newest input/ image -> faces/face_NN.jpg
python run.py build     # regenerate index.html from current faces/
python run.py all       # crop + build (no manual prune step)
python run.py deploy    # git add + commit + push (or double-click deploy.bat)
```

`deploy` is safe to run repeatedly:
- If there are no changes, it prints "Nothing to deploy" and exits cleanly
- It auto-generates a commit message with today's date
- It tells you the live URL when done

---

## Features the deployed site supports

The form has more than just labeling. Things to know:

- **Autocomplete** for first names, last names, and ~500 hospital position titles
- **Auto-saves** to localStorage as you type (refresh-safe)
- **Click any face** to zoom in (lightbox with bicubic upscaling)
- **Dark mode toggle** in the header (auto-detects OS preference on first visit)
- **Confetti** when all faces are labeled
- **Copy / Email Results** buttons at the bottom
- **Admin mode**: triple-click the title and enter password `ahmchealth` to:
  - **Generate Photobook** — produces a 2400×NNNN PNG staff directory at retina resolution, downloadable
  - **Paste & Load Data** — paste a previous export to repopulate the form

---

## Tuning the face detector

Constants live at the top of `crop_faces.py`. You almost never need to change these, but they exist if a particular photo gives bad results:

| Constant | Default | What it controls |
|---|---|---|
| `PADDING_RATIO` | `0.55` | Extra context around each detected face. Higher = more shoulders, lower = tighter crop. |
| `SCORE_THRESHOLD` | `0.5` | YuNet's internal confidence threshold during detection. |
| `NMS_THRESHOLD` | `0.3` | Non-max suppression — prevents the same face being detected twice. |
| `CONFIDENCE_CUTOFF` | `0.7` | After detection, drop faces below this final confidence. Lower if real faces are being skipped, raise if junk is getting through. |
| `JPEG_QUALITY` | `95` | Output JPEG quality. 95 is near-lossless. |

Faces are sorted **left-to-right** by x-coordinate, so `face_01.jpg` is the leftmost person in the photo.

---

## Troubleshooting

**"No image found in input/"** — Drop a jpg or png into `input/`. Anything else (heic, webp, etc.) won't be picked up.

**"No faces detected"** — Lower `CONFIDENCE_CUTOFF` (try 0.5) or `SCORE_THRESHOLD` (try 0.3). Or check that the photo isn't sideways — YuNet doesn't auto-rotate based on EXIF.

**Face count is wrong** — Run `python run.py crop`, manually delete unwanted files in `faces/`, then `python run.py build`. Don't try to renumber the files — `generate.py` always renumbers display labels (#01..#NN) based on file order.

**`deploy.bat` window closes immediately** — It shouldn't. If it does, open a terminal, run `python run.py deploy` directly, and read the error.

**`generatePhotobook is not defined` or similar console error** — `index.html` is stale. Run `python run.py build` to regenerate.

**Browser auto dark-mode breaks form inputs** — Already fixed. If it ever recurs, check that `:root` and `[data-theme="dark"]` both have `color-scheme` declared.

---

## Git workflow notes

- The `input/` folder has a `.gitkeep` placeholder; the photos inside are gitignored (they're often large and may contain PII).
- The `faces/` folder IS tracked in git — every cropped face is committed, so the deployed `index.html` and the source images stay in sync.
- `deploy.bat` runs `git add -A` then `git commit` then `git push`. It does NOT run `git rm` for deleted face files — but `git add -A` handles deletions automatically.
- The `.gitignore` excludes `.claude/` (local Claude Code session config), `__pycache__/`, and OS junk like `Thumbs.db`.

---

## Re-running on the same photo

The crop is deterministic — running `python run.py crop` on the same input image produces byte-identical face files every time. So if you ever want to reproduce a past directory exactly, just put the same photo back in `input/` and run it.
