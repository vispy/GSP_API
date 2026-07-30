# P038 ChatGPT Pro consultation: canonical Panel and producer capability contract

Copy the complete prompt below into ChatGPT Pro. No attachments or repository access are required.

---

You are reviewing two pre-publication architecture decisions for GSP 0.2 alpha, a
backend-independent scientific graphics session protocol. Give a decisive, implementation-ready
answer. The project is unpublished and explicitly permits aggressive breaking refactors now in
order to obtain the best long-term architecture.

## Authority and product topology

The accepted topology is:

- fresh-root `gsp` owns protocol authority, specifications, conformance, provider SPI, and
  Matplotlib/Datoviz adapters;
- fresh-root `vispy2` owns the high-level plotting producer;
- `gsp-core` imports as `gsp`;
- `gsp-matplotlib` imports as `gsp_matplotlib`;
- `gsp-datoviz` imports as `gsp_datoviz`;
- `vispy2` imports as `vispy2`;
- figures and axes own semantic producer state only;
- sessions own backend selection, capabilities, native resources, event loops, and display;
- unsupported behavior and adaptations must fail closed;
- GSP_API is a historical archive and is not current authority.

The current code and packages are unpublished `0.2.0a1`. No backward compatibility with an
external user base is required, but internal conformance and migration evidence must remain
traceable.

## Decision 1: canonical Panel record

The shipped Python record is:

```python
@dataclass(frozen=True, slots=True)
class Panel:
    id: str
    figure_id: str
    viewport_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
```

Validation requires a finite positive normalized rectangle fully contained in `[0, 1]²`.
`viewport_rect` is outer-panel allocation intent in render-target coordinates. A resolver maps it
to a logical-pixel outer panel. A separate `ResolvedLayoutSnapshot.plot_rect_px` is the contained
data viewport after guide/layout allocation. DATA rendering, queries, rays, picking, and
layout-aware navigation use `plot_rect_px`.

The current canonical specification draft instead says:

```text
Panel fields:
- id: required identifier
- parent_id: optional panel identifier, default null
- clip: boolean, default true
- background_rgba: RGBA8 or null
- metadata: string-keyed map

Panel geometry is not stored as an unqualified backend rectangle. Requested layout intent and
resolved logical-pixel geometry are distinct records.
```

That draft omits `figure_id` and `viewport_rect`. The implementation does not implement
`parent_id`, panel `clip`, `background_rgba`, or `metadata`. View2D already has a `clip` field.
Scenes also contain explicit panels, views, visual attachments, guides, and one render target.
The present producer supports exactly one 2D or 3D axes, but the protocol should retain a sound
multi-panel future.

Historical accepted viewport semantics say:

- `Panel.viewport_rect` allocates the outer panel inside the resolved render target;
- its values are normalized fractions, not logical pixels;
- `ResolvedLayoutSnapshot.panel_rect_px` is the resolved outer panel;
- `ResolvedLayoutSnapshot.plot_rect_px` is the contained data viewport;
- DATA and panel-NDC mapping, queries, rays, picking, and navigation use `plot_rect_px`;
- panel allocation and plot viewport must never be conflated.

Questions:

1. What should the canonical GSP 0.2-alpha `Panel` record be?
2. Should `figure_id` exist, given that a Scene already owns panels and there is one render target?
3. Should `viewport_rect` remain on Panel, move into a separate typed layout-intent record, or be
   replaced by a more extensible layout model now?
4. Should `clip`, `background_rgba`, `metadata`, and `parent_id` be implemented now, reserved in
   specification, or removed from the 0.2-alpha contract?
5. Where should clipping live: panel, view, attachment, or a combination with explicit semantics?
6. Give exact dataclass/type shapes, invariants, migration steps, and normative wording.

Optimize for long-term protocol clarity, multi-panel extensibility, transport independence,
deterministic layout, and separation of semantic intent from resolved backend geometry. Do not
preserve a field merely because current code has it.

## Decision 2: producer capability namespace

The accepted producer identity is now distribution/import `vispy2`. However, canonical registry
and Python constants still contain unpublished identifiers:

```text
gsp_vispy2.producer.mesh.texture2d_unlit.v1
gsp_vispy2.producer.mesh.texture_filter.linear.v1
```

Renderer capabilities are separately named:

```text
meshvisual.material.texture2d_unlit.v1
meshvisual.texture_filter.linear.v1
```

The producer identifiers mean that VisPy2 can emit the relevant semantic records. They are not
renderer-support claims. Nothing using the old `gsp_vispy2` identifiers has been publicly released.

Questions:

1. Should producer emission capabilities exist in the GSP protocol registry at all, or should
   producer support be documented/tested outside renderer session capabilities?
2. If retained, what durable namespace should they use: `vispy2.producer.*`,
   `producer.vispy2.*`, a reverse-DNS/vendor namespace, or another design?
3. Should there be aliases or migration compatibility for the unpublished old identifiers?
4. Give exact identifier strings, ownership rules, collision/versioning rules, and migration steps.

Optimize for multiple independent producers, stable wire identity, no package-name leakage where
inappropriate, and clear separation of producer emission from renderer execution.

## Required output format

Return exactly these sections:

1. **Executive decision** — one concise paragraph covering both decisions.
2. **Canonical Panel contract** — exact recommended records/types and normative invariants.
3. **Clipping and layout ownership** — explicit ownership table.
4. **Panel migration plan** — ordered breaking steps with tests/spec files that must change.
5. **Producer capability decision** — whether these belong in GSP and exact final identifiers.
6. **Capability migration plan** — ordered breaking steps and conformance requirements.
7. **Rejected alternatives** — concise rationale for each serious alternative.
8. **Release gate checklist** — objective conditions required before `0.2.0a1` publication.
9. **Risks and future extension points** — bounded, no speculative implementation program.

Do not ask follow-up questions. Do not recommend retaining contradictions for compatibility. Make
the best long-term pre-publication decision.

---
