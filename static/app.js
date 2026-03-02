/* ═══════════════════════════════════════════════════════════
   app.js — Frontend logic for News Semantic Summarizer
   ═══════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  // ── DOM refs ─────────────────────────────────────────
  const searchForm     = document.getElementById("search-form");
  const topicInput     = document.getElementById("search-topic");
  const modeSelect     = document.getElementById("search-mode");
  const queryInput     = document.getElementById("search-query");
  const searchBtn      = document.getElementById("search-btn");
  const btnText        = searchBtn.querySelector(".btn-text");
  const btnLoader      = searchBtn.querySelector(".btn-loader");

  const resultsArea    = document.getElementById("results-area");
  const summaryCard    = document.getElementById("summary-card");
  const summaryBadge   = document.getElementById("summary-badge");
  const summaryTopic   = document.getElementById("summary-topic");
  const summaryBody    = document.getElementById("summary-body");
  const summaryMeta    = document.getElementById("summary-meta");
  const articlesGrid   = document.getElementById("articles-grid");

  const errorArea      = document.getElementById("error-area");
  const errorMsg       = document.getElementById("error-msg");

  const topicsList     = document.getElementById("topics-list");
  const newTopicInput  = document.getElementById("new-topic-input");
  const addTopicBtn    = document.getElementById("add-topic-btn");
  const defaultMode    = document.getElementById("default-mode-select");
  const historyList    = document.getElementById("history-list");

  const sidebarToggle  = document.getElementById("sidebar-toggle");
  const sidebar        = document.getElementById("sidebar");

  // ── Sidebar toggle (mobile) ──────────────────────────
  sidebarToggle.addEventListener("click", () => sidebar.classList.toggle("open"));

  // Close sidebar on outside click (mobile)
  document.addEventListener("click", (e) => {
    if (window.innerWidth <= 900 && sidebar.classList.contains("open")) {
      if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
        sidebar.classList.remove("open");
      }
    }
  });

  // ── Helpers ──────────────────────────────────────────
  function showLoading() {
    btnText.style.display  = "none";
    btnLoader.style.display = "inline-flex";
    searchBtn.disabled = true;
  }
  function hideLoading() {
    btnText.style.display  = "inline";
    btnLoader.style.display = "none";
    searchBtn.disabled = false;
  }
  function showError(msg) {
    errorMsg.textContent = msg;
    errorArea.style.display = "block";
    resultsArea.style.display = "none";
  }
  function hideError() { errorArea.style.display = "none"; }

  function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  }

  // ── Search ───────────────────────────────────────────
  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const topic = topicInput.value.trim();
    const mode  = modeSelect.value;
    const query = queryInput.value.trim();
    if (!topic) return;

    showLoading();

    try {
      const params = new URLSearchParams({ topic, mode, query });
      const res = await fetch(`/api/search?${params}`);
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Something went wrong.");
        hideLoading();
        return;
      }

      // Summary
      summaryBadge.textContent = data.mode.toUpperCase();
      summaryTopic.textContent = data.topic;
      summaryBody.textContent  = data.summary;
      summaryMeta.textContent  = `${data.total_fetched} articles fetched · Top ${data.articles.length} used for summary`;

      // Re-trigger animation
      summaryCard.classList.remove("fade-in");
      void summaryCard.offsetWidth;
      summaryCard.classList.add("fade-in");

      // Articles
      articlesGrid.innerHTML = "";
      data.articles.forEach((a) => {
        const card = document.createElement("a");
        card.className = "article-card";
        card.href = a.url || "#";
        card.target = "_blank";
        card.rel = "noopener noreferrer";
        card.innerHTML = `
          <span class="article-title">${escapeHtml(a.title)}</span>
          <span class="article-source">${escapeHtml(a.source || "Unknown source")}</span>
          <span class="article-date">${formatDate(a.publishedAt)}</span>
        `;
        articlesGrid.appendChild(card);
      });

      resultsArea.style.display = "block";
      resultsArea.scrollIntoView({ behavior: "smooth", block: "start" });

      // Refresh sidebar
      loadHistory();
    } catch (err) {
      showError("Network error. Please check your connection.");
    } finally {
      hideLoading();
    }
  });

  // ── Topics ───────────────────────────────────────────
  async function loadTopics() {
    try {
      const res  = await fetch("/api/topics");
      const data = await res.json();
      renderTopics(data.topics || []);
    } catch (e) { /* silent */ }
  }

  function renderTopics(topics) {
    if (!topics.length) {
      topicsList.innerHTML = '<p class="empty-state">No saved topics yet</p>';
      return;
    }
    topicsList.innerHTML = "";
    topics.forEach((t) => {
      const chip = document.createElement("div");
      chip.className = "topic-chip";
      chip.innerHTML = `
        <span class="topic-name">${escapeHtml(t)}</span>
        <button class="remove-btn" title="Remove">✕</button>
      `;
      // Click topic name → fill search
      chip.querySelector(".topic-name").addEventListener("click", () => {
        topicInput.value = t;
        topicInput.focus();
        if (window.innerWidth <= 900) sidebar.classList.remove("open");
      });
      // Click remove
      chip.querySelector(".remove-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        deleteTopic(t);
      });
      topicsList.appendChild(chip);
    });
  }

  addTopicBtn.addEventListener("click", () => saveTopic());
  newTopicInput.addEventListener("keydown", (e) => { if (e.key === "Enter") saveTopic(); });

  async function saveTopic() {
    const t = newTopicInput.value.trim();
    if (!t) return;
    try {
      const res  = await fetch("/api/topics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: t }),
      });
      const data = await res.json();
      renderTopics(data.topics || []);
      newTopicInput.value = "";
    } catch (e) { /* silent */ }
  }

  async function deleteTopic(t) {
    try {
      const res  = await fetch("/api/topics", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: t }),
      });
      const data = await res.json();
      renderTopics(data.topics || []);
    } catch (e) { /* silent */ }
  }

  // ── Preferences ──────────────────────────────────────
  async function loadPreferences() {
    try {
      const res  = await fetch("/api/preferences");
      const data = await res.json();
      defaultMode.value = data.default_mode || "brief";
      modeSelect.value  = data.default_mode || "brief";
    } catch (e) { /* silent */ }
  }

  defaultMode.addEventListener("change", async () => {
    try {
      await fetch("/api/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ default_mode: defaultMode.value }),
      });
      modeSelect.value = defaultMode.value;
    } catch (e) { /* silent */ }
  });

  // ── History ──────────────────────────────────────────
  async function loadHistory() {
    try {
      const res  = await fetch("/api/history");
      const data = await res.json();
      renderHistory(data.history || []);
    } catch (e) { /* silent */ }
  }

  function renderHistory(items) {
    if (!items.length) {
      historyList.innerHTML = '<p class="empty-state">No searches yet</p>';
      return;
    }
    historyList.innerHTML = "";
    // Show newest first
    [...items].reverse().forEach((item) => {
      const el = document.createElement("div");
      el.className = "history-item";
      el.innerHTML = `
        <div class="history-topic">${escapeHtml(item.topic)}</div>
        <div>${escapeHtml(item.user_query || "")}</div>
        <div class="history-time">${formatDate(item.ts)} · ${item.mode}</div>
      `;
      el.addEventListener("click", () => {
        topicInput.value = item.topic;
        queryInput.value = item.user_query || "";
        modeSelect.value = item.mode || "brief";
        if (window.innerWidth <= 900) sidebar.classList.remove("open");
        topicInput.focus();
      });
      historyList.appendChild(el);
    });
  }

  // ── Utility ──────────────────────────────────────────
  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  // ── Init ─────────────────────────────────────────────
  loadTopics();
  loadPreferences();
  loadHistory();
});
