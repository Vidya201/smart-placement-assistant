// Shared helpers + page logic. Every page loads this file and runs the block matching <body data-page="...">.
const API_BASE = location.port === "8000" ? "" : "http://127.0.0.1:8000";
const DEMO_STUDENT_ID = 1; // seeded demo student (no login in this version)

// Send a request to FastAPI and return parsed JSON, or throw an Error with a friendly message.
async function api(path, options = {}) {
  let res;
  try {
    res = await fetch(API_BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    throw new Error("Cannot reach the backend. Start it with: uvicorn main:app --reload");
  }
  let data = null;
  try { data = await res.json(); } catch (_) { /* no JSON body */ }
  if (!res.ok) {
    let detail = data && data.detail;
    if (Array.isArray(detail)) detail = detail.map(d => d.msg).join("; "); // Pydantic validation errors
    throw new Error(detail || `Request failed (HTTP ${res.status}).`);
  }
  return data;
}

// Tiny DOM helper. Uses textContent, so server data is never injected as HTML.
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) node.append(c);
  return node;
}

function showMessage(box, text, kind) {
  box.className = "msg " + kind;
  box.textContent = text;
  box.hidden = false;
}

const page = document.body.dataset.page;

/* ---------------- Home: API status ---------------- */
if (page === "home") {
  const status = document.getElementById("status");
  api("/")
    .then(d => showMessage(status, "Backend connected: " + d.message, "ok"))
    .catch(e => showMessage(status, e.message, "error"));
}

/* ---------------- Questions ---------------- */
if (page === "questions") {
  const list = document.getElementById("qlist");
  const detail = document.getElementById("detail");
  const catSel = document.getElementById("category");
  const diffSel = document.getElementById("difficulty");
  let selectedId = null;

  async function loadQuestions() {
    list.replaceChildren(el("li", { class: "empty" }, "Loading questions..."));
    const params = new URLSearchParams();
    if (catSel.value) params.set("category", catSel.value);
    if (diffSel.value) params.set("difficulty", diffSel.value);
    try {
      const questions = await api("/questions?" + params);
      // Fill the category filter once, from real data
      if (catSel.options.length === 1) {
        const all = await api("/questions");
        [...new Set(all.map(q => q.category))].forEach(c => catSel.append(new Option(c, c)));
      }
      if (!questions.length) {
        list.replaceChildren(el("li", { class: "empty" }, "No questions match these filters. Try clearing them."));
        return;
      }
      list.replaceChildren(...questions.map(q => {
        const btn = el("button", { class: "qitem", type: "button", "aria-pressed": String(q.question_id === selectedId),
            onclick: () => openQuestion(q.question_id) },
          el("span", {}, q.title, el("small", {}, q.category)),
          el("span", { class: "tag " + q.difficulty }, q.difficulty));
        return el("li", {}, btn);
      }));
    } catch (e) {
      list.replaceChildren(el("li", { class: "msg error" }, e.message));
    }
  }

  async function openQuestion(id) {
    selectedId = id;
    detail.replaceChildren(el("p", { class: "empty" }, "Loading question..."));
    list.querySelectorAll(".qitem").forEach(b => b.setAttribute("aria-pressed", "false"));
    try {
      const q = await api("/questions/" + id);
      list.querySelectorAll(".qitem").forEach(b => {
        if (b.textContent.startsWith(q.title)) b.setAttribute("aria-pressed", "true");
      });
      const answer = el("textarea", { id: "answer", rows: "3", placeholder: "Type the output your code prints for the sample input" });
      const result = el("div", { hidden: "" });
      const submitBtn = el("button", { type: "button" }, "Submit answer");
      const doneBtn = el("button", { type: "button", class: "secondary" }, "Mark as completed");

      async function send(body, btn) {
        btn.disabled = true;
        try {
          const r = await api("/attempts", { method: "POST", body: JSON.stringify({ student_id: DEMO_STUDENT_ID, question_id: id, ...body }) });
          showMessage(result, `${r.message} Score: ${r.score}`, r.completed ? "ok" : "error");
        } catch (e) { showMessage(result, e.message, "error"); }
        btn.disabled = false;
      }
      submitBtn.addEventListener("click", () => {
        if (!answer.value.trim()) return showMessage(result, "Type an answer first, or use Mark as completed.", "error");
        send({ submitted_answer: answer.value }, submitBtn);
      });
      doneBtn.addEventListener("click", () => send({ completed: true }, doneBtn));

      detail.replaceChildren(
        el("h2", {}, q.title),
        el("p", {}, el("span", { class: "tag " + q.difficulty }, q.difficulty), " ", el("span", { class: "empty" }, q.category)),
        el("p", {}, q.description),
        el("label", {}, "Sample input"), el("pre", {}, q.sample_input || "(none)"),
        el("label", {}, "Expected output format"), el("pre", {}, q.expected_output || "(none)"),
        el("label", { for: "answer" }, "Your answer"), answer,
        el("div", { class: "actions" }, submitBtn, doneBtn),
        result);
    } catch (e) {
      detail.replaceChildren(el("p", { class: "msg error" }, e.message));
    }
  }

  catSel.addEventListener("change", loadQuestions);
  diffSel.addEventListener("change", loadQuestions);
  loadQuestions();
}

/* ---------------- Progress ---------------- */
if (page === "progress") {
  const stats = document.getElementById("stats");
  const tbody = document.getElementById("recent");
  const err = document.getElementById("error");
  api(`/students/${DEMO_STUDENT_ID}/progress`).then(p => {
    const stat = (n, label) => el("div", { class: "card stat" }, el("b", {}, String(n)), el("span", {}, label));
    stats.replaceChildren(
      stat(`${p.questions_completed}/${p.total_questions}`, "questions completed"),
      stat(p.questions_attempted, "questions attempted"),
      stat(p.total_attempts, "total attempts"),
      stat(p.average_score + "%", "average score"));
    if (!p.recent_attempts.length) {
      tbody.replaceChildren(el("tr", {}, el("td", { colspan: "4", class: "empty" }, "No attempts yet. Open the Questions page and try one.")));
      return;
    }
    tbody.replaceChildren(...p.recent_attempts.map(a => el("tr", {},
      el("td", {}, a.title), el("td", {}, a.score + "%"),
      el("td", {}, a.completed ? "Completed" : "Not yet"),
      el("td", {}, new Date(a.attempted_at).toLocaleString()))));
  }).catch(e => showMessage(err, e.message, "error"));
}

/* ---------------- Chatbot ---------------- */
if (page === "chatbot") {
  const log = document.getElementById("log");
  const form = document.getElementById("chatform");
  const input = document.getElementById("message");

  function bubble(text, who) {
    log.append(el("div", { class: "bubble " + who }, text));
    log.scrollTop = log.scrollHeight;
  }
  async function ask(text) {
    text = text.trim();
    if (!text) return bubble("Please type a question first.", "bot");
    bubble(text, "user");
    input.value = "";
    try {
      const r = await api("/chat", { method: "POST", body: JSON.stringify({ message: text }) });
      bubble(r.reply, "bot");
    } catch (e) { bubble(e.message, "bot"); }
  }
  form.addEventListener("submit", e => { e.preventDefault(); ask(input.value); });
  document.querySelectorAll("[data-ask]").forEach(b => b.addEventListener("click", () => ask(b.dataset.ask)));
  bubble("Hi! Ask me about Python, REST APIs, FastAPI, MySQL or interview practice. This is a rule-based bot, not Generative AI.", "bot");
}
