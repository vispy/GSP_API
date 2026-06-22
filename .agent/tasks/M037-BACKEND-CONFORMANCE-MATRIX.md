# M037-BACKEND-CONFORMANCE-MATRIX - Backend conformance matrix

## Mission

M037

## Goal

Continue S018 with an explicit backend conformance matrix and skip-clean expectations.

## Acceptance

- Matrix lists Matplotlib and Datoviz.
- Matplotlib executes the in-process semantic replay harness.
- Datoviz is visible but skipped cleanly with a diagnostic reason.
- Tests assert pass/skip expectations without requiring JSON/base64 fixtures.

## Stop conditions

Stop before adding transport fixture schemas, Datoviz runtime replay, JSON/base64 array encoding,
pixel comparison, or backend certification claims.

## Result

Completed. `fixtures.conformance.matrix.backend_conformance_matrix()` records the current pass/skip
expectations and the parametrized test reports Datoviz as an intentional skip.
