# S050 Datoviz offscreen batch crash isolation

Date: 2026-07-04

Mission: M217 - S050 Datoviz offscreen batch crash isolation

## Outcome

Completed with a GSP QA-harness isolation fix and a narrowed Datoviz/native lifecycle
classification.

The current local Datoviz v0.4-dev checkout still reproduces the combined five-case TextVisual
batch crash as a child-process signal 11. Direct child probes show that most affected single-case
TextVisual runs write complete PNG and `report.json` artifacts before the Python process segfaults
during garbage collection with no Python frame. This points at Datoviz/native teardown behavior, not
a Python-level visual semantic failure.

GSP now runs `datoviz-offscreen-opt-in` review packs one Datoviz child process per selected case. A
complete child report is preserved even if native teardown crashes after report generation, and the
parent records an explicit `*.child_teardown_crash.json` warning artifact for that case. Child runs
that crash before producing a complete report remain structured crash rows.

No public visual/query semantics changed. No sibling Datoviz files were edited.

## Evidence

Reproduced combined batch crash:

- artifact: `artifacts/visual_qa/s050/m217-dataviz-offscreen-batch-crash/`
- result: parent completed, Datoviz child signal 11, all five rows recorded as structured crash rows

Direct sequence probes:

- artifact: `artifacts/visual_qa/s050/m217-dataviz-offscreen-sequences/`
- `text/anchor_grid_ndc` single-case child exited cleanly
- `text/basic_ndc`, `text/rotation_alpha_ndc`, `text/data_vs_ndc`, and
  `text/multiline_unicode_smoke` single-case children wrote rendered artifacts and complete reports,
  then exited with signal 11
- `PYTHONFAULTHANDLER=1` on `text/basic_ndc` reported segmentation fault while garbage-collecting,
  with no Python frame

Updated per-case review-pack run:

- artifact: `artifacts/visual_qa/s050/m217-dataviz-offscreen-per-case/`
- strategy: `one_process_per_case`

| Case | Datoviz row | Teardown evidence |
|---|---|---|
| `text/basic_ndc` | rendered / adapted | yes |
| `text/anchor_grid_ndc` | rendered / adapted | no |
| `text/rotation_alpha_ndc` | rendered / strict | yes |
| `text/data_vs_ndc` | rendered / adapted | yes |
| `text/multiline_unicode_smoke` | rendered / adapted | yes |

The strict/adapted classification is unchanged from the prior TextVisual strictness proof: only the
bounded `text/rotation_alpha_ndc` row remains strict.

Local Datoviz checkout used read-only:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `a9492af6526fbb722e2c0783811758f1b15be10e`
- imported module: `/home/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`

## Decision

Keep Datoviz offscreen review packs isolated one case per child process. Treat post-report native
teardown segfaults as stability evidence, not as grounds to discard complete rendered artifacts.

Do not broaden Datoviz TextVisual strictness. Do not treat this as a Datoviz API compatibility issue
inside GSP, and do not add legacy aliases or compatibility shims.

## Validation

Passed:

```bash
PYTHONPATH=src uv run python -m pytest \
  tests/test_visual_qa_harness.py \
  -k 'datoviz_offscreen_review_pack' -q
```

Result: `4 passed, 35 deselected`.

Passed:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s024 \
  --case text/basic_ndc \
  --case text/anchor_grid_ndc \
  --case text/rotation_alpha_ndc \
  --case text/data_vs_ndc \
  --case text/multiline_unicode_smoke \
  --out artifacts/visual_qa/s050/m217-dataviz-offscreen-per-case \
  --run-id s050-m217-textvisual-per-case
```

Result: parent exit code `0`, all five Datoviz rows rendered, and teardown-crash evidence recorded
for four rows.
