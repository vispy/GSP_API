## 1. **Executive decision**

Make `Panel` a scene-scoped identity node containing only `id`; remove `figure_id`, `viewport_rect`, and all unimplemented draft fields. Move outer-panel allocation into a required, scene-level, versioned `PanelLayoutIntent`, initially supporting only explicit normalized rectangles, while keeping all logical-pixel geometry exclusively in `ResolvedLayoutSnapshot`. Move rectangular clipping from `Panel` and `View2D` to each visual attachment through an explicit clip scope. Remove producer-emission identifiers from the GSP capability registry and session negotiation entirely; retain only the renderer capabilities there, while exposing producer support as `vispy2`-owned, non-wire emission-feature identifiers with no legacy aliases.

## 2. **Canonical Panel contract**

### Canonical records

```python
from dataclasses import dataclass
from typing import Literal, TypeAlias


PanelId: TypeAlias = str


@dataclass(frozen=True, slots=True)
class Panel:
    id: PanelId


@dataclass(frozen=True, slots=True)
class NormalizedRenderTargetRect:
    left: float
    top: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class PanelPlacement:
    panel_id: PanelId
    allocation_rect: NormalizedRenderTargetRect


@dataclass(frozen=True, slots=True)
class ExplicitPanelLayoutV1:
    placements: tuple[PanelPlacement, ...]
    kind: Literal["layout.panel.explicit_rects.v1"] = (
        "layout.panel.explicit_rects.v1"
    )


# Closed union in GSP 0.2 alpha. Future versions may add new variants.
PanelLayoutIntent: TypeAlias = ExplicitPanelLayoutV1
```

The existing `Scene` record gains two required fields:

```python
panels: tuple[Panel, ...]
panel_layout: PanelLayoutIntent
```

There is no implicit protocol-level layout. A producer convenience API may create a full-target placement, but the emitted canonical scene must contain it explicitly:

```python
PanelPlacement(
    panel_id="panel-0",
    allocation_rect=NormalizedRenderTargetRect(
        left=0.0,
        top=0.0,
        width=1.0,
        height=1.0,
    ),
)
```

Resolved geometry becomes explicitly per-panel:

```python
@dataclass(frozen=True, slots=True)
class LogicalPixelRect:
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class ResolvedPanelLayout:
    panel_id: PanelId
    panel_rect_px: LogicalPixelRect
    plot_rect_px: LogicalPixelRect


@dataclass(frozen=True, slots=True)
class ResolvedLayoutSnapshot:
    target_width_px: int
    target_height_px: int
    panels: tuple[ResolvedPanelLayout, ...]
```

A singular top-level `panel_rect_px` or `plot_rect_px` is not canonical, even while `vispy2` emits only one panel.

### Normative invariants

1. `Panel.id` MUST be non-empty and unique within its owning `Scene`. Panel identity is scene-scoped, not globally scoped.

2. `Panel` MUST NOT contain `figure_id`. A figure is producer state; it is not a GSP ownership boundary. All panel references in views, attachments, and guides use `panel_id`. Cross-scene references are invalid.

3. `Panel` MUST NOT contain layout geometry, clipping policy, hierarchy, background styling, or generic metadata in GSP 0.2 alpha.

4. A scene MUST contain exactly one `panel_layout`. Every scene panel MUST appear in exactly one `PanelPlacement`; duplicate, missing, and unknown `panel_id` references are errors.

5. `ExplicitPanelLayoutV1.kind` MUST be serialized as the exact string:

   ```text
   layout.panel.explicit_rects.v1
   ```

   Unknown layout kinds MUST be rejected. They MUST NOT be treated as explicit rectangles or silently approximated.

6. `allocation_rect` describes requested **outer-panel allocation** in normalized render-target coordinates. It is not a data viewport and MUST never be named or interpreted as a viewport.

7. Normalized render-target coordinates use an origin at the logical render target’s top-left, with increasing coordinates to the right and downward. They are independent of device-pixel ratio and physical pixels.

8. For each rectangle, all four values MUST be finite and:

   ```text
   0 ≤ left < left + width ≤ 1
   0 ≤ top  < top  + height ≤ 1
   width  > 0
   height > 0
   ```

   NaN, infinity, zero-area, negative-area, and out-of-range rectangles are invalid.

9. In `layout.panel.explicit_rects.v1`, panel interiors MUST NOT overlap. Shared edges are permitted and gaps are permitted. Placement order has no z-order or compositing meaning. Overlapping or inset panels require a future layout kind with explicit stacking semantics.

10. Resolution to logical pixels MUST occur in the protocol-defined resolver, not independently in each adapter. For normalized edge coordinate `u` and target extent `N`, use:

    ```text
    Q(u, N) = min(N, max(0, floor(u × N + 0.5)))
    ```

    Then:

    ```text
    x0 = Q(left, target_width_px)
    x1 = Q(left + width, target_width_px)
    y0 = Q(top, target_height_px)
    y1 = Q(top + height, target_height_px)
    ```

    The resulting `panel_rect_px` is:

    ```text
    left   = x0
    top    = y0
    width  = x1 - x0
    height = y1 - y0
    ```

    A rectangle resolving to zero width or height MUST produce a layout-resolution error; it MUST NOT be expanded or clamped to one pixel.

11. `plot_rect_px` is computed after guide and layout allocation. It MUST be a positive-area rectangle fully contained in `panel_rect_px`.

12. DATA coordinate mapping, DATA rendering transforms, queries, rays, DATA picking, and layout-aware navigation MUST use `plot_rect_px`. They MUST NOT use `panel_rect_px` or `allocation_rect`.

13. Device-pixel conversion occurs only after the logical-pixel snapshot has been produced. Matplotlib and Datoviz adapters MUST consume the same resolved snapshot and MUST NOT apply backend-specific normalized-rectangle rounding.

14. Normative text should use **plot NDC** for coordinates normalized to `plot_rect_px`. The historically ambiguous term “panel NDC” should remain only in migration documentation.

15. The schema is closed. `figure_id`, `viewport_rect`, `parent_id`, panel `clip`, `background_rgba`, and `metadata` MUST be rejected as unknown `Panel` fields.

## 3. **Clipping and layout ownership**

The existing `View2D.clip` field is removed. The visual-attachment record gains:

```python
from enum import StrEnum


class ClipScope(StrEnum):
    PLOT = "plot"
    PANEL = "panel"
    RENDER_TARGET = "render_target"
```

```python
clip_scope: ClipScope = ClipScope.PLOT
```

| Concern                               | Canonical owner                          | Normative semantics                                                                                            |
| ------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Panel identity                        | `Panel`                                  | Stable scene-local anchor for views, guides, and attachments.                                                  |
| Outer-panel allocation intent         | `Scene.panel_layout` / `PanelPlacement`  | Normalized request relative to the render target.                                                              |
| Resolved outer panel                  | `ResolvedPanelLayout.panel_rect_px`      | Logical-pixel result of layout-intent resolution.                                                              |
| Resolved data viewport                | `ResolvedPanelLayout.plot_rect_px`       | Panel rectangle after guide/layout consumption.                                                                |
| DATA transform and interaction domain | View plus resolved layout                | Always based on `plot_rect_px`, irrespective of raster clip scope.                                             |
| Rectangular raster clipping           | `VisualAttachment.clip_scope`            | Per-attachment choice of plot, panel, or render-target scissor.                                                |
| View                                  | View record                              | Owns coordinate transform, limits, camera, and navigation state; no clipping boolean.                          |
| Panel                                 | Panel record                             | Does not enable or disable clipping. It only identifies a layout region.                                       |
| Render-target bounds                  | Session/backend                          | Always the final hard bound; native rendering cannot address pixels outside it.                                |
| Guide rendering                       | Guide renderer                           | Uses resolved guide geometry within `panel_rect_px`; it is not controlled by a view clip.                      |
| Arbitrary clip paths or masks         | Future typed attachment/visual extension | Must intersect the selected rectangular scope; not part of 0.2 alpha.                                          |
| Panel background                      | Not present in 0.2 alpha                 | Future typed panel decoration or explicit visual semantics, not an RGBA field added without composition rules. |

Exact clipping semantics:

* `PLOT`: intersect rasterization with `plot_rect_px`.
* `PANEL`: intersect rasterization with `panel_rect_px`.
* `RENDER_TARGET`: apply no panel-derived scissor; only render-target bounds remain.
* `clip_scope` changes only raster clipping. It MUST NOT change DATA transforms, picking coordinates, rays, queries, or navigation domains.
* Unsupported clip scopes MUST cause scene rejection before rendering. An adapter MUST NOT replace `PANEL` with `PLOT`, replace `RENDER_TARGET` with `PANEL`, or otherwise narrow or broaden the requested region.
* The default is `PLOT`, but canonical serializers should emit it explicitly.

## 4. **Panel migration plan**

1. **Record the decision.** Add `spec/decisions/P038-panel-and-producer-capabilities.md` containing the final records, field removals, old-to-new mapping, and the statement that no runtime compatibility is provided.

2. **Replace the normative specifications.**

   * Rewrite `spec/records/panel.md` so `Panel` contains only `id`.
   * Add `spec/layout/panel-layout.md` defining `layout.panel.explicit_rects.v1`.
   * Rewrite `spec/layout/resolved-layout-snapshot.md` around per-panel `ResolvedPanelLayout`.
   * Add or update `spec/rendering/clipping.md`.
   * Remove the unimplemented `parent_id`, panel `clip`, `background_rgba`, and `metadata` wording.
   * Remove `viewport_rect` from current normative text.

3. **Change the core Python models.**

   * In `gsp-core/src/gsp/protocol/panel.py`, reduce `Panel` to `id`.
   * Add `NormalizedRenderTargetRect`, `PanelPlacement`, and `ExplicitPanelLayoutV1` in `gsp-core/src/gsp/protocol/layout.py`.
   * Change `ResolvedLayoutSnapshot` to contain per-panel entries.
   * Add `VisualAttachment.clip_scope`.
   * Delete `View2D.clip`.

4. **Change transport schemas and serializers.**

   * Update or add `panel.schema.json`, `panel-layout.schema.json`, `resolved-layout-snapshot.schema.json`, and `visual-attachment.schema.json`.
   * Require `layout.panel.explicit_rects.v1` on the wire.
   * Set all relevant object schemas to reject additional properties.
   * Remove serialization branches for all deleted fields.

5. **Migrate internal fixtures with a one-shot tool, not runtime aliases.** Add `tools/migrate_p038_internal_fixtures.py` with the exact transformation:

   ```python
   old_panel = Panel(
       id=old.id,
       figure_id=old.figure_id,
       viewport_rect=(x, y, width, height),
   )

   new_panel = Panel(id=old.id)

   new_placement = PanelPlacement(
       panel_id=old.id,
       allocation_rect=NormalizedRenderTargetRect(
           left=x,
           top=y,
           width=width,
           height=height,
       ),
   )
   ```

   Before dropping `figure_id`, the tool MUST verify that panel IDs are unique in each resulting scene. A collision MUST stop migration for explicit repair; the tool MUST NOT invent replacement IDs.

6. **Migrate clipping explicitly.**

   * For every visual attachment using a `View2D` with `clip=True`, write `clip_scope=ClipScope.PLOT`.
   * For every visual attachment using a `View2D` with `clip=False`, write `clip_scope=ClipScope.RENDER_TARGET`.
   * Delete the view field after attachments have been rewritten.
   * Do not map old `clip=False` to `PANEL`; that would silently change its meaning.

7. **Centralize resolution.**

   * Implement rectangle validation and `Q(u, N)` once in `gsp-core`.
   * Resolve every panel before guide allocation.
   * Resolve every `plot_rect_px` after guide allocation.
   * Reject zero-area resolved panel or plot rectangles.
   * Prevent adapters from recomputing normalized layout.

8. **Update producers and adapters.**

   * `vispy2` must emit one explicit full-target placement for its current single axes.
   * `gsp_matplotlib` must consume `panel_rect_px` and `plot_rect_px`, converting only the already-resolved logical coordinates into Matplotlib’s native coordinate convention.
   * `gsp_datoviz` must use `plot_rect_px` for the data viewport and the attachment’s selected rectangle for scissoring.
   * An adapter that cannot support a requested multi-panel or clip configuration must reject it before allocating backend resources.

9. **Add mandatory tests.**

   * `tests/protocol/test_panel_contract.py`: only `id` accepted; all deleted fields rejected.
   * `tests/layout/test_explicit_panel_layout.py`: finite values, bounds, duplicate/missing references, touching panels, overlap rejection.
   * `tests/layout/test_layout_quantization.py`: golden tests for `Q`, shared boundaries, tiny rectangles, and odd target dimensions.
   * `tests/layout/test_resolved_layout_snapshot.py`: per-panel entries and plot containment.
   * `tests/conformance/test_plot_rect_semantics.py`: rendering transforms, queries, rays, picking, and navigation all use `plot_rect_px`.
   * `tests/conformance/test_attachment_clip_scope.py`: exact `PLOT`, `PANEL`, and `RENDER_TARGET` behavior.
   * Adapter tests must include a protocol-constructed two-panel scene. Each adapter must either render it conformantly or fail with the standardized unsupported error.
   * Add `tests/fixtures/migration/p038/before/` and `after/` plus a checked-in migration report.

10. **Delete compatibility code.** After fixture migration, remove the migration tool from runtime packaging. Old field names may remain only in the P038 decision record, migration fixtures, and release notes.

## 5. **Producer capability decision**

Producer-emission support does **not** belong in the GSP protocol capability registry or `SessionCapabilities`. GSP capabilities describe what a provider session can execute, not what a particular high-level library can construct. The canonical renderer capability identifiers remain exactly:

```text
meshvisual.material.texture2d_unlit.v1
meshvisual.texture_filter.linear.v1
```

`vispy2` should expose its producer support through a local, non-wire `EmissionFeature` API:

```python
from enum import StrEnum


class EmissionFeature(StrEnum):
    MESHVISUAL_MATERIAL_TEXTURE2D_UNLIT_V1 = (
        "vispy2.emit.meshvisual.material.texture2d_unlit.v1"
    )
    MESHVISUAL_TEXTURE_FILTER_LINEAR_V1 = (
        "vispy2.emit.meshvisual.texture_filter.linear.v1"
    )
```

These identifiers MUST NOT be serialized in GSP scenes, sent during session negotiation, inserted into the GSP registry, or accepted as renderer capabilities.

Ownership and naming rules:

* GSP owns `meshvisual.*` capability semantics and their conformance requirements.
* `vispy2` owns `vispy2.emit.*` identifiers and their producer-side tests.
* The `vispy2` prefix is a declared stable producer identity, not a value inferred dynamically from a module path.
* Other producers may use the local convention:

  ```text
  <stable-producer-id>.emit.<gsp-semantic-feature-id>
  ```

  but those identifiers remain owned and interpreted by that producer.
* Identifiers are case-sensitive, lowercase, dot-delimited, and end in the semantic feature’s `vN` suffix.
* `vN` versions the meaning of the emitted GSP semantic feature, not the package release. Bug fixes or support for additional input forms do not require a new identifier if the emitted protocol semantics are unchanged.
* A producer feature does not authorize execution. Rendering is allowed only when the producer can emit the record **and** the selected session advertises the corresponding GSP renderer capability.
* There are no aliases for either old `gsp_vispy2.producer.*` identifier.

## 6. **Capability migration plan**

1. **Remove producer entries from GSP authority.**

   * Delete both `gsp_vispy2.producer.*` entries from the canonical capability registry, generated documentation, constants, schemas, and session-capability fixtures.
   * Ensure `gsp-core` contains no import or dependency on `vispy2`.

2. **Add the local `vispy2` feature API.**

   * Create `vispy2/src/vispy2/emission_features.py`.

   * Define the two exact `EmissionFeature` values above.

   * Expose a typed immutable set such as:

     ```python
     EMISSION_FEATURES: frozenset[EmissionFeature]
     ```

   * Do not name it `SESSION_CAPABILITIES` or expose it through the GSP provider SPI.

3. **Update internal references directly.**

   * Replace producer-side checks of:

     ```text
     gsp_vispy2.producer.mesh.texture2d_unlit.v1
     gsp_vispy2.producer.mesh.texture_filter.linear.v1
     ```

     with the corresponding `EmissionFeature` members.
   * Replace renderer-side checks with the canonical `meshvisual.*` identifiers, never with `vispy2.emit.*`.

4. **Keep a non-runtime migration table for traceability only.**

   ```text
   gsp_vispy2.producer.mesh.texture2d_unlit.v1
     -> vispy2.emit.meshvisual.material.texture2d_unlit.v1

   gsp_vispy2.producer.mesh.texture_filter.linear.v1
     -> vispy2.emit.meshvisual.texture_filter.linear.v1
   ```

   Store this mapping in the P038 decision record and migration fixture. Do not import it from production code.

5. **Strengthen session validation.**

   * `SessionCapabilities` MUST reject both `gsp_vispy2.producer.*` and `vispy2.emit.*`.
   * A requested material or filter unsupported by the selected renderer MUST fail before native resource creation.
   * Linear filtering MUST NOT silently degrade to nearest filtering.
   * Unsupported textured material MUST NOT silently become an untextured or differently shaded material.

6. **Add producer conformance tests.**

   * Each `EmissionFeature` member must have a minimal `vispy2` input fixture.
   * The fixture must produce canonical GSP records accepted by the GSP schema and semantic validator.
   * The emitted record must declare or imply the corresponding renderer requirement through the canonical GSP mechanism.
   * Tests must verify that producer emission succeeds independently of renderer availability.

7. **Add producer–renderer integration tests.**

   * Producer supports feature, renderer supports feature: execution succeeds.
   * Producer supports feature, renderer lacks feature: session rejects.
   * Renderer supports feature, producer API does not support requested construction: producer rejects before scene submission.
   * Old identifier supplied anywhere: deterministic validation error.
   * No test may infer renderer support from `vispy2.EMISSION_FEATURES`.

8. **Remove aliases and fallback parsing.**

   * No deprecated constants.
   * No string rewrite in registry lookup.
   * No warning-and-continue path.
   * Historical strings remain only in P038 migration evidence.

## 7. **Rejected alternatives**

| Alternative                                                                   | Reason for rejection                                                                                                                                                                               |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Keep `Panel(id, figure_id, viewport_rect)`                                    | Leaks producer topology into the protocol and couples panel identity to one layout representation.                                                                                                 |
| Put `viewport_rect` directly back on `Panel`                                  | Continues the panel-allocation/data-viewport ambiguity and makes future grid, constraint, or nested layout structurally awkward.                                                                   |
| Adopt the draft `parent_id`, `clip`, `background_rgba`, and `metadata` fields | The semantics are incomplete, the implementation does not support them, and accepting them would violate fail-closed behavior.                                                                     |
| Reserve unimplemented Panel fields                                            | Reserved-but-accepted fields create false interoperability expectations. Closed schemas should reject them until a versioned semantic contract exists.                                             |
| Add a grid/flex/constraint solver in 0.2 alpha                                | Prematurely commits to a large layout language. A discriminated layout union gives the necessary extension point without speculative semantics.                                                    |
| Allow overlapping panels in explicit-rectangle v1                             | Requires z-order, picking precedence, background composition, and interaction-routing rules that are not otherwise defined.                                                                        |
| Keep clipping on `Panel`                                                      | One boolean cannot distinguish data, overlays, annotations, and visuals with different clip requirements inside the same panel.                                                                    |
| Keep clipping on `View2D`                                                     | Clipping is a rendering policy of an attachment, not an intrinsic property of a coordinate transform; it also fails to generalize uniformly to 3D and mixed attachments.                           |
| Use an unqualified `clip=False`                                               | “No clip” is not precise because render-target bounds always apply. `RENDER_TARGET` states the actual effective boundary.                                                                          |
| Keep `gsp_vispy2.producer.*`                                                  | Encodes an obsolete package identity and incorrectly implies that producer support is a GSP session capability.                                                                                    |
| Rename them to `vispy2.producer.*` inside the GSP registry                    | Fixes the spelling but not the category error; GSP would still be registering implementation-specific producer claims.                                                                             |
| Use `producer.vispy2.*` in the GSP registry                                   | Makes producer identity part of the global protocol capability taxonomy without a negotiation use case.                                                                                            |
| Use reverse-DNS identifiers now                                               | Collision resistance does not justify putting non-wire producer information into the protocol. Reverse-DNS becomes appropriate only if a future cross-process producer descriptor is standardized. |
| Provide aliases for unpublished identifiers                                   | Creates permanent ambiguity and test burden for identifiers that have no external compatibility requirement.                                                                                       |

## 8. **Release gate checklist**

* [ ] The canonical Python `Panel` record contains exactly one field: `id`.
* [ ] The wire schema rejects `figure_id`, `viewport_rect`, `parent_id`, panel `clip`, `background_rgba`, and `metadata`.
* [ ] Every serialized scene contains an explicit `panel_layout` with kind `layout.panel.explicit_rects.v1`.
* [ ] Every panel is placed exactly once; missing, duplicate, unknown, invalid, overlapping, and zero-resolved-area placements fail validation.
* [ ] `ResolvedLayoutSnapshot` contains per-panel `panel_rect_px` and `plot_rect_px`; no singular single-panel shortcut remains canonical.
* [ ] Golden tests fix the normalized-to-logical-pixel quantization algorithm.
* [ ] Tests demonstrate that guide allocation changes `plot_rect_px` without changing `panel_rect_px`.
* [ ] DATA transforms, queries, rays, picking, and navigation are tested against `plot_rect_px`, including points lying inside the panel but outside the plot.
* [ ] `View2D.clip` is absent from models, schemas, serializers, and current specifications.
* [ ] Every visual attachment has an explicit or canonical-default `clip_scope`, and all three scopes have conformance tests.
* [ ] Matplotlib and Datoviz consume the core-resolved layout snapshot rather than resolving normalized rectangles independently.
* [ ] A direct protocol-level multi-panel fixture is covered by each adapter through conformant rendering or standardized fail-closed rejection.
* [ ] The GSP registry contains the two canonical `meshvisual.*` renderer capabilities and no producer-emission identifiers.
* [ ] `vispy2` exposes the two exact `vispy2.emit.meshvisual.*` local features outside the provider/session API.
* [ ] Session capability validation rejects both old `gsp_vispy2.producer.*` values and all `vispy2.emit.*` values.
* [ ] Producer–renderer integration tests prove that producer emission support never substitutes for renderer capability support.
* [ ] No runtime alias, fallback parser, warning-based adaptation, or legacy field conversion remains.
* [ ] Repository-wide searches find historical field names and old capability strings only in P038, migration fixtures, and release notes.
* [ ] Checked-in before/after fixtures and a deterministic migration report preserve internal migration evidence.
* [ ] Package imports match the accepted topology: `gsp`, `gsp_matplotlib`, `gsp_datoviz`, and `vispy2`.
* [ ] All unsupported layout, clipping, material, and filtering cases fail before backend resource allocation.

## 9. **Risks and future extension points**

| Risk or future need                                              | Bounded extension point                                                                                                                                   |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Very small normalized panels can quantize to zero logical pixels | Keep fail-closed resolution and require callers to choose a representable layout for the current target size.                                             |
| Grid, row/column, weighted, or constraint layouts                | Add a new `PanelLayoutIntent` variant with a new `kind`; do not mutate `layout.panel.explicit_rects.v1`.                                                  |
| Insets, overlapping panels, or panel stacking                    | Add a versioned layout variant defining z-order, picking precedence, clipping, and composition together.                                                  |
| Nested panels                                                    | Represent hierarchy in a future layout tree whose leaves reference flat `Panel` IDs; do not add `Panel.parent_id`.                                        |
| Panel-specific backgrounds or borders                            | Add a typed panel-decoration record with explicit composition order and capability semantics.                                                             |
| Application annotations or private metadata                      | Use namespaced, typed extension records. Do not add an unconstrained core metadata map.                                                                   |
| Arbitrary clipping planes, paths, or masks                       | Add a typed attachment/visual clip specification intersected with `clip_scope`.                                                                           |
| Cross-process producer discovery                                 | Introduce a separate `ProducerDescriptor` with an explicit stable producer authority, potentially reverse-DNS; do not overload `SessionCapabilities`.     |
| Future producer package renaming                                 | Keep `vispy2` as the stable producer identity for existing local feature tokens; package release versions remain separate from semantic feature versions. |
