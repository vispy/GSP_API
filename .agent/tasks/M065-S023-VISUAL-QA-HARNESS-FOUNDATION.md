# M065-S023-VISUAL-QA-HARNESS-FOUNDATION - Visual QA harness foundation

## Mission

M065

## Goal

Create the repeatable manual visual QA workflow before adding new visual families. The harness
should initially use existing Point/Image protocol scenes and prove artifact layout, report schema,
contact sheets, and Datoviz unsupported handling.

## Required Inputs

- Completed M064 probe module/report contract.
- `.agent/consultations/P008-response.md`, especially sections 3 and 8.

## Target CLI Shape

Implement a practical subset first:

```bash
python -m gsp.qa.visual list --suite s023
python -m gsp.qa.visual run --suite s023 --backends matplotlib,datoviz-v04 --out artifacts/visual_qa/s023/dev --contact-sheet
```

Optional flags from P008 can be deferred unless simple:

```text
--case
--strict
--allow-unsupported datoviz-v04
--resolution 800x600
--seed 1234
--write-scene-json
--write-scene-npz
```

## Artifact Layout

Use this shape unless local project conventions suggest a small adjustment:

```text
artifacts/visual_qa/s023/<run_id>/
  run_manifest.json
  environment.json
  report.json
  summary.md
  manual_notes.yaml
  scenes/
    point_basic_ndc.scene.json
    point_basic_ndc.arrays.npz
  backends/
    matplotlib/
      point_basic_ndc.png
      point_basic_ndc.log.txt
    datoviz-v04/
      point_basic_ndc.png
      point_basic_ndc.unsupported.json
      point_basic_ndc.log.txt
  contact_sheets/
    point_basic_ndc.png
    s023_all_cases.png
  notes/
    point_basic_ndc.md
```

## Initial Cases

- `point/basic_ndc`: small colored point set with known positions and diameters.
- `point/diameter_ramp_ndc`: several points at fixed positions with increasing pixel diameters.
- `image/checker_nearest_ndc`: tiny checkerboard image, nearest interpolation, explicit extent.
- `overlay/point_over_image_ndc`: point/image ordering and alpha check.

## Report Requirements

`report.json` must include:

- schema version;
- stage;
- run id/time;
- environment summary;
- M064 Datoviz probe summary;
- per-case scene paths;
- required features;
- per-backend status: `rendered`, `unsupported`, or `error`;
- artifact path or unsupported report path;
- manual review status.

Unsupported Datoviz cases must be explicit JSON records, never silently absent.

## Acceptance

- Matplotlib path renders PNGs for all initial cases.
- Datoviz path either renders PNGs or writes structured unsupported reports.
- Contact sheets include labeled placeholder tiles for unsupported Datoviz cases.
- Tests validate report schema, artifact creation, non-empty Matplotlib PNGs, and unsupported
  Datoviz reporting.
- No code imports legacy `gsp_datoviz.renderer`.

## Stop Conditions

- Stop if harness design starts requiring JSON/base64 for local in-process rendering arrays.
- Stop if Datoviz failures are hidden or replaced with Matplotlib images.
- Stop if examples call backend APIs directly instead of constructing protocol scenes.
