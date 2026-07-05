# 🌳 Opportunity Solution Tree (OST) Architect

A zero-cost, GitHub-native AI pipeline that maps business outcomes directly to technical execution — visually.

Built for Product Managers. Runs entirely on GitHub Actions + GitHub Pages. Powered by Google Gemini.

---

## What It Does

You drop your OKR doc and user interview notes into the `inputs/` folder (or paste them via the web form), push to GitHub, and within minutes you get an **interactive, collapsible Opportunity Solution Tree** published to your GitHub Pages URL.

```
Business Outcome (OKR)
  └── Customer Opportunity (from interviews)
        └── Experiment / Feature Hypothesis
        └── Experiment / Feature Hypothesis
  └── Customer Opportunity
        └── Experiment / Feature Hypothesis
```

---

## How It Works — The 4-Agent Pipeline

| Agent | Role | Input | Output |
|---|---|---|---|
| 🎯 **Discovery Mapper** (Orchestrator) | Coordinates the full pipeline | All input files | `tree_data.json` |
| 📊 **Outcome Tracker** (Subagent A) | Locks in the north-star business metric | `inputs/okr.md` + `inputs/context/` | Top-level outcome node |
| 🗣️ **Pain Point Synthesizer** (Subagent B) | Parses interviews into opportunity branches | `inputs/interviews/` | Customer opportunity nodes |
| 💡 **Experiment Ideator** (Subagent C) | Generates testable hypotheses per opportunity | Each opportunity branch | Experiment leaf nodes |

---

## Quick Start

### 1. Fork this repo
Click **Fork** on GitHub. Keep it public (free Actions minutes).

### 2. Add your Gemini API key as a GitHub Secret
- Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
- Name: `GEMINI_API_KEY`
- Value: your key from [aistudio.google.com](https://aistudio.google.com)

### 3. Add your inputs
Drop files into:
- `inputs/okr.md` — your OKR or business outcome statement
- `inputs/interviews/` — user interview notes (`.md`, `.docx`, or `.pdf`)
- `inputs/context/` — optional mission/vision/product goals docs

### 4. Run the pipeline
- Go to **Actions** → **Generate OST** → **Run workflow**
- Or just push a change to any file in `inputs/` — it triggers automatically

### 5. View your tree
Open your GitHub Pages URL:
`https://<your-username>.github.io/Opportunity-Solution-Tree-Architect/`

---

## Web Paste Form (No file commits needed)
Visit `https://<your-username>.github.io/Opportunity-Solution-Tree-Architect/input.html`

Paste your OKR and interview notes directly in the browser. Enter your GitHub PAT to trigger the pipeline remotely.

---

## Folder Structure

```
├── .github/workflows/
│   └── generate-ost.yml        # GitHub Actions pipeline
├── inputs/
│   ├── okr.md                  # Your OKR / business outcome
│   ├── interviews/             # User interview notes
│   └── context/                # Mission, vision, product goals (optional)
├── agents/
│   ├── orchestrator.py         # Primary agent — assembles the tree
│   ├── outcome_tracker.py      # Subagent A
│   ├── pain_point_synthesizer.py # Subagent B
│   └── experiment_ideator.py   # Subagent C
├── utils/
│   ├── file_parser.py          # Parses .md, .docx, .pdf → plain text
│   └── gemini_client.py        # Gemini API wrapper
├── web/
│   ├── index.html              # D3.js interactive OST tree
│   ├── input.html              # Web paste form
│   └── tree_data.json          # Generated tree (auto-updated by pipeline)
├── requirements.txt
└── .env.example
```

---

## Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | GitHub Secret | Authenticates Gemini API in Actions |
| GitHub PAT | Browser localStorage (input.html only) | Triggers workflow from web form |

> ⚠️ Never commit your API key or PAT to the repository.

---

## Local Development

```bash
# Clone
git clone https://github.com/alihabbache/Opportunity-Solution-Tree-Architect
cd Opportunity-Solution-Tree-Architect

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the pipeline locally
python agents/orchestrator.py

# Open the tree
open web/index.html
```

---

## Stack

- **AI**: Google Gemini 1.5 Pro (via `google-generativeai` SDK)
- **Compute**: GitHub Actions (free tier)
- **Hosting**: GitHub Pages (free)
- **Visualization**: D3.js v7
- **Language**: Python 3.11
- **Input formats**: Markdown, Word (.docx), PDF

---

*Built as a zero-cost PM side project. No servers. No databases. No monthly bills.*
