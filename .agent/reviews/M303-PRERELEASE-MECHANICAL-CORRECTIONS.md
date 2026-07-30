# M303 pre-release mechanical corrections

Date: 2026-07-30

## Outcome

All non-architectural M302 publication blockers are resolved.

## Integrated commits

- GSP implementation and packaging: `aee00ca`
- GSP qualification: `e667c30`
- VisPy2 implementation and packaging: `c60d994`
- VisPy2 qualification: `dd69947`

## Corrections

- Replaced the Matplotlib exact-pixel-count test with normalized semantic mesh-footprint and
  face-representation assertions.
- Corrected the stale Datoviz DATA-space image changelog boundary.
- Added Markdown long descriptions, SPDX `BSD-3-Clause`, packaged license files, project URLs,
  authors, classifiers, and typing classifiers to all distributions.
- Added the GSP changelog.
- Defined `gsp-core`, `gsp-matplotlib`, and `vispy2[matplotlib]` as the intended first ordinary
  publication set.
- Removed the unresolved `vispy2[datoviz]` extra and kept `gsp-datoviz` explicitly
  development-only.
- Made cross-provider conformance skip cleanly when the optional Datoviz adapter is not installed.
- Refreshed release-facing backend evidence and committed qualification records.

## Evidence

| Gate | Result |
|---|---|
| complete GSP source pytest | 804 passed |
| complete VisPy2 source pytest on Matplotlib 3.11.1 | 124 passed |
| strict mypy | GSP 51 files; VisPy2 3 files clean |
| Ruff | clean |
| documentation validation | 30 Python blocks; 64 local links |
| strict MkDocs | pass with known informational checkout-link notices |
| isolated three-package environment | 628 passed; one Datoviz-only conformance module skipped |
| installed semantic example | pass |
| wheels and sdists | all built |
| Twine | all artifacts passed without warnings |
| wheel contents | all passed |
| licenses | SPDX metadata and LICENSE present in every wheel |

M303 does not resolve the canonical Panel contract or producer capability namespace. Those remain
correctly blocked on P038 under M304.
