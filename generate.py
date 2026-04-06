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
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js" defer></script>
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
    --border-banner: #E3C8BA;
    --banner-text: #6B3A24;
    --input-bg: #FAFAF8;
    --input-focus-bg: #FFFFFF;
    --placeholder: #B5AFA3;
    --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06);
    --shadow-hover: 0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.1);
    --header-bg: rgba(244,241,235,0.85);
    --action-bar-bg: rgba(255,255,255,0.92);
    --img-placeholder: #E8E4DC;
    --overlay-bg: rgba(0,0,0,0.85);
    --radius: 12px;
    --font-display: 'Instrument Serif', Georgia, serif;
    --font-body: 'DM Sans', system-ui, sans-serif;
  }

  [data-theme="dark"] {
    --bg: #1A1918;
    --card: #2A2826;
    --accent: #D4774F;
    --accent-light: #3A2820;
    --accent-hover: #E8956E;
    --green: #5AAF80;
    --green-light: #1E3328;
    --text: #E8E4DC;
    --text-muted: #9A958A;
    --border: #3D3A36;
    --border-banner: #5A3A28;
    --banner-text: #D4A080;
    --input-bg: #232120;
    --input-focus-bg: #2E2C2A;
    --placeholder: #6A6560;
    --shadow: 0 1px 3px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.3);
    --shadow-hover: 0 2px 8px rgba(0,0,0,0.3), 0 8px 24px rgba(0,0,0,0.4);
    --header-bg: rgba(26,25,24,0.9);
    --action-bar-bg: rgba(42,40,38,0.92);
    --img-placeholder: #3A3836;
    --overlay-bg: rgba(0,0,0,0.92);
  }

  html { scroll-behavior: smooth }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.3s, color 0.3s;
  }

  /* ── Header ── */
  .header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--header-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    transition: background-color 0.3s, border-color 0.3s;
  }

  .header-inner {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }

  .header h1 {
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 400;
    letter-spacing: -0.01em;
    color: var(--text);
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  /* ── Progress Ring ── */
  .progress-ring-wrap {
    position: relative;
    width: 46px;
    height: 46px;
  }

  .progress-ring-svg {
    transform: rotate(-90deg);
    width: 46px;
    height: 46px;
  }

  .progress-ring-bg {
    fill: none;
    stroke: var(--border);
    stroke-width: 4;
    transition: stroke 0.3s;
  }

  .progress-ring-fill {
    fill: none;
    stroke: var(--accent);
    stroke-width: 4;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.6s cubic-bezier(0.22, 1, 0.36, 1), stroke 0.4s;
  }

  .progress-ring-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.62rem;
    font-weight: 600;
    color: var(--text-muted);
    pointer-events: none;
    white-space: nowrap;
  }

  /* ── Dark Mode Toggle ── */
  .theme-toggle {
    background: none;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    width: 36px;
    height: 36px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    transition: all 0.3s;
  }
  .theme-toggle:hover {
    border-color: var(--accent);
    color: var(--accent);
  }
  .theme-toggle svg { width: 18px; height: 18px; transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
  .theme-toggle:active svg { transform: rotate(30deg) scale(0.85); }
  .icon-sun, .icon-moon { display: none; }
  :root .icon-sun { display: block; }
  :root .icon-moon { display: none; }
  [data-theme="dark"] .icon-sun { display: none; }
  [data-theme="dark"] .icon-moon { display: block; }

  /* ── Instruction Banner ── */
  .banner {
    max-width: 960px;
    margin: 24px auto 0;
    padding: 0 24px;
  }

  .banner-inner {
    background: var(--accent-light);
    border: 1px solid var(--border-banner);
    border-radius: var(--radius);
    padding: 14px 20px;
    font-size: 0.9rem;
    color: var(--banner-text);
    line-height: 1.5;
    transition: background-color 0.3s, border-color 0.3s, color 0.3s;
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
    transition: box-shadow 0.25s ease, transform 0.25s ease, background-color 0.3s, border-color 0.3s;
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
    background: var(--img-placeholder);
    overflow: hidden;
    cursor: zoom-in;
    transition: background-color 0.3s;
  }

  .card-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease;
  }

  .card-img-wrap:hover img {
    transform: scale(1.04);
  }

  .card-fields {
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .field {
    position: relative;
  }

  .field label {
    display: block;
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 5px;
    transition: color 0.3s;
  }

  .field input {
    width: 100%;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text);
    background: var(--input-bg);
    transition: border-color 0.2s, box-shadow 0.2s, background-color 0.3s, color 0.3s;
    outline: none;
  }

  .field input::placeholder {
    color: var(--placeholder);
  }

  .field input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(184, 86, 54, 0.12);
    background: var(--input-focus-bg);
  }

  [data-theme="dark"] .field input:focus {
    box-shadow: 0 0 0 3px rgba(212, 119, 79, 0.2);
  }

  /* ── Autocomplete Dropdown ── */
  .ac-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 50;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 8px;
    margin-top: 4px;
    box-shadow: var(--shadow-hover);
    max-height: 220px;
    overflow-y: auto;
    display: none;
    transition: background-color 0.3s, border-color 0.3s;
  }

  .ac-dropdown.open { display: block; }

  .ac-item {
    padding: 10px 12px;
    font-size: 0.9rem;
    color: var(--text);
    cursor: pointer;
    transition: background-color 0.1s;
  }

  .ac-item:hover, .ac-item.active {
    background: var(--accent-light);
    color: var(--accent);
  }

  .ac-item + .ac-item {
    border-top: 1px solid var(--border);
  }

  /* ── Lightbox ── */
  .lightbox {
    position: fixed;
    inset: 0;
    z-index: 300;
    background: var(--overlay-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
  }

  .lightbox.open {
    opacity: 1;
    pointer-events: auto;
  }

  .lightbox img {
    max-width: min(85vw, 500px);
    max-height: 80vh;
    border-radius: 16px;
    box-shadow: 0 16px 64px rgba(0,0,0,0.5);
    transform: scale(0.9);
    transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .lightbox.open img {
    transform: scale(1);
  }

  .lightbox-close {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(255,255,255,0.15);
    border: none;
    color: #fff;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }

  .lightbox-close:hover {
    background: rgba(255,255,255,0.3);
  }

  .lightbox-label {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255,255,255,0.7);
    font-size: 0.85rem;
    font-weight: 500;
    background: rgba(0,0,0,0.4);
    padding: 6px 16px;
    border-radius: 8px;
  }

  /* ── Bottom Action Bar ── */
  .action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: var(--action-bar-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    padding: 16px 24px;
    transition: background-color 0.3s, border-color 0.3s;
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
    border-color: var(--text-muted);
    transform: translateY(-1px);
  }

  /* ── Toast ── */
  .toast {
    position: fixed;
    bottom: 90px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: var(--text);
    color: var(--bg);
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
    <div class="header-controls">
      <div class="progress-ring-wrap">
        <svg class="progress-ring-svg" viewBox="0 0 46 46">
          <circle class="progress-ring-bg" cx="23" cy="23" r="19"/>
          <circle class="progress-ring-fill" id="progress-ring" cx="23" cy="23" r="19"
            stroke-dasharray="119.38"
            stroke-dashoffset="119.38"/>
        </svg>
        <span class="progress-ring-text" id="progress-text">0/TOTAL_COUNT</span>
      </div>
      <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode">
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </div>
</div>

<div class="banner">
  <div class="banner-inner">
    Please enter the <strong>Name</strong> and <strong>Position</strong> for each person below. Your progress is saved automatically. Click any photo to zoom in. When finished, use the buttons at the bottom to send your entries.
  </div>
</div>

<div class="grid" id="grid">
'''

CARD_TEMPLATE = '''  <div class="card" id="card-{idx}" data-idx="{idx}">
    <div class="card-img-wrap" data-img-idx="{idx}">
      <span class="card-number">#{display_num}</span>
      <div class="card-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <img src="data:image/jpeg;base64,{b64}" alt="Person #{display_num}" loading="lazy">
    </div>
    <div class="card-fields">
      <div class="field">
        <label for="name-{idx}">Name</label>
        <input type="text" id="name-{idx}" placeholder="Full name" autocomplete="off" data-idx="{idx}" data-field="name" data-ac="name">
      </div>
      <div class="field">
        <label for="pos-{idx}">Position</label>
        <input type="text" id="pos-{idx}" placeholder="Title / role" autocomplete="off" data-idx="{idx}" data-field="position" data-ac="position">
      </div>
    </div>
  </div>
'''

TEMPLATE_BOTTOM = r'''</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox">
  <button class="lightbox-close" id="lightbox-close">&times;</button>
  <img id="lightbox-img" src="" alt="Zoomed face">
  <div class="lightbox-label" id="lightbox-label"></div>
</div>

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
  const RING_CIRCUMFERENCE = 2 * Math.PI * 19; // r=19

  // ── Autocomplete Data ──
  const FIRST_NAMES = [
    'Aaron','Abel','Abigail','Adam','Adrian','Aiden','Alejandro','Alex','Alexander','Alexis',
    'Alice','Alison','Amanda','Amber','Amelia','Amy','Andrea','Andrew','Angela','Anna','Anne',
    'Anthony','Antonio','Aria','Ariana','Ashley','Austin','Ava','Barbara','Benjamin','Beth',
    'Brandon','Brian','Brianna','Brittany','Brooke','Bruce','Bryan','Caleb','Cameron','Carlos',
    'Caroline','Catherine','Charles','Charlotte','Chloe','Christian','Christina','Christopher',
    'Claire','Cody','Connor','Daniel','David','Derek','Diana','Diego','Dominic','Donald',
    'Dylan','Edward','Elena','Eli','Elijah','Elizabeth','Ella','Emily','Emma','Eric','Ethan',
    'Eva','Evan','Evelyn','Faith','Fernando','Gabriel','Gavin','George','Grace','Gregory',
    'Hailey','Hannah','Harper','Harry','Heather','Henry','Hunter','Isaac','Isabella','Isaiah',
    'Jack','Jackson','Jacob','James','Jasmine','Jason','Jayden','Jeffrey','Jennifer','Jessica',
    'John','Jonathan','Jordan','Jose','Joseph','Joshua','Julia','Julian','Justin','Katherine',
    'Katie','Kayla','Kenneth','Kevin','Kimberly','Kyle','Lauren','Leah','Leo','Liam','Lily',
    'Linda','Logan','Lucas','Lucy','Luis','Luke','Madeline','Madison','Marco','Margaret',
    'Maria','Mark','Martin','Mary','Mason','Matthew','Maya','Megan','Melissa','Mia','Michael',
    'Michelle','Miguel','Mila','Nathan','Nicholas','Nicole','Noah','Nora','Oliver','Olivia',
    'Owen','Paige','Patricia','Patrick','Paul','Peter','Rachel','Rebecca','Richard','Riley',
    'Robert','Ryan','Samantha','Samuel','Sandra','Sarah','Savannah','Scott','Sean','Sebastian',
    'Sophia','Stephanie','Stephen','Steven','Sydney','Taylor','Thomas','Timothy','Tyler',
    'Victoria','Vincent','William','Wyatt','Xavier','Zachary','Zoe'
  ];

  const LAST_NAMES = [
    'Adams','Allen','Anderson','Bailey','Baker','Barnes','Bell','Bennett','Brooks','Brown',
    'Bryant','Butler','Campbell','Carter','Chen','Clark','Coleman','Collins','Cook','Cooper',
    'Cox','Cruz','Davis','Diaz','Edwards','Ellis','Evans','Fisher','Flores','Ford','Foster',
    'Garcia','Gomez','Gonzalez','Gray','Green','Griffin','Gutierrez','Hall','Hamilton',
    'Harris','Harrison','Hayes','Henderson','Hernandez','Hill','Howard','Hughes','Hunt',
    'Jackson','James','Jenkins','Johnson','Jones','Jordan','Kelly','Kennedy','Kim','King',
    'Lee','Lewis','Li','Lin','Liu','Long','Lopez','Martin','Martinez','Miller','Mitchell',
    'Moore','Morales','Morgan','Morris','Murphy','Myers','Nelson','Nguyen','Ortiz','Owens',
    'Parker','Patel','Patterson','Perez','Perry','Peterson','Phillips','Powell','Price',
    'Ramirez','Reed','Reyes','Reynolds','Richardson','Rivera','Roberts','Robinson','Rodriguez',
    'Rogers','Ross','Russell','Sanchez','Sanders','Scott','Shaw','Simmons','Singh','Smith',
    'Stewart','Sullivan','Taylor','Thomas','Thompson','Torres','Turner','Walker','Wang',
    'Ward','Washington','Watson','White','Williams','Wilson','Wood','Wright','Wu','Yang',
    'Young','Zhang'
  ];

  const POSITIONS = [
    'CEO','CFO','COO','CTO','CIO','CMO','CHRO','VP of Sales','VP of Marketing',
    'VP of Engineering','VP of Operations','VP of Finance','VP of Product',
    'VP of Human Resources','VP of Business Development',
    'Director of Engineering','Director of Marketing','Director of Sales',
    'Director of Operations','Director of Product','Director of Finance',
    'Director of HR','Director of Design','Director of Communications',
    'Senior Vice President','Executive Vice President','Managing Director',
    'General Manager','Regional Manager','Branch Manager','Operations Manager',
    'Project Manager','Product Manager','Program Manager','Account Manager',
    'Senior Software Engineer','Software Engineer','Staff Engineer','Principal Engineer',
    'Lead Engineer','Frontend Engineer','Backend Engineer','Full Stack Developer',
    'DevOps Engineer','Data Engineer','Machine Learning Engineer','QA Engineer',
    'Senior Designer','UX Designer','UI Designer','Product Designer','Graphic Designer',
    'Creative Director','Art Director',
    'Data Scientist','Data Analyst','Business Analyst','Financial Analyst',
    'Marketing Manager','Brand Manager','Content Manager','Social Media Manager',
    'Sales Manager','Account Executive','Business Development Manager',
    'HR Manager','Recruiter','Talent Acquisition Specialist',
    'Consultant','Senior Consultant','Managing Consultant',
    'Attorney','Paralegal','Legal Counsel',
    'Accountant','Controller','Auditor',
    'Nurse','Physician','Pharmacist','Surgeon',
    'Professor','Teacher','Research Scientist','Research Assistant',
    'Coordinator','Specialist','Administrator','Assistant','Associate',
    'Intern','Fellow','Volunteer','Board Member','Advisor','Founder','Co-Founder','Partner'
  ];

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

  // ── Milestone tracking ──
  const shownMilestones = new Set();
  const MILESTONES = [
    { count: 1,  msg: 'Nice, you\'re off to a great start!' },
    { count: 5,  msg: 'Quarter of the way there' },
    { count: 9,  msg: 'Halfway done \u2014 keep it up!' },
    { count: 13, msg: 'Almost there, just a few left!' },
  ];
  let prevFilledCount = -1;
  let confettiFired = false;

  // ── Update card filled states & progress ring ──
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

    // Progress ring
    const ring = document.getElementById('progress-ring');
    const offset = RING_CIRCUMFERENCE - (filledCount / TOTAL) * RING_CIRCUMFERENCE;
    ring.style.strokeDashoffset = offset;
    // Color: accent -> green as progress increases
    const pct = filledCount / TOTAL;
    ring.style.stroke = pct >= 1 ? 'var(--green)' : pct >= 0.5 ? 'var(--green)' : 'var(--accent)';
    document.getElementById('progress-text').textContent = filledCount + '/' + TOTAL;

    // Milestones (only on increase)
    if (filledCount > prevFilledCount) {
      for (const m of MILESTONES) {
        if (filledCount >= m.count && !shownMilestones.has(m.count)) {
          shownMilestones.add(m.count);
          showToast(m.msg);
        }
      }
      // Confetti on completion
      if (filledCount === TOTAL && !confettiFired && typeof confetti === 'function') {
        confettiFired = true;
        fireConfetti();
      }
    }

    // Reset confetti flag if they un-fill something
    if (filledCount < TOTAL) confettiFired = false;

    prevFilledCount = filledCount;
    updateEmailHref();
  }

  // ── Confetti ──
  function fireConfetti() {
    const colors = ['#B85636','#D4774F','#3A7D5C','#5AAF80','#E8C468','#E87B5A'];
    confetti({ particleCount: 80, spread: 70, origin: { x: 0.15, y: 0.6 }, colors: colors });
    confetti({ particleCount: 80, spread: 70, origin: { x: 0.85, y: 0.6 }, colors: colors });
    setTimeout(() => {
      confetti({ particleCount: 40, spread: 100, origin: { x: 0.5, y: 0.4 }, colors: colors });
    }, 300);
    showToast('All done! Amazing work!');
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

  // ── Keyboard flow: Enter/Shift+Enter ──
  const allInputs = Array.from(document.querySelectorAll('.card-fields input'));
  allInputs.forEach((input, i) => {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const next = e.shiftKey ? allInputs[i - 1] : allInputs[i + 1];
        if (next) {
          next.focus();
          const card = next.closest('.card');
          if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  });

  // ── Autocomplete ──
  function setupAutocomplete(input) {
    const acType = input.dataset.ac;
    const fieldEl = input.closest('.field');
    const dropdown = document.createElement('div');
    dropdown.className = 'ac-dropdown';
    fieldEl.appendChild(dropdown);

    let activeIdx = -1;
    let items = [];

    function getDataset(value) {
      if (acType === 'position') return POSITIONS;
      // For names: if there's a space, suggest last names; otherwise first names
      if (value.includes(' ')) return LAST_NAMES;
      return FIRST_NAMES;
    }

    function getQuery(value) {
      if (acType === 'name' && value.includes(' ')) {
        return value.split(' ').pop();
      }
      return value;
    }

    function show(filtered) {
      items = filtered.slice(0, 6);
      activeIdx = -1;
      if (items.length === 0) { hide(); return; }
      dropdown.innerHTML = items.map((item, i) =>
        '<div class="ac-item" data-i="' + i + '">' + item + '</div>'
      ).join('');
      dropdown.classList.add('open');
    }

    function hide() {
      dropdown.classList.remove('open');
      dropdown.innerHTML = '';
      items = [];
      activeIdx = -1;
    }

    function selectItem(idx) {
      const val = items[idx];
      if (!val) return;
      if (acType === 'name' && input.value.includes(' ')) {
        const parts = input.value.split(' ');
        parts[parts.length - 1] = val;
        input.value = parts.join(' ');
      } else if (acType === 'name') {
        input.value = val + ' ';
      } else {
        input.value = val;
      }
      input.dispatchEvent(new Event('input', { bubbles: true }));
      hide();
      // Advance to next field
      const currentI = allInputs.indexOf(input);
      if (acType === 'position' || (acType === 'name' && !input.value.endsWith(' '))) {
        const next = allInputs[currentI + 1];
        if (next) next.focus();
      }
    }

    function highlight(idx) {
      dropdown.querySelectorAll('.ac-item').forEach((el, i) => {
        el.classList.toggle('active', i === idx);
      });
    }

    input.addEventListener('input', function() {
      const query = getQuery(this.value).toLowerCase();
      if (query.length < 1) { hide(); return; }
      const dataset = getDataset(this.value);
      const filtered = dataset.filter(item => item.toLowerCase().startsWith(query));
      show(filtered);
    });

    input.addEventListener('keydown', function(e) {
      if (!dropdown.classList.contains('open')) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
        highlight(activeIdx);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        highlight(activeIdx);
      } else if (e.key === 'Enter' && activeIdx >= 0) {
        e.preventDefault();
        e.stopPropagation();
        selectItem(activeIdx);
      } else if (e.key === 'Escape') {
        hide();
      }
    });

    dropdown.addEventListener('mousedown', function(e) {
      e.preventDefault(); // Prevent input blur
      const item = e.target.closest('.ac-item');
      if (item) selectItem(parseInt(item.dataset.i));
    });

    input.addEventListener('blur', function() {
      setTimeout(hide, 150);
    });

    input.addEventListener('focus', function() {
      const query = getQuery(this.value).toLowerCase();
      if (query.length >= 1) {
        const dataset = getDataset(this.value);
        const filtered = dataset.filter(item => item.toLowerCase().startsWith(query));
        show(filtered);
      }
    });
  }

  document.querySelectorAll('.card-fields input[data-ac]').forEach(setupAutocomplete);

  // ── Lightbox ──
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxLabel = document.getElementById('lightbox-label');

  document.querySelectorAll('.card-img-wrap').forEach(wrap => {
    wrap.addEventListener('click', function() {
      const img = this.querySelector('img');
      const idx = this.dataset.imgIdx;
      const displayNum = parseInt(idx) + 1;
      lightboxImg.src = img.src;
      const name = (saved[idx] && saved[idx].name && saved[idx].name.trim()) || '';
      lightboxLabel.textContent = name ? '#' + String(displayNum).padStart(2,'0') + ' \u2014 ' + name : '#' + String(displayNum).padStart(2,'0');
      lightbox.classList.add('open');
    });
  });

  lightbox.addEventListener('click', function(e) {
    if (e.target === lightbox || e.target.id === 'lightbox-close') {
      lightbox.classList.remove('open');
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && lightbox.classList.contains('open')) {
      lightbox.classList.remove('open');
    }
  });

  // ── Dark Mode ──
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('face-dir-theme', theme);
  }

  function initTheme() {
    const stored = localStorage.getItem('face-dir-theme');
    if (stored) {
      setTheme(stored);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }

  document.getElementById('theme-toggle').addEventListener('click', function() {
    const current = document.documentElement.getAttribute('data-theme');
    setTheme(current === 'dark' ? 'light' : 'dark');
  });

  initTheme();

  // ── Build formatted results text ──
  function buildResults() {
    let lines = ['Face Directory Results', '='.repeat(30), ''];
    for (let i = 0; i < TOTAL; i++) {
      const displayNum = String(i + 1).padStart(2, '0');
      const name = (saved[i] && saved[i].name && saved[i].name.trim()) || '(not filled)';
      const pos = (saved[i] && saved[i].position && saved[i].position.trim()) || '(not filled)';
      lines.push('#' + displayNum + '  Name: ' + name + '  |  Position: ' + pos);
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
    setTimeout(() => t.classList.remove('show'), 2500);
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
    cards_html = []

    for idx, img_path in enumerate(images):
        display_num = str(idx + 1).zfill(2)

        with open(img_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')

        cards_html.append(CARD_TEMPLATE.format(idx=idx, display_num=display_num, b64=b64))

    html = TEMPLATE_TOP.replace('TOTAL_COUNT', str(total))
    html += ''.join(cards_html)

    bottom = TEMPLATE_BOTTOM.replace('TOTAL_COUNT', str(total))
    html += bottom

    out_path = os.path.join(script_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Generated index.html ({size_kb:.0f} KB) with {total} face images")


if __name__ == '__main__':
    main()
