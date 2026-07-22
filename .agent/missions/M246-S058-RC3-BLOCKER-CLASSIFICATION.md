# M246 - S058 RC3 blocker classification

## Stage

S058 - Datoviz v0.4-dev Rolling Compatibility And RC3 Feedback

## Status

Completed.

## Summary

Classify M245 evidence against the latest committed pre-RC replay and inspect the current Datoviz
public/runtime evidence for Texture2D sampling, mesh triangle identity, image payloads, guide
strictness, and session lifecycle.

## Result

Four visual rows improved, none regressed, and all native cases are crash-free. No new GSP
capability is ready for promotion: guide rows remain adapted, image rich payloads remain absent,
mesh face queries still lack canonical native triangle identity, and the planned field-slot sampling
API is not implemented. Full details are in `.agent/S058_M245_ROLLING_BASELINE.md`.

## Approval

Covered by the project owner's approval of the S058 sequence on 2026-07-22.
