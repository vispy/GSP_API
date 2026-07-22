# S061 proposal - GSP and VisPy2 migration foundation

Date: 2026-07-22

Status: approved; M257 completed and M258 is ready.

## Objective

Convert the accepted parts of P037 into a reproducible, non-destructive migration foundation before
any new product repository is created: decide the topology and target identity, freeze and verify the
source baseline, preserve a recoverable local archive, and approve a curated migration inventory.

## Proposed sequence

| Mission | State | Scope |
|---|---|---|
| M257 | completed | Accepted ADR-0035 and recorded owner approval of the two-repository topology and `vispy2` identity. |
| M258 | approved | Reproduce the source baseline and prepare a verified local source archive with exact provenance. |
| M259 | draft | Classify authoritative files and logical components as migrate-now, archive-only, or defer/reassess. |
| M260 | draft | Review the manifest, close S061, and propose the separately approved local bootstrap of new repositories. |

## Guardrails

- Do not delete, rewrite, filter, force-push, or mark `GSP_API` read-only.
- Do not create remote repositories, pushes, PRs, public tags, releases, or package publications.
- Do not change public Python APIs or move implementation files during S061.
- Do not copy bulk artifacts or agent-control history into a new product tree.
- A local bundle must be stored outside the Git working tree and verified by checksum, bundle
  verification, clean clone, and `git fsck`; its durable destination remains an owner decision.
- Creating the new `gsp` and `vispy2` repositories requires a later explicit mission approval.

## Approval

The project owner explicitly approved the P037 two-repository topology, the target `vispy2`
distribution/import identity, and M257-M260 as the bounded S061 migration-foundation sequence in the
active Mission Control conversation on 2026-07-22.
