import argparse
import logging

from analyzer import analyze_ads
from cleaner import clean_ads
from generator import generate_ads
from scraper import scrape_ads


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Facebook Ad Library pipeline: scrape -> clean -> analyze -> generate -> export"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="",
        help="Keyword to search in Meta Ad Library (e.g. dating)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of ads to collect",
    )
    return parser.parse_args()


def prompt_keyword_if_missing(keyword: str) -> str:
    if keyword.strip():
        return keyword.strip()

    value = input("Enter keyword for Ad Library search (default: dating): ").strip()
    return value or "dating"


def run_pipeline(keyword: str, limit: int) -> None:
    print("\n=== Facebook Ad Library Pipeline Started ===")

    print("[1/5] Scraping ads...")
    scraped = scrape_ads(keyword=keyword, limit=limit)
    print(f"Scraping complete. Ads collected: {len(scraped)}")

    print("[2/5] Cleaning data...")
    cleaned = clean_ads()
    print(f"Cleaning complete. Clean records: {len(cleaned)}")

    print("[3/5] Analyzing ads with local rules...")
    analyzed = analyze_ads()
    print(f"Analysis complete. Analyzed records: {len(analyzed)}")

    print("[4/5] Generating RSOC ad text...")
    generated = generate_ads()
    print(f"Generation complete. Generated records: {len(generated)}")

    print("[5/5] Exporting CSV...")
    # CSV export happens in generate_ads() by design.
    print("CSV export complete. Output: data/final.csv")

    print("=== Pipeline Finished Successfully ===\n")


def main() -> None:
    configure_logging()
    args = parse_args()
    keyword = prompt_keyword_if_missing(args.keyword)
    run_pipeline(keyword=keyword, limit=args.limit)


if __name__ == "__main__":
    main()
