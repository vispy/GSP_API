# Recommendation

Create **two new repositories with fresh root commits**: `gsp` and `vispy2`. The `gsp` repository must be the authority for the semantic protocol, session model, capability system, backend plugin contract, conformance corpus, and reference adapters. The `vispy2` repository must own only the plotting API, producer-side semantic state, and translation into GSP scenes. GSP must not be placed inside VisPy2: the charter defines GSP as an independent protocol usable by other producers and by in-process, remote, browser, and cloud servers.  

Use several distributions rather than another umbrella package: `gsp-core` importing as `gsp`, `gsp-matplotlib` importing as `gsp_matplotlib`, `gsp-datoviz` importing as `gsp_datoviz`, and `vispy2` importing as `vispy2`. Keep the three GSP distributions in the `gsp` repository and the producer distribution in the `vispy2` repository. The base `vispy2` distribution should depend only on `gsp-core`; convenience extras should install adapters without changing the dependency direction.

Backend discovery should be owned by `gsp-core` and implemented through lazy Python entry points in the `gsp.backends` group. VisPy2 must never import `gsp_matplotlib` or `gsp_datoviz`. `Figure.savefig()` and blocking `Figure.show()` may remain as 0.x conveniences, but they must create a transient Matplotlib session through the backend-neutral GSP runtime. Interactive and non-blocking execution must use an explicit GSP session, which owns all adapter, device, event-loop, and display state. This directly implements the already accepted producer/session boundary. 

Perform the repository migration **before the first public 0.2 prerelease**. Preserve `GSP_API` unchanged as the recoverable historical archive, with annotated source/final tags, a verified full Git bundle, and machine-readable provenance manifests in both new repositories. Release `gsp-core`, `gsp-matplotlib`, and `vispy2` prereleases independently of Datoviz RC3. Migrate the Datoviz v0.4 adapter immediately, but do not publish `gsp-datoviz` until an installable RC3-compatible artifact passes the native checkpoint and full conformance suite.

## Decision Table

| Decision                               | Recommendation                                                                                                                                                                                                                                                     | Reason                                                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| 1. Product/repository topology         | Create new repositories `gsp` and `vispy2`; retain `GSP_API` as a read-only archive.                                                                                                                                                                               | Separates protocol authority from one producer while providing clean development histories.                |
| 2. Python distribution/import topology | `gsp-core` → `gsp`; `gsp-matplotlib` → `gsp_matplotlib`; `gsp-datoviz` → `gsp_datoviz`; `vispy2` → `vispy2`. No umbrella distribution.                                                                                                                             | Backend dependencies and release cycles differ; protocol-only installations remain small.                  |
| 3. Dependency direction and discovery  | `vispy2 → gsp-core`; each adapter `→ gsp-core`; optional extras `vispy2[matplotlib] → gsp-matplotlib` and later `vispy2[datoviz] → gsp-datoviz`. Discover adapters through `gsp.backends` entry points.                                                            | Prevents reverse dependencies and concrete adapter imports while permitting optional backend installation. |
| 4. Public API                          | Keep `vp.subplots()`, plotting methods, `Figure.to_scene()`, default Matplotlib `savefig()`/blocking `show()`, and canonical `gsp.open_session(...)`. Remove public `render_matplotlib()` and do not put backend selection on figures or axes.                     | Small, semantic producer API; backend-neutral explicit execution.                                          |
| 5. Migration/history                   | Use new root commits, an annotated source tag, an annotated final archive tag, a verified `git bundle --all`, and per-file provenance manifests. Do not rewrite or filter the existing repository.                                                                 | Gives clean histories without destroying research evidence or obscuring provenance.                        |
| 6. Curated migration inventory         | Migrate formal protocol, accepted specifications/ADRs, canonical fixtures, current tests, current adapters, and the new producer. Archive legacy object graphs, Datoviz 0.3, bulk artifacts, and control-plane material. Defer network/Pydantic/extra experiments. | Preserves semantic authority and conformance evidence rather than accidental module paths.                 |
| 7. Release sequencing                  | Migrate first; release `gsp-core`, `gsp-matplotlib`, and `vispy2` as 0.2 prereleases before RC3 if their gates pass; publish `gsp-datoviz` only after RC3 validation.                                                                                              | Avoids making protocol and publication rendering depend on a native backend release.                       |
| 8. Implementation plan                 | Use separately accepted stages: archive baseline, bootstrap GSP, recover conformance, add discovery, bootstrap VisPy2, validate installed wheels, release prereleases, then validate Datoviz RC3.                                                                  | Every stage has an observable checkpoint and rollback path; no big-bang rewrite.                           |
| 9. Risks and rejected alternatives     | Explicitly reject GSP-inside-VisPy2, a combined distribution, cleanup-in-place, destructive filtering, legacy branches in new repositories, and implicit backend state.                                                                                            | These alternatives recreate authority inversion, dependency coupling, or historical ambiguity.             |

## Target Repository Topology

| Repository | Ownership boundary                               | Included                                                                                                                                                                                                             | Explicitly excluded                                                                                                  |
| ---------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `gsp`      | GSP protocol and backend-conformance maintainers | Semantic model, session contract, capability model, adaptation diagnostics, backend plugin SPI, encoding-independent resources, specifications, ADRs, conformance fixtures, Matplotlib adapter, Datoviz v0.4 adapter | VisPy2 plotting objects, legacy object graph, old Datoviz 0.3 implementation, experimental network/Pydantic packages |
| `vispy2`   | VisPy2 plotting API and producer maintainers     | Figures, axes, plotting primitives, producer-side semantic state, GSP scene construction, plotting documentation and examples                                                                                        | Protocol authority, concrete adapters, device/window/event-loop state, backend-specific handles                      |
| `GSP_API`  | Historical archive only                          | Complete existing history, artifacts, experiments, old implementations, agent records, superseded documentation                                                                                                      | New development, public releases, rewritten history                                                                  |

Recommended `gsp` layout:

```text
gsp/
├── README.md
├── PROVENANCE.md
├── migration-manifest.json
├── specs/
├── adrs/
├── conformance/
│   ├── fixtures/
│   └── tests/
├── packages/
│   ├── gsp-core/
│   │   ├── pyproject.toml
│   │   └── src/gsp/
│   ├── gsp-matplotlib/
│   │   ├── pyproject.toml
│   │   └── src/gsp_matplotlib/
│   └── gsp-datoviz/
│       ├── pyproject.toml
│       └── src/gsp_datoviz/
├── docs/
└── examples/
```

Recommended `vispy2` layout:

```text
vispy2/
├── README.md
├── PROVENANCE.md
├── migration-manifest.json
├── pyproject.toml
├── src/
│   └── vispy2/
├── tests/
├── docs/
└── examples/
```

Repository rules:

1. A semantic or protocol change begins with a specification or ADR in `gsp`.
2. VisPy2 consumes a released or explicitly pinned `gsp-core` prerelease; it does not vendor or subtree GSP.
3. Adapter conformance is tested in `gsp` against the same canonical fixtures.
4. Cross-repository changes use coordinated pull requests and prerelease pins, not Git submodules.
5. The GSP repository is a multi-distribution monorepo, not an umbrella distribution. Its root does not produce a wheel containing all packages.
6. Adapter code may evolve with protocol changes in one GSP commit, while adapter dependencies remain isolated at installation time.

This topology avoids both undesirable extremes: one repository containing unrelated product surfaces, and one repository per small adapter with excessive operational fragmentation.

## Target Python Package Topology

| Distribution     | Import           | Repository | Required dependencies                                                                         | Responsibility                                                                    |
| ---------------- | ---------------- | ---------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `gsp-core`       | `gsp`            | `gsp`      | Only dependencies required by the semantic model, session API, discovery, and typed resources | Protocol records, capabilities, diagnostics, scene/session interfaces, plugin SPI |
| `gsp-matplotlib` | `gsp_matplotlib` | `gsp`      | `gsp-core>=0.2,<0.3`, Matplotlib                                                              | Reference, conformance, publication, and default 0.x one-shot backend             |
| `gsp-datoviz`    | `gsp_datoviz`    | `gsp`      | `gsp-core>=0.2,<0.3`, installable Datoviz v0.4 dependency                                     | Flagship local GPU backend                                                        |
| `vispy2`         | `vispy2`         | `vispy2`   | `gsp-core>=0.2,<0.3` plus producer-side numerical dependencies                                | High-level plotting API and GSP scene production                                  |

Target optional dependencies:

```toml
[project.optional-dependencies]
matplotlib = [
    "gsp-matplotlib>=0.2.0a1,<0.3",
]
datoviz = [
    "gsp-datoviz>=0.2.0a1,<0.3",
]
```

The `datoviz` extra should not be present in a public `vispy2` release until `gsp-datoviz` is publicly installable. Before that point, development installations can install the two repositories explicitly.

Recommended installation surfaces:

```bash
# Semantic protocol and session API only.
pip install gsp-core

# VisPy2 producer with the default publication backend.
pip install "vispy2[matplotlib]"

# VisPy2 with the GPU backend, once the adapter is released.
pip install "vispy2[datoviz]"
```

Dependency rules:

```text
vispy2 -----------------------> gsp-core
gsp-matplotlib ---------------> gsp-core
gsp-datoviz ------------------> gsp-core

vispy2[matplotlib] -----------> gsp-matplotlib
vispy2[datoviz] --------------> gsp-datoviz

gsp-core -X-> any adapter
gsp-core -X-> vispy2
adapter  -X-> vispy2
```

Do not carry the following package topology into the new repositories:

* No combined `gsp-vispy2` distribution.
* No `gsp_extra` catch-all package.
* No protocol dependency on `gsp_network` or `gsp_pydantic`.
* No adapter modules inside the `gsp` core import package.
* No namespace-package overlay in which several distributions contribute arbitrary modules under `gsp.*`.
* No public `gsp_vispy2` compatibility shim. There are no known stable external consumers, and publishing a shim would turn an internal prototype path into a compatibility obligation.

Use package-specific release tags in the GSP monorepo, for example:

```text
gsp-core-v0.2.0a1
gsp-matplotlib-v0.2.0a1
gsp-datoviz-v0.2.0a1
```

The target producer name is `vispy2`. Public publication under that name must nevertheless be preceded by an explicit naming and governance decision confirming that the package will not be misrepresented as an upstream release. Failure to obtain that decision is a publication stop condition, not a reason to merge GSP and VisPy2.

## Dependency And Backend Discovery Model

`gsp-core` should expose a small backend provider SPI. Concrete adapter distributions register providers through Python package entry points:

```toml
# gsp-matplotlib/pyproject.toml
[project.entry-points."gsp.backends"]
matplotlib = "gsp_matplotlib.plugin:get_provider"
```

```toml
# gsp-datoviz/pyproject.toml
[project.entry-points."gsp.backends"]
datoviz = "gsp_datoviz.plugin:get_provider"
```

The entry-point target should be a lightweight factory. Importing `gsp`, enumerating entry-point metadata, or importing the adapter’s `plugin` module must not create a window, device, event loop, renderer, or native graphics resource.

Candidate core SPI:

```python
from collections.abc import Collection
from typing import Protocol


class BackendProvider(Protocol):
    name: str
    plugin_api_version: int

    def describe(self) -> "BackendDescriptor":
        """Return static protocol versions and declared capabilities."""

    def probe(self) -> "BackendInfo":
        """Check runtime availability without creating a display."""

    def open_session(self, request: "SessionRequest") -> "Session":
        """Create the backend-owned session."""
```

`BackendDescriptor` should include at least:

```python
BackendDescriptor(
    name="datoviz",
    plugin_api_version=1,
    protocol_min="0.2",
    protocol_max_exclusive="0.3",
    declared_capabilities=frozenset(...),
)
```

Discovery and selection must follow this order:

1. Enumerate `gsp.backends` entry points without importing every native backend.
2. Reject duplicate backend names rather than choosing one nondeterministically.
3. Load only providers needed for inspection or selection.
4. Check plugin API and protocol compatibility.
5. Probe runtime availability.
6. Compare required semantic capabilities.
7. Construct an explicit adaptation plan, if an adaptation policy was supplied.
8. Reject unsupported required behavior before scene execution.
9. Open the session and expose all adaptations and warnings through diagnostics.

Recommended core entry points:

```python
def discover_backends(*, probe: bool = False) -> tuple["BackendInfo", ...]:
    ...


def open_session(
    backend: str | None = None,
    *,
    require: Collection[str] = (),
    prefer: tuple[str, ...] = (),
    adaptation: "AdaptationPolicy | None" = None,
) -> "Session":
    ...
```

Selection semantics:

* `backend="datoviz"` means Datoviz or an error; it must not silently fall back.
* `backend="matplotlib"` means Matplotlib or an error.
* `backend=None, prefer=("datoviz", "matplotlib")` permits deterministic caller-authorized fallback.
* `backend=None` with no preference should raise `BackendSelectionRequired`; GSP itself has no universal default backend.
* `Figure.savefig()` and blocking `Figure.show()` are the only 0.x APIs with an implicit backend policy, and that policy is Matplotlib.
* `adaptation=None` means exact capability satisfaction.
* Any permitted adaptation must be named by an `AdaptationPolicy` and returned in `session.diagnostics`.
* Capability failure must identify the unsupported semantic feature, the selected backend, and any available explicit adaptations.

The in-process path must pass typed GSP records, arrays, memory views, and resource objects directly to the provider. A local session must not serialize through JSON, base64, or a network schema. Encoders and transports should later consume the same semantic model through separate packages; they must not become the internal representation of `gsp-core`.

VisPy2 execution conveniences should delegate only to `gsp`:

```python
# vispy2/_execution.py

import gsp


def savefig(figure, path, **kwargs):
    scene = figure.to_scene()

    with gsp.open_session(
        "matplotlib",
        require={"output.file"},
    ) as session:
        return session.render(scene, target=path, **kwargs)
```

There is no import of `gsp_matplotlib` here. The entry-point resolver owns that relationship.

## Proposed VisPy2 API

The bounded public surface should consist of:

```text
vispy2.subplots
Figure.to_scene
Figure.savefig
Figure.show
Axes limit/label/title/grid methods
Axes scatter/plot/imshow/mesh methods
```

Remove `Figure.render_matplotlib()` from the public API. It exposes a concrete backend and duplicates `savefig()` and the session API.

Canonical session operations should live in `gsp`, not in a VisPy2-specific session class:

```text
gsp.discover_backends
gsp.open_session
Session.render
Session.display
Session.run
Session.close
Session.backend_name
Session.capabilities
Session.diagnostics
```

### One-shot publication output

```python
import vispy2 as vp

fig, ax = vp.subplots()

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Demo")
ax.grid(True)

ax.scatter(x, y, color=rgba, size=36)
ax.plot(x, y, color=rgba, width=4)

fig.savefig("out.pdf")
```

`savefig()` creates and closes an ephemeral Matplotlib session. It stores no backend, adapter, or renderer on `fig` or `ax`.

When `gsp-matplotlib` is not installed, it should raise an actionable error such as:

```text
BackendUnavailable: backend 'matplotlib' is not installed.
Install it with: pip install "vispy2[matplotlib]"
```

It must not try Datoviz or another backend silently.

### Interactive Datoviz display

```python
import gsp
import vispy2 as vp

fig, ax = vp.subplots()
ax.scatter(x, y, color=rgba, size=36)

with gsp.open_session(
    "datoviz",
    require={"display.interactive", "visual.points"},
) as session:
    display = session.display(fig.to_scene())
    session.run()
```

The session owns the Datoviz application, GPU device, window, event-loop integration, backend resources, and display handle. Closing the session releases them.

### Explicit backend-neutral session

```python
import gsp

with gsp.open_session(
    require={"visual.points", "visual.paths"},
    prefer=("datoviz", "matplotlib"),
) as session:
    image = session.render(
        fig.to_scene(),
        size=(1200, 800),
    )

print(session.backend_name)
```

The plotting code and scene are unchanged. The caller supplies an explicit selection policy; GSP selects a provider satisfying the requirements.

For a caller that already chose a backend name, the same session interface remains backend-neutral:

```python
def render_with(backend: str):
    with gsp.open_session(
        backend,
        require={"visual.points", "visual.paths"},
    ) as session:
        return session.render(fig.to_scene(), size=(1200, 800))
```

### Capability inspection

```python
import gsp

for info in gsp.discover_backends(probe=True):
    print(info.name)
    print("  available:", info.available)
    print("  protocol:", info.protocol_versions)
    print("  capabilities:")
    for capability in sorted(info.capabilities):
        print("   ", capability)

    for diagnostic in info.diagnostics:
        print("  diagnostic:", diagnostic)
```

Capability identifiers should be semantic and versioned by GSP, for example:

```text
display.interactive
output.file
visual.points
visual.paths
visual.image
visual.mesh
resource.texture2d
sampler.nearest
sampler.linear
```

They must not expose implementation concepts such as shader slots, Datoviz controllers, Matplotlib artists, draw calls, or native handles.

### API behavior contract

| Operation                        | Backend selection           | Lifetime             | Blocking behavior                                  |
| -------------------------------- | --------------------------- | -------------------- | -------------------------------------------------- |
| `fig.savefig(path)`              | Implicit Matplotlib default | Ephemeral session    | Completes before returning                         |
| `fig.show()`                     | Implicit Matplotlib default | Ephemeral session    | Blocking during 0.x                                |
| `gsp.open_session("datoviz")`    | Explicit                    | Caller-controlled    | Non-blocking display available through the session |
| `gsp.open_session("matplotlib")` | Explicit                    | Caller-controlled    | Determined by explicit session operations          |
| `gsp.open_session(prefer=...)`   | Explicit caller policy      | Caller-controlled    | Determined by selected capabilities                |
| `fig.to_scene()`                 | None                        | No backend resources | Pure producer snapshot                             |

`Figure.to_scene()` should return a logically immutable GSP scene snapshot. For local execution, large resources may remain zero-copy or shared read-only; logical immutability must not imply mandatory serialization or duplication.

## Migration And History Preservation

Use a **new-root curated migration**, not a history rewrite.

### 1. Establish the source baseline in `GSP_API`

Before copying files:

```bash
SOURCE_COMMIT=$(git rev-parse HEAD)

git tag -a migration/source-2026-07-22 \
    "$SOURCE_COMMIT" \
    -m "Source baseline for the GSP and VisPy2 repository split"

git status --short
git fsck --full
```

Record in a machine-readable baseline file:

```json
{
  "source_repository": "GSP_API",
  "source_commit": "<SOURCE_COMMIT>",
  "source_tag": "migration/source-2026-07-22",
  "date": "2026-07-22",
  "baseline_checks": {
    "tests": "680 passed, 2 skipped",
    "mypy": "strict passed",
    "ruff": "passed",
    "documentation_validation": "passed",
    "isolated_wheel_install": "passed",
    "isolated_sdist_install": "passed",
    "datoviz_texture2d_checkpoint": "passed at recorded development commit"
  }
}
```

The reported baseline includes 680 passing tests, strict checks, isolated package installation, and the Datoviz Texture2D checkpoint against the recorded development commit. 

Do not delete legacy files or reorganize the existing repository during this stage.

### 2. Create a preliminary complete archive

```bash
git bundle create GSP_API-source-2026-07-22.bundle --all
git bundle verify GSP_API-source-2026-07-22.bundle
sha256sum GSP_API-source-2026-07-22.bundle \
    > GSP_API-source-2026-07-22.bundle.sha256
```

Verify recoverability:

```bash
rm -rf /tmp/GSP_API-bundle-check

git clone \
    GSP_API-source-2026-07-22.bundle \
    /tmp/GSP_API-bundle-check

git -C /tmp/GSP_API-bundle-check fsck --full
git -C /tmp/GSP_API-bundle-check show migration/source-2026-07-22
```

Store the bundle and checksum in durable archival storage independent of the working clones.

### 3. Create both new repositories with fresh histories

Each new repository begins with a root commit containing:

```text
README.md
LICENSE
PROVENANCE.md
migration-manifest.json
initial package or workspace skeleton
```

Do not create the new roots with:

* `git filter-branch`;
* `git filter-repo` output;
* `git subtree split`;
* grafts or `git replace`;
* a shallow copy of the old commit graph;
* an imported `legacy` branch.

A filtered tree may be useful locally to inspect historical ownership, but it must not become the published history.

### 4. Record file-level provenance

Each curated file or logical group should be represented in `migration-manifest.json`:

```json
{
  "source_repository": "GSP_API",
  "source_commit": "<SOURCE_COMMIT>",
  "source_tag": "migration/source-2026-07-22",
  "entries": [
    {
      "source_path": "gsp/protocol/...",
      "source_blob": "<git-blob-id>",
      "destination_path": "packages/gsp-core/src/gsp/...",
      "classification": "migrate-now",
      "migration_commit": "<new-repository-commit>"
    }
  ]
}
```

Migration commit messages should include the source location:

```text
Import GSP 0.2 semantic records

Source: GSP_API@<SOURCE_COMMIT>
Paths: gsp/protocol/...
Classification: migrate-now
```

For rewritten files, list all contributing source paths and state that the destination is a derived rewrite rather than a byte-identical copy.

### 5. Build the new histories by responsibility

Use separate commits for:

1. protocol models and resources;
2. capability and diagnostics model;
3. session and plugin SPI;
4. normative specifications and ADRs;
5. conformance fixtures;
6. current tests;
7. Matplotlib adapter;
8. Datoviz v0.4 adapter;
9. VisPy2 producer;
10. documentation and examples.

This makes each migration decision reviewable and revertible.

### 6. Finalize the old repository as an archive

After the new repository locations and provenance documents have been reviewed, add one final non-destructive archive commit to `GSP_API` containing:

```text
ARCHIVED.md
MIGRATION.md
links or identifiers for the two new repositories
source and migration tags
bundle filename and SHA-256
instructions for verifying the bundle
```

Then create:

```bash
FINAL_COMMIT=$(git rev-parse HEAD)

git tag -a archive/gsp-api-final-2026-07-22 \
    "$FINAL_COMMIT" \
    -m "Final archived state before development moved to gsp and vispy2"

git bundle create GSP_API-full-2026-07-22.bundle --all
git bundle verify GSP_API-full-2026-07-22.bundle
sha256sum GSP_API-full-2026-07-22.bundle \
    > GSP_API-full-2026-07-22.bundle.sha256
```

Verify the final bundle with a clean clone and `git fsck --full`, then mark the repository read-only in its hosting service.

The old repository itself is the legacy branch and historical evidence base. Do not copy a `legacy` branch into either new repository; doing so would restore the clone size and conceptual ambiguity that the migration is intended to remove.

## Curated Migration Inventory

| Material                                                                                       | Classification   | Destination and action                                                                                                     |
| ---------------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Formal `gsp.protocol` semantic records                                                         | `migrate-now`    | Move to `gsp-core`; remove dependencies on legacy object-graph modules.                                                    |
| Session, capability, adaptation, and diagnostic contracts that implement accepted architecture | `migrate-now`    | Move to `gsp-core`; stabilize as the backend-neutral public runtime surface.                                               |
| Current normative specifications                                                               | `migrate-now`    | Move to `gsp/specs`; preserve identifiers and add source provenance.                                                       |
| Accepted, current ADRs                                                                         | `migrate-now`    | Move to `gsp/adrs`; preserve ADR identifiers where meaningful and mark their source status.                                |
| Superseded, exploratory, or unresolved specifications and ADRs                                 | `archive-only`   | Leave in `GSP_API`; summarize only material historical rationale in new ADRs.                                              |
| Canonical protocol and conformance fixtures                                                    | `migrate-now`    | Move the smallest authoritative fixture set to `gsp/conformance/fixtures`.                                                 |
| Bulk generated outputs and duplicated evidence artifacts                                       | `archive-only`   | Preserve in `GSP_API` and bundle; do not copy thousands of generated files.                                                |
| Exact Texture2D expected data and reproducible checkpoint test                                 | `migrate-now`    | Move the compact expected data, test, provenance, and backend/version requirements to the Datoviz package.                 |
| Raw Texture2D logs, screenshots, and repeated generated runs                                   | `archive-only`   | Preserve in the archived repository.                                                                                       |
| Current formal protocol unit tests                                                             | `migrate-now`    | Move to `gsp-core` tests; run against installed wheels as well as source.                                                  |
| Backend-neutral conformance tests                                                              | `migrate-now`    | Move to the GSP repository root and parameterize by registered provider.                                                   |
| Current Matplotlib protocol renderer                                                           | `migrate-now`    | Move to `gsp-matplotlib`; remove any legacy object-graph entry points.                                                     |
| Matplotlib conformance/publication tests                                                       | `migrate-now`    | Move with the adapter and canonical reference fixtures.                                                                    |
| Current Datoviz v0.4 protocol adapter                                                          | `migrate-now`    | Move to `gsp-datoviz`; build and test immediately, but defer publication until RC3 validation.                             |
| Datoviz 0.3 and `datoviz-legacy` support                                                       | `archive-only`   | Keep only in `GSP_API`; do not expose an extra or compatibility layer in new packages.                                     |
| New `gsp_vispy2` producer implementation                                                       | `migrate-now`    | Move to `vispy2/src/vispy2`; rename imports and update tests before public prerelease.                                     |
| Current producer tests                                                                         | `migrate-now`    | Move to `vispy2/tests`; test generated GSP scenes independently of any adapter.                                            |
| Old `vispy2` compatibility package and older plotting helpers                                  | `archive-only`   | Leave in `GSP_API`; do not publish compatibility aliases.                                                                  |
| Legacy `gsp` object-graph implementation                                                       | `archive-only`   | Preserve as research history; extract only independently justified algorithms or concepts.                                 |
| Legacy Matplotlib and Datoviz examples                                                         | `archive-only`   | Preserve in the archive; do not translate automatically.                                                                   |
| Current protocol-aligned examples                                                              | `migrate-now`    | Curate a small set covering each supported semantic visual family and both adapters.                                       |
| Current user documentation describing the accepted architecture                                | `migrate-now`    | Split between GSP protocol/session documentation and VisPy2 plotting documentation.                                        |
| Generated documentation output                                                                 | `archive-only`   | Rebuild from curated sources; do not migrate generated sites.                                                              |
| `gsp_network` experiments                                                                      | `defer/reassess` | Keep in the archive until a transport ADR defines framing, lifecycle, error handling, and capability negotiation.          |
| `gsp_pydantic` experiments                                                                     | `defer/reassess` | Keep outside the core; reassess as an optional encoding/validation package after the semantic model stabilizes.            |
| `gsp_extra`                                                                                    | `defer/reassess` | Review module by module. Move an item only into the package that owns its semantics; never recreate the catch-all package. |
| Remote/browser/cloud experiments                                                               | `defer/reassess` | Preserve as design input but do not let them define the current protocol core implicitly.                                  |
| `.agent` missions, consultations, control-plane history                                        | `archive-only`   | Retain in `GSP_API`; migrate only accepted decisions rewritten as concise ADRs with provenance.                            |
| `.claude`, `tmp/`, `my_doc/`, transient experiments                                            | `archive-only`   | Preserve through the old repository and bundle only.                                                                       |
| Package build outputs and temporary installation environments                                  | `archive-only`   | Regenerate in clean CI; do not migrate.                                                                                    |

A file should migrate only when it satisfies at least one of these tests:

* it defines current semantic authority;
* it is required to build the curated packages;
* it is required to reproduce a current conformance result;
* it is current user-facing documentation or an example for the target API.

Historical interest alone is not sufficient, because the complete historical repository remains recoverable.

## Release Sequencing Around Datoviz RC3

Repository migration and public package release must be separate decisions.

### Before RC3

The following can be migrated, built, tested, and publicly released as prereleases without an installable Datoviz RC3:

1. `gsp-core==0.2.0a1`;
2. `gsp-matplotlib==0.2.0a1`;
3. `vispy2==0.2.0a1`, with the `matplotlib` extra;
4. GSP specifications and conformance fixtures;
5. the backend discovery and explicit-session API;
6. source and internal build artifacts for `gsp-datoviz`.

The first public prerelease should occur only after the new repository and package topology is in place. Do not publish the old combined `gsp-vispy2` 0.2 distribution and rename it afterward. That would immediately create compatibility obligations around the architecture being intentionally removed.

Recommended sequence:

```text
new gsp repository accepted
    ↓
gsp-core 0.2.0a1
    ↓
gsp-matplotlib 0.2.0a1
    ↓
new vispy2 repository accepted
    ↓
vispy2 0.2.0a1 with matplotlib extra
```

Build `gsp-datoviz` continuously against the explicitly recorded Datoviz development checkout, but label those results as development evidence rather than a releasable dependency configuration.

### RC3 gate

Publish `gsp-datoviz==0.2.0a1` only after all of the following are true:

* an RC3 development artifact or normal installable dependency is available;
* no local-path dependency is required;
* the adapter imports in a clean environment;
* its provider can be discovered without creating a window or device;
* declared and probed capabilities agree;
* the complete adapter conformance suite passes;
* the exact native Texture2D checkpoint passes;
* nearest and linear texture-filter semantics pass;
* isolated wheel and sdist installations pass;
* no Datoviz-specific type leaks into `gsp-core` or `vispy2`;
* the dependency range is explicit and reproducible.

Then release:

```text
gsp-datoviz 0.2.0a1
    ↓
vispy2 0.2.0a2 with datoviz extra
```

Do not declare the coordinated 0.2 line stable until both the Matplotlib reference backend and the Datoviz flagship backend have passed the same protocol/conformance generation. RC3 should gate the stable dual-backend claim, but it should not gate alpha releases of the protocol, reference backend, or producer.

## Staged Implementation Plan

| Stage                                          | Repository                                 | Change                                                                                                                 | Reversible checkpoint                                                                              | Stop condition                                                                                         |
| ---------------------------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 0. Freeze the source baseline                  | Existing `GSP_API`                         | Record source commit, run existing checks, create source tag and preliminary full bundle. Make no deletions.           | Verified tag, bundle checksum, clean bundle clone, archived test report.                           | Any baseline result cannot be reproduced or the bundle cannot be verified.                             |
| 1. Approve the migration inventory             | Existing `GSP_API`                         | Add the proposed split ADR, authoritative-file inventory, and migration manifest draft.                                | Explicitly reviewed list of migrate/archive/defer paths.                                           | Protocol authority or file ownership remains disputed.                                                 |
| 2. Bootstrap `gsp`                             | New `gsp`                                  | Create fresh root; add provenance, workspace skeleton, protocol specs, and package boundaries.                         | Root commit can be discarded and recreated without affecting `GSP_API`.                            | The proposed core cannot be expressed without importing legacy object-graph packages.                  |
| 3. Recover `gsp-core` conformance              | New `gsp`                                  | Curate semantic records, resources, capabilities, diagnostics, sessions, fixtures, and tests.                          | `gsp-core` wheel installs in isolation and core tests pass.                                        | The wheel pulls Matplotlib, Datoviz, network, Pydantic, or legacy packages.                            |
| 4. Add provider discovery and Matplotlib       | New `gsp`                                  | Implement `gsp.backends` discovery; migrate Matplotlib renderer; run reference conformance.                            | Matplotlib provider is discoverable and installed-wheel conformance matches the accepted baseline. | Discovery imports all backends eagerly, creates resources, or allows silent capability adaptation.     |
| 5. Bootstrap `vispy2`                          | New `vispy2`                               | Create fresh root; migrate producer; rename `gsp_vispy2` to `vispy2`; add `to_scene()`; remove direct adapter imports. | Producer tests pass against an installed `gsp-core` wheel without any adapter installed.           | Figure, axes, or visuals retain backend/session/device state.                                          |
| 6. Restore one-shot and explicit execution     | Both new repositories                      | Implement Matplotlib `savefig()`/blocking `show()` delegation and explicit GSP session examples.                       | Same scene renders through both provider interfaces; optional dependency errors are actionable.    | `vispy2` imports `gsp_matplotlib` or `gsp_datoviz`, or backend selection is stored on the figure.      |
| 7. Cross-repository release qualification      | Both new repositories                      | Test package combinations from built wheels, validate docs/examples, and verify protocol version ranges.               | Release-candidate reports for `gsp-core`, `gsp-matplotlib`, and `vispy2`.                          | Tests pass only through source-tree imports or editable cross-repository paths.                        |
| 8. Finalize archive and publish initial alphas | Existing archive and both new repositories | Add archive pointers to `GSP_API`, create final tag/bundle, mark it read-only, publish approved prereleases.           | New repositories and complete archive are independently recoverable.                               | Provenance manifest, final bundle, naming authorization, or package ownership has not been accepted.   |
| 9. Validate Datoviz RC3                        | New `gsp`                                  | Install RC3 artifact normally; rerun adapter, native, Texture2D, capability, and packaging checks.                     | Accepted Datoviz release report and `gsp-datoviz` release candidate.                               | Any local checkout, undeclared dependency, native mismatch, or capability/conformance failure remains. |
| 10. Publish Datoviz adapter                    | New `gsp`, then `vispy2`                   | Publish `gsp-datoviz`; add the `vispy2[datoviz]` extra in the next VisPy2 alpha.                                       | Both backends satisfy the same GSP 0.2 compatibility range.                                        | The extra cannot resolve entirely from published artifacts.                                            |

Stages 0–7 must not depend on RC3. Stages 2–7 occur in new, initially unpublished repositories and can be abandoned or reconstructed while `GSP_API` remains authoritative. Publication is the first externally consequential checkpoint.

## Risks And Rejected Alternatives

### Key risks

| Risk                                 | Consequence                                                                                                                      | Mitigation                                                                                                                    |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Making GSP subordinate to VisPy2     | Protocol semantics become tied to one producer’s release cycle; other producers and remote servers appear secondary or internal. | Separate repositories and governance; all semantic changes originate in `gsp`.                                                |
| Cross-repository protocol drift      | VisPy2 may emit records unsupported by released adapters.                                                                        | Explicit `gsp-core>=0.2,<0.3` bounds, conformance fixtures, coordinated prerelease CI, and installed-wheel integration tests. |
| Loss of convenient historical blame  | New root commits do not provide direct `git blame` across the migration boundary.                                                | Full old repository, verified bundle, source tags, per-file blob mapping, and source references in migration commits.         |
| Accidental loss of research evidence | Curated copying may omit historical artifacts later considered valuable.                                                         | Archive the complete repository before migration; do not delete or rewrite it.                                                |
| Plugin discovery nondeterminism      | Multiple packages may claim the same backend name, or unavailable providers may be selected unexpectedly.                        | Reject duplicate names; use explicit backend or ordered preferences; expose probe diagnostics.                                |
| Native imports during discovery      | Merely importing GSP could fail on systems without graphics drivers or display access.                                           | Lightweight provider factories; defer native imports and resource creation to `probe()` or `open_session()`.                  |
| Optional Matplotlib default          | Bare `savefig()` may fail in a minimal VisPy2 installation.                                                                      | Actionable `BackendUnavailable` error and documented `vispy2[matplotlib]` installation. No silent fallback.                   |
| Capability vocabulary instability    | Backend-specific concepts may contaminate the semantic protocol.                                                                 | Version capability identifiers in GSP and require ADR review for additions or semantic changes.                               |
| Datoviz RC3 API changes              | The migrated adapter may need further work before publication.                                                                   | Isolate it in its own distribution and do not block core, Matplotlib, or producer alphas.                                     |
| `vispy2` product naming ambiguity    | Users may interpret an experimental package as an official upstream release.                                                     | Require explicit naming/governance authorization before public publication.                                                   |

### Rejected alternatives

| Alternative                                                                    | Decision                      | Reason                                                                                                                              |
| ------------------------------------------------------------------------------ | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Put GSP inside the VisPy2 repository                                           | Reject                        | Inverts the accepted architecture and subordinates a multi-producer, multi-server protocol to one producer.                         |
| One clean monorepo containing GSP, adapters, and VisPy2                        | Reject as the target topology | Cleaner than the current repository, but still couples product governance, issue tracking, releases, and historical identity.       |
| Clean `GSP_API` in place while retaining all history                           | Reject                        | Leaves a 1,009-commit mixed research history as the default development history and obscures the new product boundaries.            |
| Destructively rewrite or force-push `GSP_API`                                  | Reject                        | Risks evidence loss, invalidates references, and conflicts with the archival requirement.                                           |
| Publish filtered or subtree-extracted history as the new authoritative history | Reject                        | Filtering cannot reliably distinguish semantic authority from accidental co-location and may create misleading ancestry.            |
| Import a `legacy` branch into each new repository                              | Reject                        | Reintroduces repository size, confusion, and duplicated archival authority.                                                         |
| Keep one distribution containing all packages                                  | Reject                        | Makes backend and legacy dependencies mandatory and prevents independent release lifecycles.                                        |
| Create a repository for every adapter immediately                              | Reject for 0.2                | Adds release and CI fragmentation before third-party adapter governance exists. Separate distributions inside `gsp` are sufficient. |
| Preserve `gsp_vispy2` and legacy object paths as public compatibility packages | Reject                        | No known stable consumers justify permanent compatibility debt.                                                                     |
| Add `backend=` to `subplots()` or persist it on `Figure`                       | Reject                        | Mixes semantic producer state with execution policy and backend resources.                                                          |
| Let VisPy2 import adapters directly                                            | Reject                        | Makes optional dependencies effectively mandatory and couples the producer to concrete implementations.                             |
| Silently adapt unsupported visuals                                             | Reject                        | Violates explicit adaptation and diagnostic requirements and makes cross-backend output unpredictable.                              |

## ADR Draft

```markdown
# ADR-0001: Separate GSP protocol authority from the VisPy2 producer

- Status: proposed
- Date: 2026-07-22
- Decision scope: repository topology, Python package topology, backend discovery, and migration history
- Source repository: GSP_API
- Target protocol repository: gsp
- Target producer repository: vispy2

## Context

GSP is intended to be a backend-independent server and session protocol for
scientific visualization. It must support local in-process execution, remote
servers, browser or cloud execution, multiple producers, capability discovery,
and explicit adaptation.

VisPy2 is a high-level Python producer of GSP scenes. Matplotlib is the
reference and publication backend. Datoviz v0.4 is the flagship local GPU
backend.

The current GSP_API repository contains formal protocol work, current adapters,
the new producer, legacy object-graph implementations, experiments, generated
evidence, and control-plane history. It also publishes several import packages
from one distribution. There are no known public compatibility obligations.

## Accepted prior constraints

The following constraints predate this ADR and are not changed by it:

1. GSP semantics are independent of encoding and transport.
2. GSP is not defined by VisPy2.
3. Visual families are semantic contracts rather than backend draw calls.
4. A local in-process path must not require JSON or base64 serialization.
5. Capability discovery and explicit adaptation are mandatory.
6. Unsupported required behavior must be rejected before scene execution.
7. Figures, axes, and visuals own semantic producer state only.
8. Sessions own backend selection, adapter state, resources, event-loop
   integration, and displays.
9. Backend selection must not be stored on figures or axes.
10. Matplotlib remains the default for bare blocking show() and savefig()
    during 0.x.
11. Non-blocking display requires an explicit session.
12. Backend-specific handles and native concepts must not leak into the
    producer API.

## Decision

Two new repositories will be created with fresh root commits.

The `gsp` repository will own:

- the GSP semantic and session model;
- capability identifiers and adaptation diagnostics;
- the backend provider SPI;
- protocol specifications and ADRs;
- conformance fixtures and tests;
- the Matplotlib reference adapter;
- the Datoviz v0.4 adapter.

The `vispy2` repository will own:

- the public plotting API;
- producer-side figure and axes state;
- construction of typed GSP scene snapshots;
- plotting documentation and examples.

The following Python distributions and imports will be used:

- `gsp-core`, imported as `gsp`;
- `gsp-matplotlib`, imported internally as `gsp_matplotlib`;
- `gsp-datoviz`, imported internally as `gsp_datoviz`;
- `vispy2`, imported as `vispy2`.

`vispy2`, `gsp-matplotlib`, and `gsp-datoviz` will depend on `gsp-core`.
`gsp-core` will not depend on any producer or adapter.

Adapters will register lightweight provider factories in the
`gsp.backends` Python entry-point group. GSP will load providers lazily.
Explicit backend names will not fall back silently. Backend-neutral selection
will require an explicit ordered preference and capability requirements.

VisPy2 will expose `Figure.to_scene()`. `Figure.savefig()` and blocking
`Figure.show()` will create transient Matplotlib sessions through `gsp`.
Interactive and non-blocking execution will use `gsp.open_session(...)`.
`Figure.render_matplotlib()` will not be part of the target public API.

The `GSP_API` repository will not be rewritten. It will be preserved as a
read-only historical archive with annotated tags, a verified complete Git
bundle, checksums, and migration provenance.

The two new repositories will contain per-file or per-component provenance
mapping their imported material to the exact source commit, path, and Git blob.

## Consequences

Positive consequences:

- GSP remains usable and governable independently of VisPy2.
- Protocol-only users do not install Matplotlib, Datoviz, network, or legacy
  dependencies.
- Matplotlib and Datoviz may release on different schedules.
- New clones and default history contain only current product material.
- The old research history remains fully recoverable and auditable.
- The VisPy2 public API no longer exposes concrete backend implementations.

Negative consequences:

- Some changes require coordinated pull requests across two repositories.
- Direct `git blame` stops at the curated migration boundary.
- Several distributions must be built and released independently.
- Public use of the `vispy2` name requires an explicit governance decision.
- The Datoviz adapter may remain unreleased while waiting for an installable
  RC3-compatible dependency.

## Migration

Migration will use curated copies into new root commits. It will not use
force-pushes, destructive rewriting, filtered published history, subtree
ancestry, grafts, or imported legacy branches.

Only current protocol authority, conformance evidence, adapters, producer
code, current tests, and curated documentation/examples will migrate.
Legacy object graphs, Datoviz 0.3 support, bulk generated artifacts, and agent
control-plane history will remain archive-only. Network, Pydantic, and extra
experiments will be reassessed after the core 0.2 surface is stable.

Repository migration will precede the first public 0.2 prerelease.

`gsp-core`, `gsp-matplotlib`, and `vispy2` prereleases may be published before
Datoviz RC3. `gsp-datoviz` publication requires a normally installable RC3
artifact, full conformance, isolated package installation, and the exact
native Texture2D checkpoint.

## Rejected alternatives

- GSP inside the VisPy2 repository;
- one combined GSP and VisPy2 distribution;
- cleaning GSP_API in place as the new default development repository;
- rewriting or force-pushing GSP_API;
- publishing filtered legacy ancestry as the new project history;
- importing legacy branches into the new repositories;
- storing backend selection or resources on producer objects;
- direct imports of concrete adapters from VisPy2;
- silent backend fallback or silent capability adaptation.

## Out of scope

This ADR does not define:

- a network framing or transport protocol;
- a Pydantic or JSON encoding;
- incremental scene-delta semantics;
- remote authentication or authorization;
- browser deployment;
- a broad Matplotlib-compatible plotting surface;
- third-party adapter governance beyond the initial provider SPI.
```

## Stop Conditions

| Stop condition                                             | Trigger                                                                                                                                    | Required action                                                                                      |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Source baseline is not reproducible                        | Existing tests, strict checks, package installation, or recorded native checkpoint cannot be rerun from the tagged source commit.          | Stop extraction. Keep `GSP_API` authoritative until the discrepancy is understood and recorded.      |
| Archive is not independently recoverable                   | Bundle verification, clean clone, checksum verification, or `git fsck --full` fails.                                                       | Do not modify archive status or publish new repositories. Recreate and reverify the bundle.          |
| Provenance is incomplete                                   | A migrated normative file, fixture, or implementation cannot be mapped to source commit/path or documented as a rewrite.                   | Do not merge the relevant migration commit.                                                          |
| Core still depends on legacy code                          | `gsp-core` imports the old object graph, compatibility packages, or experimental network/Pydantic modules.                                 | Stop the core migration and either remove the dependency or explicitly reclassify the required code. |
| Protocol-only installation pulls a backend                 | Installing `gsp-core` installs Matplotlib, Datoviz, or backend-specific dependencies.                                                      | Reject the package boundary and correct dependency metadata.                                         |
| Discovery is eager or side-effectful                       | `import gsp` or unprobed discovery imports native libraries, creates graphics resources, or accesses a display.                            | Do not accept the provider SPI implementation.                                                       |
| Capability behavior is implicit                            | Unsupported behavior reaches rendering, adaptation occurs without policy, or diagnostics omit substitutions.                               | Stop API stabilization and correct the capability/adaptation contract.                               |
| Producer owns execution state                              | Figure, axes, or visuals retain backend, session, adapter, device, window, event-loop, or display state.                                   | Reject the VisPy2 migration commit.                                                                  |
| VisPy2 imports concrete adapters                           | `vispy2` imports `gsp_matplotlib` or `gsp_datoviz` directly.                                                                               | Replace the dependency with GSP provider discovery before proceeding.                                |
| Installed-wheel integration fails                          | Tests succeed only through source-tree or editable cross-repository imports.                                                               | Do not publish prereleases; fix packaging and dependency metadata first.                             |
| Matplotlib reference conformance regresses                 | Current semantic scenes or canonical fixtures no longer pass the accepted reference backend tests.                                         | Stop the core/Matplotlib prerelease.                                                                 |
| Datoviz remains a local-only dependency                    | RC3 is unavailable through a reproducible artifact or ordinary dependency resolution.                                                      | Continue development builds only; do not publish `gsp-datoviz`.                                      |
| Datoviz native checkpoint regresses                        | Texture2D, texture-filter, capability, packaging, or native integration validation fails.                                                  | Do not publish the Datoviz adapter or advertise the `vispy2[datoviz]` extra.                         |
| Public `vispy2` naming is unauthorized                     | Product ownership, upstream relationship, or package-name authority is unresolved.                                                         | Do not publish under the `vispy2` name until a separate governance decision is recorded.             |
| A migration step requires destructive history modification | Any proposal requires force-pushing, deleting old refs, or rewriting the existing repository.                                              | Reject that step. Preserve the existing repository and use new-root migration instead.               |
| Scope expands into a big-bang rewrite                      | Migration begins redesigning remote transport, incremental updates, all legacy features, or broad Matplotlib compatibility simultaneously. | Stop the expanded work and return to the bounded 0.2 migration inventory.                            |

