from __future__ import annotations

import random
from datetime import datetime, timezone

import questionary

from ..console import print_error, print_step, print_success, print_warning
from ..dhis2.client import DHIS2Client, DHIS2Error
from ..dhis2.metadata import load_elements_index
from ..state import load_state, save_state

SEED_PERIOD = "2024July"

# Source dataset UIDs (same as install constants, avoids circular import)
DISTRICT_TO_DATASET: dict[str, str] = {
    "BUGESERA":  "m16tH53PKTq",
    "GATSIBO":   "IclTerKK5vZ",
    "KAYONZA":   "R5rTjEx1PsA",
    "KIREHE":    "NUa3VpZcAur",
    "NGOMA":     "sVdCdZRwyP0",
    "NYAGATARE": "LtSqjIdsDwl",
    "RWAMAGANA": "HBk9ysphONu",
}

# Maps district name to the source dataset ID key in datasets_elements.json
DISTRICT_TO_SOURCE_ID: dict[str, str] = {
    "BUGESERA":  "m16tH53PKTq",
    "GATSIBO":   "IclTerKK5vZ",
    "KAYONZA":   "R5rTjEx1PsA",
    "KIREHE":    "NUa3VpZcAur",
    "NGOMA":     "sVdCdZRwyP0",
    "NYAGATARE": "LtSqjIdsDwl",
    "RWAMAGANA": "HBk9ysphONu",
}


def _is_target(name: str) -> bool:
    n = name.lower()
    return "target" in n and "achiev" not in n


def run(client: DHIS2Client) -> None:
    state = load_state()
    if state is None:
        print_error("Not installed. Run 'install' first.")
        return
    if state.target_url != client.base_url:
        print_error(f"State was created for {state.target_url}. Connect to that instance to seed.")
        return
    if state.seeded:
        answer = questionary.confirm("Already seeded. Re-seed and overwrite existing data?", default=False).ask()
        if not answer:
            return

    elements_index = load_elements_index()
    print_step(f"Seeding demo data for period {SEED_PERIOD}...")

    for district, dataset_uid in DISTRICT_TO_DATASET.items():
        ou_uid = state.org_units.get(district)
        if not ou_uid:
            print_warning(f"  No org unit UID for {district}, skipping")
            continue

        source_id = DISTRICT_TO_SOURCE_ID[district]
        elements = elements_index.get(source_id, {}).get("elements", [])

        if not elements:
            print_warning(f"  No elements found for {district}, skipping")
            continue

        data_values = []
        for element in elements:
            if _is_target(element["name"]):
                value = random.randint(500, 1000)
            else:
                base = random.randint(500, 1000)
                value = int(base * random.uniform(0.70, 0.90))
            data_values.append({"dataElement": element["id"], "value": str(value)})

        payload = {
            "dataSet": dataset_uid,
            "orgUnit": ou_uid,
            "period": SEED_PERIOD,
            "dataValues": data_values,
        }

        try:
            client.post_data_values(payload)
            print_success(f"  {district}: {len(data_values)} data values seeded")
        except DHIS2Error as e:
            print_warning(f"  {district}: seed failed — {e}")

    state.seeded = True
    state.seeded_at = datetime.now(timezone.utc).isoformat()
    save_state(state)
    print_success("Seed complete!")
