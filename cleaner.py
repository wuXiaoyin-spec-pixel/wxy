import json
import logging
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw.json"
CLEAN_PATH = DATA_DIR / "clean.json"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(value: str) -> str:
    if not value:
        return ""
    return " ".join(str(value).strip().split())


def clean_ads() -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()

    if not RAW_PATH.exists():
        logging.warning("Raw file not found: %s. Creating empty clean file.", RAW_PATH)
        CLEAN_PATH.write_text("[]", encoding="utf-8")
        return []

    with RAW_PATH.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned = []
    seen = set()

    for item in raw_data:
        primary_text = normalize_text(item.get("primary_text", ""))
        headline = normalize_text(item.get("headline", ""))
        image = normalize_text(item.get("image", ""))

        if not any([primary_text, headline, image]):
            continue

        record = {
            "primary_text": primary_text,
            "headline": headline,
            "image": image,
        }

        dedupe_key = (primary_text.lower(), headline.lower(), image)
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        cleaned.append(record)

    with CLEAN_PATH.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    logging.info("Saved %s cleaned ads to %s", len(cleaned), CLEAN_PATH)
    return cleaned


if __name__ == "__main__":
    clean_ads()
