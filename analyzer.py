import json
from pathlib import Path

DATA_ROOT = Path("data")

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



def _paths(keyword):
    safe_keyword = keyword.replace("/", "_").replace("\\", "_").strip() or "default"
    keyword_dir = DATA_ROOT / safe_keyword
    return keyword_dir / "clean.json", keyword_dir / "analysis.json"



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



def analyze_ads(keyword):
    clean_path, analysis_path = _paths(keyword)
    analysis_path.parent.mkdir(parents=True, exist_ok=True)

    if not clean_path.exists():
        print(f"[analyzer] Missing input file: {clean_path}")
        with analysis_path.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    with clean_path.open("r", encoding="utf-8") as f:
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

    with analysis_path.open("w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    print(f"[analyzer] Saved {len(analyzed)} analyzed ads to {analysis_path}")
    return analyzed


if __name__ == "__main__":
    analyze_ads("dating")
