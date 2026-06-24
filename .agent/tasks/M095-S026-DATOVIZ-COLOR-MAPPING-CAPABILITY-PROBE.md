# M095-S026 - S026 Datoviz color mapping capability probe

## Mission

M095

## Goal

Probe Datoviz v0.4 color mapping/colorbar/scalar readback capabilities against the accepted S026
baseline.

## Status

Completed.

## Deliverables

- Completed: Header/runtime evidence for accepted S026 features.
- Completed: Capability matrix entries and structured unsupported diagnostics.
- Completed: Recommendations for Datoviz implementation or deferral.

## Notes

- Added `color_mapping_symbols` and `color_mapping_capability_matrix` to the Datoviz v0.4 probe report.
- Wrote M095 artifacts under `artifacts/visual_qa/s026/datoviz_color_probe/`.
- Runtime gates are unsupported in the current environment because the Datoviz Python facade/raw modules are not importable.
- Sibling source evidence exists for implementation candidates: scales, accepted colormaps including gray, scalar sampled fields, visual scale binding, colorbars, and query APIs.

## Acceptance

- M091 baseline exists.
- Evidence avoids exposing backend internals as public protocol.

## Stop Conditions

- Stop if the probe would require credential, network, or external repo modification.
