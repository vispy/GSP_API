# DATOVIZ-V04-PYTHON-FACADE-CONTRACT - Clarify v0.4 Python facade target

Goal: avoid future GSP agents targeting the obsolete Datoviz v0.3-style Python wrapper.

Finding from M004:

- The local Datoviz v0.4 package exposes C-shaped `dvz_*` APIs through `import datoviz as dvz`.
- It does not expose `datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`, or `datoviz._texture`.
- Any high-level Python wrapper examples or published references must be treated as stale unless they are verified against `../datoviz/` current branch. The local v0.4 docs say the old plotting API is external/GSP and the Python facade preserves C names.

M018 update:

- `../datoviz` is on `v0.4-dev` commit `bc9adbb40`; headers expose the required v0.4 symbols.
- The current GSP environment imports Datoviz `0.3.5` from `.venv`, which exposes no public `dvz_*`
  functions and no v0.4 ctypes classes.
- Future Datoviz runtime work must explicitly activate a v0.4-dev source-built facade/raw binding
  before claiming binding support.

Needed Datoviz-side outcome:

- make public docs unambiguous that GSP should target the v0.4 scene/app facade and raw ctypes APIs;
- mark old high-level Python wrapper material as legacy, external, or not applicable to v0.4 if it remains published or present in release artifacts.

GSP dependency:

- The new GSP Datoviz backend should use only documented `dvz_*` scene/app APIs.
