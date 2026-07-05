# OST Architect — Build Plan

## Top-Level Overview

**Goal:** Build a GitHub-native, zero-cost Opportunity Solution Tree (OST) Architect that maps business outcomes to technical execution using a multi-agent AI pipeline.

**Approach:**
- Input files (Markdown, Word, PDF) or pasted text are processed by a Python multi-agent orchestrator
- The orchestrator calls the Google Gemini API through a 4-agent chain
- Output is a static interactive D3.js collapsible tree published to GitHub Pages
- The pipeline runs on GitHub Actions (free tier), triggered manually or on file push
- No server, no database, no paid hosting — GitHub is the entire platform

**Scope:** Personal POC for a Product Manager. Prioritize working software over polish.

**Non-goals:**
- User authentication / multi-user support
- Real-time collaboration
- Mobile optimization
- Production-grade error handling

---

## Architecture Overview

```
[Input Layer]
  Markdown files / .docx / PDF / Web paste form
        |
        v
[GitHub Actions Pipeline]
  Primary Agent (Discovery Mapper)
    |-- Subagent A (Outcome Tracker)
    |-- Subagent B (Pain Point Synthesizer)
    |-- Subagent C (Experiment Ideator)
        |
        v
  Output: tree_data.json
        |
        v
[GitHub Pages]
  index.html — D3.js interactive collapsible tree
  (color-coded by agent layer, click to expand/collapse)
```

---

## Repository Structure (Target)

```
ost-architect/
├── .github/
│   └── workflows/
│       └── generate-ost.yml          # GitHub Actions pipeline
├── inputs/
│   ├── okr.md                        # OKR / business outcome doc
│   ├── interviews/                   # User interview notes (.md, .docx, .pdf)
│   └── context/                      # Mission, vision, product goals (optional)
├── agents/
│   ├── orchestrator.py               # Primary Agent: Discovery Mapper
│   ├── outcome_tracker.py            # Subagent A
│   ├── pain_point_synthesizer.py     # Subagent B
│   └── experiment_ideator.py         # Subagent C
├── utils/
│   ├── file_parser.py                # Handles .md, .docx, .pdf ingestion
│   └── gemini_client.py              # Gemini API wrapper
├── web/
│   ├── index.html                    # D3.js tree viewer (GitHub Pages root)
│   └── tree_data.json                # Generated output consumed by D3
├── requirements.txt
├── README.md
└── ost-architect-plan.md             # This file
```

---

## Sub-Tasks

---

### Sub-Task 1 — Repository Scaffold & GitHub Setup

**Intent:**
Create the full repository structure, README, and GitHub Pages configuration so the project is immediately hostable and navigable on GitHub.

**Expected Outcomes:**
- Repository exists at `github.com/<your-username>/ost-architect`
- GitHub Pages is enabled, serving from the `web/` folder or `docs/` root
- README explains the project, how to add inputs, and how to trigger the pipeline
- All folder structure and placeholder files are in place

**Todo List:**
1. Create the repository on GitHub (public, so Actions minutes are free)
2. Create the full folder structure as defined in the architecture above
3. Write `README.md` with: project description, folder guide, how to use, how to trigger
4. Add `.gitignore` (Python, env files, `.env`)
5. Add `requirements.txt` with initial dependencies: `google-generativeai`, `python-docx`, `pypdf2`, `markdown`
6. Enable GitHub Pages in repo Settings → Pages → set source to `web/` folder on `main` branch
7. Add a placeholder `web/index.html` and `web/tree_data.json` so Pages has something to serve immediately

**Relevant Context:**
- GitHub Pages serves static files — the `web/` folder is the only thing the browser sees
- `tree_data.json` is the contract between the Python pipeline and the D3 frontend
- Public repos get unlimited GitHub Actions minutes on the free plan

**Status:** [ ] pending

---

### Sub-Task 2 — File Parser Utility

**Intent:**
Build a single utility that accepts any supported file type and returns clean plain text, so all agents receive a uniform string input regardless of the original format.

**Expected Outcomes:**
- `utils/file_parser.py` correctly extracts text from `.md`, `.docx`, and `.pdf` files
- A single function `parse_file(filepath) -> str` is the public interface
- Graceful handling of unsupported file types with a clear error message

**Todo List:**
1. Implement Markdown parser: read file, strip Markdown syntax, return plain text
2. Implement Word (.docx) parser using `python-docx`: extract all paragraphs as plain text
3. Implement PDF parser using `PyPDF2`: extract text from all pages
4. Implement a dispatcher function `parse_file(filepath)` that detects extension and routes to the correct parser
5. Write a simple test script `utils/test_parser.py` with sample files to verify each format works

**Relevant Context:**
- `inputs/` folder is where all source files live
- Agents only receive strings — file format complexity is fully hidden in this layer
- Keep encoding handling robust (UTF-8, fallback to latin-1)

**Status:** [ ] pending

---

### Sub-Task 3 — Gemini API Client Wrapper

**Intent:**
Create a reusable, clean wrapper around the Google Gemini API so all agents call one consistent interface, and the API key is managed securely via GitHub Secrets.

**Expected Outcomes:**
- `utils/gemini_client.py` exposes a single function `ask(prompt: str, system: str) -> str`
- API key is read from environment variable `GEMINI_API_KEY` (set as GitHub Secret)
- Model is configurable (default: `gemini-1.5-pro`)
- Basic retry logic on rate limit errors

**Todo List:**
1. Install and configure `google-generativeai` SDK
2. Implement `ask(prompt, system_instruction)` function using `gemini-1.5-pro`
3. Read `GEMINI_API_KEY` from `os.environ` — never hardcoded
4. Add retry with exponential backoff (3 attempts) for `429 Resource Exhausted` errors
5. Add a `.env.example` file documenting required environment variables
6. Document how to set the secret in GitHub: Settings → Secrets → `GEMINI_API_KEY`

**Relevant Context:**
- GitHub Actions can inject secrets as environment variables — see Sub-Task 5 for workflow config
- Gemini 1.5 Pro has a 1M token context window — more than sufficient for PM docs
- The free API quota on Gemini is generous enough for a POC even without the Pro membership

**Status:** [ ] pending

---

### Sub-Task 4 — The Four Agents (Python)

**Intent:**
Implement the 4-agent chain in Python. Each agent has a focused prompt and a clear input/output contract. The orchestrator assembles the final tree JSON.

**Expected Outcomes:**
- `agents/outcome_tracker.py` returns a structured dict with the top-level business outcome, key metric, and alignment to mission/vision if context docs are provided
- `agents/pain_point_synthesizer.py` returns a list of distinct customer opportunity branches parsed from interview notes
- `agents/experiment_ideator.py` takes one opportunity branch and returns a list of testable feature hypotheses
- `agents/orchestrator.py` calls all three subagents in sequence, assembles a nested `tree_data.json` output, and writes it to `web/tree_data.json`

**Todo List:**

**Subagent A — Outcome Tracker:**
1. Define system prompt: role is a business analyst locking in the north star metric
2. Input: parsed text from `inputs/okr.md` + optional `inputs/context/` files
3. Output JSON: `{ "outcome": str, "metric": str, "alignment": str }`

**Subagent B — Pain Point Synthesizer:**
1. Define system prompt: role is a UX researcher extracting distinct opportunity areas
2. Input: parsed text from all files in `inputs/interviews/`
3. Output JSON: `[ { "id": str, "opportunity": str, "evidence": str }, ... ]`

**Subagent C — Experiment Ideator:**
1. Define system prompt: role is a product manager generating testable hypotheses
2. Input: one opportunity branch from Subagent B output
3. Output JSON per branch: `[ { "hypothesis": str, "experiment": str, "signal": str }, ... ]`
4. Called once per branch (loop in orchestrator)

**Orchestrator — Discovery Mapper:**
1. Load and parse all input files using `file_parser.py`
2. Call Subagent A → get outcome node
3. Call Subagent B → get opportunity branches
4. Loop: call Subagent C for each branch → get hypotheses
5. Assemble nested tree structure compatible with D3 hierarchy format
6. Write output to `web/tree_data.json`

**D3 Tree JSON format:**
```json
{
  "name": "<outcome>",
  "type": "outcome",
  "children": [
    {
      "name": "<opportunity>",
      "type": "opportunity",
      "children": [
        {
          "name": "<hypothesis>",
          "type": "experiment"
        }
      ]
    }
  ]
}
```

**Relevant Context:**
- Each agent is stateless — it receives a prompt and returns a string that is then parsed as JSON
- Ask Gemini to respond in strict JSON using explicit instructions in the system prompt
- The `type` field on each node drives D3 color-coding by layer

**Status:** [ ] pending

---

### Sub-Task 5 — GitHub Actions Workflow

**Intent:**
Wire the entire pipeline into a GitHub Actions workflow so it runs automatically on push (when input files change) or can be triggered manually from the GitHub UI.

**Expected Outcomes:**
- `.github/workflows/generate-ost.yml` runs the full agent pipeline end-to-end
- Workflow triggers on: manual dispatch (`workflow_dispatch`) AND push to `inputs/**`
- `GEMINI_API_KEY` is injected from GitHub Secrets
- Generated `web/tree_data.json` is committed back to the repo automatically
- GitHub Pages serves the updated tree within ~1 minute of a run completing

**Todo List:**
1. Create `.github/workflows/generate-ost.yml`
2. Set triggers: `workflow_dispatch` + `on: push: paths: ['inputs/**']`
3. Add steps: checkout repo, set up Python 3.11, install requirements, run `agents/orchestrator.py`
4. Inject `GEMINI_API_KEY` secret as environment variable
5. Add a commit step: use `git add web/tree_data.json && git commit && git push` to persist output
6. Add a job summary step that prints the generated outcome and branch count to the Actions log

**Relevant Context:**
- `workflow_dispatch` allows manual trigger from GitHub UI — no code push needed
- The commit-back step requires `contents: write` permission on the workflow token
- GitHub Pages will auto-redeploy when `web/` files change on `main`

**Status:** [ ] pending

---

### Sub-Task 6 — D3.js Interactive Tree Frontend

**Intent:**
Build the static `web/index.html` that reads `tree_data.json` and renders it as an interactive, collapsible D3.js tree — color-coded by agent layer, with click-to-expand/collapse nodes.

**Expected Outcomes:**
- `web/index.html` loads `tree_data.json` and renders a full-width collapsible tree
- Three distinct colors: one per layer (outcome = blue, opportunity = orange, experiment = green)
- Clicking a node collapses/expands its children
- Node tooltips show full text on hover (important for long hypothesis text)
- Works offline from the file system (relative paths, no CDN dependencies that require internet... or use CDN with fallback)
- Page title and header show "OST Architect" branding

**Todo List:**
1. Set up `index.html` with D3.js v7 loaded from CDN
2. Implement `fetch('tree_data.json')` to load tree data on page load
3. Implement D3 collapsible tree layout (horizontal left-to-right layout works best for OST)
4. Color-code nodes by `type` field: outcome / opportunity / experiment
5. Implement click handler for collapse/expand with smooth transition animation
6. Add tooltip on hover showing full node text
7. Add a top navigation bar with: title "OST Architect", last updated timestamp from JSON, link to GitHub repo
8. Make the tree SVG pan-and-zoomable (D3 zoom behavior)
9. Test with sample `tree_data.json` before wiring to real agent output

**Relevant Context:**
- `tree_data.json` is written by the orchestrator — the frontend is purely a reader
- D3 v7 collapsible tree examples are well-documented; the Mike Bostock collapsible tree is the canonical reference
- Horizontal tree layout (root on left, leaves on right) maps naturally to the OST mental model

**Status:** [ ] pending

---

### Sub-Task 7 — Web Paste Form (GitHub Pages Input UI)

**Intent:**
Add a simple single-page form to GitHub Pages where you can paste OKR text, interview notes, and context directly in the browser — without committing files to the repo. The form submits to a GitHub Actions workflow via the GitHub API.

**Expected Outcomes:**
- A second page `web/input.html` with three text areas: OKR/Outcome, Interview Notes, Context (optional)
- On submit, the form calls the GitHub API to trigger `workflow_dispatch` with the pasted text as inputs
- The user sees a confirmation message with a link to the Actions run
- No backend server required — the GitHub REST API is called directly from the browser using a Personal Access Token stored in the form

**Todo List:**
1. Create `web/input.html` with three labeled `<textarea>` fields and a Submit button
2. Add a PAT (Personal Access Token) input field — user enters their GitHub PAT once; it is stored in `localStorage` (never sent anywhere except GitHub's own API)
3. On submit: call `POST /repos/{owner}/{repo}/actions/workflows/generate-ost.yml/dispatches` with the pasted content as `inputs`
4. Update `generate-ost.yml` to accept `workflow_dispatch` inputs: `okr_text`, `interview_text`, `context_text`
5. Update `orchestrator.py` to check for env vars `INPUT_OKR_TEXT` etc. and use them if set, otherwise fall back to reading files from `inputs/`
6. Add a link to `input.html` from the main `index.html` nav bar

**Relevant Context:**
- GitHub `workflow_dispatch` supports up to 10 custom string inputs — sufficient for our 3 text fields
- The PAT needs `repo` and `actions:write` scope
- This is a power-user feature — the file-based approach in `inputs/` remains the primary path

**Status:** [ ] pending

---

### Sub-Task 8 — Sample Data & End-to-End Test

**Intent:**
Provide realistic sample input files so anyone cloning the repo can run the full pipeline immediately without writing their own OKR or interview notes. Validate the complete end-to-end flow works.

**Expected Outcomes:**
- `inputs/okr.md` contains a realistic PM-style OKR example
- `inputs/interviews/` contains 2-3 sample interview note files (one `.md`, one `.docx`, one `.pdf`)
- Running `python agents/orchestrator.py` locally produces a valid `web/tree_data.json`
- Opening `web/index.html` in a browser shows a fully rendered, interactive OST tree
- The GitHub Actions workflow runs to completion on a fresh clone

**Todo List:**
1. Write `inputs/okr.md` — realistic OKR for a fictional SaaS product (e.g., "Increase weekly active users by 20% in Q3")
2. Write `inputs/interviews/interview_1.md` — 3-5 fictional user quotes with pain points
3. Create `inputs/interviews/interview_2.docx` and `inputs/interviews/interview_3.pdf` as sample files
4. Write `inputs/context/product_goals.md` — brief mission/vision/product goals doc
5. Run full pipeline locally and confirm `tree_data.json` is valid JSON matching D3 schema
6. Open `web/index.html` and visually verify tree renders correctly
7. Trigger GitHub Actions manually and confirm the commit-back step works

**Relevant Context:**
- Sample data is critical for a GitHub POC — it lets anyone evaluate the project without setup
- The `.docx` and `.pdf` samples prove the file parser works on non-Markdown formats

**Status:** [ ] pending

---

## Key Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Hosting | GitHub Pages | Free, zero config |
| Compute | GitHub Actions | Free 2,000 min/month on public repos |
| AI Provider | Google Gemini 1.5 Pro | User has existing membership; generous free API quota |
| Language | Python 3.11 | Best LLM tooling ecosystem |
| Visualization | D3.js v7 collapsible tree | Interactive, open source, no backend required |
| Input formats | Markdown, .docx, .pdf, web form | Covers all real PM workflow inputs |
| Agent pattern | Sequential chain via orchestrator | Simple, debuggable, no framework overhead for POC |
| No LangChain | Direct Gemini SDK calls | Reduces dependencies and complexity for a POC |

---

## Environment Variables / Secrets Required

| Variable | Where set | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | GitHub Secrets | Authenticates Gemini API calls in Actions |
| GitHub PAT | Browser localStorage (input.html) | Triggers workflow_dispatch from web form |
