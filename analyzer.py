import json
import logging
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

DATA_DIR = Path("data")
CLEAN_PATH = DATA_DIR / "clean.json"
ANALYSIS_PATH = DATA_DIR / "analysis.json"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def analyze_single_ad(client: OpenAI, ad: Dict[str, str], model: str) -> Dict[str, str]:
    text = ad.get("primary_text", "")
    headline = ad.get("headline", "")

    prompt = f"""
Analyze the ad copy below and return ONLY strict JSON with keys:
- hook_type
- emotional_trigger
- format

Ad primary text: {text}
Ad headline: {headline}
""".strip()

    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )

    output_text = response.output_text.strip()

    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        parsed = {
            "hook_type": "unknown",
            "emotional_trigger": "unknown",
            "format": "unknown",
        }

    return {
        "hook_type": parsed.get("hook_type", "unknown"),
        "emotional_trigger": parsed.get("emotional_trigger", "unknown"),
        "format": parsed.get("format", "unknown"),
    }


def analyze_ads(model: str = "gpt-4.1-mini") -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    if not CLEAN_PATH.exists():
        logging.warning("Clean file not found: %s. Writing empty analysis file.", CLEAN_PATH)
        ANALYSIS_PATH.write_text("[]", encoding="utf-8")
        return []

    with CLEAN_PATH.open("r", encoding="utf-8") as f:
        clean_ads = json.load(f)

    client = OpenAI(api_key=api_key)

    analyzed: List[Dict[str, str]] = []
    for idx, ad in enumerate(clean_ads, start=1):
        try:
            analysis = analyze_single_ad(client=client, ad=ad, model=model)
        except Exception as exc:
            logging.warning("Analysis failed for ad %s: %s", idx, exc)
            analysis = {
                "hook_type": "unknown",
                "emotional_trigger": "unknown",
                "format": "unknown",
            }

        record = {
            **ad,
            **analysis,
        }
        analyzed.append(record)
        logging.info("Analyzed ad %s/%s", idx, len(clean_ads))

    with ANALYSIS_PATH.open("w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    logging.info("Saved analysis for %s ads to %s", len(analyzed), ANALYSIS_PATH)
    return analyzed


if __name__ == "__main__":
    analyze_ads()
