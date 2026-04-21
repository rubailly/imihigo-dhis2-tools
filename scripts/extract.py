#!/usr/bin/env python3
"""
One-time script to pull dataset metadata bundles from the source DHIS2 instance.
Run this from the repo root after cloning. Outputs are committed to src/data/.

Usage:
    python scripts/extract.py
    python scripts/extract.py --url https://... --username u --password p
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

DATASET_IDS: dict[str, str] = {
    "BUGESERA":  "m16tH53PKTq",
    "GATSIBO":   "IclTerKK5vZ",
    "KAYONZA":   "R5rTjEx1PsA",
    "KIREHE":    "NUa3VpZcAur",
    "NGOMA":     "sVdCdZRwyP0",
    "NYAGATARE": "LtSqjIdsDwl",
    "RWAMAGANA": "HBk9ysphONu",
}

OUT_DIR = Path(__file__).parent.parent / "src" / "imihigo_dhis2_tools" / "data"


def extract(base_url: str, username: str, password: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.auth = (username, password)
    session.headers["Accept"] = "application/json"

    for district, uid in DATASET_IDS.items():
        url = f"{base_url.rstrip('/')}/api/dataSets/{uid}/metadata.json"
        print(f"Fetching {district} ({uid})...", end=" ", flush=True)

        resp = session.get(url, timeout=60)
        if resp.status_code == 401:
            print("FAILED — invalid credentials")
            sys.exit(1)
        resp.raise_for_status()

        bundle = resp.json()
        de_count = len(bundle.get("dataElements", []))
        out_path = OUT_DIR / f"{district}.json"
        out_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        print(f"OK ({de_count} data elements → {out_path.name})")

    # Also copy datasets_elements.json if it exists in the parent workspace
    source_index = Path(__file__).parent.parent.parent / "claudeimihigo" / "datasets_elements.json"
    dest_index = OUT_DIR / "datasets_elements.json"
    if source_index.exists() and not dest_index.exists():
        dest_index.write_text(source_index.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Copied datasets_elements.json to {dest_index}")
    elif dest_index.exists():
        print(f"datasets_elements.json already present at {dest_index}")
    else:
        print(f"Warning: datasets_elements.json not found at {source_index}")
        print("         You can copy it manually to src/imihigo_dhis2_tools/data/")

    print(f"\nDone! {len(DATASET_IDS)} bundles written to {OUT_DIR}")
    print("Commit the data/ directory to include these bundles in the package.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Imihigo metadata from source DHIS2 instance")
    parser.add_argument("--url", default=os.getenv("DHIS2_BASE_URL"), help="Source DHIS2 base URL")
    parser.add_argument("--username", default=os.getenv("DHIS2_USERNAME"), help="Username")
    parser.add_argument("--password", default=os.getenv("DHIS2_PASSWORD"), help="Password")
    args = parser.parse_args()

    if not all([args.url, args.username, args.password]):
        parser.error("--url, --username, and --password are required (or set in .env)")

    extract(args.url, args.username, args.password)
