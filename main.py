import argparse
import sys

from analyzer import analyze_ads
from cleaner import clean_ads
from generator import generate_outputs
from scraper import scrape_ads


def build_parser():
    parser = argparse.ArgumentParser(
        description="Local Facebook Ad Library pipeline: scrape -> clean -> analyze -> generate -> export"
    )
    parser.add_argument("--keyword", type=str, required=True, help="Search keyword")
    parser.add_argument("--limit", type=int, default=20, help="Number of ads to collect")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    keyword = args.keyword.strip()
    limit = max(1, args.limit)

    print("[main] Step 1/5: Scraping ads...")
    ads = scrape_ads(keyword=keyword, limit=limit)
    if not ads:
        print("[main] Scraping returned zero ads. Pipeline stopped.")
        return 1

    print("[main] Step 2/5: Cleaning ads...")
    cleaned = clean_ads()
    if not cleaned:
        print("[main] Cleaning returned zero valid ads. Pipeline stopped.")
        return 1

    print("[main] Step 3/5: Analyzing ads...")
    analyzed = analyze_ads()
    if not analyzed:
        print("[main] Analysis returned zero rows. Pipeline stopped.")
        return 1

    print("[main] Step 4/5 and 5/5: Generating text and exporting CSV...")
    generated = generate_outputs()
    if not generated:
        print("[main] Generation returned zero rows. Pipeline stopped.")
        return 1

    print("[main] Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
