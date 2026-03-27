# Facebook Ad Library Pipeline (Python)

A production-like end-to-end pipeline that:

1. Scrapes ads from the Meta/Facebook Ad Library using Playwright
2. Cleans and normalizes ad data
3. Analyzes each ad with OpenAI (hook type, emotional trigger, format)
4. Rewrites each ad into RSOC-style text
5. Exports final generated content to CSV

---

## Project Structure

```text
.
├── analyzer.py
├── cleaner.py
├── generator.py
├── main.py
├── requirements.txt
├── run_pipeline.bat
├── scraper.py
├── .env.example
├── README.md
└── data/
    ├── raw.json
    ├── clean.json
    ├── analysis.json
    ├── generated.json
    └── final.csv
```

---

## Prerequisites

- Python 3.10+
- Windows PowerShell / Command Prompt (for `.bat` launcher)
- Internet connection
- OpenAI API key

---

## Setup

1. Clone or download this project.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright Chromium:

   ```bash
   python -m playwright install chromium
   ```

5. Configure environment variables:

   ```bash
   copy .env.example .env
   ```

   Open `.env` and set:

   ```env
   OPENAI_API_KEY=your_real_openai_key
   ```

---

## Run Manually

### Option A: Keyword passed in command line

```bash
python main.py --keyword dating --limit 50
```

### Option B: Prompt input

```bash
python main.py
```

Then enter keyword when prompted.

---

## One-Click Windows Launcher

Double-click:

- `run_pipeline.bat`

or from CMD:

```bat
run_pipeline.bat dating
```

The launcher will:

- Create `.venv` if missing
- Install/update dependencies
- Install Playwright Chromium
- Create `.env` from `.env.example` if needed
- Ask for keyword if not provided
- Run `main.py`

---

## Pipeline Stages

`main.py` executes in this order:

1. **Scrape** (`scraper.py`) → `data/raw.json`
2. **Clean** (`cleaner.py`) → `data/clean.json`
3. **Analyze** (`analyzer.py`) → `data/analysis.json`
4. **Generate RSOC** (`generator.py`) → `data/generated.json`
5. **Export CSV** (`generator.py`) → `data/final.csv`

---

## Output Files

After a successful run, expect:

- `data/raw.json`: raw scraped records
- `data/clean.json`: normalized + deduplicated records
- `data/analysis.json`: ad + AI analysis fields
- `data/generated.json`: ad + RSOC rewrite
- `data/final.csv`: columns `original_text`, `rsoc_text`

---

## Troubleshooting

### 1) `OPENAI_API_KEY is missing`
- Ensure `.env` exists and contains `OPENAI_API_KEY=...`
- Confirm no surrounding quotes or trailing spaces

### 2) Playwright browser errors
- Re-run:
  ```bash
  python -m playwright install chromium
  ```
- Ensure antivirus/proxy is not blocking browser downloads

### 3) Scraper returns few or zero ads
- Meta Ad Library DOM can change often; selectors are defensive but may still break
- Try another keyword and rerun
- Increase runtime and retry later

### 4) API rate or network errors
- The pipeline logs and gracefully continues with fallback values where possible
- Re-run when network/API is stable

---

## Notes

- This project is for research/analysis workflows.
- Respect Meta platform terms and applicable laws when scraping data.
