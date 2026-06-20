# Recommended mission sequence after M005

| Mission ID | Title | Goal | Why now | Dependencies | Risk | ChatGPT Pro / ADR |
|---|---|---|---|---|---|---|
| M006 | Protocol hardening and conformance baseline | Freeze current point/image/query slice into a coherent v0.1 mini-contract. | Prevents drift before Datoviz, VisPy2, and extensions. | M001-M005 | Low-Medium | ADR recommended: v0.1 scope |
| M007 | Datoviz v0.4 point/image adapter slice | Add bounded Datoviz v0.4 protocol-renderer slice for point/image only. | Datoviz is flagship backend; mapping already assessed feasible. | M004, M006 | Medium-High | Consultation only if API gap appears |
| M008 | VisPy2 producer MVP | Add minimal VisPy2 API that emits GSP point/image scenes and renders through Matplotlib. | Gives user-facing proof without Datoviz query readiness. | M006, M003 | Medium | ADR optional if API scope expands |
| M009 | Query hardening and Datoviz query handoff | Harden query schema/status/capability model and produce exact Datoviz query handoff tasks. | Query is first-class, but Datoviz Python query decode is not ready. | M005, M006, M004 | Medium | ADR only if result schema changes |
| M010 | Agentic control-plane provider hardening | Fix provider inventory, Claude profile issue, worker launch logs, review flow. | Enables longer autonomous sessions. | M001 | Low | No |
| M011 | Extensions and virtual data-source architecture proof | Spec-first proof for virtual/tiled data sources and extension manifests. | Important long-term feature but should follow v0.1 stabilization. | M006, ideally M008 | High | ChatGPT Pro consultation required before coding |

Very next mission: M006.
