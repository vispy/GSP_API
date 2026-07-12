# What is GSP?

Scientific plotting libraries usually combine two decisions: **what a visualization means** and
**how it is drawn**. GSP separates them.

A producer describes points, images, text, meshes, views, guides, resources, and queries using
backend-neutral records. A backend adapter declares which contracts it supports and either executes
them, reports an explicit adaptation, or rejects them with a diagnostic.

## The five roles

| Role | Responsibility |
|---|---|
| Producer | Creates valid GSP operations. The independent `gsp_vispy2` package is the current high-level Python producer. |
| Protocol | Defines commands, records, validation, capabilities, results, and diagnostics. |
| Session | Owns identifiers and state while operations are negotiated and executed. |
| Transport | Carries operations. It does not define their meaning. |
| Backend adapter | Maps supported semantics to Matplotlib, Datoviz, or another renderer. |

The server in this model does not have to be remote. An in-process implementation is still a GSP
server and can exchange NumPy arrays without mandatory JSON or base64 encoding.

## What GSP is not

- It is not a promise that every backend supports every feature.
- It is not defined by JSON or a network API.
- It is not a backend draw-call abstraction.
- It is not the repository's older `RendererBase` object API.

The current project is a research prototype. Protocol records and substantial reference behavior
exist today, while the complete end-user session layer remains incomplete.
