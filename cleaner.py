import json
import re
from pathlib import Path

DATA_ROOT = Path("data")

NOISE_PHRASES = [
    "赞助内容",
    "投放中",
    "已停止",
    "打开下拉菜单",
    "查看广告详情",
    "查看摘要详情",
    "平台",
    "资料库编号",
    "Sponsored",
    "See ad details",
    "See summary details",
    "Ad Library ID",
]



def _paths(keyword):
    safe_keyword = keyword.replace("/", "_").replace("\\", "_").strip() or "default"
    keyword_dir = DATA_ROOT / safe_keyword
    return keyword_dir / "raw.json", keyword_dir / "clean.json"



def _remove_noise(text):
    cleaned = str(text or "")
    for phrase in NOISE_PHRASES:
        cleaned = cleaned.replace(phrase, " ")
    return cleaned



def _remove_duplicate_fragments(text):
    if not text:
        return ""

    chunks = [c.strip() for c in re.split(r"[\n\r|•]+|(?<=[。！？!?;；.])\s+", text) if c.strip()]
    unique_chunks = []
    seen = set()
    for chunk in chunks:
        norm = " ".join(chunk.split()).lower()
        if norm in seen:
            continue
        seen.add(norm)
        unique_chunks.append(" ".join(chunk.split()))

    if not unique_chunks:
        return ""

    collapsed = " ".join(unique_chunks)
    words = collapsed.split()
    deduped_words = []
    for word in words:
        if deduped_words and deduped_words[-1].lower() == word.lower():
            continue
        deduped_words.append(word)

    return " ".join(deduped_words)



def _norm_text(value):
    value = _remove_noise(value)
    value = _remove_duplicate_fragments(value)
    return " ".join(str(value).split()).strip()



def _is_valid(record):
    if not isinstance(record, dict):
        return False
    if not record.get("primary_text") and not record.get("headline"):
        return False
    return True



def _dedup_key(ad):
    snapshot = ad.get("ad_snapshot_url", "").lower().strip()
    if snapshot:
        return ("snapshot", snapshot)
    return (
        "composite",
        ad.get("page_name", "").lower().strip(),
        ad.get("primary_text", "").lower().strip(),
        ad.get("headline", "").lower().strip(),
        ad.get("image", "").lower().strip(),
    )



def clean_ads(keyword):
    raw_path, clean_path = _paths(keyword)
    clean_path.parent.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        print(f"[cleaner] Missing input file: {raw_path}")
        with clean_path.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    with raw_path.open("r", encoding="utf-8") as f:
        raw_ads = json.load(f)

    cleaned = []
    seen = set()

    for item in raw_ads:
        normalized = {
            "page_name": _norm_text(item.get("page_name", "")),
            "primary_text": _norm_text(item.get("primary_text", "")),
            "headline": _norm_text(item.get("headline", "")),
            "image": _norm_text(item.get("image", "")),
            "ad_snapshot_url": _norm_text(item.get("ad_snapshot_url", "")),
        }
        normalized["original_text"] = normalized["primary_text"]

        if not _is_valid(normalized):
            continue

        key = _dedup_key(normalized)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(normalized)

    with clean_path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"[cleaner] Saved {len(cleaned)} cleaned ads to {clean_path}")
    return cleaned


if __name__ == "__main__":
    clean_ads("dating")
