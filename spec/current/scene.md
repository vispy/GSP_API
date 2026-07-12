# Scene model

The scene is session-owned semantic state assembled from accepted records. It is not a required
Python object graph and does not contain backend handles.

## Identity

Every addressable protocol entity uses a non-empty validated identifier. References must resolve within the relevant session state. Missing, duplicate, stale, or wrong-kind references must produce deterministic validation errors.

### Identifier contract

| Rule | Requirement |
|---|---|
| `GSP-SCENE-001` | An identifier is a non-empty Unicode string with no surrounding whitespace or control characters. |
| `GSP-SCENE-002` | Identity comparison is exact code-point equality; implementations must not case-fold or normalize identifiers implicitly. |
| `GSP-SCENE-003` | IDs are unique among simultaneously live entities of all core kinds unless a command schema explicitly defines a separate namespace. |
| `GSP-SCENE-004` | References are session-local. Cross-session references are invalid even when their text matches. |

Colon-separated names such as `visual:temperature` are a recommended producer convention, not a
semantic hierarchy.

## Ownership and lifetime

`GSP-SCENE-005`: the session owns accepted semantic records. A producer may reuse its local values,
but subsequent local mutation must not change accepted state without an update command.

`GSP-SCENE-006`: deleting an entity that is still referenced is rejected unless the same atomic
batch removes or replaces every dependent reference first. Shutdown releases all session-owned
entities.

Each mutable entity has a monotonic revision. Creating establishes revision zero; each accepted
semantic update increments it exactly once. Backend-internal rebuilds do not change semantic
revision.

## Panels

A panel is a rectangular presentation and query region. It associates views, visuals, and guides with resolved layout geometry. Panel coordinates are the common boundary for rendering, navigation, and queries.

### Panel record

| Field | Type | Required | Default | Meaning |
|---|---|---:|---|---|
| `id` | identifier | yes | — | Panel identity. |
| `parent_id` | panel identifier or null | no | null | Optional layout parent; cycles are invalid. |
| `clip` | boolean | no | true | Clip data contributions to the resolved plot rectangle. |
| `background_rgba` | RGBA8 or null | no | null | Semantic background; null inherits presentation policy. |
| `metadata` | string-keyed map | no | empty | Non-semantic application metadata. |

`GSP-SCENE-007`: panel geometry is not stored as an unqualified backend rectangle. Requested layout
intent and resolved logical-pixel geometry are distinct records.

## Views

`View2D` maps two-dimensional data domains into a panel. `View3D` combines a camera and projection with a panel. A visual in data coordinates requires the appropriate view; a visual already expressed in panel NDC does not acquire data meaning implicitly.

`GSP-SCENE-008`: a panel may have at most one active primary data view per view role in core GSP
0.2. Multiple overlay views require explicit attachments and capability support; association is
never inferred from creation order.

## Visuals

A visual is a semantic family, not a backend draw call. Accepted families are points, markers, segments, paths, images, text, and triangle meshes. Each declares its coordinate space, geometry, styling inputs, and referenced resources explicitly.

### Visual attachment

| Field | Type | Required | Default | Meaning |
|---|---|---:|---|---|
| `visual_id` | visual identifier | yes | — | Attached visual. |
| `panel_id` | panel identifier | yes | — | Presentation/query panel. |
| `view_id` | view identifier or null | conditional | null | Required for DATA-space visuals. |
| `z_order` | signed integer | no | 0 | Ordering among contributions where depth semantics do not override it. |
| `visible` | boolean | no | true | Semantic participation flag. |

`GSP-SCENE-009`: attachments are explicit scene relationships. A visual can be attached more than
once only when the backend advertises the required multi-attachment capability and query identities
remain unambiguous.

## Guides

Guides express semantic annotation intent:

- `AxisGuide` defines an axis dimension, side, label, tick intent, grid intent, and style.
- `PanelTextGuide` defines panel-level text roles such as a title.
- `ColorbarGuide` represents the display of a scalar color scale.

Guides are not pre-rendered decorations. Query geometry and exact layout require separate backend capabilities.

### Guide common fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | identifier | yes | Guide identity. |
| `panel_id` | panel identifier | yes | Owning panel. |
| `visible` | boolean | no | Defaults true. |
| `style` | typed guide-style record | no | Logical-pixel and RGBA styling only. |

`GSP-SCENE-010`: guides participate in layout and queries only when the corresponding capability is
advertised. Rendering an axis line does not imply tick-label layout or guide-query support.

## State relationships

Resources must exist before visuals that reference them are executed. Views and transforms used by a visual must be valid for its coordinate space. Layout, view, and resource revisions that affect a query must participate in snapshot freshness checks.

## Mutation ordering

The dependency order for creation is resource → transform/view → visual/guide → attachment → frame.
Commands in one atomic batch may establish dependencies earlier in that batch. Forward references
to later commands are invalid in core GSP 0.2.

`GSP-SCENE-011`: an update validates the complete replacement semantic record. Patch operations are
not field-by-field backend mutations; omitted fields retain their value only when the command schema
explicitly defines patch semantics.

`GSP-SCENE-012`: a renderer may retain or rebuild native objects, but identity, revision, ordering,
query attribution, and diagnostics remain expressed through public semantic IDs.
