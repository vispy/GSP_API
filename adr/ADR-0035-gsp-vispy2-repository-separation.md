# ADR-0035: Separate GSP Protocol Authority From The VisPy2 Producer

Status: accepted

Date: 2026-07-22

## Context

GSP is an encoding-independent scientific graphics session protocol intended for multiple
producers, local and remote servers, and several rendering backends. VisPy2 is a high-level Python
plotting producer for GSP. The current `GSP_API` research repository mixes the formal GSP 0.2
implementation with legacy object graphs, old adapters, experiments, generated artifacts, and
control-plane history, and ships seven imports from one distribution.

The project needs a clean product history and dependency structure without losing the complete
research record. P037 reviewed repository topology, distribution boundaries, backend discovery,
public producer execution, provenance, and release sequencing.

## Accepted prior constraints

- GSP semantics are not defined by VisPy2, a backend, or an encoding.
- Figures, axes, visuals, and scene snapshots contain semantic producer state only.
- Sessions own backend choice, adapters, native resources, event loops, and displays.
- Capability requirements, adaptations, and unsupported behavior are explicit.
- Local execution does not require JSON or base64.
- Matplotlib is the reference/publication backend and the 0.x one-shot default.
- Datoviz v0.4 is the flagship GPU backend.

## Decision

Create two repositories with fresh root commits:

1. `gsp` owns protocol authority, specifications, ADRs, conformance, the backend provider SPI, and
   the initial Matplotlib and Datoviz adapter packages.
2. `vispy2` owns the plotting API, producer-side semantic state, scene construction, producer tests,
   and plotting documentation.

Use separate distributions:

| Distribution | Import | Repository |
|---|---|---|
| `gsp-core` | `gsp` | `gsp` |
| `gsp-matplotlib` | `gsp_matplotlib` | `gsp` |
| `gsp-datoviz` | `gsp_datoviz` | `gsp` |
| `vispy2` | `vispy2` | `vispy2` |

`vispy2` and each adapter depend on `gsp-core`; core depends on neither producers nor adapters.
Adapters register lazy providers through the `gsp.backends` entry-point group. VisPy2 converts a
figure to an immutable semantic scene and invokes only GSP session APIs. It does not import concrete
adapters. Backend selection is never stored on a figure or axes.

Preserve `GSP_API` without rewriting it. Curate current files into the new repositories with source
commit, source path, and blob provenance. Preserve the full historical repository and a verified Git
bundle rather than publishing filtered ancestry or copying legacy branches into the new repositories.

Repository migration precedes the first public 0.2 prerelease. `gsp-core`, `gsp-matplotlib`, and
`vispy2` may qualify independently of Datoviz RC3. Publishing `gsp-datoviz` requires a normally
installable RC3-compatible dependency plus full adapter, packaging, capability, native, and
Texture2D checkpoints.

## Consequences

- Protocol-only installations do not pull Matplotlib, Datoviz, or legacy/network dependencies.
- GSP remains independently usable by other producers and server implementations.
- VisPy2 and GSP require coordinated versioned integration rather than same-repository imports.
- Direct blame stops at the curated root, but full history and file-level provenance remain
  recoverable.
- Multiple distributions and two repositories add release and CI coordination.
- The temporary `gsp-vispy2`/`gsp_vispy2` identity from ADR-0033 is superseded only if this ADR and
  the `vispy2` naming/governance decision are explicitly accepted.

## Rejected alternatives

- placing GSP inside the VisPy2 repository;
- another combined umbrella distribution;
- cleaning `GSP_API` in place as the new product history;
- destructive or force-pushed history rewriting;
- publishing filtered/subtree ancestry or importing legacy branches;
- direct VisPy2 imports of Matplotlib or Datoviz adapters;
- implicit backend state, fallback, or silent adaptation.

## Approval

The project owner explicitly approved the two-repository topology, the target `vispy2`
distribution/import identity, and the bounded S061 migration-foundation stage in the active Mission
Control conversation on 2026-07-22. This acceptance does not authorize remote repository creation,
pushes, publication, archival hosting changes, destructive history modification, or the later
new-repository bootstrap stage.
