# S023 Visual QA

S023 defines the first protocol visual-family review pack for GSP's formal protocol path. It covers
point, marker, segment, path, image, and simple overlay scenes. The scenes are built from formal GSP
protocol visuals and rendered through the Matplotlib reference backend and the Datoviz v0.4 adapter.

## Run the review pack

Use the visual QA harness to regenerate scenes, backend renders, contact sheets, and manual review
notes:

```bash
PYTHONPATH=../datoviz:. \
DYLD_LIBRARY_PATH=../datoviz/build/src \
DVZ_SHADERC_RUNTIME_LIBRARY=../datoviz/build/src/libshaderc_shared.dylib \
uv run python -m gsp.qa.visual run \
  --backends matplotlib,datoviz \
  --out artifacts/visual_qa/s023/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

When Datoviz v0.4 is not available, run the Matplotlib-only path:

```bash
uv run python -m gsp.qa.visual run \
  --backends matplotlib \
  --out artifacts/visual_qa/s023/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

## Inspect artifacts

Primary review artifacts:

- `artifacts/visual_qa/s023/latest-local/contact_sheets/s023_all_cases.png`
- `artifacts/visual_qa/s023/latest-local/manual_notes.yaml`
- `artifacts/visual_qa/s023/latest-local/report.json`
- `artifacts/visual_qa/s023/latest-local/summary.md`

Per-case notes live under:

- `artifacts/visual_qa/s023/latest-local/notes/`

## Protocol examples

The S023 producer examples use the VisPy2 protocol API and do not call backend implementation APIs
directly:

- `examples/vispy2_protocol_scatter.py`
- `examples/vispy2_protocol_marker.py`
- `examples/vispy2_protocol_segment.py`
- `examples/vispy2_protocol_path.py`
- `examples/vispy2_protocol_imshow.py`
- `examples/vispy2_protocol_image_scalar.py`
- `examples/vispy2_protocol_point_over_image.py`
- `examples/vispy2_protocol_guides.py`

Run any example directly, for example:

```bash
uv run python examples/vispy2_protocol_path.py
```

Outputs are written under `examples/output/`.

## Scope boundaries

S023 deliberately stops before remote images, tiled data, volume rendering, colorbars, broad colormap
registries, text/glyph visuals, mesh visuals, and advanced normalization. Those belong to later
missions.
