"""Generate index.html with embedded face images for labeling."""
import base64
import glob
import os

TEMPLATE_TOP = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Face Directory</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300;1,9..40,400&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

  :root {
    --bg: #F4F1EB;
    --card: #FFFFFF;
    --accent: #B85636;
    --accent-light: #F0DDD4;
    --accent-hover: #9A4529;
    --green: #3A7D5C;
    --green-light: #D4EDE0;
    --text: #1A1A1A;
    --text-muted: #7A7567;
    --border: #DDD8CE;
    --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06);
    --shadow-hover: 0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.1);
    --radius: 12px;
    --font-display: 'Instrument Serif', Georgia, serif;
    --font-body: 'DM Sans', system-ui, sans-serif;
  }

  html { scroll-behavior: smooth }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* ── Header ── */
  .header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(244,241,235,0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
  }

  .header-inner {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
  }

  .header h1 {
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 400;
    letter-spacing: -0.01em;
    color: var(--text);
  }

  .progress-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.85rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  .progress-bar-track {
    width: 120px;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--green);
    border-radius: 3px;
    transition: width 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    width: 0%;
  }

  /* ── Instruction Banner ── */
  .banner {
    max-width: 960px;
    margin: 24px auto 0;
    padding: 0 24px;
  }

  .banner-inner {
    background: var(--accent-light);
    border: 1px solid #E3C8BA;
    border-radius: var(--radius);
    padding: 14px 20px;
    font-size: 0.9rem;
    color: #6B3A24;
    line-height: 1.5;
  }

  /* ── Grid ── */
  .grid {
    max-width: 960px;
    margin: 24px auto 140px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
  }

  @media (min-width: 540px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
  }

  @media (min-width: 820px) {
    .grid { grid-template-columns: repeat(3, 1fr); }
  }

  /* ── Card ── */
  .card {
    background: var(--card);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    display: flex;
    flex-direction: column;
    border: 1px solid transparent;
  }

  .card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
  }

  .card.filled {
    border-color: var(--green);
    background: linear-gradient(to bottom, var(--green-light) 0%, var(--card) 40%);
  }

  .card-number {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(0,0,0,0.55);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 6px;
    letter-spacing: 0.04em;
  }

  .card-check {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 24px;
    height: 24px;
    background: var(--green);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transform: scale(0.5);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .card.filled .card-check {
    opacity: 1;
    transform: scale(1);
  }

  .card-check svg { width: 14px; height: 14px; }

  .card-img-wrap {
    position: relative;
    aspect-ratio: 1;
    background: #E8E4DC;
    overflow: hidden;
  }

  .card-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .card-fields {
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .field label {
    display: block;
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 5px;
  }

  .field input {
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text);
    background: #FAFAF8;
    transition: border-color 0.2s, box-shadow 0.2s;
    outline: none;
  }

  .field input::placeholder {
    color: #B5AFA3;
  }

  .field input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(184, 86, 54, 0.12);
    background: #fff;
  }

  /* ── Bottom Action Bar ── */
  .action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    padding: 16px 24px;
  }

  .action-bar-inner {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    border-radius: 10px;
    font-family: var(--font-body);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .btn svg { width: 18px; height: 18px; flex-shrink: 0; }

  .btn-primary {
    background: var(--accent);
    color: #fff;
  }
  .btn-primary:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(184, 86, 54, 0.3);
  }

  .btn-secondary {
    background: var(--card);
    color: var(--text);
    border: 1.5px solid var(--border);
  }
  .btn-secondary:hover {
    border-color: #BBB5A8;
    background: #F9F7F3;
    transform: translateY(-1px);
  }

  /* ── Toast ── */
  .toast {
    position: fixed;
    bottom: 90px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: #1A1A1A;
    color: #fff;
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 500;
    z-index: 200;
    opacity: 0;
    transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    pointer-events: none;
    white-space: nowrap;
  }

  .toast.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }

  /* ── Animations ── */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .card {
    animation: fadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .card:nth-child(1) { animation-delay: 0.03s }
  .card:nth-child(2) { animation-delay: 0.06s }
  .card:nth-child(3) { animation-delay: 0.09s }
  .card:nth-child(4) { animation-delay: 0.12s }
  .card:nth-child(5) { animation-delay: 0.15s }
  .card:nth-child(6) { animation-delay: 0.18s }
  .card:nth-child(7) { animation-delay: 0.21s }
  .card:nth-child(8) { animation-delay: 0.24s }
  .card:nth-child(9) { animation-delay: 0.27s }
  .card:nth-child(10) { animation-delay: 0.30s }
  .card:nth-child(11) { animation-delay: 0.33s }
  .card:nth-child(12) { animation-delay: 0.36s }
  .card:nth-child(13) { animation-delay: 0.39s }
  .card:nth-child(14) { animation-delay: 0.42s }
  .card:nth-child(15) { animation-delay: 0.45s }
  .card:nth-child(16) { animation-delay: 0.48s }
  .card:nth-child(17) { animation-delay: 0.51s }
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <h1>Face Directory</h1>
    <div class="progress-badge">
      <span id="progress-text">0 / TOTAL_COUNT filled</span>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" id="progress-fill"></div>
      </div>
    </div>
  </div>
</div>

<div class="banner">
  <div class="banner-inner">
    Please enter the <strong>Name</strong> and <strong>Position</strong> for each person below. Your progress is saved automatically. When finished, use the buttons at the bottom to send your entries.
  </div>
</div>

<div class="grid" id="grid">
'''

CARD_TEMPLATE = '''  <div class="card" id="card-{idx}" data-idx="{idx}">
    <div class="card-img-wrap">
      <span class="card-number">#{num}</span>
      <div class="card-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <img src="data:image/jpeg;base64,{b64}" alt="Person #{num}" loading="lazy">
    </div>
    <div class="card-fields">
      <div class="field">
        <label for="name-{idx}">Name</label>
        <input type="text" id="name-{idx}" placeholder="Full name" autocomplete="off" data-idx="{idx}" data-field="name">
      </div>
      <div class="field">
        <label for="pos-{idx}">Position</label>
        <input type="text" id="pos-{idx}" placeholder="Title / role" autocomplete="off" data-idx="{idx}" data-field="position">
      </div>
    </div>
  </div>
'''

TEMPLATE_BOTTOM = r'''</div>

<div class="action-bar">
  <div class="action-bar-inner">
    <button class="btn btn-secondary" onclick="copyResults()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      Copy Results
    </button>
    <a class="btn btn-primary" id="email-btn" href="#">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      Email Results
    </a>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
(function() {
  const TOTAL = TOTAL_COUNT;
  const STORAGE_KEY = 'face-directory-data';
  const EMAIL = 'kaihuang.business@gmail.com';

  // ── Load saved data ──
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch(e) {}

  // ── Populate inputs from saved data ──
  document.querySelectorAll('.card-fields input').forEach(input => {
    const idx = input.dataset.idx;
    const field = input.dataset.field;
    if (saved[idx] && saved[idx][field]) {
      input.value = saved[idx][field];
    }
  });

  // ── Update card filled states & progress ──
  function updateState() {
    let filledCount = 0;
    for (let i = 0; i < TOTAL; i++) {
      const card = document.getElementById('card-' + i);
      const name = (saved[i] && saved[i].name) || '';
      const pos = (saved[i] && saved[i].position) || '';
      const isFilled = name.trim() !== '' && pos.trim() !== '';
      card.classList.toggle('filled', isFilled);
      if (isFilled) filledCount++;
    }
    document.getElementById('progress-text').textContent = filledCount + ' / ' + TOTAL + ' filled';
    document.getElementById('progress-fill').style.width = (filledCount / TOTAL * 100) + '%';
    updateEmailHref();
  }

  // ── Auto-save on input ──
  document.querySelectorAll('.card-fields input').forEach(input => {
    input.addEventListener('input', function() {
      const idx = this.dataset.idx;
      const field = this.dataset.field;
      if (!saved[idx]) saved[idx] = {};
      saved[idx][field] = this.value;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
      updateState();
    });
  });

  // ── Build formatted results text ──
  function buildResults() {
    let lines = ['Face Directory Results', '='.repeat(30), ''];
    for (let i = 0; i < TOTAL; i++) {
      const num = FACE_NUMBERS[i];
      const name = (saved[i] && saved[i].name && saved[i].name.trim()) || '(not filled)';
      const pos = (saved[i] && saved[i].position && saved[i].position.trim()) || '(not filled)';
      lines.push('#' + num + '  Name: ' + name + '  |  Position: ' + pos);
    }
    lines.push('', '='.repeat(30));
    return lines.join('\n');
  }

  // ── Copy to clipboard ──
  window.copyResults = function() {
    const text = buildResults();
    navigator.clipboard.writeText(text).then(() => {
      showToast('Copied to clipboard!');
    }).catch(() => {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast('Copied to clipboard!');
    });
  };

  // ── Email results ──
  function updateEmailHref() {
    const body = encodeURIComponent(buildResults());
    const subject = encodeURIComponent('Face Directory - Completed Labels');
    document.getElementById('email-btn').href = 'mailto:' + EMAIL + '?subject=' + subject + '&body=' + body;
  }

  // ── Toast notification ──
  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2200);
  }

  updateState();
})();
</script>
</body>
</html>
'''

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images = sorted(glob.glob(os.path.join(script_dir, 'face_*.jpg')))

    if not images:
        print("No face_*.jpg files found!")
        return

    total = len(images)
    face_numbers = []
    cards_html = []

    for idx, img_path in enumerate(images):
        filename = os.path.basename(img_path)
        num = filename.replace('face_', '').replace('.jpg', '')
        face_numbers.append(num)

        with open(img_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')

        cards_html.append(CARD_TEMPLATE.format(idx=idx, num=num, b64=b64))

    html = TEMPLATE_TOP.replace('TOTAL_COUNT', str(total))
    html += ''.join(cards_html)

    bottom = TEMPLATE_BOTTOM.replace('TOTAL_COUNT', str(total))
    bottom = bottom.replace('FACE_NUMBERS', str(face_numbers))
    html += bottom

    out_path = os.path.join(script_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Generated index.html ({size_kb:.0f} KB) with {total} face images")


if __name__ == '__main__':
    main()
