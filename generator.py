import csv
import json
from pathlib import Path

DATA_ROOT = Path("data")
CSV_COLUMNS = [
    "keyword",
    "page_name",
    "original_text",
    "headline",
    "hook_type",
    "emotional_trigger",
    "format",
    "image",
    "ad_snapshot_url",
    "rsoc_text",
]

TEMPLATES = [
    (
        "{page} presents a {fmt} creative that uses a {hook} framing with a {emotion} tone. "
        "The visible headline is '{headline}', while the body references '{primary}'. "
        "Overall, the message is structured as factual product communication, emphasizing what is offered, "
        "the context for likely audiences, and how details are positioned in straightforward language."
    ),
    (
        "In this {fmt} ad, {page} appears to rely on a {hook} hook and a {emotion} emotional signal. "
        "Its headline states '{headline}' and the main copy includes '{primary}'. "
        "The content reads as informational brand messaging focused on features, audience fit, and practical value "
        "without exaggerated claims, urgency pressure, or direct response prompting."
    ),
    (
        "{page} is running a {fmt} execution where the dominant hook type is {hook} and the emotional cue is {emotion}. "
        "The headline shown is '{headline}', and the core text says '{primary}'. "
        "The narrative remains neutral, outlining offer details and relevance in a clear explanatory style that supports "
        "understanding rather than persuasive hype or explicit call-to-action language."
    ),
]



def _paths(keyword):
    safe_keyword = keyword.replace("/", "_").replace("\\", "_").strip() or "default"
    keyword_dir = DATA_ROOT / safe_keyword
    return keyword_dir / "analysis.json", keyword_dir / "generated.json", keyword_dir / "final.csv"



def _limit_words(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).strip()



def _ensure_word_range(text, min_words=60, max_words=80):
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]).strip()
    if len(words) < min_words:
        pad = (
            " The summary keeps a neutral tone, describes observable message elements, "
            "and avoids promotional exaggeration while preserving clarity and context."
        )
        combined = (text + pad).split()
        return " ".join(combined[:max_words]).strip()
    return " ".join(words).strip()



def _build_rsoc(ad, index):
    page_name = ad.get("page_name") or "This advertiser"
    hook = ad.get("hook_type", "neutral")
    emotion = ad.get("emotional_trigger", "neutral")
    ad_format = ad.get("format", "image_text")
    headline = ad.get("headline", "").strip() or "No explicit headline"
    primary = _limit_words(ad.get("primary_text", "").strip() or "No visible body copy", 24)

    template = TEMPLATES[index % len(TEMPLATES)]
    rsoc_text = template.format(
        page=page_name,
        fmt=ad_format,
        hook=hook,
        emotion=emotion,
        headline=headline,
        primary=primary,
    )
    rsoc_text = " ".join(rsoc_text.split())
    return _ensure_word_range(rsoc_text, min_words=60, max_words=80)



def generate_outputs(keyword):
    analysis_path, generated_path, final_csv_path = _paths(keyword)
    generated_path.parent.mkdir(parents=True, exist_ok=True)

    if not analysis_path.exists():
        print(f"[generator] Missing input file: {analysis_path}")
        with generated_path.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with final_csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        return []

    with analysis_path.open("r", encoding="utf-8") as f:
        analyzed_ads = json.load(f)

    generated = []
    for idx, ad in enumerate(analyzed_ads):
        rsoc_text = _build_rsoc(ad, idx)

        merged = dict(ad)
        merged["keyword"] = keyword
        merged["rsoc_text"] = rsoc_text
        generated.append(merged)

    with generated_path.open("w", encoding="utf-8") as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)

    with final_csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in generated:
            writer.writerow({column: item.get(column, "") for column in CSV_COLUMNS})

    print(f"[generator] Saved {len(generated)} records to {generated_path}")
    print(f"[generator] Saved CSV export to {final_csv_path}")
    return generated


if __name__ == "__main__":
    generate_outputs("dating")
