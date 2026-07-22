# M264 - S062 Datoviz v0.4 provider

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Approved; M263 completed.

## Summary

Migrate the current Datoviz v0.4 protocol adapter into `gsp-datoviz`, register a lazy provider, and
replay exact source-development checkpoints without making a release claim.

## Acceptance

- Metadata discovery does not import Datoviz or initialize native resources.
- Explicit probe/open operations report exact dependency and capability diagnostics.
- Current visual/session/native/Texture2D gates pass at recorded Datoviz provenance.
- The package boundary can later accept an ordinary RC3 dependency without core or VisPy2 changes.

## Stop conditions

Stop on unisolated native failure, capability overclaim, type leakage into core, implicit local-path
dependency in publishable metadata, or any edit to the sibling Datoviz repository.
