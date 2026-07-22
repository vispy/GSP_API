# M259 curated migration inventory

Date: 2026-07-22

## Outcome

The migration inventory is complete at component level and tied to source baseline
`463d34d1d6560f045e5c40af594372d0fea93ab5`. It classifies 31 components and records an exact Git
blob or tree object for every source component:

| Classification | Components | Meaning |
|---|---:|---|
| `migrate-now` | 16 | Required for the first clean GSP/VisPy2 product repositories |
| `archive-only` | 11 | Preserved in `GSP_API` and the verified bundle, not copied wholesale |
| `defer-reassess` | 4 | Product idea may return later under a new explicit owner and contract |

The machine-readable authority is `.agent/migration/S061_migration_manifest.json`.

## Target ownership

| Target | Migrates now |
|---|---|
| `vispy/gsp` / `gsp-core` | Formal protocol records, future session/provider SPI, current specification, accepted rationale, canonical fixtures, core tests |
| `vispy/gsp` / `gsp-matplotlib` | Current protocol renderer/query/layout/navigation/color/guide implementation and focused tests |
| `vispy/gsp` / `gsp-datoviz` | Current v0.4 protocol renderer/capability/query/import implementation, exact native checkpoints, focused tests |
| `vispy/gsp` / conformance workspace | Backend-neutral cases, reports, comparisons, compact expectations, provider-parameterized replay |
| `vispy/vispy2` | Current semantic Figure/Axes producer behavior, producer tests, curated plotting docs/examples, rewritten session delegation |

## Dependency audit

The formal protocol tree has no dependency on the legacy GSP object graph. The current formal
Matplotlib and Datoviz implementation files depend on formal `gsp.protocol` records rather than
legacy visuals, provided their legacy package initializers and registration modules are excluded.

Four expected couplings must be removed during the new-repository bootstrap:

| Boundary | Current coupling | Required migration action |
|---|---|---|
| `gsp-core` | `gsp.protocol.color_mapping` imports Matplotlib for named colormap lookup | Replace with backend-independent canonical color data/logic or move renderer realization behind the adapter boundary |
| `gsp-matplotlib` | Current `__init__.py` eagerly imports legacy animator/renderer/extra/utils/event packages | Write a minimal new initializer and lazy `gsp.backends` provider; do not copy the legacy initializer |
| `gsp-datoviz` | `v04_import.py` and probes bootstrap a sibling source checkout | Keep source bootstrap development-only, make discovery side-effect-free, and require an ordinary RC3-compatible artifact before publication |
| `vispy2` | `protocol.py` imports Matplotlib and `session.py` imports Datoviz directly | Add `Figure.to_scene()`, move sessions to `gsp-core`, and remove every concrete adapter import |

The shared QA runner also imports both adapters directly. It migrates only as a provider-parameterized
conformance tool outside `gsp-core`.

No unexplained archive-only dependency was found. Tests that exercise legacy buffers, materials,
renderers, or mixed old/new import surfaces remain archive-only or must be split before copying.

## Curated source decisions

- All 25 modules under `src/gsp/protocol` migrate, with the Matplotlib dependency above treated as a
  blocking rewrite rather than accepted core architecture.
- The committed source inventory selects 11 consolidation chapters, 39 detailed normative sources,
  36 accepted rationale records, and 19 accepted decision records. `.agent` itself does not migrate.
- Matplotlib migrates only the formal protocol renderer/query/layout/navigation/color/guide files.
- Datoviz migrates only the v0.4 capability/query/protocol/import files; the v0.3 RendererBase tree
  and `datoviz-legacy` packaging do not migrate.
- VisPy2 migrates the current semantic producer behavior from three top-level files as a derived
  rename/rewrite. Old axes/scatter/plot/imshow helper subpackages remain research material.
- Canonical conformance fixtures and compact numeric expectations migrate. Thousands of generated
  review artifacts, screenshots, and repeated run reports stay in the archive.
- Current public documentation is split by owner and rewritten for the new package topology.
  Generated sites, legacy package reference pages, and development history are not copied verbatim.
- `gsp_network`, `gsp_pydantic`, and `gsp_extra` implementations stay archived. Their product ideas
  may be reconsidered later but cannot define or enter `gsp-core` implicitly.

## Provenance rules for the actual import

The S061 manifest records component-level source objects. Each later destination import commit must
also record every copied file's exact source path and blob ID, destination path, and whether the
destination is byte-identical or a derived rewrite. New files such as provider/session modules cite
ADR-0035 rather than claiming copied ancestry.

No filtered history, subtree ancestry, graft, `git replace`, or legacy branch is used. The verified
M258 bundle remains the complete historical authority across the fresh-root boundary.

## Bootstrap gates exposed by M259

1. `gsp-core` installs and imports without Matplotlib, Datoviz, legacy, network, or Pydantic.
2. Metadata discovery does not import native backends or create display/device resources.
3. Duplicate backend names and incompatible plugin/protocol versions fail deterministically.
4. Matplotlib and Datoviz register separate lightweight providers.
5. VisPy2 producer tests pass with only an installed `gsp-core` wheel.
6. Execution tests pass from built wheel combinations, never only from editable/source-tree imports.
7. No archive-only directory is copied wholesale.

## Next mission

M260 should review this manifest with the archive evidence, close S061, and propose the exact local
fresh-root bootstrap stage. It must not create either repository, publish a tag, or mutate a remote.

