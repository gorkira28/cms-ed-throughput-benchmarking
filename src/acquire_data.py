"""Download the current CMS hospital and ED measure extracts.

The script intentionally queries only the measures used in this project and
stores immutable, date-stamped raw CSVs. No patient-level data are involved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import requests


API_ROOT = "https://data.cms.gov/provider-data/api/1/datastore/query"
METASTORE_ROOT = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items"
DATASETS = {
    "timely_effective_care": "yv7e-xc69",
    "hospital_general_information": "xubh-q36u",
    "timely_effective_care_national": "isrn-hqyy",
}
MEASURES = ["EDV", "OP_18a", "OP_18b", "OP_18c", "OP_18d", "OP_22"]


def fetch(dataset: str, measure: str | None = None, page_size: int = 1500) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        params: dict[str, str | int] = {
            "offset": offset,
            "limit": page_size,
            "count": "true",
        }
        if measure:
            params.update(
                {
                    "conditions[0][property]": "measure_id",
                    "conditions[0][value]": measure,
                    "conditions[0][operator]": "=",
                }
            )
        response = requests.get(f"{API_ROOT}/{dataset}/0", params=params, timeout=120)
        response.raise_for_status()
        payload = response.json()
        batch = payload.get("results", [])
        rows.extend(batch)
        offset += len(batch)
        if not batch or len(rows) >= int(payload.get("count", len(rows))):
            break
    return rows


def download_dataframe(dataset: str) -> tuple[pd.DataFrame, str]:
    """Resolve the official CMS download URL from dataset metadata."""
    metadata_response = requests.get(f"{METASTORE_ROOT}/{dataset}", timeout=60)
    metadata_response.raise_for_status()
    distribution = metadata_response.json()["distribution"]
    if isinstance(distribution, list):
        distribution = distribution[0]
    download_url = distribution["downloadURL"]
    csv_response = requests.get(download_url, timeout=180)
    csv_response.raise_for_status()
    from io import BytesIO

    frame = pd.read_csv(BytesIO(csv_response.content), dtype=str, keep_default_na=False)
    frame.columns = [
        re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
        for column in frame.columns
    ]
    return frame, download_url


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    ed_all, ed_url = download_dataframe(DATASETS["timely_effective_care"])
    hospitals, hospital_url = download_dataframe(DATASETS["hospital_general_information"])
    national_all, national_url = download_dataframe(DATASETS["timely_effective_care_national"])
    files = {
        "cms_ed_measures": ed_all[ed_all["measure_id"].isin(MEASURES)].copy(),
        "cms_hospital_general_information": hospitals,
        "cms_ed_national": national_all[national_all["measure_id"].isin(MEASURES)].copy(),
    }

    manifest = {
        "retrieved_utc_date": args.as_of,
        "api_root": API_ROOT,
        "datasets": DATASETS,
        "download_urls": {
            "timely_effective_care": ed_url,
            "hospital_general_information": hospital_url,
            "timely_effective_care_national": national_url,
        },
        "measures": MEASURES,
        "files": {},
    }
    for stem, frame in files.items():
        path = args.output / f"{stem}_{args.as_of}.csv"
        frame.to_csv(path, index=False)
        manifest["files"][path.name] = {
            "rows": len(frame),
            "columns": len(frame.columns),
            "sha256": sha256(path),
        }

    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

