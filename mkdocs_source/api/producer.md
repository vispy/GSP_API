# Producer API

The independent `gsp_vispy2` package produces GSP records. It is not an official upstream VisPy 2.0
release. `subplots()` returns one semantic `Figure` and `Axes`; methods append visuals, resources,
guides, views, and attachments in deterministic creation order.

::: gsp_vispy2
    options:
      members:
        - subplots
        - affine2d
        - scatter
        - markers
        - segments
        - path
        - plot
        - text
        - mesh
        - imshow
        - color_scale
        - colorbar

## Figure and axes

::: gsp_vispy2.protocol.Figure
    options:
      members: true
      show_source: false

::: gsp_vispy2.protocol.Axes
    options:
      members: true
      show_source: false
