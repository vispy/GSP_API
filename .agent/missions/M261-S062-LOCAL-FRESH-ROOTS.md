# M261 - S062 local fresh-root repositories

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Approved.

## Summary

Create local unpublished `gsp` and `vispy2` Git repositories with fresh root commits, provenance,
migration manifests, licenses, package skeletons, validation configuration, and explicit AGENTS
rules. Do not migrate implementation code yet.

## Acceptance

- Both repositories have independent fresh roots and no inherited legacy refs.
- Provenance names GSP_API baseline `463d34d` and the verified bundle checksum.
- Package boundaries and dependency directions are encoded before implementation copying.
- Initial commits are independently revertible and contain no bulk artifacts.

## Stop conditions

Stop if either target path exists unexpectedly, repository ownership/visibility is inferred, history
is imported, a remote is added, or package boundaries conflict with ADR-0035.
