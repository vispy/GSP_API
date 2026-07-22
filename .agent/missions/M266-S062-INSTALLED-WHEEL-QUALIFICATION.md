# M266 - S062 installed-wheel qualification and closeout

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Approved; M265 completed.

## Summary

Build and install every separated distribution in clean environments, validate supported package
combinations and representative Matplotlib/Datoviz scenes, audit provenance/docs, and close the local
bootstrap without external publication.

## Acceptance

- Core-only, VisPy2+core, Matplotlib, and local-development Datoviz combinations pass from wheels.
- One unchanged VisPy2 scene renders through both provider interfaces where capabilities permit.
- Documentation states package/install/session boundaries and current Datoviz release limitations.
- Both repositories are clean, committed, independently recoverable, and have no remotes.

## Stop conditions

Stop if any validation relies on editable/source imports, provenance is incomplete, package extras
cannot resolve within approved artifact boundaries, or remote/release action would be required.
