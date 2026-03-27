# Facebook Ad Library Pipeline (Free Local-Only Version)

This project is a **fully free local-only** Python pipeline for collecting and processing Meta/Facebook Ad Library data.

✅ No OpenAI API usage  
✅ No API key required  
✅ Entire analysis and RSOC generation runs locally with rule/template logic

---

## What the Pipeline Does

The workflow runs in this exact order:

1. **Scrape** ads from Meta Ad Library (`scraper.py`) → `data/raw.json`
2. **Clean** and normalize records (`cleaner.py`) → `data/clean.json`
3. **Analyze** with local heuristic rules (`analyzer.py`) → `data/analysis.json`
4. **Generate** RSOC-style rewrites via local templates (`generator.py`) → `data/generated.json`
5. **Export** CSV (`generator.py`) → `data/final.csv`

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

## Local Analysis Rules (No AI API)

`analyzer.py` infers fields using keyword-based heuristics from `primary_text` + `headline`:

### `hook_type` examples
- **curiosity**: words like `secret`, `revealed`, `mistake`, `warning`
- **value**: words like `save`, `discount`, `cheap`
- **transformation**: phrases like `before/after`, `transform`
- fallback: `informational`

### `emotional_trigger` examples
- **fear**: `fear`, `risk`, `danger`, `urgent`
- **loneliness**: `lonely`, `alone`, `single`
- **anxiety**: `anxious`, `stress`, `worried`
- fallback: `neutral`

### `format` examples
- inferred from combinations of image/headline presence and copy length
- e.g. `image_headline_longcopy`, `image_text`, `text_only`, etc.

---

## Local RSOC Generation (No AI API)

`generator.py` builds a neutral RSOC-style paragraph using:
- original ad text
- rule-based analysis fields (`hook_type`, `emotional_trigger`, `format`)

Design rules:
- neutral, informational tone
- no aggressive CTA
- avoids promo words (e.g. `best`, `amazing`, `buy now`, `limited time`)
- targets ~60–80 words

---

## Prerequisites

- Python 3.10+
- Internet connection (for scraping + installing Playwright browser)
- Windows CMD/PowerShell (for `.bat` launcher)

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

> `requirements.txt` only includes local runtime dependency (`playwright`).

---

## Run the Pipeline

### Manual run (CLI)

```bash
python main.py --keyword dating --limit 50
```

### Manual run (prompt keyword)

```bash
python main.py
```

---

## One-Click Windows Run

Double-click `run_pipeline.bat`

or run from CMD:

```bat
run_pipeline.bat dating 50
```

- argument 1 = keyword (optional)
- argument 2 = limit (optional, default `50`)

The batch launcher will:
- create `.venv` if missing
- install dependencies
- install Playwright Chromium
- prompt for keyword if not provided
- run full pipeline

---

## Output Files

After success:

- `data/raw.json`
- `data/clean.json`
- `data/analysis.json`
- `data/generated.json`
- `data/final.csv` (columns: `original_text`, `rsoc_text`)

---

## Troubleshooting

### Playwright install fails
```bash
python -m playwright install chromium
```
Retry with stable network/proxy settings.

### Scraper returns 0 ads
- Meta DOM can change; selectors are defensive but may need updates.
- Try another keyword.
- Rerun later.

### Pipeline runs but outputs are sparse
- Some ads contain limited text/media, reducing analysis richness.
- Increase `--limit` and rerun.

---

## Notes

- This project is for research/analysis workflows.
- Respect Meta platform terms and applicable laws.
