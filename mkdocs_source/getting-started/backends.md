# Choose a backend

Backend-independent semantics do not mean universal backend parity. A session's capability snapshot
is the authority for the concrete feature combination it can execute.

| Backend | Role | Practical use |
|---|---|---|
| Matplotlib | Reference and publication backend | Portable review, conformance oracles, static output |
| Datoviz v0.4 | Capability-gated GPU backend | Retained and interactive paths where the required capabilities are proven |

Use Matplotlib for the first example. Choose Datoviz only after checking the required rows in the
[feature matrix](../support/feature-matrix.md). Rendering success alone is not evidence that queries,
layout, text, or related payloads are also supported.
