const API_BASE   = "http://localhost:5001";

const wordInput  = document.getElementById("wordInput");
const searchBtn  = document.getElementById("searchBtn");
const resultArea = document.getElementById("result");
const serverDot  = document.getElementById("server-dot");
const serverLbl  = document.getElementById("server-status");
const themeBtn   = document.getElementById("themeToggle");
const toggleIcon = document.getElementById("toggleIcon");
const html       = document.documentElement;

// ── Theme toggle ──────────────────────────────────────────────
let theme = localStorage.getItem("dict-theme") || "dark";

function applyTheme(t) {
  theme = t;
  html.setAttribute("data-theme", t);
  toggleIcon.textContent = t === "dark" ? "☀" : "☾";
  localStorage.setItem("dict-theme", t);
}

applyTheme(theme);

themeBtn.addEventListener("click", () => {
  applyTheme(theme === "dark" ? "light" : "dark");
});

// ── Health check ──────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      serverDot.className = "server-dot online";
      serverLbl.textContent = "online";
    } else throw new Error();
  } catch {
    serverDot.className = "server-dot offline";
    serverLbl.textContent = "offline";
  }
}

// ── Render helpers ────────────────────────────────────────────
function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function showLoading() {
  resultArea.innerHTML = `
    <div class="loading">
      <div class="dot-bounce">
        <span>·</span><span>·</span><span>·</span>
      </div>
      looking up
    </div>`;
}

function showEntry(word, definition, source) {
  resultArea.innerHTML = `
    <div class="entry">
      <div class="entry-header">
        <span class="entry-index">01 · definition</span>
        <span class="entry-source ${source === "local" ? "local" : ""}">${esc(source)}</span>
      </div>
      <div class="entry-word">${esc(word)}</div>
      <div class="entry-rule"></div>
      <div class="entry-definition">${esc(definition)}</div>
    </div>`;
}

function showNotFound(word) {
  resultArea.innerHTML = `
    <div class="not-found">
      <div class="not-found-word">${esc(word)}</div>
      <div class="not-found-msg">— not found in local cache or API</div>
    </div>`;
}

function showError(msg) {
  resultArea.innerHTML = `<div class="err-msg">⚠ ${esc(msg)}</div>`;
}

// ── Main lookup ───────────────────────────────────────────────
async function lookup() {
  const word = wordInput.value.trim();
  if (!word) {
    wordInput.focus();
    return;
  }

  showLoading();
  searchBtn.disabled = true;

  try {
    const res  = await fetch(`${API_BASE}/lookup?word=${encodeURIComponent(word)}`);
    const data = await res.json();

    if (data.status === "success") {
      showEntry(word, data.definition, data.source);
    } else if (data.status === "not_found") {
      showNotFound(word);
    } else {
      showError(data.error || "unknown error");
    }
  } catch {
    showError("could not reach the server — is it running?");
    serverDot.className = "server-dot offline";
    serverLbl.textContent = "offline";
  } finally {
    searchBtn.disabled = false;
  }
}

// ── Events ────────────────────────────────────────────────────
searchBtn.addEventListener("click", lookup);
wordInput.addEventListener("keydown", e => { if (e.key === "Enter") lookup(); });
wordInput.focus();

// ── Init ──────────────────────────────────────────────────────
checkHealth();