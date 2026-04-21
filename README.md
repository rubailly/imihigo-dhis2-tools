# Imihigo DHIS2 Tools

A CLI tool to set up [Imihigo](https://www.risa.rw/programs/imihigo) (performance contract) datasets for Eastern Province, Rwanda on any DHIS2 instance.

## What it does

- **install** — creates the org unit hierarchy (Rwanda → Eastern Province → 7 Districts) and imports all dataset metadata (~1,874 data elements across 7 datasets)
- **seed** — populates demo data values for the installed datasets
- **clean** — removes everything the tool created, leaving the instance as it was

The 7 districts covered: Bugesera, Gatsibo, Kayonza, Kirehe, Ngoma, Nyagatare, Rwamagana.

## Requirements

- Python 3.11+
- Access to a DHIS2 instance (v2.36+) with admin credentials

## Installation

```bash
pip install imihigo-dhis2-tools
```

Or from source:

```bash
git clone https://github.com/your-org/imihigo-dhis2-tools
cd imihigo-dhis2-tools
pip install -e .
```

## Usage

### Interactive mode

```bash
imihigo
```

Prompts for URL, username, and password, then shows a menu.

### Command-line mode

```bash
# Install
imihigo --url https://your-dhis2.org --username admin --password secret install

# Seed demo data
imihigo --url https://your-dhis2.org --username admin --password secret seed

# Clean up
imihigo --url https://your-dhis2.org --username admin --password secret clean
```

### Using a `.env` file

```bash
cp .env.example .env
# Edit .env with your credentials
imihigo install
```

## State tracking

The tool writes `.imihigo-state.json` in the current directory to track what was created. Run `clean` from the same directory to remove everything.

## For developers: refreshing metadata bundles

The pre-bundled metadata in `src/imihigo_dhis2_tools/data/` was extracted from the source DHIS2 instance. To re-extract:

```bash
# Set source credentials in .env, then:
python scripts/extract.py
```

Commit the updated JSON files.
