from __future__ import annotations

import questionary

from ..console import print_error, print_step, print_success, print_warning
from ..dhis2.client import DHIS2Client, DHIS2Error
from ..state import clear_state, load_state

DISTRICTS = ["BUGESERA", "GATSIBO", "KAYONZA", "KIREHE", "NGOMA", "NYAGATARE", "RWAMAGANA"]
SEED_PERIOD = "2024July"


def run(client: DHIS2Client) -> None:
    state = load_state()
    if state is None:
        print_warning("No .imihigo-state.json found. Nothing to clean.")
        return

    if state.target_url != client.base_url:
        print_warning(
            f"State file was created for {state.target_url}, but you're connected to {client.base_url}."
        )
        answer = questionary.confirm("Delete from the connected instance anyway?", default=False).ask()
        if not answer:
            return

    answer = questionary.confirm(
        f"This will delete all Imihigo datasets, data elements, and org units from {client.base_url}. Continue?",
        default=False,
    ).ask()
    if not answer:
        return

    skipped: list[str] = []

    # Step 1: delete seeded data values
    if state.seeded:
        print_step("Deleting seeded data values...")
        for district in DISTRICTS:
            ou_uid = state.org_units.get(district)
            ds_uid = _district_to_dataset(district)
            if ou_uid and ds_uid:
                try:
                    client.delete_data_values(ds_uid, ou_uid, SEED_PERIOD)
                    print_success(f"  Deleted data values for {district}")
                except DHIS2Error as e:
                    print_warning(f"  Could not delete data values for {district}: {e}")
                    skipped.append(f"data values / {district}")

    # Step 2: un-assign org units from datasets
    print_step("Clearing dataset → org unit assignments...")
    for ds_uid in state.dataset_uids:
        try:
            client.put(f"/api/dataSets/{ds_uid}", {"organisationUnits": []})
        except DHIS2Error as e:
            print_warning(f"  Could not clear assignments for dataset {ds_uid}: {e}")

    # Step 3: delete datasets
    print_step("Deleting datasets...")
    for ds_uid in state.dataset_uids:
        try:
            client.delete(f"/api/dataSets/{ds_uid}")
            print_success(f"  Deleted dataset {ds_uid}")
        except DHIS2Error as e:
            print_warning(f"  Could not delete dataset {ds_uid}: {e}")
            skipped.append(f"dataset/{ds_uid}")

    # Step 4: delete sections
    print_step(f"Deleting {len(state.section_uids)} sections...")
    for uid in state.section_uids:
        try:
            client.delete(f"/api/sections/{uid}")
        except DHIS2Error:
            pass  # sections often cascade-deleted with datasets

    # Step 5: delete data elements
    print_step(f"Deleting {len(state.data_element_uids)} data elements...")
    de_skipped = 0
    for uid in state.data_element_uids:
        try:
            client.delete(f"/api/dataElements/{uid}")
        except DHIS2Error as e:
            if e.status_code == 409:
                de_skipped += 1  # referenced elsewhere — expected for shared elements
            else:
                skipped.append(f"dataElement/{uid}")

    if de_skipped:
        print_warning(f"  {de_skipped} data elements skipped (referenced by other objects)")
    else:
        print_success(f"  Deleted {len(state.data_element_uids)} data elements")

    # Step 6: delete district org units
    print_step("Deleting district org units...")
    for district in DISTRICTS:
        uid = state.org_units.get(district)
        if not uid:
            continue
        try:
            client.delete(f"/api/organisationUnits/{uid}")
            print_success(f"  Deleted {district} ({uid})")
        except DHIS2Error as e:
            print_warning(f"  Could not delete {district}: {e}")
            skipped.append(f"orgUnit/{district}")

    # Step 7: delete Eastern Province / Rwanda only if we created them
    for name in ["Eastern Province", "Rwanda"]:
        uid = state.org_units.get(name)
        if uid and uid in state.created_org_units:
            try:
                client.delete(f"/api/organisationUnits/{uid}")
                print_success(f"  Deleted '{name}' ({uid})")
            except DHIS2Error as e:
                print_warning(f"  Could not delete '{name}': {e}")
                skipped.append(f"orgUnit/{name}")
        elif uid:
            print_warning(f"  '{name}' was reused (not created by this tool), leaving it in place")

    # Step 8: clear state
    clear_state()

    if skipped:
        print_warning(f"Clean complete with {len(skipped)} items skipped: {', '.join(skipped[:5])}")
    else:
        print_success("Clean complete. .imihigo-state.json removed.")


def _district_to_dataset(district: str) -> str | None:
    from .install import DISTRICT_TO_DATASET
    return DISTRICT_TO_DATASET.get(district)
