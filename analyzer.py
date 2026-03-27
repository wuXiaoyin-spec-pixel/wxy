import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

DATA_DIR = Path("data")
CLEAN_PATH = DATA_DIR / "clean.json"
ANALYSIS_PATH = DATA_DIR / "analysis.json"

HOOK_RULES: List[Tuple[str, List[str]]] = [
    ("curiosity", ["secret", "revealed", "mistake", "warning", "truth", "hidden"]),
    ("value", ["save", "discount", "cheap", "affordable", "deal", "budget"]),
    ("transformation", ["before and after", "before/after", "transform", "transformation", "results"]),
    ("problem_solution", ["problem", "solution", "fix", "improve", "struggle"]),
    ("social_proof", ["testimonial", "review", "thousands", "users", "trusted"]),
]

EMOTION_RULES: List[Tuple[str, List[str]]] = [
    ("fear", ["fear", "risk", "danger", "urgent", "warning"]),
    ("loneliness", ["lonely", "alone", "isolated", "single"]),
    ("anxiety", ["anxious", "stress", "overwhelmed", "worried"]),
    ("hope", ["hope", "better", "improve", "future", "grow"]),
    ("confidence", ["confidence", "confident", "empower", "strong"]),
]


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def normalize(value: str) -> str:
    return " ".join((value or "").lower().split())


def contains_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def infer_hook_type(text: str) -> str:
    for label, keywords in HOOK_RULES:
        if contains_any(text, keywords):
            return label
    return "informational"


def infer_emotional_trigger(text: str) -> str:
    for label, keywords in EMOTION_RULES:
        if contains_any(text, keywords):
            return label
    return "neutral"


def infer_format(primary_text: str, headline: str, image: str) -> str:
    word_count = len(primary_text.split())
    has_headline = bool(headline.strip())
    has_image = bool(image.strip())

    if has_image and has_headline and word_count >= 35:
        return "image_headline_longcopy"
    if has_image and has_headline:
        return "image_headline_shortcopy"
    if has_image and not has_headline:
        return "image_text"
    if not has_image and has_headline:
        return "text_headline"
    if word_count >= 45:
        return "long_text"
    return "text_only"


def analyze_record(ad: Dict[str, str]) -> Dict[str, str]:
    primary_text = ad.get("primary_text", "")
    headline = ad.get("headline", "")
    image = ad.get("image", "")

    combined = normalize(f"{primary_text} {headline}")

    return {
        **ad,
        "hook_type": infer_hook_type(combined),
        "emotional_trigger": infer_emotional_trigger(combined),
        "format": infer_format(primary_text, headline, image),
    }


def analyze_ads() -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()

    if not CLEAN_PATH.exists():
        logging.warning("Clean file not found: %s. Writing empty analysis file.", CLEAN_PATH)
        ANALYSIS_PATH.write_text("[]", encoding="utf-8")
        return []

    with CLEAN_PATH.open("r", encoding="utf-8") as f:
        clean_ads = json.load(f)

    analyzed: List[Dict[str, str]] = []

    for idx, ad in enumerate(clean_ads, start=1):
        try:
            record = analyze_record(ad)
        except Exception as exc:
            logging.warning("Rule-based analysis failed for ad %s: %s", idx, exc)
            record = {
                **ad,
                "hook_type": "informational",
                "emotional_trigger": "neutral",
                "format": "text_only",
            }
        analyzed.append(record)
        logging.info("Analyzed ad %s/%s", idx, len(clean_ads))

    with ANALYSIS_PATH.open("w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    logging.info("Saved analysis for %s ads to %s", len(analyzed), ANALYSIS_PATH)
    return analyzed


if __name__ == "__main__":
    analyze_ads()
