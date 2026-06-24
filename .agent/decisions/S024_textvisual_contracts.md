# S024 TextVisual contract decision

Status: accepted from P009 response.

S024 proceeds with a single public `TextVisual` protocol family. `GlyphVisual` and atlas/glyph
resources are deferred and renderer-internal for v1.

Key decisions:

- text items are `Sequence[str]` paired with finite `(N,2)`/`(N,3)` positions;
- coordinates use existing `NDC`/`DATA` semantics;
- colors use S023 RGBA validation;
- font size is logical screen pixels via `font_size_px`;
- rotation is radians via `rotation_rad`, pivoting around the resolved anchor;
- anchors are explicit `anchor_x` and `anchor_y` enums, with default `LEFT`/`BASELINE`;
- font selection uses generic `FontRole`, not arbitrary font names or font handles;
- printable ASCII plus newline is required conformance; broader Unicode is capability-gated;
- guides remain semantic guides and are not public TextVisual emitters;
- Datoviz text support is v0.4-retained-API evidence-gated.

Source consultation: `.agent/consultations/P009-response.md`.
Authoritative spec: `spec/visuals/text.md`.
ADR: `adr/ADR-0016-textvisual-v1-no-public-glyphvisual.md`.
