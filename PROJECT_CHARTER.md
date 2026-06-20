# Project Charter - GSP / VisPy2

## Mission

Create a backend-independent **Graphics Server Protocol (GSP)** for scientific visualization and a new **VisPy2** Python interface that targets GSP.

GSP should allow one semantic visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths through Datoviz/WebGPU where available;
- extension/data-source systems for huge distributed datasets.

## Non-negotiable principles

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4 is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. High-reasoning design work should be captured in durable specs, ADRs, and task files.
13. Low/medium coding agents should execute bounded missions with tests and traceable logs.

## First project application

The first application of the generic agentic workflow is the existing `vispy/GSP_API` repository.

This repo should be reused as a research prototype and implementation seed. It should not be discarded, but its current Python objects are not the final protocol authority.
