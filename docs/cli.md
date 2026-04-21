# CLI Reference

The `imihigo` command-line tool installs, seeds, and cleans up Imihigo datasets on any DHIS2 instance.

---

## Installation

```bash
pip install imihigo-dhis2-tools
```

Or from source:

```bash
git clone https://github.com/rubailly/imihigo-dhis2-tools
cd imihigo-dhis2-tools
pip install -e .
```

---

## Credentials

Credentials can be supplied in three ways (in order of precedence):

=== "Flags"
    ```bash
    imihigo --url https://your-dhis2.org --username admin --password secret install
    ```

=== ".env file"
    Create a `.env` file in your working directory:
    ```
    DHIS2_BASE_URL=https://your-dhis2.org
    DHIS2_USERNAME=admin
    DHIS2_PASSWORD=secret
    ```
    Then just run `imihigo install`.

=== "Environment variables"
    ```bash
    export DHIS2_BASE_URL=https://your-dhis2.org
    export DHIS2_USERNAME=admin
    export DHIS2_PASSWORD=secret
    imihigo install
    ```

---

## Interactive mode

Running `imihigo` with no arguments launches an interactive menu that prompts for credentials and then presents the available commands:

```
Imihigo DHIS2 Tools
Manage Eastern Province Imihigo datasets on any DHIS2 instance

? DHIS2 URL: https://your-dhis2.org
? Username: admin
? Password: ****

✓ Connected: DHIS2 v40.2.2 (your-dhis2.org)

? What would you like to do?
  > install  — Create org units and import all dataset metadata
    seed     — Seed demo data values into installed datasets
    clean    — Remove everything this tool created
    exit
```

---

## Commands

### `install`

Creates the org unit hierarchy and imports all dataset metadata.

```bash
imihigo install
# or
imihigo --url URL --username USER --password PASS install
```

**What it does:**

1. Checks for an existing installation (`.imihigo-state.json` in the current directory)
2. Finds or creates **Rwanda** and **Eastern Province** org units
3. Creates the seven **district** org units as children of Eastern Province
4. Imports the merged metadata bundle (~1,874 data elements, 7 datasets)
5. Assigns each dataset to its district org unit
6. Saves `.imihigo-state.json` to track everything created

!!! warning "Re-installing"
    If `.imihigo-state.json` already exists for the target instance, `install` will warn and exit. Run `clean` first to reset.

---

### `seed`

Populates demo data values into the installed datasets.

```bash
imihigo seed
```

**What it does:**

- Requires `install` to have run first (reads `.imihigo-state.json`)
- Generates random plausible values for period `2024July`:
    - **Target** indicators: random integer 500–1,000
    - **Achievement** indicators: random integer at 70–90% of a target baseline
- Posts one data value set per district via `POST /api/dataValueSets`

!!! info "Re-seeding"
    Running `seed` again will prompt for confirmation before overwriting existing values.

---

### `clean`

Removes everything created by `install` and `seed`.

```bash
imihigo clean
```

**What it does (in order):**

1. Deletes seeded data values (if `seed` was run)
2. Clears dataset → org unit assignments
3. Deletes the 7 datasets
4. Deletes all data elements
5. Deletes the 7 district org units
6. Deletes Eastern Province and Rwanda **only if this tool created them** (not if they were pre-existing)
7. Removes `.imihigo-state.json`

!!! danger "Destructive operation"
    `clean` will prompt for confirmation before deleting anything. This action cannot be undone.

---

## State file

The tool writes `.imihigo-state.json` in the **current working directory**. It records every UID created so that `clean` knows exactly what to remove.

```json
{
  "target_url": "https://your-dhis2.org",
  "installed_at": "2025-01-15T09:30:00+00:00",
  "org_units": {
    "Rwanda": "uid...",
    "Eastern Province": "uid...",
    "BUGESERA": "uid...",
    ...
  },
  "created_org_units": ["uid...", ...],
  "dataset_uids": ["m16tH53PKTq", ...],
  "data_element_uids": ["uid...", ...],
  "section_uids": [],
  "seeded": false,
  "seeded_at": null
}
```

!!! tip
    Run `install` and `clean` from the **same directory** so the tool can find the state file.

---

## Refreshing metadata bundles

The JSON bundles in `src/imihigo_dhis2_tools/data/` were extracted from the source DHIS2 instance. To re-extract (e.g. after the source datasets are updated):

```bash
# Set source credentials in .env, then:
python scripts/extract.py
```

Commit the updated JSON files and push.
