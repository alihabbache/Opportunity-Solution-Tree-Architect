# inputs/ — OST Architect input documents

The pipeline reads files from this folder to build your Opportunity Solution Tree.

---

## Structure

| Path | Purpose | Required |
|---|---|---|
| `okr.md` | Your OKR or business outcome statement | Yes |
| `interviews/` | User interview notes (`.md`, `.txt`, `.docx`, `.pdf`) | Yes |
| `context/` | Mission, vision, product goals (`.md`, `.txt`, `.docx`, `.pdf`) | No |

---

## Getting started

Template / example files are provided with a `.example` extension:

- `okr.md.example` — copy to `okr.md` and edit
- `interviews/interview_1.md.example` — copy and rename, add your own notes
- `context/product_goals.md.example` — copy to `product_goals.md` and edit

```bash
cp inputs/okr.md.example inputs/okr.md
cp inputs/interviews/interview_1.md.example inputs/interviews/my_interview.md
cp inputs/context/product_goals.md.example inputs/context/product_goals.md
```

---

## Privacy & security

> **Do not commit real interview notes or OKR documents to this repository.**

- `inputs/okr.md`, `inputs/interviews/*.md`, and `inputs/context/*.md` are in `.gitignore` and will not be tracked by git.
- The `.example` template files ARE tracked — they contain only fictional placeholder data.
- All input text is sent to the Groq API for processing. Do not include participant names, email addresses, or other personally identifiable information (PII).
- For sensitive data, trigger the pipeline via the web form (data goes directly to GitHub Actions — never stored in git).

---

## File format limits

- Supported formats: `.md`, `.txt`, `.docx`, `.pdf`
- Maximum file size: 5 MB per file
