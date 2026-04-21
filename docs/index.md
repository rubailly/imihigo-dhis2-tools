# Imihigo DHIS2 Datasets

**Imihigo** (imihigo in Kinyarwanda — meaning "performance contracts") is Rwanda's system of local government accountability. Each district signs an annual contract with the President committing to specific, measurable targets across health, agriculture, infrastructure, social protection, and governance. Progress is tracked quarterly.

This project provides a **CLI tool and pre-bundled metadata** to set up all Imihigo datasets for the seven districts of **Eastern Province** on any DHIS2 instance — creating the full org unit hierarchy, importing all ~1,874 data elements, and optionally seeding demo data.

---

## Coverage

| | |
|---|---|
| **Province** | Eastern Province, Rwanda |
| **Districts** | 7 (Bugesera, Gatsibo, Kayonza, Kirehe, Ngoma, Nyagatare, Rwamagana) |
| **Fiscal year** | 2024–2025 (July–June) |
| **Unique data elements** | 1,874 |
| **Total element slots** | 7,824 (across all 7 datasets) |
| **Reporting periods** | Quarterly (Q1–Q4) within the fiscal year |

---

## Structure of each dataset

Every dataset follows the same two-column pattern:

=== "Target indicators"
    Set at the beginning of the fiscal year — what the district commits to achieve.
    Labelled with the suffix **Target** in each element name.

    > *e.g. "Family Planning (FP) services provided — Q2 Target"*

=== "Achievement indicators"
    Reported each quarter — actual results against the target.
    Labelled with the suffix **Achieved** in each element name.

    > *e.g. "Family Planning (FP) services provided — Q2 Achieved"*

Sectors covered include **agriculture**, **health & WASH**, **social protection**, **infrastructure**, **governance**, and **education**.

---

## Quick start

```bash
pip install imihigo-dhis2-tools

# Interactive mode — prompts for your DHIS2 URL and credentials
imihigo

# Or non-interactively
imihigo --url https://your-dhis2.org --username admin --password secret install
```

See the [CLI Reference](cli.md) for full usage, or jump straight to the [Datasets Overview](datasets/index.md).

---

## Repository layout

```
src/imihigo_dhis2_tools/data/
├── BUGESERA.json     ← full metadata bundle (datasets, elements, categories)
├── GATSIBO.json
├── KAYONZA.json
├── KIREHE.json
├── NGOMA.json
├── NYAGATARE.json
└── RWAMAGANA.json
```

Each JSON file is a complete DHIS2 metadata export produced by `GET /api/dataSets/{id}/metadata.json` and can be imported directly into any DHIS2 instance via `POST /api/metadata`.
