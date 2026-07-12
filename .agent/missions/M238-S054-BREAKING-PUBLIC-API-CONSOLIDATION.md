# M238 - S054 breaking public protocol and producer API consolidation

## Stage

S054 - GSP 0.2 Protocol API And Documentation Consolidation

## Status

Completed.

## Summary

Align Python protocol records and the experimental producer surface with GSP 0.2. Prefer coherent
breaking changes over compatibility shims while preserving the accepted ADR-0033 ownership model.

## Stop Conditions

Do not add backend state to figures, expose native handles, require local serialization, or publish
an unproven general session/update contract.

## Approval

Approved by the project owner's instruction to execute the full breaking consolidation.

## Result

The distribution is `gsp-vispy2` 0.2.0 and the sole producer import is `gsp_vispy2`; the ambiguous
unqualified `vispy2` import is intentionally removed. The protocol exports version `0.2`, structured
diagnostics, explicit command status, negotiated initialize version, deterministic capability
snapshot identity, strict in-process sequencing, and lifecycle rejection after close. Legacy mesh
shading aliases are removed.

ADR-0033 remains intact: figures contain semantic producer state only and no general public session
or display/update contract is promoted. Full pytest passed with 644 passed and 2 skipped; strict
mypy, Ruff, package build, import surface, and traceability checks pass.
