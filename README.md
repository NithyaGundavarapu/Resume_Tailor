# Resume Tailor AI

A small Streamlit app that uses Claude to rewrite your resume so it matches a
specific job description — reordering and rewording to hit the JD's
keywords while keeping every fact truthful.

## How it works

1. **Your Resume** — paste it in or upload a `.txt` file.
2. **Job Description** — paste the JD you're applying to.
3. **Tailored Result** — Claude streams back a rewritten resume in Markdown,
   which you can review and download.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### API key

The app reads your Anthropic API key from the environment — there's no key
input in the UI. Set it one of these ways before running:

- **Environment variable**

  ```powershell
  $env:ANTHROPIC_API_KEY = "sk-ant-..."
  ```

- **Streamlit secrets** — create `.streamlit/secrets.toml` (gitignored) with:

  ```toml
  ANTHROPIC_API_KEY = "sk-ant-..."
  ```

See `.env.example` for the expected variable name.

## Running

```bash
streamlit run app.py
```

## CLI script

`tailor.py` is a non-interactive version of the same idea: it reads
`resume.txt` and `jd.txt` from the project root and writes `tailored_resume.md`.
Those two input files are gitignored (they'll contain your personal
resume/JD text) — create your own before running:

```bash
python tailor.py
```

## Project structure

- `app.py` — the Streamlit UI.
- `tailor.py` — CLI equivalent, reads `resume.txt` / `jd.txt` from disk.
- `requirements.txt` — Python dependencies.
