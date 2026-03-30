import json
from pathlib import Path

DATA_DIR = Path("data")
CLEAN_PATH = DATA_DIR / "clean.json"
ANALYSIS_PATH = DATA_DIR / "analysis.json"


HOOK_KEYWORDS = {
    "urgency": ["today", "now", "limited", "last chance", "ending", "deadline"],
    "social proof": ["review", "rated", "customers", "people", "trusted", "community"],
    "transformation": ["before", "after", "transform", "improve", "change", "results"],
    "value": ["save", "free", "discount", "deal", "offer", "price", "bonus"],
    "curiosity": ["discover", "secret", "why", "how", "learn", "find out"],
}

EMOTION_KEYWORDS = {
    "urgency": ["fast", "urgent", "ending", "now"],
    "value": ["save", "free", "affordable", "deal"],
    "transformation": ["better", "improve", "confidence", "results"],
    "social proof": ["reviews", "trusted", "join", "thousands"],
}


def _pick_label(text, mapping, default_label="neutral"):
    lower_text = text.lower()
    for label, words in mapping.items():
        if any(word in lower_text for word in words):
            return label
    return default_label


def _infer_format(ad):
    text = ad.get("primary_text", "")
    image = ad.get("image", "")
    has_video_hint = "video" in (ad.get("headline", "") + " " + text).lower()

    if has_video_hint:
        return "video_text"
    if image:
        return "image_text"
    if len(text.split()) <= 20:
        return "short_copy"
    return "long_copy"


def analyze_ads():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CLEAN_PATH.exists():
        print(f"[analyzer] Missing input file: {CLEAN_PATH}")
        with ANALYSIS_PATH.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    with CLEAN_PATH.open("r", encoding="utf-8") as f:
        ads = json.load(f)

    analyzed = []
    for ad in ads:
        combined = f"{ad.get('headline', '')} {ad.get('primary_text', '')}".strip()
        hook_type = _pick_label(combined, HOOK_KEYWORDS)
        emotional_trigger = _pick_label(combined, EMOTION_KEYWORDS)
        ad_format = _infer_format(ad)

        enriched = dict(ad)
        enriched["hook_type"] = hook_type
        enriched["emotional_trigger"] = emotional_trigger
        enriched["format"] = ad_format
        analyzed.append(enriched)

    with ANALYSIS_PATH.open("w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    print(f"[analyzer] Saved {len(analyzed)} analyzed ads to {ANALYSIS_PATH}")
    return analyzed


if __name__ == "__main__":
    analyze_ads()
