# Datasets Overview

All seven datasets cover the **2024–2025 fiscal year** (July 2024 – June 2025) and use the **FinancialJuly** period type. Each dataset is scoped to one district and tracks quarterly targets and achievements across all Imihigo performance areas.

---

## Summary table

| District | Dataset UID | Data Elements | Target | Achieved | Raw JSON |
|---|---|---|---|---|---|
| [Bugesera](bugesera.md) | `m16tH53PKTq` | 1,160 | 580 | 580 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/BUGESERA.json){ .md-button } |
| [Gatsibo](gatsibo.md) | `IclTerKK5vZ` | 1,088 | 544 | 544 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/GATSIBO.json){ .md-button } |
| [Kayonza](kayonza.md) | `R5rTjEx1PsA` | 1,200 | 588 | 612 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/KAYONZA.json){ .md-button } |
| [Kirehe](kirehe.md) | `NUa3VpZcAur` | 1,104 | 552 | 552 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/KIREHE.json){ .md-button } |
| [Ngoma](ngoma.md) | `sVdCdZRwyP0` | 1,080 | 540 | 540 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/NGOMA.json){ .md-button } |
| [Nyagatare](nyagatare.md) | `LtSqjIdsDwl` | 1,144 | 544 | 600 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/NYAGATARE.json){ .md-button } |
| [Rwamagana](rwamagana.md) | `HBk9ysphONu` | 1,048 | 524 | 524 | [↓ Download](https://raw.githubusercontent.com/rubailly/imihigo-dhis2-tools/master/src/imihigo_dhis2_tools/data/RWAMAGANA.json){ .md-button } |
| **Total (unique)** | | **1,874** | | | |

---

## Element sharing across districts

A large share of indicators are common to all districts — they represent the national Imihigo framework. The remainder are district-specific commitments.

| Scope | Count | Share |
|---|---|---|
| Shared across **all 7** districts | 703 | 37.5 % |
| Shared across **2–6** districts | 498 | 26.6 % |
| **Unique** to a single district | 673 | 35.9 % |
| **Total unique elements** | **1,874** | 100 % |

!!! info "What this means"
    Any analysis across districts can rely on the 703 common elements as a **comparable core**. The 673 district-specific elements reflect local priorities and should be interpreted per district.

---

## Org unit hierarchy

When you run `imihigo install`, the following hierarchy is created on the target instance:

```
Rwanda  (level 1)
└── Eastern Province  (level 2)
    ├── Bugesera   (level 3)
    ├── Gatsibo    (level 3)
    ├── Kayonza    (level 3)
    ├── Kirehe     (level 3)
    ├── Ngoma      (level 3)
    ├── Nyagatare  (level 3)
    └── Rwamagana  (level 3)
```

If **Rwanda** or **Eastern Province** already exist on the target instance, they are reused. The seven district org units are always created fresh and assigned to their respective datasets.
