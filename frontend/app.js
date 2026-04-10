const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:5001"
  : "https://multi-thread-dictionary.onrender.com";
const wordInput  = document.getElementById("wordInput");
const searchBtn  = document.getElementById("searchbtn");
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
  if (toggleIcon) {
    toggleIcon.textContent = t === "dark" ? "☀" : "☾";
  }
  
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
  const lang = document.getElementById("langSelect").value; // Get selected lang
  
  if (!word) return;

  showLoading();
  searchBtn.disabled = true;

  try {
    // Pass the language to the backend
    const res = await fetch(`${API_BASE}/lookup?word=${encodeURIComponent(word)}&lang=${lang}`);
    const data = await res.json();

    if (data.status === "success") {
      showEntry(word, data.definition, data.source);
      addToHistory(word);
    } else if (data.status === "not_found") {
      showNotFound(word);
    }
  } catch {
    showError("Connection failed.");
  } finally {
    searchBtn.disabled = false;
  }
}
// ... (Keep existing API_BASE and checkHealth logic)

const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistory");

let searchHistory = JSON.parse(localStorage.getItem("dict-history")) || [];

// ── Enhanced Render Logic ─────────────────────────────────────
function updateHistoryUI() {
  historyList.innerHTML = searchHistory
    .map(word => `<li class="history-item" onclick="quickLookup('${word}')">${word}</li>`)
    .join('');
}

function addToHistory(word) {
  if (!searchHistory.includes(word)) {
    searchHistory.unshift(word);
    searchHistory = searchHistory.slice(0, 10); // Keep last 10
    localStorage.setItem("dict-history", JSON.stringify(searchHistory));
    updateHistoryUI();
  }
}

// Global function for sidebar clicks
window.quickLookup = (word) => {
  wordInput.value = word;
  lookup();
};

async function lookup() {
  const word = wordInput.value.trim();
  if (!word) return;

  showLoading();
  searchBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/lookup?word=${encodeURIComponent(word)}`);
    const data = await res.json();

    if (data.status === "success") {
      showEntry(word, data.definition, data.source);
      addToHistory(word); // Success! Add to history
    } else if (data.status === "not_found") {
      showNotFound(word);
    }
  } catch {
    showError("Connection failed.");
  } finally {
    searchBtn.disabled = false;
  }
}

clearHistoryBtn.addEventListener("click", () => {
  searchHistory = [];
  localStorage.removeItem("dict-history");
  updateHistoryUI();
});
async function setupAutocomplete() {
  const datalist = document.getElementById("wordSuggestions");
  // In a real distributed system, you'd fetch this from a /words endpoint
  // For now, let's assume you have a list of common words
  const commonWords = ["latency", "concurrency", "mutex", "protocol", "socket", "thread", "process", "cache", "load balancer", "replication", "sharding", "consistency", "availability", "partition tolerance", "scalability", "throughput", "bandwidth", "queue", "worker", "event loop", "asynchronous", "synchronous", "API", "endpoint", "microservice", "container", "orchestration", "virtualization", "cloud", "serverless", "database", "indexing", "query", "transaction", "rollback", "commit", "deadlock", "race condition", "idempotent", "caching", "load testing", "stress testing", "monitoring", "logging", "tracing", "debugging", "profiling", "optimization", "refactoring", "code review", "version control", "CI/CD", "devops"]; 
  
  datalist.innerHTML = commonWords
    .map(word => `<option value="${word}">`)
    .join('');
}


// ── Events ────────────────────────────────────────────────────
searchBtn.addEventListener("click", lookup);
wordInput.addEventListener("keydown", e => { if (e.key === "Enter") lookup(); });
wordInput.focus();

// ── Init ──────────────────────────────────────────────────────
updateHistoryUI();
checkHealth();
setupAutocomplete();
