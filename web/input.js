const REPO_OWNER = "alihabbache";
const REPO_NAME  = "Opportunity-Solution-Tree-Architect";
const WORKFLOW_FILE = "generate-ost.yml";
const PAT_KEY = "ost_architect_pat";

// ── PAT persistence (sessionStorage — cleared on tab close) ───────────────
const patInput = document.getElementById("pat-input");

const saved = sessionStorage.getItem(PAT_KEY);
if (saved) patInput.value = saved;

document.getElementById("save-pat-btn").addEventListener("click", () => {
  const val = patInput.value.trim();
  if (!val) { alert("Enter a PAT first."); return; }
  sessionStorage.setItem(PAT_KEY, val);
  setStatus("PAT saved for this session.", "success");
});

document.getElementById("clear-pat-btn").addEventListener("click", () => {
  sessionStorage.removeItem(PAT_KEY);
  patInput.value = "";
  setStatus("PAT cleared.", "");
});

// ── Char counters ──────────────────────────────────────────────────────────
function wireCounter(textareaId, counterId) {
  const ta = document.getElementById(textareaId);
  const counter = document.getElementById(counterId);
  ta.addEventListener("input", () => {
    counter.textContent = ta.value.length;
  });
}
wireCounter("okr-text",       "okr-count");
wireCounter("interview-text", "interview-count");
wireCounter("context-text",   "context-count");

// ── Submit ─────────────────────────────────────────────────────────────────
document.getElementById("submit-btn").addEventListener("click", async () => {
  const pat       = patInput.value.trim();
  const okr       = document.getElementById("okr-text").value.trim();
  const interview = document.getElementById("interview-text").value.trim();
  const context   = document.getElementById("context-text").value.trim();

  if (!pat)       { setStatus("A GitHub PAT is required to trigger the pipeline.", "error"); return; }
  if (!okr)       { setStatus("OKR / Business Outcome text is required.", "error"); return; }
  if (!interview) { setStatus("User Interview Notes are required.", "error"); return; }

  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  setStatus("Triggering pipeline...", "");

  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${WORKFLOW_FILE}/dispatches`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + pat,
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: "main", inputs: { okr_text: okr, interview_text: interview, context_text: context } }),
    });

    if (response.status === 204) {
      setStatus("Pipeline triggered! Your tree will be ready in ~2 minutes.", "success");
      document.getElementById("run-link").style.display = "inline-block";
      sessionStorage.setItem(PAT_KEY, pat);
    } else {
      const body = await response.json().catch(() => ({}));
      setStatus("GitHub API error: " + (body.message || `HTTP ${response.status}`), "error");
    }
  } catch (err) {
    setStatus("Network error: " + err.message, "error");
  } finally {
    btn.disabled = false;
  }
});

// ── Helper ────────────────────────────────────────────────────────────────
function setStatus(msg, type) {
  const el = document.getElementById("status-msg");
  el.textContent = msg;
  el.className = type;
}
