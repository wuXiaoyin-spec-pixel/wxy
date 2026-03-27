import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw.json"
META_AD_LIBRARY_URL = "https://www.facebook.com/ads/library/"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def safe_text(element, selector: str) -> str:
    try:
        target = element.query_selector(selector)
        if not target:
            return ""
        value = target.inner_text(timeout=1500).strip()
        return value
    except Exception:
        return ""


def safe_image(element) -> str:
    image_selectors = ["img[src]", "image"]
    for selector in image_selectors:
        try:
            target = element.query_selector(selector)
            if not target:
                continue
            src = target.get_attribute("src") or ""
            if src:
                return src
        except Exception:
            continue
    return ""


def extract_ad(entry) -> Optional[Dict[str, str]]:
    primary_candidates = [
        "div[dir='auto']",
        "span[dir='auto']",
        "div[style*='white-space']",
    ]
    headline_candidates = [
        "h3",
        "h4",
        "strong",
    ]

    primary_text = ""
    for selector in primary_candidates:
        primary_text = safe_text(entry, selector)
        if primary_text:
            break

    headline = ""
    for selector in headline_candidates:
        headline = safe_text(entry, selector)
        if headline and headline != primary_text:
            break

    image = safe_image(entry)

    if not any([primary_text, headline, image]):
        return None

    return {
        "primary_text": primary_text,
        "headline": headline,
        "image": image,
    }


def build_search_url(keyword: str) -> str:
    # country=ALL and media_type=all keeps coverage broad
    return (
        f"{META_AD_LIBRARY_URL}?active_status=all&ad_type=all&country=ALL"
        f"&q={keyword}&search_type=keyword_unordered"
    )


def scrape_ads(keyword: str, limit: int = 50, retries: int = 3) -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()

    for attempt in range(1, retries + 1):
        logging.info("Scrape attempt %s/%s for keyword='%s'", attempt, retries, keyword)
        ads: List[Dict[str, str]] = []

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36"
                    ),
                )
                page = context.new_page()
                page.set_default_timeout(15000)

                url = build_search_url(keyword)
                logging.info("Opening %s", url)
                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                # Give page and dynamic scripts time to render ad cards.
                page.wait_for_timeout(3000)

                prev_count = 0
                stagnation_rounds = 0

                while len(ads) < limit and stagnation_rounds < 5:
                    page.mouse.wheel(0, 3000)
                    page.wait_for_timeout(2000)

                    card_selectors = [
                        "div[role='article']",
                        "div.x1n2onr6",
                        "div:has-text('Sponsored')",
                    ]

                    cards = []
                    for selector in card_selectors:
                        cards = page.query_selector_all(selector)
                        if cards:
                            break

                    for card in cards:
                        if len(ads) >= limit:
                            break
                        parsed = extract_ad(card)
                        if parsed:
                            ads.append(parsed)

                    # Deduplicate while preserving order
                    unique_ads = []
                    seen = set()
                    for ad in ads:
                        key = (
                            ad.get("primary_text", "").strip(),
                            ad.get("headline", "").strip(),
                            ad.get("image", "").strip(),
                        )
                        if key in seen:
                            continue
                        seen.add(key)
                        unique_ads.append(ad)
                    ads = unique_ads

                    if len(ads) == prev_count:
                        stagnation_rounds += 1
                    else:
                        stagnation_rounds = 0
                    prev_count = len(ads)

                    logging.info("Collected %s/%s ads", len(ads), limit)

                browser.close()

                if ads:
                    with RAW_PATH.open("w", encoding="utf-8") as f:
                        json.dump(ads[:limit], f, ensure_ascii=False, indent=2)
                    logging.info("Saved %s ads to %s", len(ads[:limit]), RAW_PATH)
                    return ads[:limit]

                logging.warning("No ads collected in attempt %s", attempt)

        except PlaywrightTimeoutError as exc:
            logging.warning("Timeout during scrape attempt %s: %s", attempt, exc)
        except Exception as exc:
            logging.exception("Unexpected error during scrape attempt %s: %s", attempt, exc)

        backoff_seconds = attempt * 2
        logging.info("Retrying in %s seconds...", backoff_seconds)
        time.sleep(backoff_seconds)

    logging.error("Scraping failed after %s attempts", retries)
    with RAW_PATH.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Facebook Ad Library ads")
    parser.add_argument("--keyword", type=str, default="dating", help="Search keyword")
    parser.add_argument("--limit", type=int, default=50, help="Maximum ads to collect")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scrape_ads(keyword=args.keyword, limit=args.limit)


if __name__ == "__main__":
    main()
