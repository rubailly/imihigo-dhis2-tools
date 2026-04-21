from __future__ import annotations

from datetime import datetime, timezone

from ..console import make_spinner, print_error, print_import_summary, print_step, print_success, print_warning
from ..dhis2.client import DHIS2Client, DHIS2Error
from ..dhis2.metadata import merge_bundles
from ..state import ImihingoState, load_state, save_state

DISTRICT_TO_DATASET: dict[str, str] = {
    "BUGESERA":  "m16tH53PKTq",
    "GATSIBO":   "IclTerKK5vZ",
    "KAYONZA":   "R5rTjEx1PsA",
    "KIREHE":    "NUa3VpZcAur",
    "NGOMA":     "sVdCdZRwyP0",
    "NYAGATARE": "LtSqjIdsDwl",
    "RWAMAGANA": "HBk9ysphONu",
}

ORG_UNIT_SPECS: dict[str, dict] = {
    "Rwanda": {
        "shortName": "Rwanda",
        "openingDate": "1960-01-01",
        "parent": None,
    },
    "Eastern Province": {
        "shortName": "Eastern",
        "openingDate": "1960-01-01",
        "parent": "Rwanda",
    },
    "BUGESERA":  {"shortName": "Bugesera",  "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "GATSIBO":   {"shortName": "Gatsibo",   "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "KAYONZA":   {"shortName": "Kayonza",   "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "KIREHE":    {"shortName": "Kirehe",    "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "NGOMA":     {"shortName": "Ngoma",     "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "NYAGATARE": {"shortName": "Nyagatare", "openingDate": "1960-01-01", "parent": "Eastern Province"},
    "RWAMAGANA": {"shortName": "Rwamagana", "openingDate": "1960-01-01", "parent": "Eastern Province"},
}


def run(client: DHIS2Client) -> None:
    existing = load_state()
    if existing and existing.target_url == client.base_url:
        print_warning("Already installed on this instance. Run 'clean' first to reinstall.")
        return

    ou_uids: dict[str, str] = {}
    created_ou_uids: list[str] = []

    # Step 1: org units
    print_step("Setting up org unit hierarchy...")
    try:
        for name, spec in ORG_UNIT_SPECS.items():
            is_district = spec["parent"] == "Eastern Province"
            reusable = not is_district  # Rwanda and Eastern Province may already exist

            if reusable:
                existing_ou = client.get_org_unit_by_name(name)
                if existing_ou:
                    ou_uids[name] = existing_ou["id"]
                    print_warning(f"  Found existing '{name}' ({existing_ou['id']}), reusing it")
                    continue

            payload: dict = {
                "name": name,
                "shortName": spec["shortName"],
                "openingDate": spec["openingDate"],
            }
            parent_name = spec["parent"]
            if parent_name:
                payload["parent"] = {"id": ou_uids[parent_name]}

            uid = client.post_org_unit(payload)
            ou_uids[name] = uid
            created_ou_uids.append(uid)
            print_success(f"  Created '{name}' ({uid})")

    except DHIS2Error as e:
        print_error(f"Failed creating org units: {e}")
        # Save partial state so clean can roll back what was created
        _save_partial(client, ou_uids, created_ou_uids)
        return

    # Step 2: merge and import metadata
    print_step("Merging metadata bundles...")
    bundle, de_uids, section_uids = merge_bundles()
    print_success(
        f"  Merged: {len(bundle.get('dataElements', []))} data elements, "
        f"{len(bundle.get('dataSets', []))} datasets, "
        f"{len(bundle.get('sections', []))} sections"
    )

    print_step("Importing metadata to DHIS2 (this may take a moment)...")
    try:
        with make_spinner("Importing...") as progress:
            progress.add_task("")
            result = client.import_metadata(bundle)
    except DHIS2Error as e:
        print_error(f"Metadata import failed: {e}")
        _save_partial(client, ou_uids, created_ou_uids)
        return

    status = result.get("status", "")
    if status == "ERROR":
        print_error(f"Import returned ERROR status:\n{result}")
        _save_partial(client, ou_uids, created_ou_uids)
        return

    print_import_summary(result)

    # Step 3: assign org units to datasets
    print_step("Assigning org units to datasets...")
    for district, dataset_uid in DISTRICT_TO_DATASET.items():
        ou_uid = ou_uids.get(district)
        if not ou_uid:
            print_warning(f"  No OU uid found for {district}, skipping assignment")
            continue
        try:
            client.assign_org_unit_to_dataset(dataset_uid, ou_uid)
            print_success(f"  {district} → {dataset_uid}")
        except DHIS2Error as e:
            print_warning(f"  Could not assign {district}: {e}")

    # Step 4: save state
    state = ImihingoState(
        target_url=client.base_url,
        installed_at=datetime.now(timezone.utc).isoformat(),
        org_units=ou_uids,
        created_org_units=created_ou_uids,
        dataset_uids=list(DISTRICT_TO_DATASET.values()),
        data_element_uids=de_uids,
        section_uids=section_uids,
    )
    save_state(state)
    print_success("Installation complete! State saved to .imihigo-state.json")


def _save_partial(client: DHIS2Client, ou_uids: dict, created_ou_uids: list) -> None:
    state = ImihingoState(
        target_url=client.base_url,
        installed_at=datetime.now(timezone.utc).isoformat(),
        org_units=ou_uids,
        created_org_units=created_ou_uids,
        dataset_uids=[],
        data_element_uids=[],
        section_uids=[],
    )
    save_state(state)
    print_warning("Partial state saved — run 'clean' to roll back created objects.")
