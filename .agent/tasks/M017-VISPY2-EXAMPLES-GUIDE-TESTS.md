# M017-VISPY2-EXAMPLES-GUIDE-TESTS - VisPy2 examples and guide API tests

## Mission

M017

## Goal

Add runnable VisPy2 examples and tests covering the bounded guide API surface.

## Acceptance

- Examples cover scatter, image, limits, labels, title, explicit ticks, and grid intent.
- Tests exercise the examples as runnable artifacts.
- Tests assert public guide getters, semantic guide objects, and Matplotlib-rendered guide state.
- `Figure.visuals()` remains data visuals only.

## Stop conditions

Stop before adding broad Matplotlib compatibility, query-scope architecture, or backend-provider
details to the public VisPy2 API.
