# S058 M245 Datoviz v0.4-dev rolling baseline

Date: 2026-07-22

## Provenance

| Field | Value |
|---|---|
| Datoviz checkout | `/Users/cyrille/GIT/Viz/datoviz` |
| Branch | `v0.4-dev` |
| Commit | `71c444cee65a6b4bb825ba4e0a4e448036707037` |
| Describe | `v0.4.0rc2-12-g71c444cee` |
| Imported module | `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py` |
| GSP branch | `main` |

The sibling checkout had pre-existing untracked paper outputs and was not modified. The Datoviz
probe recorded the same exact source revision and import path in the review-pack report.

## Compatibility replay

The S028 review pack completed all 60 backend rows with 53 strict, seven adapted, and zero crashed,
unsupported, disabled, experimental, or not-run rows. Datoviz cases run one process per case.

Compared with `artifacts/visual_qa/s050/latest_pre_rc_compat_s028`, the current run has four
improvements, zero regressions, and 56 unchanged rows:

| Datoviz case | Previous | Current |
|---|---|---|
| `color/scalar_image_viridis_colorbar` | crashed | strict |
| `guide/view2d_auto_grid` | crashed | adapted |
| `guide/view2d_grid_clip_title_boundary` | crashed | adapted |
| `guide/view2d_reversed_explicit` | crashed | adapted |

Guide rows remain adapted because public native panel-title support and full strict guide semantics
are still absent. The absence of crashes is an execution improvement, not a strictness promotion.

## Query and capability evidence

- Datoviz facade, capture, sampled fields, and query bindings are ready.
- Live point identity remains proven.
- Live image queries still do not populate texel, displayed RGBA, or value payloads.
- Mesh face/triangle enums and result fields exist, but mesh eligibility still accepts only
  none/item/object targets, query geometry still emits one id for every non-instanced triangle, and
  native tests cover item identity only. GSP mesh-triangle capability remains unpromoted.
- The planned public field-slot sampling descriptor and setter do not exist. Textured mesh emission
  still lacks the explicit nearest/clamp/no-mipmap control required by the GSP Texture2D contract.

## Lifecycle evidence

| Probe | Result |
|---|---|
| Public blocking and polling | 10/10 clean, zero timeouts |
| Internal five-mode lifecycle matrix | 25/25 clean exits and complete reports, zero timeouts |
| Maintained public examples | blocking and polling modes completed cleanly |

The internal matrix includes bounded execution, callback-stopped blocking, explicit polling,
retained View2D updates, and retained point-data updates with changed capture hashes.

## Repository validation

- full pytest with coverage: 666 passed, 2 skipped, 66% aggregate coverage;
- strict mypy: clean across 220 source files;
- Ruff: clean;
- Matplotlib and local-source Datoviz imports: clean;
- `git diff --check` and Mission Control JSON validation: clean.

## Classification and next action

M245 and the M246 classification are complete. No public GSP capability should change at this
revision. M247 remains deferred because neither Texture2D sampling nor canonical mesh-triangle
identity has the required public native semantics and tests.

The next actionable mission is M248: replace the pre-RC-named replay entry point with a rolling
`v0.4-dev` checkpoint that records exact provenance and runs the compatibility, lifecycle, focused
test, and matrix-comparison lanes in one bounded command. Future Datoviz runtime commits can then
trigger targeted Texture2D, triangle-pick, image-payload, or guide follow-up from comparable
evidence.
