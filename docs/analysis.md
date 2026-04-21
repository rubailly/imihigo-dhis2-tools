# Data Elements Analysis

This page breaks down the 1,874 unique data elements across all seven datasets — what's shared, what differs, and how indicators are structured.

---

## Element counts per district

| District | Total elements | Target | Achieved |
|---|---|---|---|
| Bugesera | 1,160 | 580 | 580 |
| Gatsibo | 1,088 | 544 | 544 |
| Kayonza | 1,200 | 588 | 612 |
| Kirehe | 1,104 | 552 | 552 |
| Ngoma | 1,080 | 540 | 540 |
| Nyagatare | 1,144 | 544 | 600 |
| Rwamagana | 1,048 | 524 | 524 |
| **Unique across all** | **1,874** | | |

!!! note "Why counts differ"
    Districts with asymmetric target/achieved counts (Kayonza, Nyagatare) have some multi-quarter achievement indicators that don't have a strict 1:1 pairing with a single target element. This reflects local reporting commitments agreed in their individual Imihigo contracts.

---

## Sharing across districts

| Scope | Element count | % of total |
|---|---|---|
| Present in **all 7** districts | 703 | 37.5 % |
| Present in **2–6** districts | 498 | 26.6 % |
| **Unique** to a single district | 673 | 35.9 % |
| **Total unique** | **1,874** | 100 % |

### What the shared core covers

The 703 elements common to all seven districts represent the **national Imihigo framework** — indicators every district must track regardless of local priorities. These include:

- Family planning and community health worker targets
- Livestock vaccination campaigns (PPR, FMD, LSD by species)
- Fertilizer distribution and improved seed adoption
- VUP (Vision 2020 Umurenge Programme) social protection transfers
- Girinka (one-cow-per-poor-family) programme delivery
- Land consolidation and crop insurance coverage
- Water supply system functionality rates
- Governance indicators (legal case processing, audits)

### District-specific indicators

The 673 elements unique to a single district reflect **local commitments** negotiated in each district's contract. Examples include:

- Hospital construction phases (specific to districts with active infrastructure projects)
- Specialised irrigation schemes (district-specific water systems)
- Local economic zone targets
- District-specific public works programmes

---

## Indicator naming convention

All element names follow a structured pattern that encodes sector, metric, quarter, and type:

```
<Metric description> - Q<1|2|3|4> <Target|Achieved|Actual>
```

**Examples:**

| Element name | Quarter | Type |
|---|---|---|
| `Family Planning (FP) services provided - Q1 Target` | Q1 | Target |
| `Family Planning (FP) services provided - Q1 Achieved` | Q1 | Achievement |
| `Number of Livestock Vaccinated - PPR Sheep - Q3 - Target` | Q3 | Target |
| `Ha of land irrigated using Small scale irrigation technologies - Q2 target` | Q2 | Target |
| `Percentage of operational public water taps on functional water supply systems in Q4 Target` | Q4 | Target |

!!! tip "Filtering by quarter"
    To isolate a specific quarter's data, filter element names containing `Q1`, `Q2`, `Q3`, or `Q4`. To compare only targets vs achievements, filter on the trailing word `Target` or `Achieved`.

---

## Sectors at a glance

| Sector | Key themes |
|---|---|
| **Agriculture** | Livestock vaccination (PPR, FMD, LSD, Brucellosis), land consolidation, fertilizer use, improved seeds, irrigation, crop & plantation insurance |
| **Health & WASH** | Family planning, community health worker coverage, CBHI enrolment, water supply functionality, hospital construction |
| **Social Protection** | VUP direct support & public works, Girinka programme, support for people with disabilities (PwDs) |
| **Infrastructure** | Road rehabilitation, water supply construction, public building upgrades |
| **Governance** | Legal case processing (IECMS), risk-based audits, civil registration, biometric data capture |
| **Education** | School construction, enrolment rates, teacher training |

---

## Using the data

### Import to any DHIS2 instance

```bash
# Install the tool and run
pip install imihigo-dhis2-tools
imihigo install
```

See the [CLI Reference](cli.md) for full options.

### Direct metadata import (API)

Each district's full metadata bundle (datasets, data elements, category combos) is available as a single JSON file importable via the DHIS2 metadata API:

```bash
curl -X POST "https://your-dhis2.org/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE" \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d @BUGESERA.json
```

Download links for individual district bundles are on each [dataset page](datasets/index.md).
