# Architecture - GSP / VisPy2

## Layered target

```text
VisPy2 / plotting APIs / domain libraries
  -> GSP producer API
    -> GSP session and protocol model
      -> backend adapters
        -> Matplotlib reference backend
        -> Datoviz v0.4 GPU backend
        -> future remote/web/specialized backends
```

## Session model

GSP is a client/server/session protocol. The server may be:

- in-process local renderer;
- subprocess;
- remote renderer;
- browser/worker runtime;
- cloud GPU service.

A server exposes capabilities, accepts scene/resource/visual commands, executes frames, returns query/readback results, and emits diagnostics.

## Transport model

The protocol semantics are independent from any encoding.

Supported transport classes:

- `inproc`: direct Python/ctypes/memoryview path;
- `binary-ipc`: shared memory or binary chunks;
- `network`: remote commands plus server-side data fetch;
- `debug-json`: JSON/base64 fixtures and replay.

The local desktop path must not require JSON or base64.

## Control plane and data plane

Control plane:

- scene commands;
- visual creation/update;
- transforms;
- queries;
- capabilities;
- diagnostics;
- events.

Data plane:

- buffers;
- textures;
- tiles/chunks;
- external data-source handles;
- server-side fetch descriptors;
- cache and LOD policies.

## Capability model

Every backend exposes a `CapabilitySnapshot`. Planning/adaptation happens before execution. Unsupported behavior must produce one of:

- accept;
- simplify with diagnostic;
- deactivate with diagnostic;
- reject with fatal diagnostic.

## Transform model

Transforms should be declarative and staged:

1. source/data transforms;
2. attribute transforms;
3. coordinate transforms;
4. controller/navigation transforms;
5. material/shading transforms;
6. query/readout inverse transforms.

Placement may be CPU, GPU, client-side, server-side, or backend-defined, but semantics must be stable.

## Query model

Use a unified panel query:

```text
what rendered scene contribution is under this panel coordinate?
```

Query results should carry identity, item/group/face/voxel/texel ids, visual/data/UVW coordinates, displayed RGBA, depth/order, and optional value/readout payloads.

## Extension model

Extensions can define:

- custom visual families;
- custom transforms;
- custom data sources;
- custom formats/decoders;
- custom query/readout payloads;
- transports.

Every extension needs an ID, version, schema, capability requirements, implementation declarations, fallback policy, and query contract where applicable.

## Agentic workflow

Codex is the primary interactive Mission Control interface.

Mission Control uses `tools/agentctl` under the hood to inspect status, update project files, launch worker agents through `aisw`, track runs, create review items, and request ChatGPT Pro consultations for high-reasoning questions.
