import json
import time
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

DEBUG_BROWSER = False
DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw.json"

CARD_SELECTORS = [
    "div[role='article']",
    "div.x1n2onr6",
    "div[data-testid='ad-library-ad']",
]

PAGE_NAME_SELECTORS = [
    "h4",
    "a[role='link'] span",
    "div[dir='auto'] strong",
]

PRIMARY_TEXT_SELECTORS = [
    "div[dir='auto']",
    "div.xdj266r",
    "span[dir='auto']",
]

HEADLINE_SELECTORS = [
    "h2",
    "h3",
    "strong",
    "div[role='heading']",
]

IMAGE_SELECTORS = [
    "img",
]

SNAPSHOT_LINK_SELECTORS = [
    "a[href*='ad_snapshot']",
    "a[href*='/ads/library/']",
]


def _safe_text(card, selectors):
    for selector in selectors:
        try:
            node = card.query_selector(selector)
            if node:
                text = (node.inner_text() or "").strip()
                if text:
                    return text
        except Exception:
            continue
    return ""


def _safe_attr(card, selectors, attr):
    for selector in selectors:
        try:
            node = card.query_selector(selector)
            if node:
                value = (node.get_attribute(attr) or "").strip()
                if value:
                    return value
        except Exception:
            continue
    return ""


def _extract_snapshot_url(card):
    for selector in SNAPSHOT_LINK_SELECTORS:
        try:
            links = card.query_selector_all(selector)
            for link in links:
                href = (link.get_attribute("href") or "").strip()
                if not href:
                    continue
                if href.startswith("/"):
                    href = "https://www.facebook.com" + href
                return href
        except Exception:
            continue
    return ""


def _dedup_key(ad):
    return (
        ad.get("page_name", "").lower().strip(),
        ad.get("primary_text", "").lower().strip(),
        ad.get("headline", "").lower().strip(),
        ad.get("ad_snapshot_url", "").lower().strip(),
    )


def scrape_ads(keyword, limit=20):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    encoded_keyword = quote_plus(keyword.strip())
    url = (
        "https://www.facebook.com/ads/library/?active_status=all"
        "&ad_type=all&country=US&is_targeted_country=false"
        f"&media_type=all&search_type=keyword_unordered&q={encoded_keyword}"
    )

    unique_ads = []
    seen = set()

    print(f"[scraper] Opening: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not DEBUG_BROWSER,
            slow_mo=400 if DEBUG_BROWSER else 0,
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
        except PlaywrightTimeoutError:
            print("[scraper] Initial page load timed out.")

        stale_height_rounds = 0
        stale_count_rounds = 0
        last_height = 0
        last_count = 0

        for round_number in range(1, 60):
            cards = []
            for selector in CARD_SELECTORS:
                try:
                    found = page.query_selector_all(selector)
                    if found:
                        cards = found
                        break
                except Exception:
                    continue

            print(f"[scraper] Round {round_number}: cards found={len(cards)}")

            for card in cards:
                ad = {
                    "page_name": _safe_text(card, PAGE_NAME_SELECTORS),
                    "primary_text": _safe_text(card, PRIMARY_TEXT_SELECTORS),
                    "headline": _safe_text(card, HEADLINE_SELECTORS),
                    "image": _safe_attr(card, IMAGE_SELECTORS, "src"),
                    "ad_snapshot_url": _extract_snapshot_url(card),
                }

                if not ad["primary_text"] and not ad["headline"]:
                    continue

                key = _dedup_key(ad)
                if key in seen:
                    continue
                seen.add(key)
                unique_ads.append(ad)

                if len(unique_ads) >= limit:
                    break

            current_height = page.evaluate("document.body.scrollHeight")
            print(
                f"[scraper] unique ads={len(unique_ads)} | page height={current_height}"
            )

            if len(unique_ads) >= limit:
                print("[scraper] Reached requested limit.")
                break

            if current_height == last_height:
                stale_height_rounds += 1
            else:
                stale_height_rounds = 0

            if len(unique_ads) == last_count:
                stale_count_rounds += 1
            else:
                stale_count_rounds = 0

            if stale_height_rounds >= 4:
                print("[scraper] Stopping: page height stopped changing.")
                break

            if stale_count_rounds >= 5:
                print("[scraper] Stopping: unique ad count stopped growing.")
                break

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500)

            last_height = current_height
            last_count = len(unique_ads)

        context.close()
        browser.close()

    with RAW_PATH.open("w", encoding="utf-8") as f:
        json.dump(unique_ads[:limit], f, ensure_ascii=False, indent=2)

    print(f"[scraper] Saved {len(unique_ads[:limit])} ads to {RAW_PATH}")
    return unique_ads[:limit]


if __name__ == "__main__":
    scrape_ads("dating", 20)
