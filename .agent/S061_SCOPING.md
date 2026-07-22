# S061 proposal - GSP and VisPy2 migration foundation

Date: 2026-07-22

Status: proposed; awaiting explicit project-owner approval.

## Objective

Convert the accepted parts of P037 into a reproducible, non-destructive migration foundation before
any new product repository is created: decide the topology and target identity, freeze and verify the
source baseline, preserve a recoverable local archive, and approve a curated migration inventory.

## Proposed sequence

| Mission | State | Scope |
|---|---|---|
| M257 | draft | Accept or revise ADR-0035 and record the owner decision on the `vispy2` identity. |
| M258 | draft | Reproduce the source baseline and prepare a verified local source archive with exact provenance. |
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

## Approval requested

Approve the P037 two-repository topology and the target `vispy2` distribution/import identity, then
approve M257-M260 as the bounded S061 migration-foundation sequence.

