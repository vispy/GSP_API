# M248 - S058 rolling Datoviz checkpoint

## Stage

S058 - Datoviz v0.4-dev Rolling Compatibility And RC3 Feedback

## Status

Completed.

## Summary

Create one bounded rolling-development entry point that records exact local Datoviz provenance and
runs the maintained facade smoke, isolated S028 review pack, latest-baseline comparison, public and
internal lifecycle probes, focused adapter tests, and concise result summary.

## Acceptance

- The command rejects a missing or wrongly imported sibling checkout.
- Output paths and run identifiers include or record the exact Datoviz revision.
- Native visual cases and lifecycle modes retain subprocess isolation and timeouts.
- Existing focused unit tests cover command construction or reusable Python helpers where useful.
- The command does not edit Datoviz, promote capabilities, or publish artifacts.

## Approval

Covered by the project owner's approval of the S058 sequence on 2026-07-22.

## Result

Added `tools/run_datoviz_v04dev_checkpoint.sh` and documented it in `tools/README.md`. An end-to-end
one-iteration validation checkpoint against Datoviz `71c444cee` passed exact import provenance, the
60-row isolated S028 review and comparison, 2/2 public lifecycle runs, 5/5 internal lifecycle modes,
and 168 focused tests. The full five-iteration lifecycle evidence remains recorded by M245.
