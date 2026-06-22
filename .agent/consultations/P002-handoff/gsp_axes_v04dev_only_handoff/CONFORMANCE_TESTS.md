# Conformance Tests

## Tests that prove the design

1. **MVP remains clean**

   Create scatter and image visuals. Confirm `Figure.visuals()` returns only `PointVisual` and `ImageVisual`.

2. **View state exists**

   Create a plot, call `set_xlim(-1, 2)` and `set_ylim(-3, 4)`, and confirm the full scene has one `View2D` with those ranges.

3. **Matplotlib honors `View2D`**

   Render through Matplotlib and assert `mpl_axes.get_xlim()` and `get_ylim()` match GSP state exactly.

4. **Provider capability discovery**

   Matplotlib reports `matplotlib.native.axes.v0`. Datoviz reports `datoviz.v04.panel_axis.wip` only when the local v0.4-dev bindings expose required symbols.

5. **Provider selection**

   Request `require_strict_gsp`, `prefer_native`, and `generated_primitives_only`; assert expected provider or diagnostic.

6. **Explicit tick strictness**

   Given explicit ticks `[0, 0.5, 1]` and labels `['zero', 'half', 'one']`, strict Matplotlib output uses exactly those values/labels.

7. **Datoviz explicit-tick adaptation**

   If Datoviz v0.4-dev native axes cannot accept explicit tick values, a request for strict explicit ticks must not silently use native auto ticks. It should either fall back or report an adapted-provider diagnostic.

8. **Guide query scope**

   Query over a tick label location. `scope='data'` excludes guides; `scope='guides'` includes them if provider supports guide query; Datoviz returns `unsupported` if guide query is not exposed.

9. **Visible domain readback**

   Datoviz provider proof should call its visible-domain readback if exposed and map the result back to GSP `View2D`/controller readback semantics.

10. **Data coordinate mapping**

   Test Datoviz data-to-visual mapping either through verified data-coordinate attachments or through `dvz_panel_data_to_visual_positions()`/GSP normalization.

## Tests to avoid early

- Pixel-perfect equality of Matplotlib and Datoviz axes.
- Exact glyph metrics or antialiasing.
- Exact Datoviz native tick choices as GSP conformance unless a GSP-equivalent policy is confirmed.
- Log/date/category/polar/3D/twin axes.
- Full pan/zoom gesture replay.
- Tests requiring v0.3 Python plotting APIs.
- Tests that assume generated axes appear in `Figure.visuals()`.
