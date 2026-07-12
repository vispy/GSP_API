# Python API

GSP 0.2 has two public layers:

| Layer | Import | Purpose |
|---|---|---|
| Producer | `gsp_vispy2` | Build semantic figures and visuals with a compact plotting API. |
| Protocol | `gsp.protocol` | Construct, validate, negotiate, transport, query, or implement GSP records directly. |

Most application authors should start with the [producer](producer.md). Renderer and transport
authors should start with [lifecycle and transport](lifecycle.md), then the record-family pages.

The normative specification controls semantics. Generated Python signatures document this
implementation; they do not silently expand backend support. Consult the
[feature matrix](../support/feature-matrix.md) and runtime capability snapshot.

## Stability

The 0.2 API is experimental and may break before 1.0. The removed `vispy2` package name has no alias.
Legacy object-graph APIs are documented only in [development history](../development-history/index.md).
