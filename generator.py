import csv
import json
import logging
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

DATA_DIR = Path("data")
ANALYSIS_PATH = DATA_DIR / "analysis.json"
GENERATED_PATH = DATA_DIR / "generated.json"
FINAL_CSV_PATH = DATA_DIR / "final.csv"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_rsoc_text(client: OpenAI, ad: Dict[str, str], model: str) -> str:
    base_text = ad.get("primary_text", "")
    headline = ad.get("headline", "")

    prompt = f"""
Rewrite the ad below in RSOC style.
Requirements:
- Neutral tone
- Informational style
- No promotional language
- 60-80 words
Return only the rewritten text.

Original ad text: {base_text}
Headline: {headline}
""".strip()

    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=0.3,
    )

    return response.output_text.strip()


def generate_ads(model: str = "gpt-4.1-mini") -> List[Dict[str, str]]:
    configure_logging()
    ensure_data_dir()
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    if not ANALYSIS_PATH.exists():
        logging.warning("Analysis file not found: %s. Writing empty generated file.", ANALYSIS_PATH)
        GENERATED_PATH.write_text("[]", encoding="utf-8")
        FINAL_CSV_PATH.write_text("original_text,rsoc_text\n", encoding="utf-8")
        return []

    with ANALYSIS_PATH.open("r", encoding="utf-8") as f:
        analyzed_ads = json.load(f)

    client = OpenAI(api_key=api_key)

    generated_records = []
    for idx, ad in enumerate(analyzed_ads, start=1):
        try:
            rsoc_text = generate_rsoc_text(client=client, ad=ad, model=model)
        except Exception as exc:
            logging.warning("Generation failed for ad %s: %s", idx, exc)
            rsoc_text = ""

        record = {
            **ad,
            "original_text": ad.get("primary_text", ""),
            "rsoc_text": rsoc_text,
        }
        generated_records.append(record)
        logging.info("Generated RSOC ad %s/%s", idx, len(analyzed_ads))

    with GENERATED_PATH.open("w", encoding="utf-8") as f:
        json.dump(generated_records, f, ensure_ascii=False, indent=2)

    export_to_csv(generated_records)

    logging.info("Saved generated ads to %s", GENERATED_PATH)
    return generated_records


def export_to_csv(records: List[Dict[str, str]]) -> None:
    ensure_data_dir()
    with FINAL_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original_text", "rsoc_text"])
        writer.writeheader()
        for row in records:
            writer.writerow(
                {
                    "original_text": row.get("original_text", ""),
                    "rsoc_text": row.get("rsoc_text", ""),
                }
            )

    logging.info("Exported CSV to %s", FINAL_CSV_PATH)


if __name__ == "__main__":
    generate_ads()
