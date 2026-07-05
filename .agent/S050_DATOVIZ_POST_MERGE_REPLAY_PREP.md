# S050 Datoviz post-merge replay prep

Date: 2026-07-05

Mission: M230 - S050 Datoviz post-merge replay comparison prep

## Outcome

Prepared a GSP-side replay path for the Datoviz `api/pre-rc-cleanup` branch once it lands or
materially changes.

This does not edit Datoviz and does not unblock M222.

## New replay entry points

Generate a post-merge candidate pack and compare it to the committed pre-RC baseline:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_pre_rc_replay.sh
```

The wrapper runs:

1. `tools/datoviz_v04_smoke.py`
2. `tools/probe_datoviz_guide_axis.py`
3. `python -m gsp.qa.visual review-pack --suite s028 --mode datoviz-offscreen-opt-in`
4. `python -m gsp.qa.visual compare-matrix`

Default outputs:

- candidate review pack: `artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028/`
- guide-axis probe: `artifacts/visual_qa/s050/post_merge_datoviz_guide_axis/`
- comparison report:
  `artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028/comparison_to_pre_rc_baseline/`

The comparison baseline defaults to:

```text
artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/
```

## Comparison semantics

The new `python -m gsp.qa.visual compare-matrix` command compares two
`capability_matrix.json` files by `(backend, case_id)`.

It records:

- `improved`: status rank increases, for example `crashed` to `adapted` or `strict`;
- `regressed`: status rank decreases, for example `strict` to `crashed`;
- `changed`: same rank but changed status or reason code;
- `added` and `removed`: row-set differences;
- `unchanged`: identical status and reason code.

Status rank is intentionally conservative:

```text
not_run < crashed < disabled/unsupported < experimental < adapted < strict
```

## Acceptance

Focused validation passed:

```bash
python -m py_compile src/gsp/qa/visual/review_compare.py src/gsp/qa/visual/cli.py
```

```bash
.venv/bin/pytest -q \
  tests/test_visual_qa_harness.py::test_capability_matrix_comparison_reports_improvements_and_regressions \
  tests/test_visual_qa_harness.py::test_visual_review_pack_writes_matrix_and_index
```

Result: `2 passed`.

CLI self-comparison passed:

```bash
PYTHONPATH=. .venv/bin/python -m gsp.qa.visual compare-matrix \
  --baseline artifacts/visual_qa/s050/pre_rc_compat_s028_timeout \
  --candidate artifacts/visual_qa/s050/pre_rc_compat_s028_timeout \
  --out /tmp/gsp-pre-rc-self-compare
```

Result: `/tmp/gsp-pre-rc-self-compare/comparison.md`.

## Next use

After the Datoviz branch lands or changes, run the replay wrapper and inspect
`comparison_to_pre_rc_baseline/comparison.md`.

Promotion remains blocked unless the comparison and fresh runtime artifacts remove the relevant
M222/M228 blockers without introducing strict-row regressions.
