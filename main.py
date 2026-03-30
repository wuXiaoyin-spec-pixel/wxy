import argparse
import sys
from pathlib import Path

from analyzer import analyze_ads
from cleaner import clean_ads
from generator import generate_outputs
from scraper import scrape_ads



def _load_keywords(args):
    keywords = []

    if args.keywords:
        keywords.extend([k.strip() for k in args.keywords.split(",") if k.strip()])

    if args.keyword_file:
        path = Path(args.keyword_file)
        if not path.exists():
            print(f"[main] Keyword file not found: {path}")
        else:
            lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
            keywords.extend([line for line in lines if line and not line.startswith("#")])

    if args.keyword:
        keywords.append(args.keyword.strip())

    deduped = []
    seen = set()
    for keyword in keywords:
        key = keyword.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(keyword)

    return deduped or ["dating"]



def build_parser():
    parser = argparse.ArgumentParser(
        description="Local Facebook Ad Library pipeline: scrape -> clean -> analyze -> generate -> export"
    )
    parser.add_argument("--keyword", type=str, help="Single search keyword (optional)")
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords, e.g. dating,fitness,finance")
    parser.add_argument("--keyword-file", type=str, help="File with one keyword per line")
    parser.add_argument("--limit", type=int, default=30, help="Number of ads to collect per keyword")
    return parser



def main():
    parser = build_parser()
    args = parser.parse_args()

    limit = max(1, args.limit)
    keywords = _load_keywords(args)

    print(f"[main] Keywords to process: {keywords}")

    summaries = []

    for keyword in keywords:
        print(f"\n[main] Processing keyword: {keyword}")
        print("[main] Step 1/5: Scraping ads...")
        raw_ads = scrape_ads(keyword=keyword, limit=limit)

        print("[main] Step 2/5: Cleaning ads...")
        cleaned = clean_ads(keyword=keyword)

        print("[main] Step 3/5: Analyzing ads...")
        analyzed = analyze_ads(keyword=keyword)

        print("[main] Step 4/5 and 5/5: Generating text and exporting CSV...")
        generated = generate_outputs(keyword=keyword)

        final_csv_path = Path("data") / keyword.replace("/", "_").replace("\\", "_") / "final.csv"
        summaries.append(
            {
                "keyword": keyword,
                "raw": len(raw_ads),
                "clean": len(cleaned),
                "generated": len(generated),
                "final_csv": str(final_csv_path),
                "analyzed": len(analyzed),
            }
        )

    print("\n[main] Summary")
    for item in summaries:
        print(
            f"[main] {item['keyword']} -> raw {item['raw']} -> clean {item['clean']} "
            f"-> generated {item['generated']} -> {item['final_csv']}"
        )

    has_any_generated = any(item["generated"] > 0 for item in summaries)
    if not has_any_generated:
        print("[main] No generated records for any keyword.")
        return 1

    print("[main] Pipeline completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
