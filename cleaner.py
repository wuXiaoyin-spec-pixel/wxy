import json
from pathlib import Path

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw.json"
CLEAN_PATH = DATA_DIR / "clean.json"


def _norm_text(value):
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


def _is_valid(record):
    if not isinstance(record, dict):
        return False
    if not record.get("primary_text") and not record.get("headline"):
        return False
    return True


def clean_ads():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_PATH.exists():
        print(f"[cleaner] Missing input file: {RAW_PATH}")
        with CLEAN_PATH.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    with RAW_PATH.open("r", encoding="utf-8") as f:
        raw_ads = json.load(f)

    cleaned = []
    for item in raw_ads:
        normalized = {
            "page_name": _norm_text(item.get("page_name", "")),
            "primary_text": _norm_text(item.get("primary_text", "")),
            "headline": _norm_text(item.get("headline", "")),
            "image": _norm_text(item.get("image", "")),
            "ad_snapshot_url": _norm_text(item.get("ad_snapshot_url", "")),
        }

        normalized["original_text"] = normalized["primary_text"]

        if _is_valid(normalized):
            cleaned.append(normalized)

    with CLEAN_PATH.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"[cleaner] Saved {len(cleaned)} cleaned ads to {CLEAN_PATH}")
    return cleaned


if __name__ == "__main__":
    clean_ads()
