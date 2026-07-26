# M293 - S065 macOS Datoviz subprocess lifecycle correction

## Status

Approved for direct execution with `codex-ucl-gpt-5.6-sol-medium`.

## Baseline and evidence

- VisPy2 `81557b8` contains the accepted fail-closed gallery validator.
- GSP `6b5b8bc` contains the accepted logical layout fix.
- M292 exact wheels are valid and Gallery 2 succeeds from both source and the isolated exact-wheel
  project site when launched normally.
- On macOS, the exact same Gallery 2 child launched by Python with
  `start_new_session=True` writes its valid PNG and then returns `-11`.
- With `start_new_session=False`, it writes the same PNG and returns zero.
- The full validator always requests a new session so it falsely classifies successful native
  Datoviz teardown as a rendering crash. This is a harness/process-lifecycle defect, not evidence
  requiring a Datoviz source change.

## Required implementation

1. Keep the validator's timeout and retry semantics bounded.
2. On macOS only, launch native Datoviz gallery subprocesses without `start_new_session`.
3. When no new process group is created, terminate and then kill the direct child on timeout using
   `Popen.terminate()`/`Popen.kill()`; never call `killpg` on the harness process group.
4. Preserve process-group isolation and `killpg` cleanup for Matplotlib/check subprocesses and for
   Datoviz on platforms where it is safe.
5. Express the policy explicitly through typed helper/parameters. Do not infer it from an arbitrary
   command substring inside the generic runner.
6. Do not add sleeps, ignore negative return codes, weaken retry/fresh-output checks, special-case a
   gallery filename, or edit Datoviz/GSP.
7. Document the macOS native-child exception without claiming that third-party dependencies or
   Datoviz were rebuilt.

## Required tests

- Normal process-group path requests `start_new_session=True`.
- macOS native Datoviz path requests `False`.
- Timeout on the process-group path sends TERM/KILL to the process group.
- Timeout on the direct-child path calls child terminate/kill and never `killpg`.
- Nonzero native child exits still fail; retry behavior remains exact.
- Existing six fail-closed gallery contract tests stay green.

## Required validation

- Focused gallery contract tests.
- Full VisPy2 pytest.
- Strict VisPy2 and validator mypy, Ruff, docs/link validation, and `git diff --check`.
- No native Datoviz presentation in the worker sandbox.
- Commit one coherent VisPy2 correction.

## Acceptance

- Independent source/static review issues unconditional ACCEPT.
- Bounded timeout behavior is preserved on every path.
- macOS Datoviz subprocesses no longer use `setsid`.
- No GSP, Datoviz, public API, capability, visual, or layout semantic changes.

## Stop conditions

- Stop rather than accepting SIGSEGV as success or weakening output validation.
- Stop on need for a Datoviz edit, unbounded child lifetime, or cross-platform process regression.
- Do not push, merge, tag, release, publish, create a PR, or change package versions.
