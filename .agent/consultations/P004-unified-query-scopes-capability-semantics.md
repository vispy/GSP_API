# P004 - Unified query scopes and capability semantics

Status: pending ChatGPT Pro response.

## Why This Is Needed

GSP already has a first-slice panel query model for data visuals and a bounded reference guide-query
proof for semantic axis guides. The next architecture question is how to unify query scopes before
Datoviz query/capability parity work begins.

This is architectural because it affects protocol semantics, capability planning, backend fallback,
Matplotlib reference behavior, Datoviz v0.4 implementation constraints, guide query status rules,
and future extension/query payloads. Do not implement dependent code until the Pro response is
pasted or committed.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

You are an architecture reviewer for the GSP / VisPy2 project.

GSP is a backend-independent Graphics Server Protocol for semantic scientific visualization. VisPy2
is the high-level Python producer API that targets GSP. Matplotlib is the
reference/conformance/publication backend. Datoviz v0.4-dev is the flagship GPU backend. GSP is
intended to be a server/session protocol, not merely a Python object graph.

Your task is to decide the v0.1/v0.2 architecture for unified query scopes and capability semantics.
The answer must be concrete enough for Codex worker agents to update specs, ADRs, tests, and a
bounded implementation without inventing semantics.

## Current Project Principles

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4-dev is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. Existing source code is implementation material, not protocol authority.

## Current Mission State

Completed stages:

| Stage | Title |
|---|---|
| S001 | Agentic control plane and legacy map |
| S002 | Protocol spine |
| S003 | Matplotlib reference slice |
| S004 | Datoviz v0.4 adapter assessment |
| S005 | Query proof |
| S006 | Protocol hardening and conformance baseline |
| S007 | Datoviz v0.4 point/image adapter slice |
| S008 | VisPy2 producer MVP |
| S009 | Query hardening and Datoviz handoff |
| S010 | Agentic control plane provider hardening |
| S011 | Extensions and virtual data source architecture proof |
| S012 | Matplotlib strict guide/tick provider baseline |
| S013 | VisPy2 semantic guide API growth |
| S014 | Datoviz v0.4 binding evidence and handoff |

Current stage:

| Stage | Title | State |
|---|---|---|
| S015 | Unified query scopes and capability semantics | planned |

Mission Control recommendation:

- Propose S015 next: unified query scopes and capability semantics, likely requiring ChatGPT Pro
  consultation before implementation.
- Use ChatGPT Pro before implementing broad `data` / `guides` / `all-rendered` query-scope
  precedence beyond bounded guide-query fixtures.
- Before Datoviz query/capability parity implementation, activate a v0.4-dev Python facade/raw
  binding; the current GSP environment imports Datoviz 0.3.5.

## Current Query Spec

GSP uses a unified panel query:

```text
What rendered scene contribution is under this panel coordinate?
```

First-slice `QueryRequest` fields:

- request id;
- panel id;
- coordinate;
- coordinate space;
- hit policy;
- requested payload;
- freshness policy.

First-slice `QueryResult` fields:

- request id;
- status;
- hit/miss;
- panel/framebuffer coordinate;
- visual id;
- visual family;
- item/texel id where applicable;
- visual/data coordinate where available;
- displayed RGBA;
- optional scalar/vector/category/text value.

Statuses must distinguish miss from unsupported capability and backend/readback terminal states.

Current statuses:

| Status | Meaning | Payload rules |
|---|---|---|
| `hit` | A visual contribution was found. | `hit=True`; may include visual id, family, item/texel, coordinates, displayed color, source value, and extension payload. |
| `miss` | Query coordinate is inside the panel but no visual contains it. | `hit=False`; no hit payload fields. |
| `outside-panel` | Query coordinate is outside the queried panel/viewport bounds. | `hit=False`; no hit payload fields. |
| `unsupported` | Backend/capability set cannot answer requested query mode or payload. | `hit=False`; diagnostic required. |
| `stale` | A result exists but violates freshness policy. | `hit=False`; diagnostic required. |
| `dropped` | Request was cancelled, superseded, or dropped from an async queue. | `hit=False`; diagnostic required. |
| `failed` | Backend attempted the query/readback but failed operationally. | `hit=False`; diagnostic required. |

Current coarse capability names:

- `panel-query`: backend can perform a point-in-panel query at all;
- `point-item`: backend can identify a point item;
- `image-texel`: backend can identify an image texel/source value.

Backends that do not advertise a mode must reject planning with a diagnostic or return
`unsupported` for direct query attempts.

## Current Query Dataclasses

Current Python model:

```python
class QueryCoordinateSpace(str, Enum):
    PANEL = "panel"
    DATA = "data"

class QueryHitPolicy(str, Enum):
    FRONTMOST = "frontmost"
    ALL = "all"

class QueryPayload(str, Enum):
    IDENTITY = "identity"
    COORDINATE = "coordinate"
    COLOR = "color"
    VALUE = "value"

class QueryStatus(str, Enum):
    HIT = "hit"
    MISS = "miss"
    OUTSIDE_PANEL = "outside-panel"
    UNSUPPORTED = "unsupported"
    STALE = "stale"
    DROPPED = "dropped"
    FAILED = "failed"

class VisualFamily(str, Enum):
    POINT = "point"
    IMAGE = "image"

GUIDE_QUERY_PAYLOAD_KIND = "gsp.guide-query@0.1"

@dataclass(frozen=True, slots=True)
class GuideQueryPayload:
    guide_id: str
    role: str
    axis_dimension: AxisDimension | None = None
    tick_value: float | None = None
    text_value: str | None = None

@dataclass(frozen=True, slots=True)
class QueryRequest:
    id: str
    panel_id: str
    coordinate: tuple[float, float]
    coordinate_space: QueryCoordinateSpace = QueryCoordinateSpace.DATA
    hit_policy: QueryHitPolicy = QueryHitPolicy.FRONTMOST
    requested_payload: tuple[QueryPayload, ...] = (
        QueryPayload.IDENTITY,
        QueryPayload.COORDINATE,
        QueryPayload.COLOR,
        QueryPayload.VALUE,
    )
    freshness_policy: str = "latest"

@dataclass(frozen=True, slots=True)
class QueryResult:
    request_id: str
    status: QueryStatus
    hit: bool
    panel_coordinate: tuple[float, float]
    visual_id: str | None = None
    visual_family: VisualFamily | None = None
    item_id: int | None = None
    texel: tuple[int, int] | None = None
    visual_coordinate: tuple[float, float] | None = None
    data_coordinate: tuple[float, float] | None = None
    displayed_rgba: tuple[float, float, float, float] | None = None
    value: object | None = None
    extension_payload_kind: str | None = None
    extension_payload: object | None = None
    diagnostic: str | None = None
```

Important invariant: non-hit results must not include hit payload fields. Unsupported, stale,
dropped, and failed results require a diagnostic.

## Current Reference Query Behavior

Matplotlib/reference data query:

- CPU-side deterministic implementation in `gsp_matplotlib.protocol_query`.
- Evaluates `PointVisual` and `ImageVisual` protocol models directly.
- Point hits report visual id, visual family `point`, item id, coordinate, displayed RGBA.
- Image hits report visual id, visual family `image`, texel `(row, col)`, data/visual coordinate,
  displayed RGBA, and source value.
- When multiple data visuals contain the coordinate, the reference proof chooses the highest
  `z_order` entry as the frontmost result.

Matplotlib/reference guide query:

- Bounded support in `gsp_matplotlib.guide_query`.
- Evaluates semantic `AxisGuide` tick/spine contributions.
- A hit returns a normal `QueryResult` with:
  - `status=hit`;
  - `visual_id=guide.id`;
  - optional `item_id` for tick index;
  - `data_coordinate=request.coordinate`;
  - `value` as tick label/value;
  - `extension_payload_kind="gsp.guide-query@0.1"`;
  - `extension_payload=GuideQueryPayload(...)`.
- If a provider renders guides but cannot query them, it must return `unsupported`, not `miss`.

Guide-query payload fields:

```python
@dataclass(frozen=True, slots=True)
class GuideQueryPayload:
    guide_id: str
    role: str                 # e.g. "tick" or "spine"
    axis_dimension: AxisDimension | None = None
    tick_value: float | None = None
    text_value: str | None = None
```

## Current Guide / Axis Architecture

Accepted direction:

- GSP owns semantic `Panel`, `View2D`, `AxisGuide`, `TickSpec`, `PanelTextGuide` intent and identity.
- Backends choose capability-declared axis realization providers.
- Generated guides must not be appended to `Figure.visuals()` because that returns user data
  visuals only.

Current provider ids:

```text
gsp.reference.generated_primitives.v0
matplotlib.native.axes.v0
datoviz.v04.panel_axis.wip
```

Provider status may be:

```text
strict | adapted | experimental | unsupported
```

Strict provider examples:

- GSP computes ticks with `auto-linear-nice-v0`, provider renders exactly those values and labels.
- User supplies explicit ticks and labels, provider renders exactly those values and labels.

Adapted provider examples:

- Datoviz native axis uses backend auto ticks because explicit tick values are not supported by the
  exposed binding.
- Matplotlib native locator is left active in non-conformance mode.

Guide contributions must be queryable only when the provider supports guide queries. If a provider
can render guides but not query guide text/ticks, guide-scoped queries must return `unsupported`,
not `miss`.

Current axis provider capability model:

```python
AxisProviderStatus = Literal["strict", "adapted", "experimental", "unsupported"]
AxisProviderPolicy = Literal[
    "auto",
    "prefer_native",
    "require_native",
    "require_strict_gsp",
    "generated_primitives_only",
    "disabled",
]
AxisTickAuthority = Literal["gsp_resolved", "backend_resolved", "explicit_only"]
AxisQueryScopeRequirement = Literal["none", "data_only", "guides", "all_rendered"]

@dataclass(frozen=True, slots=True)
class AxisProviderCapability:
    provider_id: str
    backend_id: str
    provider_status: AxisProviderStatus
    dimensions: tuple[str, ...] = ("x", "y")
    scales: tuple[str, ...] = ("linear",)
    supports_explicit_ticks: bool = False
    supports_auto_ticks_gsp_policy: bool = False
    supports_backend_auto_ticks: bool = False
    supports_tick_labels: bool = False
    supports_axis_labels: bool = False
    supports_title: bool = False
    supports_grid: bool = False
    supports_style_basic: bool = False
    supports_units: bool = False
    supports_datetime: bool = False
    supports_guide_query: bool = False
    supports_text_query: bool = False
    supports_visible_domain_readback: bool = False
    diagnostics: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class AxisProviderRequest:
    policy: AxisProviderPolicy = "auto"
    tick_authority: AxisTickAuthority = "gsp_resolved"
    query_scope_requirement: AxisQueryScopeRequirement = "none"
```

`AxisQueryScopeRequirement` currently exists, but global query-scope semantics are not yet designed.

## Current Capability Model

Every renderer/server reports a `CapabilitySnapshot` before planning.

Capability classes:

- protocol versions;
- resource limits;
- buffer/texture formats;
- render target formats;
- shader languages;
- visual-family support;
- transform placement support;
- readback/query support;
- output/export support;
- extension support;
- determinism guarantees.

Adaptation outcomes:

- accept;
- simplify with diagnostic;
- deactivate with diagnostic;
- reject with fatal diagnostic.

Unsupported behavior must not silently degrade.

Current capability implementation includes:

```python
@dataclass(frozen=True, slots=True)
class CapabilitySnapshot:
    server_name: str
    protocol_versions: tuple[str, ...]
    transports: tuple[TransportKind, ...]
    buffer_dtypes: tuple[str, ...] = ()
    texture_formats: tuple[str, ...] = ()
    visual_families: tuple[str, ...] = ()
    transform_placements: tuple[str, ...] = ()
    query_modes: tuple[str, ...] = ()
    output_formats: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()
    deterministic: bool | None = None
    axis_providers: tuple[AxisProviderCapability, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)

    def supports_query_mode(self, mode: str) -> bool: ...
    def adapt_query_mode(self, mode: str) -> AdaptationDecision: ...
```

Current `query_modes` is coarse and string-based. It does not yet express:

- data-only vs guide-only vs all-rendered scopes;
- support for frontmost vs all hits;
- support for specific payload combinations;
- support for text/guide hit testing;
- whether a backend can distinguish unsupported guide scope from a guide miss;
- whether a backend can merge data and guide hits into correct rendered order.

## Current Extension Query Payload

`QueryResult` can carry a typed extension payload on hit results:

- `extension_payload_kind`
- `extension_payload`

For `gsp.tiled-image@0.1`, the payload is `TiledImageQueryPayload` and reports:

- source id;
- level;
- tile x/y;
- tile-local texel x/y;
- level-local source x/y;
- optional UV coordinate;
- source value.

Non-hit query results must not include extension payload fields.

## Current Datoviz State

Datoviz v0.4-dev is the flagship GPU backend, but runtime query/capability implementation is not
ready in GSP yet.

M018 evidence refresh:

- sibling checkout `../datoviz` is on `v0.4-dev` commit `bc9adbb40`;
- headers expose the v0.4 query, capability, sampled-field, and native axis APIs needed for future
  work;
- current `DvzQueryResult` header fields include request/frame identity, status/hit, scene/figure/
  panel/visual identity, raw/resolved target ids, item/texel ids, visual/data/UVW coordinates,
  displayed RGBA, scalar/vector/category/text value payloads, and scale metadata;
- current GSP Python environment imports `datoviz 0.3.5`, which exposes no public `dvz_*` symbols,
  `DvzQueryResult`, or `DvzCapabilitySnapshot`;
- therefore Datoviz query/capability work must remain capability-gated until a v0.4-dev Python
  facade/raw binding is active.

Datoviz guide query constraint:

- Datoviz v0.4-dev native axes can likely render panel axes and grid/labels through native APIs.
- Current GSP Datoviz axis provider is `datoviz.v04.panel_axis.wip`.
- It advertises backend-native auto ticks as adapted output.
- It does not advertise explicit GSP tick conformance or guide/text query support.
- If Datoviz can query data visuals but not native guide contributions, guide-scoped queries should
  be `unsupported`, not `miss`.

## The Architecture Questions To Answer

Please answer these exact questions:

1. Should `QueryRequest` gain an explicit query scope field? If so, what are the exact v0.1/v0.2
   scope values? Candidate values are `data`, `guides`, and `all-rendered`, but you may rename or
   refine them.
2. For each scope, what contributions are eligible?
   - user data visuals such as point/image;
   - semantic guides such as axes/ticks/spines/grid/title;
   - backend-generated native furniture;
   - overlays/annotations/extension visuals;
   - future UI/controller affordances.
3. What is the result precedence for `all-rendered`?
   - Should frontmost order merge data and guide contributions?
   - If yes, what defines ordering when guides are semantic/backend-native rather than ordinary
     visuals?
   - If ordering cannot be proven, should `all-rendered` be unsupported or adapted?
4. How should status precedence work when a request includes scope(s) that are partially supported?
   Examples:
   - data scope supported, guide scope unsupported, no data hit;
   - data hit exists, guide query unsupported;
   - guide hit exists, data query unsupported;
   - backend cannot determine frontmost merge order;
   - `hit_policy=ALL` requested but backend only supports frontmost.
5. Should GSP allow partial results with diagnostics, or should unsupported requested scopes/payloads
   make the entire query `unsupported`?
6. Should scope be a single enum, a set of scopes, or a richer query plan object?
7. Should query scope and payload requirements be represented as first-class typed capability
   objects rather than string `query_modes`?
8. What minimal capability schema should replace or augment current `query_modes`?
   It should express at least scope, visual family, payload, hit policy, guide query, text query,
   extension payloads, and ordering guarantees where needed.
9. How should axis provider capabilities compose with global query capabilities?
   For example, if `CapabilitySnapshot` says `data` query is supported but selected axis provider
   says `supports_guide_query=False`, what should planning do for `guides` or `all-rendered`?
10. How should Matplotlib reference behavior be defined for conformance?
    - data-only;
    - guides-only;
    - all-rendered;
    - `frontmost`;
    - `all`.
11. How should Datoviz v0.4 behavior be defined before full native guide query support exists?
12. How should extension query payloads, such as tiled-image payloads, fit into scoped queries?
13. What should be explicitly out of scope for S015 to avoid protocol bloat?
14. What is the smallest safe implementation mission after this consultation?

## Expected Output Format

Please respond with these sections exactly:

1. **Recommendation Summary**
   - 6-12 bullets with concrete decisions.

2. **ADR Draft**
   - Title.
   - Status: Proposed.
   - Context.
   - Decision.
   - In scope.
   - Out of scope.
   - Consequences.
   - Open questions.

3. **Protocol Model**
   - Exact proposed `QueryScope` model.
   - Exact proposed `QueryRequest` additions or changes.
   - Exact proposed `QueryResult` additions or changes, if any.
   - Rules for hit payloads, extension payloads, and diagnostics.
   - Rules for `frontmost` and `all`.

4. **Capability Model**
   - Minimal typed capability schema.
   - Whether to keep, replace, or deprecate string `query_modes`.
   - How to represent scope support.
   - How to represent payload support.
   - How to represent ordering/frontmost/all guarantees.
   - How axis-provider capabilities compose with query capabilities.

5. **Status And Precedence Rules**
   - Decision table for supported/unsupported/miss/hit combinations.
   - Rules for partial support and diagnostics.
   - Rules for adapted behavior.

6. **Backend Guidance**
   - Matplotlib reference/conformance behavior.
   - Datoviz v0.4 behavior while guide query support is absent.
   - Future remote/web backend behavior.

7. **Extension Guidance**
   - How extension payloads fit scoped queries.
   - Rules for unsupported extension readout.
   - Tiled-image payload example.

8. **Conformance Tests**
   - Small tests that prove the model.
   - Tests to avoid because they overconstrain backend implementation.

9. **Task List For Codex Agents**
   - Small missions in recommended execution order.
   - Paths likely touched.
   - Acceptance criteria.
   - Stop conditions.

10. **Risk Review**
    - Protocol bloat risks.
    - Backend parity risks.
    - Query semantics risks.
    - Compatibility risks.
