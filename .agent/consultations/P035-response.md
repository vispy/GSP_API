# Recommendation

Adopt a **two-part public boundary**:

1. **Public producer API now:** `Figure`, `Axes`, semantic visual methods, and scene-record inspection remain public and experimental. They are backend-independent and can be documented and tested before Datoviz v0.4 RC1.
2. **Public execution API after RC1 evidence:** backend selection is canonicalized in a separate capability-negotiated `Session`. `Figure.show()` and `Figure.savefig()` remain lightweight conveniences that delegate to a supplied session or create a one-shot session.

A `Figure` must never retain a backend, device, window, event loop, or adapter. Do not put backend selection in `vp.subplots()`.

Use **operation-specific generic methods**—`show()` for interactive display and `savefig()` for publication output. Do not add a vague public `render()` yet, and do not create a matrix of methods such as `show_datoviz()` or `render_datoviz()`.

For simple use:

```python
fig.savefig("out.png")                # Matplotlib publication path
fig.show(backend="datoviz")           # Datoviz interactive path
```

For controlled use:

```python
with vp.open_session("datoviz") as session:
    plan = session.inspect(fig, operation="display")
    display = session.show(fig)
```

Every preflight plan and execution result carries capability outcomes and diagnostics. The default policy should warn on adaptation or deactivation and reject unsupported behavior before execution.

No new public Datoviz execution API is required before RC1. The acceptance harness should remain internal until it demonstrates bounded, deterministic execution and lifecycle behavior.

## Decision Table

| Decision                    | Recommendation                                                                                                                                 | Rationale                                                                                                          | Owner Approval Required |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| Producer/backend binding    | Keep `Figure` and `Axes` completely backend-independent.                                                                                       | Preserves the mandated producer → session → adapter layering and allows one scene to execute in multiple sessions. | No                      |
| Canonical backend selection | Use `vp.open_session("matplotlib" \| "datoviz")`.                                                                                              | A session is the correct owner of capabilities, adapter state, resources, event loops, and diagnostics.            | No                      |
| Convenience selection       | Permit mutually exclusive `session=` or `backend=` arguments on `show()` and `savefig()`.                                                      | Keeps simple use concise while making explicit sessions available when control is needed.                          | No                      |
| Selection in `subplots()`   | Do not support it.                                                                                                                             | Scene construction must not depend on where or how the scene will execute.                                         | No                      |
| User-facing verbs           | Use `show()` and `savefig()`; defer generic `render()`. Do not add backend-named display methods.                                              | Display, publication, query, and offscreen rendering have different lifecycle and capability contracts.            | No                      |
| Default backends            | Keep Matplotlib as the implicit `savefig()` backend and, during the 0.x transition, the implicit `show()` backend. Datoviz remains explicit.   | Avoids silently changing existing behavior while Datoviz coverage remains uneven.                                  | Yes                     |
| Capability visibility       | Add `Session.capabilities`, `Session.inspect()`, immutable diagnostics, and per-feature dispositions.                                          | Capability negotiation must be inspectable rather than hidden behind fallback behavior.                            | No                      |
| Interactive lifecycle       | An explicit session owns backend state; a returned `Display` owns one window/scene binding. Non-blocking display requires an explicit session. | Prevents orphaned windows, ambiguous event-loop ownership, and hidden long-lived sessions.                         | No                      |
| Publication contract        | Treat file output as a distinct capability-qualified operation, not as generic backend parity.                                                 | Matplotlib publication support does not imply equivalent Datoviz operations, or vice versa.                        | No                      |
| `render_matplotlib()` tuple | Keep unchanged through RC1; post-RC wrap it in `MatplotlibRenderResult` and deprecate tuple unpacking.                                         | Avoids pre-RC churn while adding diagnostics and a common result contract later.                                   | Yes                     |
| RC1 execution surface       | Keep the Datoviz acceptance runner internal.                                                                                                   | Current evidence is sufficient for acceptance testing, not yet for a durable public lifecycle API.                 | No                      |
| Package identity            | Rename the public distribution/import before external release to `gsp-vispy2` / `gsp_vispy2`.                                                  | Retains the VisPy2 objective while avoiding an implied official upstream VisPy 2.0 claim.                          | Yes                     |

## Minimal RC Stage

### Public API before Datoviz v0.4 RC1

Make no new public backend/session commitment before RC1.

The public experimental contract should explicitly include:

* `vp.subplots()`;
* backend-independent `Figure` and `Axes`;
* semantic methods such as `plot`, `scatter`, `imshow`, and `mesh`;
* limits, labels, titles, grids, guides, and color-scale APIs;
* the existing semantic record accessors on `Figure`;
* the current Matplotlib `render_matplotlib()`, `savefig()`, and `show()` behavior.

Before RC1:

* define this surface explicitly through documentation, typing, and `__all__`;
* state that it is an independent experimental GSP producer API;
* state that `render_matplotlib()` is transitional;
* do not add `backend=` to `subplots()`;
* do not expose the Datoviz adapter or acceptance runner through `Figure`.

The existing producer API is the intentionally experimental public API required at this stage. A public session API is not required to satisfy that constraint.

### Internal-only RC acceptance work

Implement a private acceptance runner that:

* lowers representative `Figure` scenes to in-memory GSP records;
* executes the same records through Matplotlib and Datoviz adapters;
* records `strict`, `adapted`, `deactivated`, `unsupported`, and backend-failure outcomes;
* captures structured diagnostics with semantic record IDs;
* writes paired artifacts and a machine-readable manifest;
* freezes versioned GSP payload fixtures for later replay;
* records adapter version, capability snapshot, platform, and artifact hashes;
* isolates crash-prone cases in the test harness when necessary.

Frozen serialized payloads are test fixtures. Local execution must continue to use the in-process object path without mandatory JSON or base64.

### Deferred until after RC1 evidence

The first post-RC experimental execution milestone should add:

* `vp.open_session()`;
* `Session.capabilities` and `Session.inspect()`;
* `Session.show()` and `Session.savefig()`;
* `Figure.show(session=... | backend=...)`;
* `Figure.savefig(session=... | backend=...)`;
* `ExecutionPolicy`, `ExecutionPlan`, `PublicationResult`, and `Display`;
* deterministic blocking and non-blocking lifecycle behavior.

Defer retained updates until stable semantic object identity and delta submission have been demonstrated. Defer query/readback, distributed sessions, and public protocol-record submission until their capability and lifecycle contracts are separately validated.

## Proposed API

The following is the recommended **post-RC experimental** surface:

```python
from dataclasses import dataclass
from os import PathLike
from typing import Literal, Mapping

BackendName = Literal["matplotlib", "datoviz"]
Operation = Literal["publication", "display"]
Action = Literal["allow", "warn", "error"]


@dataclass(frozen=True)
class ExecutionPolicy:
    adapted: Action = "warn"
    deactivated: Action = "warn"
    unsupported: Literal["error"] = "error"


def open_session(
    backend: BackendName,
    *,
    policy: ExecutionPolicy | None = None,
    options: Mapping[str, object] | None = None,
) -> "Session": ...


class Session:
    backend: str
    capabilities: "CapabilitySet"

    def inspect(
        self,
        figure: "Figure",
        *,
        operation: Operation,
    ) -> "ExecutionPlan": ...

    def show(
        self,
        figure: "Figure",
        *,
        block: bool = True,
    ) -> "Display": ...

    def savefig(
        self,
        figure: "Figure",
        path: str | PathLike[str],
        **options: object,
    ) -> "PublicationResult": ...

    def poll(self, timeout: float = 0.0) -> int: ...
    def run(self) -> None: ...
    def close(self) -> None: ...

    def __enter__(self) -> "Session": ...
    def __exit__(self, *exc_info: object) -> None: ...


class Figure:
    def show(
        self,
        *,
        session: Session | None = None,
        backend: BackendName | None = None,
        block: bool = True,
    ) -> "Display": ...

    def savefig(
        self,
        path: str | PathLike[str],
        *,
        session: Session | None = None,
        backend: BackendName | None = None,
        **options: object,
    ) -> "PublicationResult": ...

    def render_matplotlib(self) -> "MatplotlibRenderResult": ...


class Display:
    backend: str
    is_open: bool
    diagnostics: tuple["Diagnostic", ...]

    def update(self) -> "UpdateResult": ...
    def close(self) -> None: ...


class PublicationResult:
    backend: str
    path: "Path | None"
    outcome: str
    diagnostics: tuple["Diagnostic", ...]
    native: object | None


class MatplotlibRenderResult(PublicationResult):
    figure: object
    axes: object
```

Passing both `session=` and `backend=` is an error. `backend=` creates a one-shot session. Non-blocking execution requires `session=`.

### Simple publication output

```python
import numpy as np
import gsp_vispy2 as vp

x = np.linspace(0.0, 2.0 * np.pi, 1000)

fig, ax = vp.subplots()
ax.set_xlabel("x")
ax.set_ylabel("sin(x)")
ax.plot(x, np.sin(x), color=(0.1, 0.3, 0.8, 1.0), width=2)

result = fig.savefig("sine.png")  # Matplotlib by default
print(result.backend, result.path)
```

### Simple interactive Datoviz display

```python
import numpy as np
import gsp_vispy2 as vp

rng = np.random.default_rng(0)
points = rng.normal(size=(100_000, 2))

fig, ax = vp.subplots()
ax.scatter(
    points[:, 0],
    points[:, 1],
    color=(0.2, 0.6, 0.9, 0.7),
    size=3,
)

fig.show(backend="datoviz")  # Blocking one-shot session
```

### Capability-aware execution with diagnostics

```python
import numpy as np
import gsp_vispy2 as vp

image = np.linspace(0.0, 1.0, 512 * 512).reshape(512, 512)

fig, ax = vp.subplots()
ax.imshow(image, colormap="gray", clim=(0.0, 1.0))
ax.set_title("Capability-aware display")

policy = vp.ExecutionPolicy(
    adapted="warn",
    deactivated="warn",
    unsupported="error",
)

with vp.open_session("datoviz", policy=policy) as session:
    plan = session.inspect(fig, operation="display")

    for diagnostic in plan.diagnostics:
        print(
            diagnostic.disposition,
            diagnostic.code,
            diagnostic.message,
        )

    plan.require_executable()
    display = session.show(fig, block=True)
```

### Retained interactive update

```python
import time
import numpy as np
import gsp_vispy2 as vp

x = np.linspace(0.0, 4.0 * np.pi, 2000)

fig, ax = vp.subplots()
line = ax.plot(x, np.sin(x), color=(0.9, 0.3, 0.2, 1.0), width=2)

with vp.open_session("datoviz") as session:
    display = session.show(fig, block=False)

    for phase in np.linspace(0.0, 2.0 * np.pi, 600):
        if not display.is_open:
            break

        line.set_data(x, np.sin(x + phase))
        update = display.update()

        for diagnostic in update.diagnostics:
            print(diagnostic.code, diagnostic.message)

        session.poll(timeout=0.0)
        time.sleep(1.0 / 60.0)

    display.close()
```

## Lifecycle Contract

* A `Figure` owns only semantic producer state, stable semantic IDs, resources, and revision information.
* A `Session` owns the adapter, capability snapshot, backend context or device, resource cache, event-loop integration, and all displays created through it.
* A `Display` represents one live or completed window/scene binding. It must not expose raw Datoviz handles through `Axes` or visual objects.
* `Session.close()` is idempotent. It closes all child displays, releases backend resources, and invalidates further execution.
* `Display.close()` is idempotent. It closes that display but does not close an explicitly supplied session.
* `fig.show(backend="datoviz", block=True)` creates and owns a temporary session, runs until the window closes, closes the session, and returns a completed `Display` carrying final diagnostics.
* `block=False` requires an explicit session. This prevents a hidden session from becoming an unmanaged long-lived owner.
* `Session.run()` blocks until its displays close. `Session.poll()` performs bounded event processing for embedding in an existing loop.
* Interactive sessions and updates are thread-affine unless a backend capability explicitly states otherwise.
* `Display.update()` submits semantic changes since the last accepted figure revision. The adapter may lower them incrementally or rebuild internally; this is not visible to the producer API.
* An update either becomes the accepted scene revision or fails without silently presenting a partially updated semantic scene.
* Adapted and deactivated behavior produces structured diagnostics. Unsupported behavior raises before execution under the default policy.
* Backend crashes or adapter defects raise `BackendExecutionError`; they must not be reclassified as ordinary unsupported capabilities.
* Operations on a closed session or display raise `LifecycleError`.

## Compatibility Contract

Compatibility means preservation of **semantic producer intent**, not pixel identity or global backend interchangeability.

The project should guarantee that:

* producer methods never acquire backend-specific arguments, resource handles, shader concepts, pipeline objects, or window types;
* backend support is documented per semantic capability and operation;
* capability names are semantic—for example, marker form, retained update, publication export, or picking—not Datoviz pipeline names;
* every non-strict execution outcome is discoverable through diagnostics;
* local execution does not require serialization;
* one `Figure` may be executed by multiple sessions without mutation by an adapter;
* native objects may appear only in explicit result/interop objects such as `MatplotlibRenderResult.native`;
* a capability snapshot is associated with an actual session and environment, not assumed solely from a backend name.

For the 0.x series:

* documented producer API removals receive at least one minor-version deprecation cycle;
* the post-RC session API is labeled experimental and may change between minor versions, but changes must be documented;
* the default backend for an existing convenience method must not change silently;
* GSP fixture payloads carry an independent protocol/schema version.

For `render_matplotlib()`:

1. keep the existing tuple through RC1;
2. post-RC, return `MatplotlibRenderResult`;
3. support tuple unpacking for one deprecation cycle with a warning;
4. retain `.figure` and `.axes` for explicit Matplotlib interoperation;
5. route execution through the Matplotlib session/adapter rather than directly invoking renderer helpers.

## Naming and Positioning

Use:

* **Distribution:** `gsp-vispy2`
* **Import:** `gsp_vispy2`
* **Project title:** “GSP VisPy2 Prototype”
* **Description:** “An independent experimental semantic visualization producer for GSP.”

The README, package metadata, documentation header, and repository description should state:

> This is an independent experimental project. It is not the official VisPy 2.0 API and is not an upstream VisPy release.

Do not publish the public distribution under the unqualified name `vispy2`. If internal code already uses that import, retain it temporarily as a deprecated compatibility shim.

The project may describe itself as producing evidence and design input relevant to future VisPy directions. It should not describe Datoviz as an upstream VisPy backend or imply endorsement until such a relationship exists upstream.

The rename is not a Datoviz RC1 blocker, but it should occur before the first external package release or public API announcement.

## Owner Questions

1. **Approve `gsp-vispy2` / `gsp_vispy2` as the public identity?**
   Recommended default: yes; retain `vispy2` only as a temporary internal alias.

2. **What should bare `fig.show()` use during 0.x?**
   Recommended default: preserve Matplotlib; require `backend="datoviz"` for GPU display.

3. **What is the default adaptation policy?**
   Recommended default: warn for adapted or deactivated behavior; error for unsupported behavior.

4. **What stability promise applies to the first public session API?**
   Recommended default: explicitly experimental, with documented minor-version changes but no silent semantic changes.

5. **Should native Matplotlib interoperation remain supported?**
   Recommended default: yes, through `MatplotlibRenderResult`, while deprecating the raw tuple contract.

## Rejected Alternatives

* **Backend selection in `vp.subplots()`:** couples scene construction to execution and makes one figure less reusable.
* **A backend retained on `Figure`:** introduces hidden mutable execution state and unclear ownership when a figure is rendered more than once.
* **A global `vp.use("datoviz")` switch as the primary API:** creates process-global behavior that is difficult to test, compose, and reason about.
* **`show_datoviz()` and `render_matplotlib()` as the general pattern:** grows one method per backend and operation and obscures capability negotiation.
* **A generic `fig.render()` now:** conflates publication, display, offscreen execution, native-object construction, and future distributed submission.
* **Raw Datoviz handles on axes or visuals:** violates the producer boundary and makes retained updates backend-dependent.
* **Mandatory JSON/base64 for local execution:** contradicts the required fast in-process path.
* **Public exposure of the RC acceptance runner:** freezes test-harness concepts before lifecycle and result contracts have sufficient evidence.
* **Claiming backend parity from paired images:** visual similarity is evidence for individual capabilities, not proof of interchangeable backend behavior.

## Stop Conditions

Do not publish the post-RC session API until:

* representative acceptance scenes are classified without silent drops;
* known adapter crashes are either fixed or rejected deterministically before execution;
* every adaptation or deactivation produces a structured diagnostic;
* blocking execution exits and cleans up deterministically;
* non-blocking execution has unambiguous session and event-loop ownership;
* repeated create/show/close cycles do not leak windows, devices, or retained resources.

Reject or stop any API proposal that:

* adds Datoviz-specific concepts to producer method signatures;
* requires raw backend handles for retained updates;
* requires JSON or base64 on the local path;
* cannot name the semantic capability governing an operation;
* treats a backend failure as an undocumented fallback;
* silently changes the default backend;
* promises global backend parity;
* exposes query or readback as a renderer convenience rather than a protocol capability;
* publicly uses an unqualified `vispy2` identity that could reasonably be mistaken for an upstream release.

## ADR Draft

**Title:** Separate the public semantic producer API from capability-negotiated execution

**Status:** Proposed. Producer portion applicable before Datoviz v0.4 RC1; execution portion evidence-gated until after RC1.

**Context:**
The project defines VisPy2 as a high-level producer of backend-independent GSP scenes. Matplotlib is the reference/publication backend and Datoviz v0.4 is the flagship local GPU backend. Backend capability coverage is intentionally uneven, and execution may be strict, adapted, deactivated, unsupported, or erroneous. The project must provide a useful experimental public API without implying that it is the official upstream VisPy 2.0 API.

**Decision:**
`Figure` and `Axes` remain backend-independent semantic producers. Backend selection is owned by a separate `Session`, created with `vp.open_session()`. `Figure.show()` and `Figure.savefig()` are operation-specific convenience wrappers accepting either an explicit session or a one-shot backend name. Backend selection is not accepted by `vp.subplots()` and is not retained by `Figure`.

Every session exposes a capability snapshot. `Session.inspect()` returns a scene- and operation-specific execution plan with structured diagnostics. The default policy warns on adaptations and deactivations and rejects unsupported behavior.

Interactive sessions own backend contexts, event loops, resources, and displays. Non-blocking execution requires an explicit session. Retained updates operate through semantic visual identity and `Display.update()`, never through raw Datoviz handles.

Before RC1, the existing producer API and Matplotlib path remain public and experimental. The Datoviz acceptance runner remains internal. The public session API is introduced only after RC1 evidence establishes deterministic classification, execution, and cleanup.

`render_matplotlib()` remains unchanged through RC1. It is subsequently routed through the Matplotlib session adapter and wrapped in `MatplotlibRenderResult`; tuple unpacking is deprecated.

The public project identity becomes `gsp-vispy2` / `gsp_vispy2`, with an explicit statement that it is independent and not the official upstream VisPy 2.0 API.

**Consequences:**
Simple plotting remains concise, advanced execution exposes capabilities and diagnostics, and backend-specific lifecycle state remains outside the producer model. The API does not promise backend parity, and some execution/session details remain intentionally experimental until supported by post-RC evidence.

