# DATOVIZ-V04-PYTHON-FACADE-CONTRACT - Clarify v0.4 Python facade target

Goal: avoid future GSP agents targeting the obsolete Datoviz v0.3-style Python wrapper.

Finding from M004:

- The local Datoviz v0.4 package exposes C-shaped `dvz_*` APIs through `import datoviz as dvz`.
- It does not expose `datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`, or `datoviz._texture`.
- Some online Python API reference material still documents high-level wrapper objects, which conflicts with local v0.4 docs saying the old plotting API is external/GSP and the Python facade preserves C names.

Needed Datoviz-side outcome:

- make public docs unambiguous that GSP should target the v0.4 scene/app facade and raw ctypes APIs;
- mark old high-level Python wrapper docs as legacy, external, or not applicable to v0.4 if they remain published.

GSP dependency:

- The new GSP Datoviz backend should use only documented `dvz_*` scene/app APIs.
