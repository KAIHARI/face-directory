# Face Directory — Advanced Features Design

## Context

A single-page face labeling form with 17 embedded face images, Name/Position inputs, auto-save, copy/email submission. Hosted on GitHub Pages. Goal: impress the person filling it out with a polished, delightful data-entry experience.

## Baseline Fix

Card numbering displays #01 through #17 sequentially, ignoring source file names (which start at face_02.jpg). The `generate.py` script will be updated to use a 1-based display index.

## Feature 1: Smart Autocomplete

Custom dropdown suggestions on Name and Position inputs.

**Name field:**
- Shows suggestions after 1+ characters typed
- Embedded dataset: ~200 common first names, ~150 common last names
- After a space is typed (indicating first name is done), switches to last name suggestions
- Dropdown: absolutely positioned below input, max 5 visible items, scrollable
- Navigation: arrow keys + Enter to select, Escape to dismiss, click/tap to select
- Touch targets: 44px minimum height per suggestion row
- Selecting a suggestion fills the input and advances focus to the next field

**Position field:**
- ~80 common business titles embedded (Director of X, VP of X, Software Engineer, etc.)
- Fuzzy keyword matching: typing "dir" matches all "Director of..." titles, "eng" matches Engineering titles
- Same dropdown UX as Name field

**Implementation:** Vanilla JS. A single reusable `Autocomplete` class that takes an input element and a dataset. Dropdown is a `<div>` with `position: absolute`, styled to match the card aesthetic. Hides on blur (with a small delay to allow click registration).

## Feature 2: Image Lightbox

Click/tap any face image to view it enlarged.

- Dark semi-transparent overlay (`rgba(0,0,0,0.85)`)
- Image centered, scaled to ~80% of viewport (max 500px)
- Fade-in + subtle scale animation (0.25s ease)
- Close on: click overlay, press Escape, tap X button
- Single shared lightbox DOM element, image `src` swapped on open
- No pinch-to-zoom (keeps it simple); image is large enough to identify

## Feature 3: Keyboard Flow

Optimized keyboard navigation for fast data entry.

- Tab order follows DOM (already correct): Name1 → Pos1 → Name2 → Pos2 → ...
- **Enter** in any input moves focus to next input (prevents default form submit)
- **Shift+Enter** moves focus to previous input
- When focus moves to an input in a new card, smooth-scroll that card into view with ~80px top offset (below sticky header)

## Feature 4: Progress Ring

Replace linear progress bar with a circular SVG ring.

- ~40px diameter SVG circle in the header
- Animated `stroke-dashoffset` transition (0.4s cubic-bezier)
- Center text: "5/17" count
- Color: starts as warm accent (`--accent`), transitions to green (`--green`) as progress increases (interpolated via JS or discrete thresholds)
- Replaces `.progress-bar-track` / `.progress-bar-fill` elements

## Feature 5: Encouraging Messages

Toast messages at milestones, shown once per session.

| Milestone | Count | Message |
|-----------|-------|---------|
| First card | 1/17 | "Nice, you're off to a great start!" |
| 25% | 5/17 | "Quarter of the way there" |
| 50% | 9/17 | "Halfway done — keep it up!" |
| 75% | 13/17 | "Almost there, just a few left!" |
| 100% | 17/17 | (confetti instead, no toast) |

- Uses the existing toast element and `showToast()` function
- Track shown milestones in a session variable (not localStorage — repeats each visit are fine)

## Feature 6: Confetti Celebration

Confetti burst when all 17 cards are filled.

- Load `canvas-confetti` from CDN (`https://cdn.jsdelivr.net/npm/canvas-confetti@1/dist/confetti.browser.min.js`, ~6KB gzipped)
- Trigger: two bursts from left and right sides simultaneously
- Duration: ~2 seconds
- Colors: match the page palette (accent, green, warm tones)
- Only fires once per completion event (not on page load if already complete, and not again until a card is un-filled and re-filled)

## Feature 7: Dark Mode

Toggle between light and dark themes.

**Toggle:** Sun/moon icon button in the header, next to the progress ring.

**Dark palette (CSS variables):**
- `--bg`: #1A1918
- `--card`: #2A2826
- `--text`: #E8E4DC
- `--text-muted`: #9A958A
- `--border`: #3D3A36
- `--accent`: #D4774F (slightly lighter for contrast)
- `--accent-light`: #3A2820
- `--green-light`: #1E3328
- `--shadow`: adjusted for dark background

**Behavior:**
- First visit: respect `prefers-color-scheme` media query
- Manual toggle overrides and saves to localStorage
- 0.3s CSS transition on `background-color`, `color`, `border-color`, `box-shadow`
- Toggle icon animates (rotate + swap)

## Architecture

All features are added to the existing `index.html` via the `generate.py` script. The HTML template in `generate.py` grows to include:
- Autocomplete CSS + JS class
- Lightbox CSS + HTML + JS
- Progress ring SVG markup
- Dark mode CSS variables + toggle JS
- canvas-confetti CDN `<script>` tag

No new files beyond `index.html`. The `generate.py` script remains the source of truth.

## Verification

1. Open `index.html` — all 17 images display, numbered #01-#17
2. Type in a Name field — autocomplete dropdown appears with suggestions
3. Click a face image — lightbox opens, Escape closes it
4. Press Enter in a field — focus advances to next field
5. Fill 5 cards — progress ring shows 5/17, "Quarter of the way" toast appears
6. Fill all 17 — confetti fires, progress ring is full green
7. Toggle dark mode — theme switches smoothly, persists on refresh
8. Refresh page — all data restored from localStorage
9. Test on mobile viewport — all features work with touch
