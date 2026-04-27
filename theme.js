// Shared color toggle: persists across pages via localStorage.
// Self-injects the toggle button + panel if not already present.
(function () {
  const defaultBgColor = '#ffffff';
  const defaultFontColor = '#111111';

  function applyEarlyTheme(bg, fg) {
    let css = '';
    if (bg) css += 'body{background-color:' + bg + ' !important;}';
    if (fg) {
      css += 'body{color:' + fg + ' !important;}';
      css += '.sidebar{border-right-color:' + fg + ' !important;}';
      css += '.post-date,.sidebar li,.post-link{color:' + fg + ' !important;}';
      css += '.game-toggle{background:' + fg + ' !important;}';
      css += '.email-signup-input::placeholder{color:' + fg + ' !important;opacity:0.6;}';
    }
    let s = document.getElementById('early-theme');
    if (!css) { if (s) s.remove(); return; }
    if (!s) {
      s = document.createElement('style');
      s.id = 'early-theme';
      document.head.appendChild(s);
    }
    s.textContent = css;
  }

  function rgbToHex(rgb) {
    const m = rgb.match(/\d+/g);
    if (!m) return rgb;
    const [r, g, b] = m.map(Number);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }

  function updateBackgroundColor(color) {
    document.body.style.setProperty('background-color', color, 'important');
    localStorage.setItem('customBgColor', color);
    applyEarlyTheme(color, localStorage.getItem('customFontColor'));
  }

  function updateFontColor(color) {
    document.body.style.setProperty('color', color, 'important');
    document.querySelectorAll('.post-date, .sidebar li, .post-link').forEach(el => {
      el.style.setProperty('color', color, 'important');
    });
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.style.setProperty('border-right-color', color, 'important');
    const toggle = document.querySelector('.game-toggle');
    if (toggle) toggle.style.setProperty('background-color', color, 'important');
    localStorage.setItem('customFontColor', color);
    applyEarlyTheme(localStorage.getItem('customBgColor'), color);
  }

  const updateBackgroundColorFromBox = (box) =>
    updateBackgroundColor(rgbToHex(getComputedStyle(box).backgroundColor));
  const updateFontColorFromBox = (box) =>
    updateFontColor(rgbToHex(getComputedStyle(box).backgroundColor));

  function refreshRandomColors() {
    const rand = () => '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
    for (let i = 1; i <= 4; i++) {
      const bg = document.querySelector(`.bg-random-${i}`);
      const fg = document.querySelector(`.font-random-${i}`);
      if (bg) bg.style.backgroundColor = rand();
      if (fg) fg.style.backgroundColor = rand();
    }
  }

  function resetColors() {
    localStorage.removeItem('customBgColor');
    localStorage.removeItem('customFontColor');
    document.body.style.removeProperty('background-color');
    document.body.style.removeProperty('color');
    document.querySelectorAll('.post-date, .sidebar li, .post-link').forEach(el => {
      el.style.removeProperty('color');
    });
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.style.removeProperty('border-right-color');
    const toggle = document.querySelector('.game-toggle');
    if (toggle) toggle.style.removeProperty('background-color');
    applyEarlyTheme(null, null);
  }

  function toggleColorGame() {
    document.getElementById('colorGame').classList.toggle('hidden');
  }

  function loadSavedColors() {
    const bg = localStorage.getItem('customBgColor');
    const fg = localStorage.getItem('customFontColor');
    if (bg) updateBackgroundColor(bg);
    if (fg) updateFontColor(fg);
  }

  function injectUI() {
    if (document.querySelector('.game-toggle')) return; // already present (e.g. index.html)

    const btn = document.createElement('button');
    btn.className = 'game-toggle';
    btn.addEventListener('click', toggleColorGame);

    const panel = document.createElement('div');
    panel.className = 'color-game hidden';
    panel.id = 'colorGame';
    panel.innerHTML = `
      <div class="color-controls">
        <div class="color-row">
          <div class="preset-color" data-bg="#ffffff" style="background:#ffffff" title="White"></div>
          <div class="preset-color" data-bg="#000000" style="background:#000000" title="Black"></div>
          <div class="preset-color bg-random-1" data-bg-random></div>
          <div class="preset-color bg-random-2" data-bg-random></div>
          <div class="preset-color bg-random-3" data-bg-random></div>
          <div class="preset-color bg-random-4" data-bg-random></div>
        </div>
        <div class="color-row">
          <div class="preset-color" data-fg="#000000" style="background:#000000" title="Black"></div>
          <div class="preset-color" data-fg="#ffffff" style="background:#ffffff" title="White"></div>
          <div class="preset-color font-random-1" data-fg-random></div>
          <div class="preset-color font-random-2" data-fg-random></div>
          <div class="preset-color font-random-3" data-fg-random></div>
          <div class="preset-color font-random-4" data-fg-random></div>
        </div>
      </div>
      <button class="reset-btn" data-action="reset">Reset</button>
      <button class="reset-btn" data-action="refresh" style="margin-left:0.5rem;">Refresh</button>
    `;

    panel.addEventListener('click', (e) => {
      const t = e.target;
      if (t.dataset.bg) updateBackgroundColor(t.dataset.bg);
      else if (t.dataset.fg) updateFontColor(t.dataset.fg);
      else if (t.hasAttribute('data-bg-random')) updateBackgroundColorFromBox(t);
      else if (t.hasAttribute('data-fg-random')) updateFontColorFromBox(t);
      else if (t.dataset.action === 'reset') resetColors();
      else if (t.dataset.action === 'refresh') refreshRandomColors();
    });

    document.body.prepend(panel);
    document.body.prepend(btn);
  }

  // Expose for inline handlers in index.html (keeps existing behaviour intact)
  Object.assign(window, {
    toggleColorGame, updateBackgroundColor, updateFontColor,
    updateBackgroundColorFromBox, updateFontColorFromBox,
    refreshRandomColors, resetColors,
  });

  function init() {
    injectUI();
    refreshRandomColors();
    loadSavedColors();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
