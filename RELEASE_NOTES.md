# GSP VisPy2 0.2.0 release candidate

Audit date: 2026-07-12

GSP VisPy2 0.2.0 is a deliberately breaking, pre-1.0 consolidation release. It establishes a
protocol-centered public API, an independent `gsp_vispy2` producer, evidence-backed backend
profiles, executable documentation, and a bounded experimental Datoviz session preview.

## Highlights

- Ten normative GSP 0.2 specification chapters with 90 stable requirement identifiers.
- Semantic records for visuals, guides, layouts, transforms, queries, View2D, View3D, color mapping,
  mesh materials, navigation, data sources, extensions, and security boundaries.
- Independent `gsp_vispy2` producer with deterministic figure, axes, visual, resource, and guide
  records.
- Matplotlib reference execution and capability-gated Datoviz v0.4 adapter paths.
- Experimental explicit `open_session("datoviz")` with capability inspection, bounded blocking
  display, one-frame polling, structured diagnostics, and deterministic owned cleanup.
- Machine-readable producer/backend profiles, generated feature matrix, conformance fixtures,
  visual review packs, and requirement-to-test traceability.
- Executable public documentation, migration redirects, and screenshot provenance.

## Breaking changes from 0.1

- Distribution renamed to `gsp-vispy2`; import the producer as `gsp_vispy2`.
- The ambiguous `vispy2` compatibility package is removed.
- The public learning path now uses semantic GSP records and explicit capability/execution
  boundaries instead of the legacy object-graph renderer API.
- Legacy mesh-shading aliases are removed.
- Transport sequencing, lifecycle, snapshot identity, command status, and diagnostics are stricter.

See the [0.2 migration guide](mkdocs_source/development-history/migration-0.2.md) for concrete import
and API changes.

## Backend support

- **Matplotlib:** portable reference backend for documented static rendering and conformance paths.
- **Datoviz v0.4:** optional, capability-gated GPU backend. Bounded explicit session execution is an
  experimental partial surface, not a parity claim.

Datoviz title/layout and guide-query behavior may be adapted or unsupported even when geometry
renders successfully. Texture2D mesh rendering, image scientific readback, mesh-triangle identity,
general retained display updates, implicit sessions, close callbacks, and event-loop embedding are
not promoted by this release.

## Validation evidence

- S053 internal lifecycle evidence and S056 public-wrapper conformance evidence.
- Ten repeated public Datoviz session subprocesses: five blocking and five polling, all clean with
  zero timeouts.
- Release-candidate scatter and flat-Lambert comparison images for Matplotlib and Datoviz.
- Fresh wheel and source distribution, clean Python 3.13 wheel installation, package-content audit,
  strict documentation, profile consistency, typing, lint, and full test validation.

## Installation

After publication:

```bash
python -m pip install gsp-vispy2==0.2.0
```

Datoviz v0.4 is not declared as a package dependency because a compatible public wheel is not yet
available. Datoviz examples require a separately configured compatible local binding.

## Release boundary

This candidate does not authorize or imply a Git tag, GitHub release, or package upload. Those
operations require a separate explicit release approval.
