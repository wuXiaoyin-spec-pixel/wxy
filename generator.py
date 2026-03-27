import csv
import json
import logging
import re
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path("data")
ANALYSIS_PATH = DATA_DIR / "analysis.json"
GENERATED_PATH = DATA_DIR / "generated.json"
FINAL_CSV_PATH = DATA_DIR / "final.csv"

BANNED_PROMO_WORDS = [
    "best",
    "amazing",
    "buy now",
    "limited time",
    "act now",
    "exclusive",
    "must-have",
    "guaranteed",
]


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_text(text: str) -> str:
    cleaned = " ".join((text or "").split())
    for term in BANNED_PROMO_WORDS:
        cleaned = re.sub(rf"\b{re.escape(term)}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
    return cleaned


def clamp_words(text: str, minimum: int = 60, maximum: int = 80) -> str:
    words = text.split()

    if len(words) > maximum:
        words = words[:maximum]

    if len(words) < minimum:
        filler = (
            " The message is presented as a general informational statement with context "
            "about audience needs, communication style, and the type of content shown in the ad."
        ).split()
        i = 0
        while len(words) < minimum:
            words.append(filler[i % len(filler)])
            i += 1

    return " ".join(words)


def build_rsoc_text(ad: Dict[str, str]) -> str:
    original = sanitize_text(ad.get("primary_text", ""))
    headline = sanitize_text(ad.get("headline", ""))
    hook_type = ad.get("hook_type", "informational")
    emotional_trigger = ad.get("emotional_trigger", "neutral")
    ad_format = ad.get("format", "text_only")

    if not original:
        original = "The source ad provides limited primary text content."

    parts = [
        f"This ad communicates information using a {hook_type} hook and a {ad_format} format.",
        f"The emotional framing appears {emotional_trigger}, with language focused on audience context.",
        f"Core message summary: {original}",
    ]

    if headline:
        parts.append(f"Headline context: {headline}.")

    parts.append(
        "Overall, the content can be interpreted as an informational message rather than a promotional claim, "
        "with emphasis on clarity, relevance, and communication structure."
    )

    draft = " ".join(parts)
    return clamp_words(draft, minimum=60, maximum=80)


def generate_ads() -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()

    if not ANALYSIS_PATH.exists():
        logging.warning("Analysis file not found: %s. Writing empty generated file.", ANALYSIS_PATH)
        GENERATED_PATH.write_text("[]", encoding="utf-8")
        FINAL_CSV_PATH.write_text("original_text,rsoc_text\n", encoding="utf-8")
        return []

    with ANALYSIS_PATH.open("r", encoding="utf-8") as f:
        analyzed_ads = json.load(f)

    generated_records = []
    for idx, ad in enumerate(analyzed_ads, start=1):
        try:
            rsoc_text = build_rsoc_text(ad)
        except Exception as exc:
            logging.warning("Template generation failed for ad %s: %s", idx, exc)
            rsoc_text = ""

        record = {
            **ad,
            "original_text": ad.get("primary_text", ""),
            "rsoc_text": rsoc_text,
        }
        generated_records.append(record)
        logging.info("Generated RSOC ad %s/%s", idx, len(analyzed_ads))

    with GENERATED_PATH.open("w", encoding="utf-8") as f:
        json.dump(generated_records, f, ensure_ascii=False, indent=2)

    export_to_csv(generated_records)

    logging.info("Saved generated ads to %s", GENERATED_PATH)
    return generated_records


def export_to_csv(records: List[Dict[str, str]]) -> None:
    ensure_data_dir()
    with FINAL_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original_text", "rsoc_text"])
        writer.writeheader()
        for row in records:
            writer.writerow({"original_text": row.get("original_text", ""), "rsoc_text": row.get("rsoc_text", "")})

    logging.info("Exported CSV to %s", FINAL_CSV_PATH)


if __name__ == "__main__":
    generate_ads()
