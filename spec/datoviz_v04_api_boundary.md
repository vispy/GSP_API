# Datoviz v0.4 API Boundary - Accepted S023 Baseline

Status: accepted for S023; extended by S024 TextVisual boundary.

GSP's Datoviz v0.4 adapter targets the retained scene/app facade exposed by `import datoviz as dvz`.
It does not target Datoviz v0.3 wrapper APIs.

Accepted API boundary:

- create scene/figure/panel with `dvz_scene`, `dvz_figure`, `dvz_panel_full`;
- create retained visuals with family constructors such as `dvz_point`, `dvz_marker`, `dvz_segment`,
  `dvz_path`, and `dvz_image`;
- upload dense attributes with `dvz_visual_set_data` using verified v0.4 attribute names;
- attach visuals through explicit visual attach descriptors;
- use sampled fields for RGBA8 image binding when available, otherwise texture fallback;
- use offscreen capture through `dvz_app`, `dvz_view_offscreen`, and `dvz_view_capture_png` when
  available.

Forbidden implementation boundary:

- no `datoviz.App`, `datoviz.visuals`, private `_panel`/`_figure`/`_texture` wrapper APIs;
- no v0.3 allocation functions such as `dvz_*_alloc`;
- no silent approximation of missing v0.4 helpers.

When a required v0.4 symbol is absent, the adapter or visual QA harness must return a structured
unsupported diagnostic naming the missing requirement.

## S024 TextVisual boundary

Datoviz v0.4 text support must be proven against verified retained v0.4 APIs before implementation.
The adapter must not use legacy/private text wrappers, v0.3-style allocation or setter APIs, or expose
glyph atlas fields as GSP protocol. If v0.4 requires explicit glyph or atlas resources, the Datoviz
backend owns them as internal cached realization state. Missing or unverified capabilities must return
structured diagnostics such as `TEXT_API_UNVERIFIED`, `TEXT_UNSUPPORTED`, or
`TEXT_ATLAS_CREATION_FAILED`.
