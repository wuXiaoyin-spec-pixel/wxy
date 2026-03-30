# Local Facebook Ad Library Pipeline (Free, Offline-Friendly Workflow)

This project is a fully local Python pipeline for collecting and processing Meta (Facebook) Ad Library search results.

No OpenAI services are used.
No API keys are required.
No `.env` file is required.

## Pipeline

The flow is:

1. **scrape** (`scraper.py`)
2. **clean** (`cleaner.py`)
3. **analyze** (`analyzer.py`)
4. **generate** (`generator.py`)
5. **export** (`generator.py` writes CSV)

## Project Files

- `scraper.py` - Playwright scraper with scrolling and deduplication
- `cleaner.py` - field normalization and filtering
- `analyzer.py` - local rule-based ad analysis
- `generator.py` - local template-based RSOC generation + CSV export
- `main.py` - command-line pipeline runner
- `run_pipeline.bat` - Windows one-click setup and execution
- `requirements.txt` - Python dependencies

## Windows Setup and Run

### Option A: Direct Python command

```bat
python -m pip install -r requirements.txt
python -m playwright install chromium
python main.py --keyword dating --limit 20
```

### Option B: Batch script

```bat
run_pipeline.bat
```

With custom values:

```bat
run_pipeline.bat skincare 30
```

Defaults in the batch script:
- keyword: `dating`
- limit: `20`

## Output Files

All output is created in the `data/` folder:

- `data/raw.json` - raw scraped ads
- `data/clean.json` - normalized ads
- `data/analysis.json` - ads with local heuristic labels
- `data/generated.json` - ads with generated RSOC text
- `data/final.csv` - export with:
  - `original_text`
  - `rsoc_text`

## Scraper Debugging Tips

In `scraper.py`, set:

```python
DEBUG_BROWSER = True
```

This runs Chromium in visible mode with `slow_mo` so you can inspect loading and scrolling behavior.

Extra notes:
- If too few ads are captured, increase `--limit` and rerun.
- The Ad Library DOM can change over time; selector updates may be needed.
- Network speed and Meta rate limits can affect collection count.

## Known Limitations

- Meta may change HTML structure, requiring selector maintenance.
- Some ad cards may not expose every field (`headline`, `image`, `ad_snapshot_url`).
- Region/language/cookie differences can affect visible results.
- This scraper is best-effort and does not guarantee exact parity with the UI count.
