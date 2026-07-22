# P037 - VisPy2 Plotting API And GSP Repository Architecture

Date: 2026-07-22

## Status

Awaiting ChatGPT Pro response. No repository extraction, history rewrite, package rename, or public API
restructuring may depend on this consultation until the response is recorded and accepted.

## Exact prompt for ChatGPT Pro

You are advising on the product and repository architecture of an experimental scientific
visualization project. Produce a decisive recommendation, not a generic list of possibilities. The
entire relevant context is embedded below; do not assume access to files or repositories.

### Project objective and authority

The project charter says:

- GSP (Graphics Server Protocol) is a backend-independent server/session protocol for scientific
  visualization, inspired by LSP rather than merely being a Python object graph.
- One semantic visualization description should target fast local GPU rendering through Datoviz
  v0.4, reference/publication rendering through Matplotlib, remote renderers, and future browser or
  specialized backends.
- Local execution must have an in-process path with no mandatory JSON/base64 serialization.
- Capability discovery and explicit adaptation are mandatory.
- Visual families are semantic contracts, not backend draw calls.
- Datoviz v0.4 is the flagship GPU backend; Matplotlib is the reference/conformance/publication
  backend.
- VisPy2 is the high-level Python producer of GSP scenes.
- The existing GSP_API repository is a research prototype and implementation seed. It should be
  mined rather than blindly preserved, and its old object model is not protocol authority.

The accepted layered architecture is:

```text
VisPy2 / plotting APIs / domain libraries
  -> GSP producer API
    -> GSP session and protocol model
      -> backend adapters
        -> Matplotlib reference backend
        -> Datoviz v0.4 GPU backend
        -> future remote/web/specialized backends
```

GSP semantics are encoding-independent and a GSP server may be in-process, a subprocess, remote, a
browser worker, or a cloud GPU service. Thus VisPy2 is intended to be one important producer, not
the definition of GSP itself.

### Current repository state

The repository is named `GSP_API`. It has 1,009 commits and a 71 MiB `.git` directory. It contains
substantial research and generated evidence:

- 3,623 tracked artifact files;
- 609 tracked `.agent` control-plane, mission, decision, and consultation files;
- 227 source files;
- 102 examples, 87 current documentation files, 56 specification files, 47 test files, 35 ADRs;
- 64 tracked `tmp/` experiments plus old `my_doc/` and `.claude/` material.

The current source tree ships seven import packages from one distribution named `gsp-vispy2`
version 0.2.0:

```text
gsp             114 source files (25 are under the new formal gsp.protocol subtree)
gsp_datoviz      23 source files
gsp_matplotlib   38 source files
gsp_extra        20 source files
gsp_network      12 source files
gsp_pydantic      7 source files
gsp_vispy2       13 source files
```

Much of `gsp`, both backend packages, and the examples are old object-graph implementations. The
current formal protocol, current Matplotlib protocol renderer, Datoviz v0.4 protocol adapter, and
new `gsp_vispy2` producer coexist with that legacy code. Packaging all of it in one distribution
makes current versus legacy boundaries difficult for users and maintainers to understand.

The current `pyproject.toml` makes Matplotlib and several legacy/network dependencies mandatory.
Datoviz v0.4 is deliberately not yet a declared dependency because the validated v0.4-compatible
binding exists only in a local development checkout. A `datoviz-legacy` extra still targets Datoviz
0.3.2 through 0.3.x.

GSP 0.2 source and package artifacts have passed 680 tests (2 skipped), strict mypy, Ruff, strict
documentation validation, isolated wheel/sdist installation, and an exact native Datoviz
Texture2D checkpoint. The current Datoviz evidence is against development commit
`be7f2a80354c25e85bab88c85f5ea7340975b569`, described as
`v0.4.0rc2-15-gbe7f2a803`. Release operations are intentionally waiting for the next Datoviz RC3
development commit or artifact and explicit user authorization.

### Current VisPy2 producer API

The public import is currently `gsp_vispy2`, explicitly described as an independent experimental
producer rather than an official upstream VisPy 2.0 release. Its intended user shape is:

```python
import gsp_vispy2 as vp

fig, ax = vp.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Demo")
ax.grid(True)
ax.scatter(x, y, color=rgba, size=36)
ax.plot(x, y, color=rgba, width=4)
ax.imshow(image, colormap="gray", clim=(0.0, 1.0))
ax.mesh(positions, faces, color=rgba)
fig.savefig("out.png")
```

It emits typed GSP records for figures, panels, View2D state, visual attachments, points, markers,
segments, paths, images, text, meshes, guides, color scales, and Texture2D resources. Textured mesh
supports `texture_filter="nearest" | "linear"` with bounded sampler semantics.

The accepted producer/session boundary says:

- figures and axes own semantic producer state only;
- backend, device, adapter, window, event-loop, and execution-resource state must not be stored on
  figures, axes, or visuals;
- explicit sessions own capabilities, adapter state, backend resources, event-loop integration, and
  displays;
- backend selection must not be added to `subplots()` or retained on `Figure`;
- unsupported behavior rejects before execution and adaptations produce diagnostics;
- Matplotlib remains the default for bare `show()` and `savefig()` during 0.x;
- non-blocking display requires an explicit session;
- backend-specific handles, shader slots, draw calls, and native controllers must not leak into the
  producer API.

The current prototype only partly realizes that architecture:

- `Figure.render_matplotlib()`, `Figure.savefig()`, and `Figure.show()` directly import and call the
  Matplotlib adapter.
- `open_session("datoviz")` exists as an experimental explicit session, but its implementation
  directly imports Datoviz adapter types and only accepts the literal Datoviz backend.
- The API covers useful plotting primitives but is not intended to be a broad Matplotlib clone.
- The old `vispy2` compatibility package and older plotting helpers coexist with `gsp_vispy2`.

### Product question

The owner now wants to continue toward a practical VisPy2 plotting API based on GSP where the same
plotting code works on both Datoviz and Matplotlib. The owner also wants to clean up the large amount
of old code and specifically wants a cleaner Git history. They are considering:

1. putting GSP code inside a VisPy2 repository;
2. creating a clean new GSP repository;
3. creating separate clean GSP and VisPy2 repositories;
4. keeping a monorepo but extracting only curated current code into a new root commit;
5. cleaning the current GSP_API repository in place, possibly retaining all history.

No public release, stable external consumers, or compatibility obligation is known yet. History is
valuable as an archive and evidence base, but need not remain the default development history. It
must remain recoverable and traceable. Do not recommend force-pushing or destructively rewriting
the existing repository. A new repository, archived branch, Git tag, Git bundle, or explicit
provenance manifest may be used to preserve history.

### Decisions required

Decide all of the following:

1. Product/repository topology: one clean monorepo, GSP inside a VisPy2 repo, separate GSP and
   VisPy2 repos, or cleaned-in-place GSP_API. Name the recommended repositories and their ownership
   boundaries.
2. Python distribution/import topology: whether protocol core, Matplotlib adapter, Datoviz adapter,
   and VisPy2 producer should be one distribution, several distributions in one monorepo, or
   separate distributions/repositories. Give concrete candidate distribution and import names.
3. Dependency direction and plugin discovery: show how VisPy2 opens either Matplotlib or Datoviz
   without directly importing concrete adapters in its semantic producer module and without making
   Matplotlib mandatory for protocol-only users.
4. Public API shape for the next bounded version: provide short code examples for one-shot
   publication output, interactive Datoviz display, explicit backend-neutral sessions, and
   capability inspection. Respect the accepted rule that backend selection is not stored on a
   figure or axes.
5. Migration/history strategy: specify exactly how to start clean while preserving the old
   repository as a traceable archive. Address whether to use a new root commit, filtered history,
   subtree extraction, an archived legacy branch, tags, bundles, or provenance documents.
6. Curated migration inventory: classify current material into migrate-now, archive-only, and
   defer/reassess. Include the formal protocol, specs/ADRs, fixtures, current tests, adapters,
   producer, legacy object graph, old Datoviz 0.3 adapter, network/Pydantic experiments, generated
   artifacts, agent-control history, docs, and examples.
7. Release sequencing relative to Datoviz RC3: say what can be built and released independently,
   what must wait for RC3, and whether repository migration should happen before or after the first
   public 0.2 prerelease.
8. A staged implementation plan with reversible checkpoints and explicit stop conditions. Avoid a
   big-bang rewrite.
9. Key risks and rejected alternatives. Explicitly address the architectural risk of making GSP
   subordinate to VisPy2 even though GSP is intended for other producers and remote servers.

Favor a small, understandable public surface and clean dependency boundaries over preserving the
current package layout. Preserve protocol semantics and conformance evidence, not accidental legacy
module paths. Treat repository naming and import naming as product decisions, not mere file moves.

## Exact expected output format

Return Markdown with exactly these top-level headings:

```markdown
# Recommendation
## Decision Table
## Target Repository Topology
## Target Python Package Topology
## Dependency And Backend Discovery Model
## Proposed VisPy2 API
## Migration And History Preservation
## Curated Migration Inventory
## Release Sequencing Around Datoviz RC3
## Staged Implementation Plan
## Risks And Rejected Alternatives
## ADR Draft
## Stop Conditions
```

Under `# Recommendation`, give a direct answer in no more than five paragraphs. Under `## Decision
Table`, include one row per required decision with columns `Decision`, `Recommendation`, and
`Reason`. Include concrete repository names, distribution/import names, dependency arrows, and
Python examples. The staged plan must identify which changes happen in the existing repository and
which happen in any new repository. The ADR draft must be ready to save with status `proposed` and
must distinguish accepted prior constraints from new recommendations.

## Expected result handling

Paste the complete response into `.agent/consultations/P037-response.md`. Mission Control will
review it against the charter, architecture, specification authority, and current implementation,
then propose a bounded migration mission for explicit approval. No destructive history operation,
new external repository creation, package publication, push, tag, or merge is implied by this
packet.
