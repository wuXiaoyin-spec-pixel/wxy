import csv
import json
from pathlib import Path

DATA_DIR = Path("data")
ANALYSIS_PATH = DATA_DIR / "analysis.json"
GENERATED_PATH = DATA_DIR / "generated.json"
FINAL_CSV_PATH = DATA_DIR / "final.csv"


def _limit_words(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).strip()


def _build_rsoc(ad):
    page_name = ad.get("page_name") or "This advertiser"
    hook = ad.get("hook_type", "neutral")
    emotion = ad.get("emotional_trigger", "neutral")
    ad_format = ad.get("format", "image_text")
    headline = ad.get("headline", "").strip()
    primary = _limit_words(ad.get("primary_text", "").strip(), 20)

    headline_part = f"The headline reads: '{headline}'. " if headline else ""
    text_part = f"The ad text highlights: '{primary}'. " if primary else ""

    rsoc_text = (
        f"{page_name} appears to run a {ad_format} ad with a {hook} hook and a "
        f"{emotion} emotional angle. {headline_part}{text_part}"
        "The message is presented in an informational tone and focuses on core benefits, "
        "audience relevance, and clear positioning rather than aggressive promotion."
    )

    return " ".join(rsoc_text.split())


def generate_outputs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not ANALYSIS_PATH.exists():
        print(f"[generator] Missing input file: {ANALYSIS_PATH}")
        with GENERATED_PATH.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with FINAL_CSV_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["original_text", "rsoc_text"])
            writer.writeheader()
        return []

    with ANALYSIS_PATH.open("r", encoding="utf-8") as f:
        analyzed_ads = json.load(f)

    generated = []
    for ad in analyzed_ads:
        rsoc_text = _build_rsoc(ad)
        row = {
            "original_text": ad.get("original_text", ""),
            "rsoc_text": rsoc_text,
        }

        merged = dict(ad)
        merged["rsoc_text"] = rsoc_text
        generated.append(merged)

    with GENERATED_PATH.open("w", encoding="utf-8") as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)

    with FINAL_CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["original_text", "rsoc_text"])
        writer.writeheader()
        for item in generated:
            writer.writerow(
                {
                    "original_text": item.get("original_text", ""),
                    "rsoc_text": item.get("rsoc_text", ""),
                }
            )

    print(f"[generator] Saved {len(generated)} records to {GENERATED_PATH}")
    print(f"[generator] Saved CSV export to {FINAL_CSV_PATH}")
    return generated


if __name__ == "__main__":
    generate_outputs()
