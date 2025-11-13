- PR datoviz with the whole ./datoviz as pyright 0 errors
  - add a pyright target in justfile
- code segments - matplotlib + datoviz
  - positions is [start, end]*n
  - color rgba8 * n
  - line_width float32 * n
  - cap: butt, round, square
- test dynamic group in datoviz pixels
- PR for datoviz
  - DONE issue on n_groups missing in .paths() constructor
  - DONE issue of static type checking in .segments() cap
  - DONE add test layers (with visual regression)
  - add better python API (seems hard/complicated to do)
- WONTDO for each example, `_matplotlib` `_datoviz` and `_both`
  - have a test_runner ?
- when datoviz core dump, DVZ_LOG_LEVEL=0
  - when creating a datoviz app with 350 pixel, there is a segfault
- DONE implement points in datoviz
- handle the animation loop
  - with decorator like datoviz? yes
  - API from datoviz
  - API from matplotlib
  - GSP API common



---
- DONE implement path in matplotlib + datoviz
  - issue to mix the multiple paths and the groups attributes
