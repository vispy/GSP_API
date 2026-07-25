# M285 - S065 owner visual-review corrections

## Status

Completed and independently accepted on 2026-07-25. Integrated as GSP `4ff1614` and VisPy2
`482f494`, `920966a`, `d4c8d65`, and `5ce544f`. The final installed-wheel qualification produced
fourteen 800×600 captures without retry, and the exact Gallery 5 command exits on one `Ctrl-C`
after releasing its session with no process left behind. Datoviz remained read-only evidence.

## Goal

Correct misleading cross-backend gallery differences, enforce comparable output geometry, and
return a portable owner-review pack without expanding S065's accepted semantic contracts.

## Required scope

- Expose canonical GSP `CanvasSize` through the VisPy2 `Figure`/`subplots` producer path and preserve
  it in `Figure.to_scene()`.
- Make every static gallery request one pixel-exact 800 x 600 canvas and make the installed-wheel
  validator reject any capture with different dimensions.
- Hide Matplotlib's default native frame for `View3D` scenes that have no semantic axis guides,
  while preserving semantic panel titles and existing View2D guide behavior.
- Investigate Datoviz's absent `PanelTextGuide` title in View3D captures. Implement the already
  advertised public adapted title path if it is supported by the qualified binding; otherwise
  correct the capability/documentation overclaim and record a diagnostic.
- Change gallery 3 to avoid claiming cross-backend per-vertex interpolation: use uniform primitive
  color and non-coincident pixel anchors that do not create coplanar/equal-depth ties.
- State explicitly that Datoviz raycast-sphere native shading and analytic surface depth differ
  from Matplotlib's flat projected-circle adaptation; do not add a new sphere material contract.
- Replace the live-review instructions with a repository-relative command that can be copied from
  the Mission Control `GSP_API` checkout and changes into the VisPy2 sibling checkout itself.
- Regenerate all fourteen captures, manifest hashes, capability/review documentation, and the owner
  checklist from installed wheels outside both source trees.
- Add focused source and installed-wheel regressions for canvas propagation, equal PNG dimensions,
  Matplotlib View3D frame suppression, View2D guide preservation, and unambiguous gallery-3 scene
  construction.

## Acceptance

All fourteen PNGs are exactly 800 x 600. Matplotlib View3D captures contain no unintended native
axes. Semantic titles are either present through a truthful qualified path or explicitly diagnosed
as unsupported. Gallery 3 has uniform primitive color and no pixel/primitive positional ties.
The live command starts when copied from `GSP_API`, exits cleanly, and leaves no process behind.
Full tests, strict mypy, Ruff, documentation/link validation, wheel isolation, artifact hashes, and
diff checks pass. An independent supervisor accepts the regenerated review pack.

## Stop conditions

- Stop on any code/spec contradiction or required public semantic expansion beyond existing
  `CanvasSize`, guide, visual, and View3D contracts.
- Stop rather than changing capability claims to conceal a reproducible backend failure.
- Stop before any Datoviz repository edit, release, tag, push, PR, merge, version change, or
  publication.
- Keep M284 and S065 open until the owner reviews and accepts the corrected pack.
