import importlib.resources as pkg_resources
import json

DISTRICT_NAMES = ["BUGESERA", "GATSIBO", "KAYONZA", "KIREHE", "NGOMA", "NYAGATARE", "RWAMAGANA"]

MERGEABLE_COLLECTIONS = [
    "dataElements",
    "dataElementGroups",
    "dataElementGroupSets",
    "categoryOptions",
    "categories",
    "categoryCombos",
    "categoryOptionCombos",
    "sections",
    "dataSets",
    "indicators",
    "indicatorTypes",
    "legendSets",
    "attributes",
    "trackedEntityAttributes",
    "optionSets",
    "options",
]


def load_bundle(district: str) -> dict:
    ref = pkg_resources.files("imihigo_dhis2_tools.data") / f"{district}.json"
    return json.loads(ref.read_text(encoding="utf-8"))


def load_elements_index() -> dict:
    ref = pkg_resources.files("imihigo_dhis2_tools.data") / "datasets_elements.json"
    return json.loads(ref.read_text(encoding="utf-8"))


def merge_bundles() -> tuple[dict, list[str], list[str]]:
    """
    Merge all 7 district metadata bundles into one deduplicated payload.

    Returns:
        (merged_bundle, data_element_uids, section_uids)
    """
    merged: dict[str, dict] = {key: {} for key in MERGEABLE_COLLECTIONS}

    for district in DISTRICT_NAMES:
        bundle = load_bundle(district)
        for collection in MERGEABLE_COLLECTIONS:
            for obj in bundle.get(collection, []):
                uid = obj.get("id")
                if uid and uid not in merged[collection]:
                    merged[collection][uid] = obj

    # Convert dicts back to lists
    result: dict[str, list] = {k: list(v.values()) for k, v in merged.items()}

    # Strip org units entirely — install assigns target OUs after import
    result.pop("organisationUnits", None)

    # Clear dataset organisationUnits — source OUs don't exist on target
    for ds in result.get("dataSets", []):
        ds["organisationUnits"] = []

    data_element_uids = [obj["id"] for obj in result.get("dataElements", [])]
    section_uids = [obj["id"] for obj in result.get("sections", [])]

    return result, data_element_uids, section_uids
