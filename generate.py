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
    color-scheme: light;
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
    color-scheme: dark;
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
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 22px;
    font-size: 0.95rem;
    color: var(--text);
    line-height: 1.55;
    box-shadow: var(--shadow);
    transition: background-color 0.3s, border-color 0.3s, color 0.3s, box-shadow 0.3s;
  }

  .banner-inner strong {
    color: var(--accent);
    font-weight: 600;
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
    overflow: visible;
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
    border-radius: var(--radius) var(--radius) 0 0;
  }

  .card-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease;
    /* Technique 2: CSS sharpening — perceptual contrast boost */
    filter: contrast(1.08) saturate(1.05);
    image-rendering: -webkit-optimize-contrast;
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
    caret-color: var(--accent);
    cursor: text;
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
    /* Technique 2: CSS sharpening filter (slightly stronger for upscale) */
    filter: contrast(1.1) saturate(1.08);
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

  /* ── Fallback Overlay ── */
  .fallback-overlay {
    position: fixed;
    inset: 0;
    z-index: 400;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }

  .fallback-overlay.open {
    opacity: 1;
    pointer-events: auto;
  }

  .fallback-card {
    background: var(--card);
    border-radius: 20px;
    padding: 40px 32px 32px;
    max-width: 440px;
    width: 100%;
    position: relative;
    box-shadow: 0 24px 80px rgba(0,0,0,0.3);
    transform: translateY(20px) scale(0.95);
    transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    text-align: center;
  }

  .fallback-overlay.open .fallback-card {
    transform: translateY(0) scale(1);
  }

  .fallback-close {
    position: absolute;
    top: 16px;
    right: 16px;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: var(--text-muted);
    cursor: pointer;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    transition: background 0.2s;
  }

  .fallback-close:hover {
    background: var(--accent-light);
  }

  .fallback-icon {
    margin: 0 auto 20px;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: var(--accent-light);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
  }

  .fallback-title {
    font-family: var(--font-display);
    font-size: 1.4rem;
    font-weight: 400;
    margin-bottom: 8px;
    color: var(--text);
  }

  .fallback-body {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-bottom: 24px;
    line-height: 1.5;
  }

  .fallback-steps {
    text-align: left;
    list-style: none;
    counter-reset: steps;
    margin: 0 0 28px;
    padding: 0;
  }

  .fallback-steps li {
    counter-increment: steps;
    position: relative;
    padding: 12px 12px 12px 48px;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--text);
    border-bottom: 1px solid var(--border);
  }

  .fallback-steps li:last-child {
    border-bottom: none;
  }

  .fallback-steps li::before {
    content: counter(steps);
    position: absolute;
    left: 8px;
    top: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    font-size: 0.8rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .fallback-steps strong {
    color: var(--accent);
    font-size: 0.95rem;
    user-select: all;
    word-break: break-all;
  }

  .fallback-hint {
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  .fallback-done {
    width: 100%;
    justify-content: center;
    padding: 14px;
    font-size: 1rem;
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
    max-width: 90vw;
    text-align: center;
  }

  .toast.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }

  /* ── Password Modal ── */
  .pw-modal {
    position: fixed;
    inset: 0;
    z-index: 500;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
  }

  .pw-modal.open {
    opacity: 1;
    pointer-events: auto;
  }

  .pw-card {
    background: var(--card);
    border-radius: 16px;
    padding: 32px;
    max-width: 360px;
    width: 100%;
    text-align: center;
    box-shadow: 0 24px 80px rgba(0,0,0,0.4);
    transform: translateY(16px) scale(0.96);
    transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .pw-modal.open .pw-card {
    transform: translateY(0) scale(1);
  }

  .pw-card h3 {
    font-family: var(--font-display);
    font-size: 1.3rem;
    font-weight: 400;
    margin-bottom: 6px;
    color: var(--text);
  }

  .pw-card p {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 20px;
  }

  .pw-input-wrap {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }

  .pw-input-wrap input {
    flex: 1;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text);
    background: var(--input-bg);
    outline: none;
    transition: border-color 0.2s;
  }

  .pw-input-wrap input:focus {
    border-color: var(--accent);
  }

  .pw-input-wrap button {
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    background: var(--accent);
    color: #fff;
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .pw-input-wrap button:hover {
    background: var(--accent-hover);
  }

  .pw-error {
    font-size: 0.82rem;
    color: #D44;
    height: 1.2em;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-8px); }
    40% { transform: translateX(8px); }
    60% { transform: translateX(-6px); }
    80% { transform: translateX(6px); }
  }

  .pw-card.shake {
    animation: shake 0.4s ease;
  }

  /* ── Admin Panel & Paste Modal ── */
  .admin-card {
    max-width: 380px;
    position: relative;
  }

  .admin-action {
    width: 100%;
    margin-top: 10px;
    justify-content: flex-start;
    padding: 14px 18px;
    text-align: left;
  }

  .paste-card {
    max-width: 560px;
    width: 100%;
    position: relative;
  }

  .paste-card textarea {
    width: 100%;
    min-height: 220px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Consolas, monospace;
    font-size: 0.82rem;
    line-height: 1.5;
    color: var(--text);
    background: var(--input-bg);
    resize: vertical;
    outline: none;
    margin-bottom: 8px;
  }

  .paste-card textarea:focus {
    border-color: var(--accent);
  }

  .paste-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 14px;
  }

  /* ── Photobook Preview ── */
  .photobook-overlay {
    position: fixed;
    inset: 0;
    z-index: 500;
    background: rgba(0,0,0,0.85);
    display: flex;
    flex-direction: column;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }

  .photobook-overlay.open {
    opacity: 1;
    pointer-events: auto;
  }

  .photobook-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    background: rgba(0,0,0,0.5);
    flex-shrink: 0;
  }

  .photobook-toolbar span {
    color: rgba(255,255,255,0.7);
    font-size: 0.9rem;
    font-weight: 500;
  }

  .photobook-toolbar-btns {
    display: flex;
    gap: 10px;
  }

  .photobook-toolbar button {
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 0.88rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .photobook-dl-btn {
    background: var(--accent);
    color: #fff;
  }
  .photobook-dl-btn:hover {
    background: var(--accent-hover);
  }

  .photobook-close-btn {
    background: rgba(255,255,255,0.15);
    color: #fff;
  }
  .photobook-close-btn:hover {
    background: rgba(255,255,255,0.25);
  }

  .photobook-scroll {
    flex: 1;
    overflow: auto;
    display: flex;
    justify-content: center;
    padding: 24px;
  }

  .photobook-scroll img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
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

<!-- Fallback overlay when mailto fails -->
<div class="fallback-overlay" id="fallback-overlay">
  <div class="fallback-card">
    <button class="fallback-close" onclick="closeFallback()">&times;</button>
    <div class="fallback-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="48" height="48"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
    </div>
    <h2 class="fallback-title">Results copied to clipboard!</h2>
    <p class="fallback-body">Your email app didn't open, but the results are ready to send. Here's what to do:</p>
    <ol class="fallback-steps">
      <li>Open your email app (Gmail, Outlook, etc.)</li>
      <li>Create a new email to:<br><strong id="fallback-email"></strong></li>
      <li>Paste the results into the email body<br><span class="fallback-hint">Ctrl+V on Windows &middot; Cmd+V on Mac</span></li>
      <li>Hit Send!</li>
    </ol>
    <button class="btn btn-primary fallback-done" onclick="closeFallback()">Got it</button>
  </div>
</div>

<!-- Password Modal -->
<div class="pw-modal" id="pw-modal">
  <div class="pw-card" id="pw-card">
    <h3>Admin Access</h3>
    <p>Enter the password to continue</p>
    <div class="pw-input-wrap">
      <input type="password" id="pw-input" placeholder="Password" autocomplete="off">
      <button onclick="submitPassword()">Go</button>
    </div>
    <div class="pw-error" id="pw-error"></div>
  </div>
</div>

<!-- Admin Panel -->
<div class="pw-modal" id="admin-panel">
  <div class="pw-card admin-card">
    <button class="fallback-close" onclick="closeAdminPanel()">&times;</button>
    <h3>Admin Tools</h3>
    <p>What would you like to do?</p>
    <button class="btn btn-primary admin-action" onclick="closeAdminPanel(); generatePhotobook();">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      Generate Photobook
    </button>
    <button class="btn btn-secondary admin-action" onclick="showPasteLoad();">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
      Paste &amp; Load Data
    </button>
  </div>
</div>

<!-- Paste Load Modal -->
<div class="pw-modal" id="paste-modal">
  <div class="pw-card paste-card">
    <button class="fallback-close" onclick="closePasteModal()">&times;</button>
    <h3>Paste Results</h3>
    <p>Paste a previous Face Directory export below</p>
    <textarea id="paste-textarea" placeholder="#01  Name: ...  |  Position: ...&#10;#02  Name: ...  |  Position: ...&#10;..."></textarea>
    <div class="pw-error" id="paste-error"></div>
    <div class="paste-actions">
      <button class="btn btn-secondary" onclick="closePasteModal()">Cancel</button>
      <button class="btn btn-primary" onclick="loadPastedData()">Load Data</button>
    </div>
  </div>
</div>

<!-- Photobook Preview -->
<div class="photobook-overlay" id="photobook-overlay">
  <div class="photobook-toolbar">
    <span>Staff Directory</span>
    <div class="photobook-toolbar-btns">
      <button class="photobook-dl-btn" onclick="downloadPhotobook()">Download PNG</button>
      <button class="photobook-close-btn" onclick="closePhotobook()">Close</button>
    </div>
  </div>
  <div class="photobook-scroll">
    <img id="photobook-img" src="" alt="Staff Directory">
  </div>
</div>

<div class="action-bar">
  <div class="action-bar-inner">
    <button class="btn btn-secondary" onclick="copyResults()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      Copy Results
    </button>
    <button class="btn btn-primary" id="email-btn" onclick="emailResults()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      Email Results
    </button>
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
    'Aaron','Abel','Abigail','Abraham','Ada','Adam','Addison','Adelaide','Adeline','Adrian',
    'Adriana','Adrienne','Agnes','Aiden','Aileen','Aimee','Aisha','Alan','Alana','Albert',
    'Alejandra','Alejandro','Alex','Alexa','Alexander','Alexandra','Alexis','Alfonso','Alfred',
    'Alice','Alicia','Alina','Alison','Allen','Allison','Alma','Alvin','Alyssa','Amanda',
    'Amber','Amelia','Amit','Amy','Ana','Anastasia','Andrea','Andres','Andrew','Andy',
    'Angel','Angela','Angelica','Angelina','Angie','Anika','Anita','Ann','Anna','Annabelle',
    'Anne','Annette','Annie','Anthony','Antoine','Antoinette','Antonio','April','Archer',
    'Ariana','Ariel','Arlene','Arnold','Arthur','Arya','Ashlee','Ashley','Ashton','Aspen',
    'Athena','Aubrey','Audrey','Aurora','Austin','Autumn','Ava','Avery','Ayla',
    'Bailey','Barbara','Barnaby','Barry','Beatrice','Beau','Becky','Belinda','Bella','Ben',
    'Benedict','Benjamin','Bennett','Bernadette','Bernard','Bernice','Beth','Bethany','Betty',
    'Beverly','Bianca','Bill','Billy','Blair','Blake','Blanche','Bob','Bobby','Bonnie',
    'Boris','Brad','Bradley','Brady','Brandon','Brenda','Brendan','Brent','Brett','Brian',
    'Brianna','Bridget','Brittany','Brock','Brooke','Bruce','Bruno','Bryan','Bryant','Bryce',
    'Brynn','Byron',
    'Caden','Caitlin','Caleb','Calvin','Cameron','Camila','Camille','Candace','Cara','Carl',
    'Carla','Carlos','Carly','Carmen','Carol','Carolina','Caroline','Carolyn','Carrie',
    'Carson','Carter','Casey','Cassandra','Cassidy','Catherine','Cathy','Cecelia','Cecil',
    'Cecilia','Cedric','Celeste','Celia','Chad','Chance','Chandler','Chandra','Charlene',
    'Charles','Charlie','Charlotte','Chase','Chelsea','Cheryl','Chester','Chloe','Chris',
    'Christian','Christina','Christine','Christopher','Cindy','Claire','Clara','Clare',
    'Clarence','Clarissa','Clark','Claude','Claudia','Clay','Clayton','Cliff','Clifford',
    'Clint','Clinton','Clyde','Cody','Colby','Cole','Colette','Colin','Colleen','Collin',
    'Conner','Connor','Conrad','Constance','Cooper','Cora','Corey','Corinne','Cornelius',
    'Courtney','Craig','Cristina','Crystal','Curtis','Cynthia',
    'Dahlia','Daisy','Dakota','Dale','Dallas','Dalton','Damian','Damon','Dan','Dana','Dane',
    'Daniel','Daniela','Danielle','Danny','Daphne','Darcy','Daria','Darin','Darius','Darla',
    'Darlene','Darrell','Darren','Darrin','Darryl','Darwin','Dave','David','Dawn','Dean',
    'Deanna','Debbie','Deborah','Debra','Declan','Dee','Deena','Deidre','Deirdre','Delia',
    'Delilah','Della','Delores','Demetrius','Dena','Denis','Denise','Dennis','Derek','Desiree',
    'Destiny','Devin','Devon','Diana','Diane','Diego','Dillon','Dina','Dinah','Dirk',
    'Dolores','Dominic','Dominique','Don','Donald','Donna','Donovan','Dora','Doreen','Doris',
    'Dorothy','Doug','Douglas','Drake','Drew','Duane','Duncan','Dustin','Dwayne','Dylan',
    'Earl','Ebony','Ed','Eddie','Eden','Edgar','Edith','Edmund','Eduardo','Edward','Edwin',
    'Eileen','Elaine','Eleanor','Elena','Eli','Eliana','Elias','Elijah','Elisa','Elisabeth',
    'Elise','Eliza','Elizabeth','Ella','Ellen','Ellie','Elliot','Elliott','Ellis','Elmer',
    'Eloise','Elsa','Elsie','Emerson','Emery','Emilia','Emily','Emma','Emmanuel','Emmett',
    'Eric','Erica','Erik','Erika','Erin','Ernest','Ernesto','Ervin','Esmeralda','Estelle',
    'Esther','Ethan','Eugene','Eva','Evan','Eve','Evelyn','Everett','Ezra',
    'Fabian','Faith','Faye','Felicia','Felix','Fernando','Fiona','Fletcher','Flora','Florence',
    'Floyd','Forrest','Frances','Francesca','Francis','Francisco','Frank','Franklin','Fred',
    'Freda','Frederick','Freya','Fritz',
    'Gabriel','Gabriella','Gabrielle','Gail','Gale','Garrett','Gary','Gavin','Gena','Gene',
    'Geneva','Genevieve','Geoffrey','George','Georgia','Gerald','Geraldine','Gerard','Gerry',
    'Gideon','Gilbert','Gina','Ginger','Giovanna','Giovanni','Giselle','Gladys','Glen','Glenda',
    'Glenn','Gloria','Gordon','Grace','Gracie','Graham','Grant','Grayson','Greg','Gregg',
    'Gregory','Greta','Griffin','Guadalupe','Guillermo','Gus','Guy','Gwen','Gwendolyn',
    'Hailey','Haley','Hannah','Hans','Harley','Harold','Harper','Harriet','Harris','Harrison',
    'Harry','Harvey','Hattie','Hayden','Hayley','Hazel','Heath','Heather','Hector','Heidi',
    'Helen','Helena','Helene','Henry','Herbert','Herman','Hilary','Hilda','Holly','Homer',
    'Hope','Howard','Hubert','Hudson','Hugh','Hugo','Hunter',
    'Ian','Ibrahim','Ida','Ignacio','Ilene','Imani','Imogen','Ina','India','Ingrid','Ira',
    'Irene','Iris','Irma','Irving','Isaac','Isabel','Isabella','Isabelle','Isaiah','Isiah',
    'Ismael','Israel','Ivan','Ivy',
    'Jace','Jack','Jackie','Jackson','Jacob','Jacqueline','Jade','Jaden','Jaime','Jake',
    'Jaleel','Jamal','James','Jamie','Jan','Jana','Jane','Janelle','Janet','Janette','Janice',
    'Janie','Janine','Jared','Jasmine','Jason','Jasper','Javier','Jay','Jayden','Jayla',
    'Jayne','Jean','Jeanette','Jeanne','Jeannie','Jeff','Jefferson','Jeffrey','Jenna',
    'Jennifer','Jenny','Jeremiah','Jeremy','Jermaine','Jerome','Jerry','Jesse','Jessica',
    'Jessie','Jesus','Jill','Jillian','Jim','Jimmy','Jo','Joan','Joann','Joanna','Joanne',
    'Jocelyn','Jodi','Jody','Joe','Joel','Joelle','Joey','Johan','Johanna','John','Johnathan',
    'Johnny','Jolene','Jon','Jonas','Jonathan','Jonathon','Jordan','Jorge','Jose','Joseph',
    'Josephine','Josh','Joshua','Joy','Joyce','Juan','Juanita','Judith','Judy','Julia',
    'Julian','Juliana','Julianna','Julie','Juliet','Juliette','Julio','Julius','June',
    'Junior','Justin','Justine',
    'Kaia','Kaitlyn','Kara','Karen','Kari','Karina','Karl','Karla','Kate','Katelyn',
    'Katherine','Kathleen','Kathryn','Kathy','Katie','Katrina','Kay','Kayla','Kaylee',
    'Keegan','Keith','Kelley','Kelli','Kellie','Kelly','Kelsey','Ken','Kendra','Kenneth',
    'Kenny','Kent','Kenya','Kerry','Kevin','Kiana','Kimberly','Kingsley','Kira','Kirk',
    'Kirsten','Kit','Knox','Kobe','Krista','Kristen','Kristin','Kristina','Kristine',
    'Kristopher','Krystal','Kurt','Kyle','Kylie','Kyra',
    'Lacey','Lamar','Lana','Lance','Landon','Lane','Lara','Larry','Lars','Laura','Laurel',
    'Lauren','Laurence','Laurie','Lawrence','Layla','Lea','Leah','Leandro','Lee','Leigh',
    'Lena','Leo','Leon','Leona','Leonard','Leonardo','Leroy','Leslie','Levi','Lewis','Lia',
    'Liam','Lila','Liliana','Lillian','Lillie','Lily','Lincoln','Linda','Lindsay','Lindsey',
    'Lisa','Lisette','Liv','Livia','Liz','Logan','Lois','Lola','Lonnie','Lora','Lorena',
    'Lorenzo','Loretta','Lori','Lorraine','Louie','Louis','Louise','Luca','Lucas','Lucia',
    'Lucille','Lucy','Luis','Luisa','Luke','Luna','Luther','Lydia','Lyla','Lynda','Lynn',
    'Mabel','Mackenzie','Macy','Maddox','Madeline','Madison','Mae','Maeve','Maggie',
    'Magnus','Maia','Maisie','Makayla','Malcolm','Malik','Mallory','Mandy','Manuel','Mara',
    'Marc','Marcel','Marcella','Marcia','Marco','Marcus','Margaret','Margarita','Margot',
    'Maria','Mariah','Marian','Mariana','Marianne','Marie','Marilyn','Marina','Mario',
    'Marion','Marisa','Marisol','Marissa','Marjorie','Mark','Marlene','Marlon','Marsha',
    'Marshall','Martha','Martin','Martina','Marvin','Mary','Mason','Mateo','Mathew','Matilda',
    'Matt','Matthew','Maureen','Maurice','Max','Maxim','Maximilian','Maxine','Maxwell','May',
    'Maya','Mckenzie','Meagan','Megan','Meghan','Mei','Melanie','Melinda','Melissa','Melody',
    'Mercedes','Meredith','Meryl','Mia','Micah','Michael','Michaela','Michele','Michelle',
    'Miguel','Mikaela','Mike','Mila','Mildred','Miles','Millicent','Millie','Milton','Mimi',
    'Mindy','Minerva','Miranda','Miriam','Mitchell','Moira','Molly','Mona','Monica','Monique',
    'Morgan','Morris','Moses','Muriel','Murray','Mya','Myles','Myra','Myrna','Myrtle',
    'Nadia','Nadine','Nancy','Naomi','Natalia','Natalie','Natasha','Nathan','Nathaniel',
    'Neal','Neil','Nellie','Nelson','Nessa','Neva','Nicholas','Nichole','Nick','Nicky',
    'Nicolas','Nicole','Nina','Noah','Noel','Noelle','Nolan','Nora','Norma','Norman','Nova',
    'Octavia','Olive','Oliver','Olivia','Omar','Opal','Orlando','Oscar','Otto','Owen',
    'Paige','Palmer','Pam','Pamela','Parker','Pat','Patricia','Patrick','Patsy','Patti',
    'Patty','Paul','Paula','Paulette','Pauline','Paxton','Pearl','Pedro','Peggy','Penelope',
    'Penny','Percy','Perry','Pete','Peter','Petra','Peyton','Phil','Philip','Philippe',
    'Phillip','Phoebe','Phyllis','Pierce','Piper','Polly','Porter','Preston','Priscilla',
    'Quentin','Quinn',
    'Rachael','Rachel','Rafael','Ralph','Ramona','Randall','Randolph','Randy','Raquel',
    'Rashid','Raul','Raven','Ray','Raymond','Reagan','Rebecca','Reed','Reese','Regina',
    'Reginald','Reid','Remy','Rena','Renata','Renee','Reuben','Rex','Reynaldo','Rhett',
    'Rhiannon','Rhonda','Ricardo','Richard','Rick','Ricky','Riley','Rita','Rob','Robert',
    'Roberta','Roberto','Robin','Robyn','Rocco','Rocky','Rod','Roderick','Rodney','Rodrigo',
    'Roger','Roland','Roman','Ron','Ronald','Ronaldo','Ronnie','Rosa','Rosalie','Rosalind',
    'Rosalyn','Rose','Rosemary','Rosie','Ross','Rowan','Roxanne','Roy','Ruby','Rudolph',
    'Rudy','Rufus','Russ','Russell','Ruth','Ryan',
    'Sabrina','Sadie','Sage','Sally','Salvador','Sam','Samantha','Samara','Sammy','Samuel',
    'Sandra','Sandy','Santiago','Sara','Sarah','Sasha','Saul','Savannah','Sawyer','Scarlett',
    'Scott','Sean','Sebastian','Selena','Serena','Sergio','Seth','Shana','Shane','Shania',
    'Shannon','Shari','Sharon','Shaun','Shawn','Shawna','Sheila','Shelby','Sheldon','Shelly',
    'Sheri','Sherman','Sherri','Sherry','Sheryl','Shirley','Sidney','Sienna','Sierra','Silas',
    'Silvia','Simon','Simone','Skylar','Sofia','Solomon','Sonia','Sonya','Sophia','Sophie',
    'Spencer','Stacey','Stacy','Stanley','Stella','Stephan','Stephanie','Stephen','Steve',
    'Steven','Stewart','Stuart','Sue','Summer','Susan','Susanne','Suzanne','Sven','Sydney',
    'Sylvia',
    'Tabitha','Talia','Tamara','Tammy','Tania','Tanner','Tanya','Tara','Taryn','Tasha',
    'Tate','Tatiana','Taylor','Ted','Teddy','Teresa','Teri','Terrance','Terrence','Terri',
    'Terry','Tess','Tessa','Thaddeus','Thea','Thelma','Theodore','Theresa','Thomas','Tia',
    'Tiffany','Tim','Timothy','Tina','Tobias','Toby','Todd','Tom','Tommy','Toni','Tony',
    'Tonya','Tracey','Tracy','Travis','Trent','Trevor','Trey','Tricia','Trina','Trinity',
    'Trisha','Tristan','Troy','Trudy','Tucker','Tyler','Tyrone','Tyson',
    'Ulysses','Uma','Ursula',
    'Valerie','Vanessa','Vaughn','Vera','Verna','Vernon','Veronica','Vicki','Vicky','Victor',
    'Victoria','Vincent','Viola','Violet','Virgil','Virginia','Vivian','Viviana','Vivienne',
    'Wade','Walker','Wallace','Walter','Wanda','Warren','Wayne','Wendell','Wendy','Wesley',
    'Whitney','Wilbur','Wiley','Will','Willa','William','Willie','Willow','Wilma','Wilson',
    'Winston','Wren','Wyatt',
    'Xander','Xavier','Ximena',
    'Yael','Yasmin','Yolanda','Yusuf','Yvette','Yvonne',
    'Zachary','Zane','Zara','Zelda','Zoe','Zoey','Zora'
  ];

  const LAST_NAMES = [
    'Abbott','Acevedo','Acosta','Adams','Adkins','Aguilar','Aguirre','Albert','Alexander',
    'Alfaro','Ali','Allen','Allison','Alonso','Alvarado','Alvarez','Andersen','Anderson',
    'Andrews','Anthony','Aquino','Aranda','Archer','Arias','Armstrong','Arnold','Arroyo',
    'Atkins','Austin','Avery','Avila','Ayala',
    'Baez','Bailey','Baker','Baldwin','Ball','Ballard','Banks','Barber','Barker','Barnes',
    'Barnett','Barrera','Barrett','Barrios','Barron','Barry','Barton','Bates','Bauer',
    'Baxter','Bean','Beard','Beasley','Beck','Becker','Bell','Beltran','Benitez','Benjamin',
    'Bennett','Benson','Berg','Berger','Bernal','Bernard','Berry','Best','Bishop','Black',
    'Blackwell','Blair','Blake','Blanchard','Blanco','Bland','Bloom','Blythe','Boggs',
    'Bolton','Bond','Bonilla','Booker','Boone','Booth','Bowen','Bowers','Bowman','Boyd',
    'Boyer','Boyle','Bradford','Bradley','Brady','Bragg','Branch','Brand','Brandt','Bravo',
    'Brennan','Brewer','Bridges','Briggs','Britt','Brock','Brooks','Brown','Browning','Bruce',
    'Bryan','Bryant','Buchanan','Buck','Buckley','Bullock','Burch','Burgess','Burke','Burnett',
    'Burns','Burris','Burt','Burton','Bush','Butler','Byrd','Byrne',
    'Cabrera','Cain','Calderon','Caldwell','Calhoun','Callahan','Camacho','Cameron','Campbell',
    'Campos','Cannon','Cardenas','Carey','Carlson','Carpenter','Carr','Carrillo','Carroll',
    'Carson','Carter','Caruso','Casillas','Castaneda','Castillo','Castro','Cervantes',
    'Chambers','Chan','Chandler','Chang','Chapman','Charles','Chase','Chavez','Chen','Cherry',
    'Choi','Christensen','Christian','Church','Cisneros','Clark','Clarke','Clay','Clayton',
    'Clements','Cleveland','Cline','Cobb','Cochran','Coffey','Cohen','Cole','Coleman',
    'Collier','Collins','Colon','Combs','Compton','Conley','Conner','Conrad','Contreras',
    'Conway','Cook','Cooper','Copeland','Cordero','Correa','Cortez','Costa','Cowan','Cox',
    'Craig','Crane','Crawford','Cross','Crosby','Cruz','Cummings','Cunningham','Curry',
    'Curtis',
    'Dahl','Dale','Dalton','Daly','Daniel','Daniels','Davenport','David','Davidson','Davies',
    'Davis','Dawson','Day','Dean','Decker','Delacruz','Deleon','Delgado','Dennis','Denton',
    'Diaz','Dickerson','Dickson','Dillard','Dixon','Do','Dodson','Dominguez','Donaldson',
    'Donovan','Dorsey','Dougherty','Douglas','Doyle','Drake','Draper','Duarte','Dudley',
    'Duffy','Duke','Duncan','Dunlap','Dunn','Duran','Durham','Duval','Dyer',
    'Eaton','Edwards','Elliott','Ellis','Ellison','Emerson','English','Enriquez','Erickson',
    'Espinosa','Espinoza','Esposito','Estrada','Evans','Everett',
    'Farmer','Farrell','Faulkner','Felix','Ferguson','Fernandez','Ferrell','Fields','Figueroa',
    'Finch','Fischer','Fisher','Fitzgerald','Fitzpatrick','Fleming','Fletcher','Flores',
    'Flowers','Floyd','Flynn','Foley','Fong','Forbes','Ford','Foreman','Foster','Fowler',
    'Fox','Francis','Franco','Frank','Franklin','Frazier','Frederick','Freeman','French',
    'Friedman','Frost','Fry','Fuentes','Fuller',
    'Gallagher','Gallegos','Galloway','Galvan','Gamble','Gao','Garcia','Gardner','Garner',
    'Garrett','Garrison','Garza','Gates','Gay','George','Gibbs','Gibson','Gilbert','Giles',
    'Gill','Gillespie','Gilmore','Glass','Glenn','Glover','Gomez','Gonzales','Gonzalez',
    'Good','Goodman','Goodwin','Gordon','Graham','Grant','Graves','Gray','Green','Greene',
    'Greer','Gregory','Griffin','Griffith','Grimes','Gross','Grover','Guerrero','Guo',
    'Gutierrez','Guzman',
    'Ha','Hahn','Haines','Hale','Haley','Hall','Hamilton','Hammond','Hampton','Han','Hancock',
    'Haney','Hansen','Hanson','Hardin','Harding','Hardy','Harmon','Harper','Harrell',
    'Harrington','Harris','Harrison','Hart','Hartman','Harvey','Hastings','Hatfield','Hawkins',
    'Hayden','Hayes','Haynes','Hays','Heath','Heller','Henderson','Hendricks','Hendrix',
    'Henry','Hensley','Herbert','Herman','Hernandez','Herrera','Herring','Hess','Hewitt',
    'Hickman','Hicks','Higgins','Hill','Hines','Ho','Hobbs','Hodge','Hodges','Hoffman',
    'Hogan','Holcomb','Holder','Holland','Holloway','Holmes','Holt','Hood','Hooper','Hope',
    'Hopkins','Horn','Horne','Horton','Houston','Howard','Howe','Howell','Hu','Huang',
    'Hubbard','Hudson','Huff','Huffman','Hughes','Hull','Humphrey','Hunt','Hunter','Hurley',
    'Hurst','Hutchinson','Huynh',
    'Ibarra','Im','Ingram','Irwin','Ishikawa',
    'Jackson','Jacobs','Jacobson','James','Jameson','Jarvis','Jefferson','Jenkins','Jennings',
    'Jensen','Jimenez','Johns','Johnson','Johnston','Jones','Jordan','Joseph','Joyce','Juarez',
    'Jung',
    'Kane','Kang','Kaplan','Kaufman','Kay','Keane','Kearns','Keating','Keith','Keller',
    'Kelley','Kelly','Kemp','Kennedy','Kent','Kerr','Khan','Kim','Kimball','King','Kinney',
    'Kirk','Klein','Kline','Knapp','Knight','Knox','Koch','Kramer','Krueger','Kumar',
    'Lamb','Lambert','Lancaster','Landry','Lane','Lang','Lara','Larsen','Larson','Lawrence',
    'Lawson','Le','Leach','Leblanc','Lee','Lemon','Leon','Leonard','Lester','Levine','Levy',
    'Lewis','Li','Lim','Lin','Lindsey','Little','Liu','Livingston','Lloyd','Logan','Lom',
    'Long','Lopez','Lott','Love','Lowe','Lowery','Lu','Lucas','Luna','Luo','Lutz','Lynch',
    'Lynn','Lyons',
    'Ma','Macdonald','Mack','Madden','Maddox','Maldonado','Malone','Mann','Manning',
    'Manriquez','Marin','Marks','Marquez','Marsh','Marshall','Martin','Martinez','Mason',
    'Massey','Mathews','Mathis','Matthews','Maxwell','May','Mayer','Maynard','Mayo','Mays',
    'McBride','McCann','McCarthy','McCartney','McClain','McClure','McConnell','McCoy',
    'McCullough','McDaniel','McDonald','McDowell','McFarland','McGee','McGrath','McGuire',
    'McIntosh','McIntyre','McKay','McKee','McKenzie','McKinney','McLaughlin','McLean',
    'McMahon','McNeil','McPherson','Meadows','Medina','Mejia','Melendez','Melton','Mendez',
    'Mendoza','Mercado','Mercer','Merritt','Meyer','Meyers','Meza','Middleton','Miles',
    'Miller','Mills','Miranda','Mitchell','Molina','Monroe','Montague','Montoya','Moody',
    'Moon','Moore','Mora','Morales','Moran','Moreno','Morgan','Morris','Morrison','Morrow',
    'Morse','Morton','Mosley','Moss','Moyer','Mueller','Mullen','Mullins','Munoz','Murillo',
    'Murphy','Murray','Myers',
    'Nair','Nash','Navarro','Neal','Nelson','Newman','Newton','Ng','Nguyen','Nichols',
    'Nicholson','Nielsen','Nixon','Noble','Noel','Nolan','Norman','Norris','North','Norton',
    'Novak','Nunez',
    'OBrien','OConnell','OConnor','ODonnell','ONeal','ONeil','ONeill','Ochoa','Odom',
    'Ogden','Oliver','Olsen','Olson','Ortega','Ortiz','Osborn','Osborne','Owen','Owens',
    'Pace','Pacheco','Padilla','Page','Palmer','Pan','Park','Parker','Parks','Parrish',
    'Parsons','Patel','Patrick','Patterson','Patton','Paul','Payne','Pearce','Pearson',
    'Peck','Pena','Pennington','Peralta','Perez','Perkins','Perry','Peters','Petersen',
    'Peterson','Pham','Phelps','Phillips','Pickett','Pierce','Pittman','Pitts','Pollard',
    'Ponce','Poole','Pope','Porter','Potter','Powell','Powers','Pratt','Preston','Price',
    'Prince','Proctor','Pruitt',
    'Quinn','Quintana','Quintero',
    'Ramirez','Ramos','Ramsey','Randall','Randolph','Rangel','Rao','Rasmussen','Ratliff',
    'Ray','Raymond','Reed','Reese','Reeves','Reid','Reilly','Reyes','Reynolds','Rhodes',
    'Rice','Rich','Richards','Richardson','Richmond','Riddle','Riggs','Riley','Rios','Rivas',
    'Rivera','Roach','Robbins','Roberts','Robertson','Robinson','Robles','Rocha','Rodgers',
    'Rodriguez','Rogers','Rojas','Rollins','Roman','Romero','Rosa','Rosales','Rosas','Rose',
    'Ross','Roth','Rowe','Rowland','Roy','Rubio','Ruiz','Rush','Russell','Russo','Ryan',
    'Saavedra','Salas','Salazar','Salinas','Sampson','Sanchez','Sanders','Sandoval',
    'Santana','Santiago','Santos','Sargent','Saunders','Savage','Sawyer','Schaefer','Schmidt',
    'Schneider','Schroeder','Schultz','Schwartz','Scott','Sellers','Serrano','Sexton',
    'Shah','Shannon','Sharp','Shaw','Shea','Sheldon','Shelton','Shepard','Shepherd','Sherman',
    'Shields','Shin','Short','Silva','Simmons','Simon','Simpson','Sims','Singh','Singleton',
    'Sloan','Small','Smith','Snow','Snyder','Solis','Solomon','Song','Sosa','Soto','Sparks',
    'Spears','Spencer','Stafford','Stanley','Stanton','Stark','Steele','Stein','Stephens',
    'Stephenson','Stevens','Stevenson','Stewart','Stokes','Stone','Stout','Strickland',
    'Strong','Stuart','Suarez','Sullivan','Summers','Sun','Sutton','Swanson','Sweeney',
    'Sykes',
    'Talbot','Tan','Tanner','Tate','Taylor','Terrell','Terry','Thomas','Thompson','Thornton',
    'Tian','Todd','Torres','Townsend','Tran','Travis','Trejo','Trujillo','Tucker','Turner',
    'Tyler',
    'Underwood','Uribe',
    'Valdez','Valencia','Valentine','Valenzuela','Vance','Vargas','Vasquez','Vaughan',
    'Vaughn','Vazquez','Vega','Velasquez','Velazquez','Velez','Vera','Vernon','Villa',
    'Villanueva','Villarreal','Vincent','Vo','Vogt',
    'Wade','Wagner','Walker','Wall','Wallace','Waller','Walsh','Walter','Walters','Walton',
    'Wang','Ward','Warner','Warren','Washington','Waters','Watkins','Watson','Watts','Weaver',
    'Webb','Weber','Webster','Weeks','Weiss','Welch','Wells','Werner','West','Whitaker',
    'White','Whitehead','Whitney','Wiggins','Wilcox','Wilder','Wiley','Wilkerson','Wilkins',
    'Wilkinson','Williams','Williamson','Willis','Wilson','Winters','Wise','Wolfe','Wong',
    'Woo','Wood','Woodard','Woods','Woodward','Wright','Wu','Wyatt',
    'Xiao','Xu',
    'Yam','Yan','Yang','Yao','Yates','Ye','Yi','York','Young','Yu','Yuan','Yun',
    'Zamora','Zapata','Zavala','Zhang','Zhao','Zhou','Zimmerman','Zhu','Zuniga'
  ];

  const POSITIONS = [
    // C-Suite
    'CEO','CFO','COO','CTO','CIO','CMO','CHRO','CLO','CPO','CSO','CISO','CRO',
    'Chief Executive Officer','Chief Financial Officer','Chief Operating Officer',
    'Chief Technology Officer','Chief Information Officer','Chief Marketing Officer',
    'Chief Human Resources Officer','Chief Legal Officer','Chief Product Officer',
    'Chief Strategy Officer','Chief Information Security Officer','Chief Revenue Officer',
    'Chief Data Officer','Chief Digital Officer','Chief Experience Officer',
    'Chief Communications Officer','Chief Compliance Officer','Chief Creative Officer',
    'Chief Diversity Officer','Chief Innovation Officer','Chief Medical Officer',
    'Chief Nursing Officer','Chief People Officer','Chief Sustainability Officer',
    // VP Level
    'Vice President','Senior Vice President','Executive Vice President',
    'Group Vice President','Assistant Vice President','Associate Vice President',
    'VP of Sales','VP of Marketing','VP of Engineering','VP of Operations',
    'VP of Finance','VP of Product','VP of Human Resources','VP of Business Development',
    'VP of Customer Success','VP of Design','VP of Data','VP of Legal',
    'VP of Communications','VP of Partnerships','VP of Strategy','VP of IT',
    'VP of Supply Chain','VP of Manufacturing','VP of Research','VP of Compliance',
    'VP of Talent','VP of Growth','VP of Revenue','VP of Analytics',
    // Director Level
    'Director','Senior Director','Associate Director','Assistant Director',
    'Managing Director','Executive Director','Regional Director',
    'Director of Engineering','Director of Marketing','Director of Sales',
    'Director of Operations','Director of Product','Director of Finance',
    'Director of HR','Director of Human Resources','Director of Design',
    'Director of Communications','Director of IT','Director of Technology',
    'Director of Business Development','Director of Customer Success',
    'Director of Data Science','Director of Analytics','Director of Research',
    'Director of Quality Assurance','Director of Security','Director of Compliance',
    'Director of Procurement','Director of Supply Chain','Director of Logistics',
    'Director of Manufacturing','Director of Facilities','Director of Training',
    'Director of Talent Acquisition','Director of Content','Director of Brand',
    'Director of Partnerships','Director of Strategy','Director of Innovation',
    'Director of Programs','Director of Projects','Director of Events',
    'Director of Public Relations','Director of Government Relations',
    'Director of Community','Director of Education','Director of Admissions',
    'Director of Development','Director of Fundraising','Director of Nursing',
    'Director of Pharmacy','Director of Clinical Operations',
    // Manager Level
    'Manager','Senior Manager','Assistant Manager','Associate Manager',
    'General Manager','Regional Manager','Branch Manager','Area Manager',
    'District Manager','Zone Manager','Shift Manager','Floor Manager',
    'Operations Manager','Project Manager','Product Manager','Program Manager',
    'Account Manager','Marketing Manager','Sales Manager','Brand Manager',
    'Content Manager','Social Media Manager','Community Manager','PR Manager',
    'IT Manager','Engineering Manager','Development Manager','QA Manager',
    'HR Manager','Recruitment Manager','Talent Manager','Training Manager',
    'Finance Manager','Accounting Manager','Payroll Manager','Treasury Manager',
    'Office Manager','Facilities Manager','Warehouse Manager','Logistics Manager',
    'Supply Chain Manager','Procurement Manager','Vendor Manager',
    'Customer Success Manager','Customer Service Manager','Support Manager',
    'Client Relations Manager','Relationship Manager','Partnership Manager',
    'Business Development Manager','Growth Manager','Strategy Manager',
    'Risk Manager','Compliance Manager','Audit Manager',
    'Creative Manager','Design Manager','UX Manager',
    'Data Manager','Analytics Manager','Research Manager',
    'Clinical Manager','Practice Manager','Case Manager',
    'Property Manager','Construction Manager','Maintenance Manager',
    'Event Manager','Campaign Manager','Channel Manager',
    // Engineering & Tech
    'Software Engineer','Senior Software Engineer','Staff Software Engineer',
    'Principal Software Engineer','Distinguished Engineer','Fellow Engineer',
    'Lead Engineer','Lead Software Engineer','Engineering Lead',
    'Frontend Engineer','Senior Frontend Engineer','Frontend Developer',
    'Backend Engineer','Senior Backend Engineer','Backend Developer',
    'Full Stack Engineer','Full Stack Developer','Senior Full Stack Developer',
    'Mobile Engineer','iOS Engineer','Android Engineer','React Native Developer',
    'DevOps Engineer','Senior DevOps Engineer','Site Reliability Engineer','SRE',
    'Platform Engineer','Infrastructure Engineer','Cloud Engineer','Cloud Architect',
    'Data Engineer','Senior Data Engineer','ETL Developer','Database Engineer',
    'Machine Learning Engineer','ML Engineer','AI Engineer','AI Researcher',
    'Deep Learning Engineer','NLP Engineer','Computer Vision Engineer',
    'Security Engineer','Application Security Engineer','Penetration Tester',
    'QA Engineer','Quality Assurance Engineer','Test Engineer','SDET',
    'Automation Engineer','Test Automation Engineer','QA Analyst',
    'Systems Engineer','Systems Administrator','Network Engineer','Network Administrator',
    'Solutions Engineer','Solutions Architect','Technical Architect',
    'Enterprise Architect','Software Architect','System Architect',
    'Technical Lead','Tech Lead','Engineering Manager',
    'Technical Program Manager','Technical Product Manager',
    'Release Engineer','Build Engineer','Embedded Engineer','Firmware Engineer',
    'Robotics Engineer','Hardware Engineer','Electrical Engineer',
    'Blockchain Developer','Web Developer','Web Designer','Webmaster',
    'IT Specialist','IT Analyst','IT Consultant','IT Coordinator',
    'IT Support Specialist','Help Desk Analyst','Desktop Support',
    'Database Administrator','DBA','System Analyst','Business Systems Analyst',
    'Technical Writer','Documentation Engineer',
    'Scrum Master','Agile Coach',
    // Data & Analytics
    'Data Scientist','Senior Data Scientist','Lead Data Scientist',
    'Data Analyst','Senior Data Analyst','Business Intelligence Analyst',
    'BI Developer','BI Engineer','Analytics Engineer','Reporting Analyst',
    'Quantitative Analyst','Statistician','Research Scientist','Research Analyst',
    'Data Architect','Chief Data Scientist',
    // Design
    'Designer','Senior Designer','Lead Designer','Principal Designer',
    'UX Designer','Senior UX Designer','UX Researcher','UX Writer',
    'UI Designer','Senior UI Designer','Visual Designer',
    'Product Designer','Senior Product Designer','Staff Product Designer',
    'Graphic Designer','Senior Graphic Designer','Brand Designer',
    'Motion Designer','Interaction Designer','Service Designer',
    'Design Director','Creative Director','Art Director','Design Lead',
    'Illustrator','Photographer','Videographer','Animator',
    'Design System Designer','Accessibility Designer',
    // Product
    'Product Owner','Product Lead','Senior Product Manager','Group Product Manager',
    'Principal Product Manager','Chief Product Officer',
    'Product Analyst','Product Marketing Manager','Product Operations Manager',
    // Marketing
    'Marketing Coordinator','Marketing Specialist','Marketing Analyst',
    'Senior Marketing Manager','Marketing Director',
    'Digital Marketing Manager','Digital Marketing Specialist',
    'Content Strategist','Content Creator','Content Writer','Copywriter',
    'SEO Specialist','SEO Manager','SEM Specialist','PPC Specialist',
    'Social Media Specialist','Social Media Coordinator','Social Media Strategist',
    'Email Marketing Manager','Email Marketing Specialist',
    'Growth Hacker','Growth Marketing Manager','Demand Generation Manager',
    'Marketing Operations Manager','Marketing Automation Specialist',
    'Brand Strategist','Brand Ambassador','Public Relations Specialist',
    'Communications Specialist','Communications Manager','Press Secretary',
    'Media Relations Manager','Influencer Marketing Manager',
    'Event Planner','Event Coordinator','Conference Manager',
    // Sales
    'Sales Representative','Sales Associate','Sales Consultant',
    'Account Executive','Senior Account Executive','Enterprise Account Executive',
    'Business Development Representative','BDR','Sales Development Representative','SDR',
    'Inside Sales Representative','Outside Sales Representative',
    'Sales Director','Sales Operations Manager','Sales Operations Analyst',
    'Sales Engineer','Solutions Consultant','Pre-Sales Engineer',
    'Key Account Manager','Strategic Account Manager','Client Director',
    'Territory Manager','Channel Sales Manager','Retail Sales Manager',
    'Sales Trainer','Sales Enablement Manager',
    // Customer-Facing
    'Customer Success Manager','Customer Success Specialist',
    'Customer Support Representative','Customer Service Representative',
    'Technical Support Specialist','Technical Support Engineer',
    'Client Services Manager','Client Partner','Engagement Manager',
    'Implementation Specialist','Implementation Manager','Onboarding Specialist',
    'Customer Experience Manager','Voice of Customer Analyst',
    // Finance & Accounting
    'Accountant','Senior Accountant','Staff Accountant','Tax Accountant',
    'Accounts Payable Specialist','Accounts Receivable Specialist',
    'Bookkeeper','Controller','Assistant Controller',
    'Financial Analyst','Senior Financial Analyst','FP&A Analyst',
    'Financial Planner','Financial Advisor','Wealth Manager',
    'Investment Analyst','Portfolio Manager','Fund Manager','Trader',
    'Risk Analyst','Credit Analyst','Underwriter',
    'Auditor','Internal Auditor','External Auditor','Compliance Analyst',
    'Treasury Analyst','Revenue Analyst','Cost Analyst','Budget Analyst',
    'Tax Manager','Tax Director','Finance Director',
    'Actuary','Economist',
    // HR & People
    'Human Resources Generalist','HR Generalist','HR Specialist','HR Coordinator',
    'HR Business Partner','HRBP','Senior HR Business Partner',
    'Recruiter','Senior Recruiter','Technical Recruiter','Executive Recruiter',
    'Sourcer','Talent Acquisition Specialist','Talent Acquisition Manager',
    'Talent Management Specialist','People Operations Manager',
    'Compensation Analyst','Benefits Specialist','Benefits Administrator',
    'Payroll Specialist','Payroll Administrator',
    'Learning and Development Specialist','Training Specialist','Training Coordinator',
    'Organizational Development Specialist','Employee Relations Specialist',
    'Diversity and Inclusion Manager','DEI Specialist',
    'HR Director','Chief People Officer','People Partner',
    // Legal
    'Attorney','Lawyer','Counsel','General Counsel','Associate Counsel',
    'Senior Counsel','Deputy General Counsel','In-House Counsel',
    'Paralegal','Legal Assistant','Legal Coordinator','Legal Analyst',
    'Legal Operations Manager','Contracts Manager','Contract Specialist',
    'Compliance Officer','Compliance Specialist','Compliance Analyst',
    'Intellectual Property Attorney','Patent Attorney','Patent Agent',
    'Corporate Attorney','Litigation Attorney','Regulatory Counsel',
    'Legal Secretary','Court Reporter','Mediator','Arbitrator',
    // Operations & Admin
    'Operations Analyst','Operations Coordinator','Operations Specialist',
    'Business Operations Manager','Chief of Staff',
    'Executive Assistant','Personal Assistant','Administrative Assistant',
    'Office Administrator','Office Coordinator','Receptionist',
    'Secretary','Clerk','Filing Clerk','Data Entry Specialist',
    'Virtual Assistant','Executive Coordinator',
    // Consulting
    'Consultant','Senior Consultant','Managing Consultant','Principal Consultant',
    'Strategy Consultant','Management Consultant','Technology Consultant',
    'Business Consultant','Implementation Consultant','Functional Consultant',
    'Advisory Manager','Senior Advisor','Subject Matter Expert',
    // Healthcare & Medical — Hospital Leadership
    'Hospital Administrator','Healthcare Administrator','Hospital CEO',
    'Hospital CFO','Hospital COO','Hospital CIO','Hospital CMO',
    'Chief Medical Officer','Chief Nursing Officer','Chief Clinical Officer',
    'Chief Quality Officer','Chief Patient Experience Officer',
    'Chief Pharmacy Officer','Chief Wellness Officer',
    'Vice President of Medical Affairs','Vice President of Nursing',
    'Vice President of Patient Care Services','Vice President of Clinical Operations',
    'VP of Quality and Safety','VP of Population Health',
    'Medical Director','Associate Medical Director','Assistant Medical Director',
    'Clinical Director','Nursing Director','Director of Nursing',
    'Director of Patient Services','Director of Patient Experience',
    'Director of Quality Assurance','Director of Quality Improvement',
    'Director of Infection Control','Director of Risk Management',
    'Director of Case Management','Director of Social Services',
    'Director of Rehabilitation','Director of Behavioral Health',
    'Director of Emergency Services','Director of Surgical Services',
    'Director of Perioperative Services','Director of Critical Care',
    'Director of Respiratory Care','Director of Radiology',
    'Director of Laboratory Services','Director of Pathology',
    'Director of Pharmacy','Director of Food and Nutrition Services',
    'Director of Environmental Services','Director of Plant Operations',
    'Director of Health Information Management','Director of HIM',
    'Director of Medical Records','Director of Revenue Cycle',
    'Director of Patient Access','Director of Admissions',
    'Director of Volunteer Services','Director of Pastoral Care',
    'Director of Medical Education','Director of Graduate Medical Education',
    // Hospital — Physicians & Surgeons
    'Physician','Doctor','MD','DO','Attending Physician','Staff Physician',
    'Hospitalist','Nocturnist','Intensivist','Internist',
    'Surgeon','General Surgeon','Trauma Surgeon','Vascular Surgeon',
    'Cardiothoracic Surgeon','Neurosurgeon','Orthopedic Surgeon',
    'Plastic Surgeon','Pediatric Surgeon','Transplant Surgeon',
    'Anesthesiologist','Cardiologist','Interventional Cardiologist',
    'Electrophysiologist','Cardiac Surgeon',
    'Dermatologist','Endocrinologist','Gastroenterologist',
    'Hepatologist','Hematologist','Hematologist/Oncologist',
    'Immunologist','Allergist','Infectious Disease Specialist',
    'Nephrologist','Neurologist','Neuroradiologist',
    'Obstetrician','Gynecologist','OB/GYN',
    'Maternal-Fetal Medicine Specialist','Reproductive Endocrinologist',
    'Oncologist','Medical Oncologist','Radiation Oncologist','Surgical Oncologist',
    'Ophthalmologist','Retina Specialist','Cornea Specialist',
    'Orthopedist','Sports Medicine Physician',
    'Otolaryngologist','ENT Specialist','ENT Surgeon',
    'Pathologist','Clinical Pathologist','Anatomical Pathologist',
    'Forensic Pathologist','Neuropathologist',
    'Pediatrician','Neonatologist','Pediatric Cardiologist',
    'Pediatric Neurologist','Pediatric Surgeon','Pediatric Intensivist',
    'Physiatrist','Physical Medicine and Rehabilitation Physician',
    'Psychiatrist','Child Psychiatrist','Geriatric Psychiatrist',
    'Addiction Psychiatrist','Consultation-Liaison Psychiatrist',
    'Pulmonologist','Critical Care Physician','Pulmonary/Critical Care',
    'Radiologist','Interventional Radiologist','Diagnostic Radiologist',
    'Nuclear Medicine Physician','Radiation Therapist',
    'Rheumatologist','Urologist','Geriatrician',
    'Palliative Care Physician','Hospice Physician','Pain Management Specialist',
    'Emergency Medicine Physician','ER Doctor','ER Physician',
    'Family Medicine Physician','Primary Care Physician',
    'Medical Examiner','Coroner',
    'Chief of Staff','Chief of Medicine','Chief of Surgery',
    'Chief of Pediatrics','Chief of Psychiatry','Chief of Radiology',
    'Chief of Emergency Medicine','Chief of Anesthesia',
    'Department Chair','Department Chief','Section Chief',
    'Medical Staff President','Physician Advisor',
    // Hospital — Residents & Fellows
    'Resident','Resident Physician','Medical Resident',
    'Chief Resident','Senior Resident','Junior Resident',
    'PGY-1','PGY-2','PGY-3','PGY-4','PGY-5',
    'Fellow','Clinical Fellow','Research Fellow',
    'Cardiology Fellow','Oncology Fellow','GI Fellow',
    'Pulmonary/Critical Care Fellow','Infectious Disease Fellow',
    'Medical Student','Clinical Clerk','Extern',
    // Hospital — Advanced Practice Providers
    'Nurse Practitioner','NP','Family Nurse Practitioner','FNP',
    'Adult-Gerontology Nurse Practitioner','Pediatric Nurse Practitioner',
    'Psychiatric Nurse Practitioner','Acute Care Nurse Practitioner',
    'Neonatal Nurse Practitioner','Womens Health Nurse Practitioner',
    'Physician Assistant','PA-C','Surgical PA','Emergency PA',
    'Orthopedic PA','Cardiology PA','Neurology PA',
    'Certified Registered Nurse Anesthetist','CRNA',
    'Certified Nurse Midwife','CNM',
    'Clinical Nurse Specialist','CNS',
    // Hospital — Nursing
    'Nurse','Registered Nurse','RN','BSN','MSN',
    'Licensed Practical Nurse','LPN','Licensed Vocational Nurse','LVN',
    'Certified Nursing Assistant','CNA','Patient Care Technician','PCT',
    'Charge Nurse','Staff Nurse','Float Nurse','Travel Nurse','Agency Nurse',
    'Nurse Manager','Nurse Supervisor','Nurse Educator','Nurse Navigator',
    'Nurse Coordinator','Nurse Consultant','Nurse Researcher',
    'Clinical Nurse Leader','Nursing Supervisor','Nursing Instructor',
    'Director of Nursing','DON','Assistant Director of Nursing','ADON',
    'ICU Nurse','NICU Nurse','PICU Nurse','CCU Nurse',
    'ER Nurse','Emergency Room Nurse','Trauma Nurse',
    'OR Nurse','Operating Room Nurse','Perioperative Nurse',
    'PACU Nurse','Pre-Op Nurse','Post-Op Nurse','Recovery Room Nurse',
    'Labor and Delivery Nurse','L&D Nurse','Postpartum Nurse','Mother-Baby Nurse',
    'Med-Surg Nurse','Medical-Surgical Nurse','Telemetry Nurse',
    'Oncology Nurse','Infusion Nurse','Chemotherapy Nurse',
    'Dialysis Nurse','Renal Nurse','Nephrology Nurse',
    'Cardiac Nurse','Cardiology Nurse','Cath Lab Nurse',
    'Endoscopy Nurse','GI Lab Nurse',
    'Psychiatric Nurse','Mental Health Nurse','Behavioral Health Nurse',
    'Pediatric Nurse','School Nurse','Public Health Nurse',
    'Wound Care Nurse','Ostomy Nurse','Skin Care Nurse',
    'Infection Control Nurse','Infection Preventionist',
    'Quality Improvement Nurse','Patient Safety Nurse',
    'Case Manager Nurse','Utilization Review Nurse','Discharge Planner',
    'Triage Nurse','Telephone Triage Nurse','Nurse Hotline',
    'Home Health Nurse','Hospice Nurse','Palliative Care Nurse',
    'Transplant Nurse Coordinator','Organ Procurement Coordinator',
    'Clinical Nurse Manager','Unit Manager','Floor Manager',
    'House Supervisor','Nursing House Supervisor','Night Supervisor',
    // Hospital — Allied Health & Therapy
    'Physical Therapist','PT','DPT','Senior Physical Therapist',
    'Physical Therapy Assistant','PTA',
    'Occupational Therapist','OT','OTR','Senior Occupational Therapist',
    'Occupational Therapy Assistant','OTA','COTA',
    'Speech-Language Pathologist','SLP','Speech Therapist',
    'Respiratory Therapist','RT','RRT','Certified Respiratory Therapist',
    'Respiratory Care Practitioner','Pulmonary Function Technologist',
    'Recreational Therapist','Music Therapist','Art Therapist',
    'Child Life Specialist','Certified Child Life Specialist',
    'Athletic Trainer','Exercise Physiologist','Cardiac Rehab Specialist',
    'Rehabilitation Counselor','Vocational Rehabilitation Counselor',
    // Hospital — Pharmacy
    'Pharmacist','PharmD','Clinical Pharmacist','Staff Pharmacist',
    'Pharmacy Manager','Pharmacy Director','Chief Pharmacist',
    'Pharmacy Supervisor','Pharmacy Coordinator',
    'Clinical Pharmacy Specialist','Oncology Pharmacist',
    'Critical Care Pharmacist','Emergency Medicine Pharmacist',
    'Infectious Disease Pharmacist','Pediatric Pharmacist',
    'Psychiatric Pharmacist','Ambulatory Care Pharmacist',
    'Pharmacy Technician','CPhT','Senior Pharmacy Technician',
    'Pharmacy Intern','Pharmacy Resident','Pharmacy Fellow',
    'IV Pharmacy Technician','Compounding Technician',
    // Hospital — Laboratory & Pathology
    'Medical Laboratory Scientist','MLS','Clinical Laboratory Scientist',
    'Medical Laboratory Technician','MLT','Lab Technician',
    'Laboratory Manager','Laboratory Supervisor','Lab Director',
    'Phlebotomist','Phlebotomy Technician','Blood Bank Technologist',
    'Histotechnologist','Histotechnician','Cytotechnologist',
    'Microbiologist','Clinical Microbiologist',
    'Chemistry Technologist','Hematology Technologist',
    'Molecular Diagnostics Technologist','Genetics Counselor',
    'Point-of-Care Testing Coordinator',
    // Hospital — Radiology & Imaging
    'Radiologic Technologist','RT(R)','X-Ray Technician',
    'CT Technologist','CT Technician','CT Scan Technologist',
    'MRI Technologist','MRI Technician',
    'Ultrasound Technologist','Sonographer','Diagnostic Medical Sonographer',
    'Mammography Technologist','Mammographer',
    'Nuclear Medicine Technologist','PET/CT Technologist',
    'Interventional Radiology Technologist','Cath Lab Technologist',
    'Radiation Therapist','Dosimetrist','Medical Physicist',
    'PACS Administrator','Radiology Information Systems Analyst',
    'Radiology Manager','Radiology Supervisor','Lead Technologist',
    // Hospital — Surgical & Perioperative
    'Surgical Technologist','Surgical Tech','Scrub Tech',
    'Certified Surgical Technologist','CST',
    'Sterile Processing Technician','Central Sterile Technician',
    'Sterile Processing Manager','SPD Supervisor',
    'Surgical First Assistant','Certified Surgical First Assistant',
    'Perfusionist','Cardiovascular Perfusionist',
    'Anesthesia Technician','Anesthesia Technologist',
    'OR Coordinator','Surgical Scheduler','Perioperative Coordinator',
    'OR Manager','Perioperative Manager','Surgical Services Manager',
    // Hospital — Emergency & Critical Care
    'Emergency Medical Technician','EMT','EMT-Basic','EMT-Paramedic',
    'Paramedic','Flight Paramedic','Critical Care Paramedic',
    'Flight Nurse','Transport Nurse','Critical Care Transport Nurse',
    'ED Technician','Emergency Department Technician','ER Tech',
    'Monitor Technician','Telemetry Technician','EKG Technician',
    'Critical Care Technician',
    // Hospital — Behavioral Health
    'Psychiatrist','Psychologist','Clinical Psychologist','Neuropsychologist',
    'Licensed Clinical Social Worker','LCSW',
    'Licensed Professional Counselor','LPC',
    'Licensed Marriage and Family Therapist','LMFT',
    'Licensed Mental Health Counselor','LMHC',
    'Behavioral Health Technician','Psychiatric Technician',
    'Behavioral Health Specialist','Mental Health Specialist',
    'Substance Abuse Counselor','Addiction Counselor','CADC',
    'Peer Support Specialist','Recovery Coach',
    'Psychiatric Nurse Practitioner','Psychiatric PA',
    // Hospital — Social Services & Case Management
    'Social Worker','MSW','Medical Social Worker','Hospital Social Worker',
    'Case Manager','RN Case Manager','Social Work Case Manager',
    'Utilization Review Specialist','Utilization Management Nurse',
    'Discharge Planner','Transition of Care Coordinator',
    'Patient Advocate','Patient Representative','Patient Liaison',
    'Community Health Worker','Health Navigator','Patient Navigator',
    'Interpreter','Medical Interpreter','Language Services Coordinator',
    // Hospital — Nutrition & Food Services
    'Dietitian','Registered Dietitian','RD','RDN',
    'Clinical Dietitian','Renal Dietitian','Pediatric Dietitian',
    'Nutrition Support Dietitian','Oncology Dietitian',
    'Diet Technician','Dietary Aide','Dietary Manager',
    'Food Service Director','Food Service Manager','Food Service Supervisor',
    'Executive Chef','Head Cook','Kitchen Manager',
    // Hospital — Support Services & Administration
    'Patient Access Representative','Registration Clerk','Admissions Clerk',
    'Unit Secretary','Unit Clerk','Ward Clerk','Health Unit Coordinator',
    'Medical Records Clerk','Medical Records Technician',
    'Health Information Management Specialist','HIM Specialist',
    'Medical Transcriptionist','Medical Scribe',
    'Medical Coder','Certified Professional Coder','CPC',
    'Medical Biller','Billing Specialist','Revenue Cycle Specialist',
    'Patient Financial Counselor','Financial Navigator',
    'Insurance Verification Specialist','Prior Authorization Specialist',
    'Credentialing Specialist','Medical Staff Coordinator',
    'Risk Manager','Patient Safety Officer','Quality Coordinator',
    'Compliance Officer','Privacy Officer','HIPAA Officer',
    'Biomedical Engineer','Biomedical Equipment Technician','BMET',
    'Clinical Engineer','Healthcare IT Specialist',
    'EHR Analyst','Epic Analyst','Cerner Analyst','Clinical Informaticist',
    'Health Informatics Specialist','Clinical Informatics Director',
    'Materials Manager','Supply Chain Coordinator',
    'Environmental Services Manager','EVS Supervisor','Housekeeper',
    'Facilities Manager','Plant Operations Manager','Maintenance Supervisor',
    'Security Officer','Security Director','Safety Officer',
    'Chaplain','Pastoral Care Coordinator','Spiritual Care Provider',
    'Volunteer Coordinator','Gift Shop Manager',
    'Guest Services Representative','Concierge',
    'Transport Aide','Patient Transporter','Orderly',
    'Morgue Attendant','Autopsy Technician',
    // Hospital — Clinical Research
    'Clinical Research Coordinator','CRC','Research Coordinator',
    'Clinical Research Associate','CRA','Clinical Monitor',
    'Clinical Research Nurse','Research Nurse',
    'Principal Investigator','Co-Investigator','Sub-Investigator',
    'Clinical Trial Manager','Clinical Operations Manager',
    'Regulatory Affairs Specialist','IRB Coordinator',
    'Research Assistant','Research Associate','Research Scientist',
    'Biostatistician','Epidemiologist','Outcomes Researcher',
    // Hospital — Education & Training
    'Medical Educator','Clinical Educator','Nurse Educator',
    'Simulation Center Director','Simulation Technician',
    'Residency Program Director','Residency Coordinator',
    'Fellowship Program Director','GME Coordinator',
    'Continuing Medical Education Coordinator','CME Director',
    'Staff Development Coordinator','Clinical Instructor',
    'Preceptor','Student Coordinator','Clinical Placement Coordinator',
    // Veterinary (keeping for completeness)
    'Veterinarian','Veterinary Technician',
    // Education & Academia
    'Professor','Associate Professor','Assistant Professor','Adjunct Professor',
    'Lecturer','Senior Lecturer','Instructor','Teaching Assistant',
    'Teacher','Elementary Teacher','Middle School Teacher','High School Teacher',
    'Special Education Teacher','Substitute Teacher','Tutor',
    'Principal','Vice Principal','Dean','Associate Dean','Provost',
    'Academic Advisor','Guidance Counselor','School Counselor',
    'Librarian','Media Specialist','Curriculum Developer',
    'Research Associate','Research Fellow','Postdoctoral Researcher',
    'Research Assistant','Lab Manager','Lab Director',
    'Department Chair','Department Head',
    'Superintendent','School Administrator','Registrar',
    // Creative & Media
    'Writer','Author','Editor','Senior Editor','Managing Editor','Editor-in-Chief',
    'Journalist','Reporter','Correspondent','Columnist','Critic',
    'Producer','Executive Producer','Associate Producer','Line Producer',
    'Director','Film Director','Casting Director',
    'Cinematographer','Camera Operator','Sound Engineer','Audio Engineer',
    'Music Producer','Composer','Musician','DJ',
    'Actor','Voice Actor','Model','Talent Agent',
    'Production Manager','Production Coordinator','Production Assistant',
    'Stage Manager','Set Designer','Costume Designer','Makeup Artist',
    'Broadcast Engineer','News Anchor','TV Host','Podcast Host',
    // Government & Public Sector
    'Governor','Mayor','Senator','Representative','Councilmember',
    'City Manager','City Planner','Urban Planner',
    'Policy Analyst','Policy Advisor','Legislative Assistant',
    'Government Affairs Director','Lobbyist',
    'Diplomat','Ambassador','Foreign Service Officer',
    'Intelligence Analyst','Special Agent','FBI Agent','CIA Officer',
    'Police Officer','Detective','Sheriff','Fire Chief','Firefighter',
    'Military Officer','Captain','Lieutenant','Sergeant','Colonel','General',
    'Judge','Magistrate','Prosecutor','Public Defender',
    // Nonprofit
    'Executive Director','Deputy Director','Program Director',
    'Program Manager','Program Coordinator','Program Officer',
    'Development Director','Development Manager','Development Officer',
    'Fundraiser','Grant Writer','Major Gifts Officer',
    'Volunteer Coordinator','Outreach Coordinator','Community Organizer',
    'Advocacy Director','Campaign Director',
    // Trades & Skilled Labor
    'Electrician','Plumber','Carpenter','Welder','Mechanic',
    'HVAC Technician','Pipefitter','Mason','Roofer','Painter',
    'Foreman','Superintendent','Construction Worker','General Contractor',
    'Architect','Landscape Architect','Interior Designer',
    'Civil Engineer','Structural Engineer','Mechanical Engineer',
    'Chemical Engineer','Environmental Engineer','Industrial Engineer',
    'Surveyor','Inspector','Building Inspector','Safety Inspector',
    // Real Estate & Property
    'Real Estate Agent','Realtor','Real Estate Broker',
    'Leasing Agent','Property Manager','Asset Manager',
    'Real Estate Developer','Appraiser','Mortgage Broker','Loan Officer',
    // Supply Chain & Logistics
    'Supply Chain Analyst','Logistics Coordinator','Logistics Manager',
    'Procurement Specialist','Purchasing Agent','Buyer','Senior Buyer',
    'Inventory Manager','Distribution Manager','Fleet Manager',
    'Import/Export Specialist','Customs Broker','Freight Broker',
    // Science & Research
    'Scientist','Research Scientist','Senior Research Scientist','Principal Scientist',
    'Biologist','Chemist','Physicist','Geologist','Ecologist',
    'Biochemist','Microbiologist','Geneticist','Epidemiologist',
    'Environmental Scientist','Marine Biologist','Zoologist',
    'Materials Scientist','Food Scientist',
    'Laboratory Technician','Research Technician',
    // General / Cross-functional
    'Coordinator','Senior Coordinator','Specialist','Senior Specialist',
    'Administrator','Analyst','Senior Analyst','Lead Analyst',
    'Associate','Senior Associate','Lead','Principal',
    'Advisor','Senior Advisor','Strategist',
    'Architect','Planner','Developer','Engineer',
    'Technician','Technologist','Operator',
    'Supervisor','Team Lead','Team Leader','Group Lead',
    'Head of Engineering','Head of Design','Head of Product','Head of Marketing',
    'Head of Sales','Head of Operations','Head of HR','Head of Finance',
    'Head of Legal','Head of Data','Head of Growth','Head of Content',
    'Head of Partnerships','Head of Customer Success','Head of IT',
    'Head of Security','Head of Compliance','Head of Analytics',
    'Head of Research','Head of Strategy','Head of Innovation',
    'Head of Communications','Head of Brand','Head of Talent',
    // Ownership / Board
    'Founder','Co-Founder','Owner','Co-Owner','Proprietor',
    'Partner','Senior Partner','Managing Partner','Junior Partner',
    'Board Member','Board Chair','Board Director','Trustee',
    'Chairman','Chairwoman','Chairperson','Vice Chair',
    'Investor','Angel Investor','Venture Partner',
    'Intern','Summer Intern','Fellow','Apprentice','Trainee','Volunteer',
    'Freelancer','Independent Consultant','Contractor','Self-Employed',
    'Retired','Emeritus Professor','Professor Emeritus'
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
      input.closest('.card').style.zIndex = '10';
    }

    function hide() {
      dropdown.classList.remove('open');
      dropdown.innerHTML = '';
      items = [];
      activeIdx = -1;
      input.closest('.card').style.zIndex = '';
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

  // ── Technique 3: Bicubic upscale + unsharp mask ──
  // Cache processed images so re-opening is instant
  const enhancedCache = {};

  function enhanceImage(srcImg, idx) {
    if (enhancedCache[idx]) return enhancedCache[idx];

    const targetW = srcImg.naturalWidth * 2;
    const targetH = srcImg.naturalHeight * 2;

    // First pass: upscale 2x with high-quality interpolation
    const c1 = document.createElement('canvas');
    c1.width = targetW;
    c1.height = targetH;
    const ctx1 = c1.getContext('2d');
    ctx1.imageSmoothingEnabled = true;
    ctx1.imageSmoothingQuality = 'high';
    ctx1.drawImage(srcImg, 0, 0, targetW, targetH);

    // Second pass: apply unsharp mask via 3x3 sharpen kernel
    try {
      const imgData = ctx1.getImageData(0, 0, targetW, targetH);
      const sharpened = applySharpen(imgData, 0.4);
      ctx1.putImageData(sharpened, 0, 0);
    } catch (e) {
      // CORS or other issue — just use the upscaled version
      console.log('Sharpen failed:', e);
    }

    const dataUrl = c1.toDataURL('image/jpeg', 0.92);
    enhancedCache[idx] = dataUrl;
    return dataUrl;
  }

  // 3x3 sharpen kernel: subtle sharpen with strength control
  function applySharpen(imageData, strength) {
    const w = imageData.width;
    const h = imageData.height;
    const src = imageData.data;
    const out = new Uint8ClampedArray(src);

    // Kernel: identity + (sharpen - identity) * strength
    // Sharpen: [0,-1,0; -1,5,-1; 0,-1,0]
    // Blended: center = 1 + 4*strength, neighbors = -strength
    const c = 1 + 4 * strength;
    const n = -strength;

    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const i = (y * w + x) * 4;
        for (let ch = 0; ch < 3; ch++) { // R,G,B only, skip alpha
          const v =
            src[i + ch] * c +
            src[i - 4 + ch] * n +
            src[i + 4 + ch] * n +
            src[i - w * 4 + ch] * n +
            src[i + w * 4 + ch] * n;
          out[i + ch] = v < 0 ? 0 : v > 255 ? 255 : v;
        }
      }
    }

    return new ImageData(out, w, h);
  }

  document.querySelectorAll('.card-img-wrap').forEach(wrap => {
    wrap.addEventListener('click', function() {
      const img = this.querySelector('img');
      const idx = this.dataset.imgIdx;
      const displayNum = parseInt(idx) + 1;

      // Use enhanced version if image is loaded, fallback to original
      if (img.complete && img.naturalWidth > 0) {
        lightboxImg.src = enhanceImage(img, idx);
      } else {
        lightboxImg.src = img.src;
      }

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
  window.emailResults = function() {
    const text = buildResults();
    const subject = encodeURIComponent('Face Directory - Completed Labels');
    const body = encodeURIComponent(text);
    const mailtoUrl = 'mailto:' + EMAIL + '?subject=' + subject + '&body=' + body;

    // Copy to clipboard first as a reliable fallback
    navigator.clipboard.writeText(text).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    });

    // Try mailto — detect failure via blur/focus timing
    let mailtoWorked = false;
    window.addEventListener('blur', function onBlur() {
      mailtoWorked = true;
      window.removeEventListener('blur', onBlur);
    });

    window.location.href = mailtoUrl;

    // If still here after 1s with no blur, mailto didn't open anything
    setTimeout(() => {
      if (!mailtoWorked) {
        showFallbackOverlay();
      }
    }, 1000);
  };

  // ── Fallback overlay when mailto fails ──
  function showFallbackOverlay() {
    const overlay = document.getElementById('fallback-overlay');
    overlay.classList.add('open');
    document.getElementById('fallback-email').textContent = EMAIL;
  }

  window.closeFallback = function() {
    document.getElementById('fallback-overlay').classList.remove('open');
  };

  // Keep for backwards compat with updateState calls
  function updateEmailHref() {}

  // ── Toast notification ──
  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  }

  updateState();

  // ══════════════════════════════════════════════
  // SECRET: Triple-click title → password → photobook
  // ══════════════════════════════════════════════

  // ── Triple-click detector on h1 ──
  let clickCount = 0;
  let clickTimer = null;
  document.querySelector('.header h1').addEventListener('click', function() {
    clickCount++;
    clearTimeout(clickTimer);
    if (clickCount >= 3) {
      clickCount = 0;
      showPasswordModal();
    }
    clickTimer = setTimeout(() => { clickCount = 0; }, 600);
  });

  // ── Password modal ──
  function showPasswordModal() {
    const modal = document.getElementById('pw-modal');
    const input = document.getElementById('pw-input');
    const error = document.getElementById('pw-error');
    error.textContent = '';
    input.value = '';
    modal.classList.add('open');
    setTimeout(() => input.focus(), 100);
  }

  window.submitPassword = function() {
    const input = document.getElementById('pw-input');
    const card = document.getElementById('pw-card');
    const error = document.getElementById('pw-error');

    if (input.value === 'ahmchealth') {
      document.getElementById('pw-modal').classList.remove('open');
      document.getElementById('admin-panel').classList.add('open');
    } else {
      error.textContent = 'Incorrect password';
      card.classList.remove('shake');
      void card.offsetWidth; // force reflow
      card.classList.add('shake');
    }
  };

  window.closeAdminPanel = function() {
    document.getElementById('admin-panel').classList.remove('open');
  };

  window.showPasteLoad = function() {
    closeAdminPanel();
    const modal = document.getElementById('paste-modal');
    document.getElementById('paste-error').textContent = '';
    document.getElementById('paste-textarea').value = '';
    modal.classList.add('open');
    setTimeout(() => document.getElementById('paste-textarea').focus(), 100);
  };

  window.closePasteModal = function() {
    document.getElementById('paste-modal').classList.remove('open');
  };

  window.loadPastedData = function() {
    const text = document.getElementById('paste-textarea').value;
    const errorEl = document.getElementById('paste-error');

    if (!text.trim()) {
      errorEl.textContent = 'Please paste some data first';
      return;
    }

    // Parse format: "#01  Name: Foo Bar  |  Position: Title"
    const lineRe = /^#(\d{1,3})\s+Name:\s*(.*?)\s*\|\s*Position:\s*(.*?)$/;
    const lines = text.split(/\r?\n/);
    let parsed = 0;
    const newData = {};

    for (const line of lines) {
      const m = line.match(lineRe);
      if (m) {
        const num = parseInt(m[1], 10);
        const idx = num - 1; // #01 -> idx 0
        if (idx >= 0 && idx < TOTAL) {
          const name = m[2].trim();
          const pos = m[3].trim();
          newData[idx] = {
            name: name === '(not filled)' ? '' : name,
            position: pos === '(not filled)' ? '' : pos
          };
          parsed++;
        }
      }
    }

    if (parsed === 0) {
      errorEl.textContent = 'Could not parse any entries. Check the format.';
      return;
    }

    // Merge into saved and persist
    Object.assign(saved, newData);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));

    // Update DOM inputs
    document.querySelectorAll('.card-fields input').forEach(input => {
      const idx = input.dataset.idx;
      const field = input.dataset.field;
      if (saved[idx] && saved[idx][field] !== undefined) {
        input.value = saved[idx][field];
      }
    });

    // Reset milestone tracking so we don't re-fire celebrations
    shownMilestones.clear();
    confettiFired = true; // suppress confetti on bulk load

    updateState();
    closePasteModal();
    showToast('Loaded ' + parsed + ' entries');
  };

  // Enter key in password field
  document.getElementById('pw-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') submitPassword();
    if (e.key === 'Escape') document.getElementById('pw-modal').classList.remove('open');
  });

  // Click backdrop to close
  document.getElementById('pw-modal').addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('open');
  });

  // ── Photobook generator ──
  let photobookDataUrl = null;

  window.generatePhotobook = function() {
    // ── Technique 1: 2x DPI for retina/print quality ──
    const DPI = 2;
    const COLS = 2;
    const CANVAS_W = 1200 * DPI;
    const PAD = 40 * DPI;
    const COL_W = (CANVAS_W - PAD * 3) / COLS;
    const PHOTO_SIZE = 220 * DPI; // also bumped from 180 -> 220
    const CELL_H = 280 * DPI;
    const HEADER_H = 120 * DPI;
    const ROWS = Math.ceil(TOTAL / COLS);
    const CANVAS_H = HEADER_H + ROWS * CELL_H + PAD;

    const canvas = document.createElement('canvas');
    canvas.width = CANVAS_W;
    canvas.height = CANVAS_H;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // White background
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    // Header
    ctx.fillStyle = '#1A1A1A';
    ctx.font = '700 ' + (42 * DPI) + 'px Georgia, serif';
    ctx.textAlign = 'center';
    ctx.fillText('Staff Directory', CANVAS_W / 2, 70 * DPI);

    // Subtitle line
    ctx.fillStyle = '#999';
    ctx.font = '400 ' + (16 * DPI) + 'px sans-serif';
    const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    ctx.fillText(date, CANVAS_W / 2, 98 * DPI);

    // Header divider
    ctx.strokeStyle = '#DDD';
    ctx.lineWidth = 1 * DPI;
    ctx.beginPath();
    ctx.moveTo(PAD, HEADER_H - 5 * DPI);
    ctx.lineTo(CANVAS_W - PAD, HEADER_H - 5 * DPI);
    ctx.stroke();

    ctx.textAlign = 'left';

    // Draw each person
    for (let i = 0; i < TOTAL; i++) {
      const col = i % COLS;
      const row = Math.floor(i / COLS);
      const x = PAD + col * (COL_W + PAD);
      const y = HEADER_H + row * CELL_H + 20 * DPI;

      // Get the image element from DOM
      const imgEl = document.querySelector('#card-' + i + ' img');

      // Draw face photo with rounded corners via clipping
      ctx.save();
      const photoX = x;
      const photoY = y;
      const r = 12 * DPI;
      ctx.beginPath();
      ctx.moveTo(photoX + r, photoY);
      ctx.lineTo(photoX + PHOTO_SIZE - r, photoY);
      ctx.quadraticCurveTo(photoX + PHOTO_SIZE, photoY, photoX + PHOTO_SIZE, photoY + r);
      ctx.lineTo(photoX + PHOTO_SIZE, photoY + PHOTO_SIZE - r);
      ctx.quadraticCurveTo(photoX + PHOTO_SIZE, photoY + PHOTO_SIZE, photoX + PHOTO_SIZE - r, photoY + PHOTO_SIZE);
      ctx.lineTo(photoX + r, photoY + PHOTO_SIZE);
      ctx.quadraticCurveTo(photoX, photoY + PHOTO_SIZE, photoX, photoY + PHOTO_SIZE - r);
      ctx.lineTo(photoX, photoY + r);
      ctx.quadraticCurveTo(photoX, photoY, photoX + r, photoY);
      ctx.closePath();
      ctx.clip();

      if (imgEl && imgEl.complete) {
        ctx.drawImage(imgEl, photoX, photoY, PHOTO_SIZE, PHOTO_SIZE);
      } else {
        ctx.fillStyle = '#E8E4DC';
        ctx.fillRect(photoX, photoY, PHOTO_SIZE, PHOTO_SIZE);
      }
      ctx.restore();

      // Text area to the right of the photo
      const textX = x + PHOTO_SIZE + 24 * DPI;
      const textMaxW = COL_W - PHOTO_SIZE - 24 * DPI;
      const displayNum = String(i + 1).padStart(2, '0');

      // Card number
      ctx.fillStyle = '#AAA';
      ctx.font = '500 ' + (14 * DPI) + 'px sans-serif';
      ctx.fillText('#' + displayNum, textX, y + 22 * DPI);

      // Name
      const name = (saved[i] && saved[i].name && saved[i].name.trim()) || '(not filled)';
      ctx.fillStyle = '#1A1A1A';
      ctx.font = '700 ' + (26 * DPI) + 'px sans-serif';
      wrapText(ctx, name, textX, y + 58 * DPI, textMaxW, 32 * DPI);

      // Position
      const pos = (saved[i] && saved[i].position && saved[i].position.trim()) || '(not filled)';
      // Calculate where name ended to position title below
      const nameLines = getWrappedLines(ctx, name, textMaxW);
      const nameEndY = y + 58 * DPI + (nameLines - 1) * 32 * DPI;
      ctx.fillStyle = '#666';
      ctx.font = '400 ' + (18 * DPI) + 'px sans-serif';
      wrapText(ctx, pos, textX, nameEndY + 34 * DPI, textMaxW, 24 * DPI);

      // Row divider (except last row)
      if (col === COLS - 1 || i === TOTAL - 1) {
        ctx.strokeStyle = '#EEE';
        ctx.lineWidth = 1 * DPI;
        ctx.beginPath();
        ctx.moveTo(PAD, y + CELL_H - 18 * DPI);
        ctx.lineTo(CANVAS_W - PAD, y + CELL_H - 18 * DPI);
        ctx.stroke();
      }
    }

    // Convert to image and show preview
    photobookDataUrl = canvas.toDataURL('image/png');
    const previewImg = document.getElementById('photobook-img');
    previewImg.src = photobookDataUrl;
    document.getElementById('photobook-overlay').classList.add('open');
  };

  // Text wrapping helper
  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = text.split(' ');
    let line = '';
    let lineY = y;
    for (let w = 0; w < words.length; w++) {
      const testLine = line + (line ? ' ' : '') + words[w];
      if (ctx.measureText(testLine).width > maxWidth && line) {
        ctx.fillText(line, x, lineY);
        line = words[w];
        lineY += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, lineY);
  }

  // Count wrapped lines helper
  function getWrappedLines(ctx, text, maxWidth) {
    const words = text.split(' ');
    let line = '';
    let lines = 1;
    for (let w = 0; w < words.length; w++) {
      const testLine = line + (line ? ' ' : '') + words[w];
      if (ctx.measureText(testLine).width > maxWidth && line) {
        line = words[w];
        lines++;
      } else {
        line = testLine;
      }
    }
    return lines;
  }

  // ── Download + close ──
  window.downloadPhotobook = function() {
    if (!photobookDataUrl) return;
    const a = document.createElement('a');
    a.href = photobookDataUrl;
    a.download = 'staff-directory.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  window.closePhotobook = function() {
    document.getElementById('photobook-overlay').classList.remove('open');
  };

  // Escape to close photobook
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (document.getElementById('photobook-overlay').classList.contains('open')) {
        closePhotobook();
      }
    }
  });

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
