You are Mission Control and implementation agent for the GSP / VisPy2 project in repository `GSP_API` on branch `agentic-gsp-vispy2`.

Context:
- M001-M005 are complete.
- Tests were previously clean.
- No M006 mission existed before this pack.
- This pack added M006-M011, task cards, ADR-0003 skeleton, and a consultation packet.

Goal now:
Execute M006 only: Protocol hardening and conformance baseline.

Steps:

1. Verify branch and cleanliness:
   - ensure you are on `agentic-gsp-vispy2`;
   - inspect `git status`;
   - do not merge to main;
   - do not open PRs.

2. Read:
   - AGENTS.md
   - PROJECT_CHARTER.md
   - ARCHITECTURE.md
   - SPEC_INDEX.md
   - STATUS.md
   - LEGACY_MAP.md
   - .agent/missions/M006-protocol-hardening-conformance.md
   - .agent/tasks/GSP-HARDEN-001-v01-vertical-slice-adr.md
   - .agent/tasks/GSP-HARDEN-002-conformance-fixtures.md
   - .agent/tasks/GSP-HARDEN-003-tighten-tests.md
   - .agent/tasks/GSP-HARDEN-004-conformance-readme.md
   - adr/ADR-0003-gsp-v0.1-vertical-slice.md
   - spec/protocol.md
   - spec/capabilities.md
   - spec/resources.md
   - spec/query.md
   - spec/visuals/point.md
   - spec/visuals/image.md
   - spec/backends/matplotlib.md

3. Execute only M006:
   - complete/refine ADR-0003 if needed;
   - add/refine conformance fixtures for current point/image/query/capability slice;
   - tighten tests around ID, visual schema, query status, and Matplotlib reference behavior;
   - add a compact conformance README in the most appropriate existing or new conformance/fixture directory;
   - update STATUS.md and .agent/status.json.

4. Do not do:
   - Datoviz adapter implementation;
   - VisPy2 API implementation;
   - extensions/virtual data-source implementation;
   - external Datoviz repo modification;
   - any provider/aisw credential work.

5. Run tests:
   - run the existing test suite command normally used in this repo;
   - if unsure, start with `pytest`;
   - ensure all tests pass.

6. Commit:
   - `git add` only relevant M006 files;
   - commit with message: `M006: harden protocol conformance baseline`.

7. Final report:
   - files changed;
   - tests run;
   - new/updated fixtures;
   - whether ADR-0003 is complete;
   - any blockers;
   - recommendation for next mission, choosing among M007, M008, M009, M010.

Stop conditions:
- If the v0.1 scope is ambiguous, create `.agent/consultations/P002-v01-scope.md` with an exact ChatGPT Pro prompt and stop.
- If a change would require Datoviz code, stop and create a task instead.
- If local fixtures would force JSON/base64 as the primary local path, stop and report.
