from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

STATE_FILE = Path(".imihigo-state.json")


@dataclass
class ImihingoState:
    target_url: str
    installed_at: str
    org_units: dict[str, str]
    created_org_units: list[str]
    dataset_uids: list[str]
    data_element_uids: list[str]
    section_uids: list[str]
    seeded: bool = False
    seeded_at: str | None = None


def save_state(state: ImihingoState) -> None:
    STATE_FILE.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")


def load_state() -> ImihingoState | None:
    if not STATE_FILE.exists():
        return None
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return ImihingoState(**data)


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
