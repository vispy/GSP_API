# M238 - S054 breaking public protocol and producer API consolidation

## Stage

S054 - GSP 0.2 Protocol API And Documentation Consolidation

## Status

Approved.

## Summary

Align Python protocol records and the experimental producer surface with GSP 0.2. Prefer coherent
breaking changes over compatibility shims while preserving the accepted ADR-0033 ownership model.

## Stop Conditions

Do not add backend state to figures, expose native handles, require local serialization, or publish
an unproven general session/update contract.

## Approval

Approved by the project owner's instruction to execute the full breaking consolidation.
