# P006 - Remote Data and Dynamic Extension Security Pre-Design

Status: pending ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Prompt To Paste Into ChatGPT Pro

You are advising on a security-sensitive architecture decision for GSP_API, a Python research
prototype for a backend-independent Graphics Server Protocol (GSP) for scientific visualization.

Please produce a security pre-design for **remote data sources and dynamic extensions**. This is a
pre-implementation architecture review. Do not write code. The goal is to decide what GSP should and
should not support next, and what durable specs/ADRs should say before any implementation.

### Project Context

GSP_API defines a semantic scene model for scientific visualization. The project charter says GSP
should allow one visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths through Datoviz/WebGPU where available;
- extension/data-source systems for huge distributed datasets.

Non-negotiable principles from the project charter:

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

The current architecture model:

- GSP is a client/server/session protocol.
- A server may be local/in-process, subprocess, remote renderer, browser/worker runtime, or cloud
  GPU service.
- Protocol semantics are independent from transport encoding.
- Transport classes are `inproc`, `debug-json`, future `binary-ipc`, and `network`.
- The local desktop path must not require JSON/base64.
- A server exposes capabilities, accepts scene/resource/visual commands, executes frames, returns
  query/readback results, and emits diagnostics.
- Control plane includes scene commands, visuals, transforms, queries, capabilities, diagnostics,
  and events.
- Data plane includes buffers, textures, tiles/chunks, external data-source handles, server-side
  fetch descriptors, cache, and LOD policies.
- Unsupported behavior must explicitly accept, simplify with diagnostic, deactivate with diagnostic,
  or reject with fatal diagnostic. Silent degradation is not acceptable.

### Current Implemented State

The repository is at version `0.1.0`, still a research prototype. Recent stages completed:

- Matplotlib reference backend for core visual/query behavior.
- Datoviz v0.4 capability/query smoke work, but v0.4 support remains capability-gated and not a
  package dependency.
- Static extension manifest validation.
- Local virtual tiled-image source proof.
- Conformance fixture and replay harness.
- Packaging/docs/examples cleanup.
- Full strict mypy on `src/` now passes.

Current validation commands pass:

```bash
PYTHONPATH=. uv run mypy src/ --strict --show-error-codes
PYTHONPATH=. uv run pytest -q
uv run mkdocs build --strict
uv build
```

Current package policy:

- Runtime dependencies include NumPy, Matplotlib, Pydantic, imageio, colorama, Flask, requests-file,
  loguru, and http-constants.
- Legacy Datoviz wrapper support is optional via `datoviz-legacy`.
- Datoviz v0.4-dev is validated by local smoke tests but is not declared as a package dependency
  until compatible wheel/release artifacts exist.

### Existing Extension/Data-Source Decision

ADR-0004 accepted a minimal extension and virtual data-source proof for v0.1:

- `ExtensionManifest` is static metadata.
- It is not a dynamic plugin loader.
- It does not execute code.
- Virtual data sources are core protocol objects.
- Concrete source kinds may be declared by extension manifests.
- First built-in reference extension: `gsp.tiled-image@0.1`.
- First executable source model: `TiledImageSource`.
- Current executable localities: only `synthetic` and `in-memory`.
- Current credential policy: only `none`.
- Matplotlib reference path materializes deterministic viewport mosaics.
- Tiled image query returns core `QueryResult` fields plus typed extension payload
  `TiledImageQueryPayload`.

ADR-0004 explicitly declared out of scope:

- dynamic plugin discovery/loading;
- Python entry-point/package-manager integration;
- runtime shader extension loading;
- real HTTP, S3, GCS, Zarr, OME-Zarr, COG, or map-tile clients;
- secret storage, credential exchange, or URL credential handling;
- async tile loading, prefetch, LRU cache, retry logic, or progressive refinement;
- production server-side fetch;
- remote renderer implementation;
- Datoviz tiled-image support;
- user-facing VisPy2 cloud/tiled API.

Current `spec/extensions.md` says extensions may define visual families, transforms, data sources,
formats/decoders, query/readout payloads, and transports. Every extension needs id, semantic version,
kind, schema, capability requirements, implementation declarations, fallback policy, diagnostics
policy, and query contract where applicable. Unsupported extensions must produce explicit
diagnostics.

Current `spec/extensions.md` also says:

- first extension model is static metadata, not a dynamic plugin loader;
- manifests are used only for validation, capability advertisement, diagnostics, and fixtures;
- manifests must not load code, discover packages, or execute user callbacks;
- out of scope: package entry points, plugin dependency solving, executable manifest hooks, runtime
  shader/backend extension loading, and cloud/data credentials.

Current `spec/data_sources.md` says huge datasets should be modeled as virtual data sources, not
ordinary buffers. Examples include tiled image pyramids, cloud microscopy data, map tiles,
point-cloud octrees, remote simulation timesteps, and custom chunk APIs. A data source should
declare logical shape, coordinate system, chunk/tile scheme, LODs, fetch locality, cache policy,
credentials policy, materialization policy, and query/readout behavior. Remote renderers should be
able to fetch data server-side when permitted, avoiding client data transfer.

Current `TiledImageSource` validation rejects:

- credential policy other than `none`;
- executable locality other than `synthetic` or `in-memory`.

### Why This Consultation Is Needed

The next stage, S020, is "Remote data and dynamic extension security pre-design." This is explicitly
about deferred high-risk topics. The project needs a security architecture before implementing any of
the following:

- real remote fetch over HTTP/S3/GCS/Zarr/OME-Zarr/COG/map tiles;
- server-side fetch in a remote renderer;
- preconfigured credentials or credential references;
- dynamic extension discovery or plugin loading;
- executable extension hooks;
- runtime shader/backend extension loading;
- custom data decoders;
- cache/prefetch/retry policies;
- user-facing VisPy2 APIs that expose remote data or third-party extensions.

The design must preserve the local fast path and the static v0.1 proof. It should define a safe
next step without expanding into a full cloud client, package manager, credential manager, or plugin
runtime.

### Threats To Consider

Please consider at least:

- SSRF from server-side fetch descriptors;
- exfiltration of server-local files, metadata endpoints, credentials, or internal network services;
- unsafe URL schemes and redirects;
- path traversal and local file reads;
- decompression bombs and oversized tiles/chunks;
- malicious or malformed chunk metadata;
- cache poisoning or cache key confusion;
- resource exhaustion from unbounded prefetch/retry/concurrency;
- cross-tenant leakage in remote renderers;
- untrusted manifest fields;
- dependency confusion or malicious Python packages if dynamic plugin discovery is allowed;
- arbitrary code execution through plugin hooks, decoders, shaders, or transform callbacks;
- unsafe query/readback payloads that expose values outside declared data-source scope;
- replay/debug fixture risks if remote source descriptors or credentials are serialized.

### Constraints

Hard constraints:

- Do not require JSON/base64 for local in-process rendering.
- Do not silently adapt unsupported behavior.
- Do not store raw secrets in scene JSON, conformance fixtures, manifests, or debug logs.
- Do not let untrusted manifests execute code.
- Do not let a client cause a remote renderer to fetch arbitrary URLs by default.
- Do not introduce Datoviz implementation requirements in this design step.
- Preserve Matplotlib as the reference/conformance backend.
- Preserve the existing `gsp.tiled-image@0.1` local proof as a safe baseline.

Preferred direction:

- Capability-driven design.
- Explicit allowlists or administrator-preconfigured source resolvers.
- Credential references rather than credentials in protocol payloads, if credentials are allowed at
  all.
- Static validation before execution.
- Separate control-plane metadata from data-plane materialization.
- Bounded resource limits in capability snapshots.
- Clear diagnostics and rejection modes.
- ADR/spec-first before implementation.

### Questions To Answer

1. What should S020 include and exclude?
2. Should GSP support real remote fetch descriptors next, or only preconfigured source handles?
3. Should dynamic extension loading be deferred entirely, or is there a safe static discovery model
   worth adding?
4. What should the credential model be? Is `credential_policy=preconfigured` safe if payloads carry
   only opaque credential references? What are the rules?
5. What source-locality enum values should exist beyond `synthetic` and `in-memory`, and which are
   safe for v0.2?
6. What capability fields should a renderer/server advertise for remote data and extensions?
7. What validation rules should apply to manifests, source descriptors, fetch descriptors, and
   query/readback payloads?
8. What must never be serialized into debug-json fixtures or replay logs?
9. What minimum conformance tests should be created before implementation?
10. What are the top stop conditions that should halt implementation?

### Expected Output Format

Please answer in this exact structure:

1. **Executive Recommendation**
   - 5-10 bullets with the recommended S020 scope and the strongest warnings.

2. **Threat Model**
   - Assets, trust boundaries, actors, and top abuse cases.

3. **S020 In Scope**
   - A precise list of architecture/spec artifacts and optional safe implementation proofs.

4. **S020 Out Of Scope**
   - A precise list of features to defer.

5. **Recommended Protocol Model**
   - Proposed source descriptor fields, fetch/locality enum values, credential policy values, cache
     policy fields, and capability fields.

6. **Validation Rules**
   - Concrete validation rules for manifests, source descriptors, fetch descriptors, credentials,
     cache keys, resource limits, query payloads, and replay/debug serialization.

7. **Dynamic Extensions Policy**
   - Recommendation on static manifests, package discovery, executable hooks, decoders, shaders, and
     plugin loading.

8. **Remote Fetch Policy**
   - Recommendation on URL handling, allowlists, redirects, local/private IP blocks, file schemes,
     content limits, retries, timeouts, and server-side fetch administration.

9. **Credential Policy**
   - Recommendation on raw secrets, credential references, resolver ownership, audit logging,
     redaction, fixture/replay behavior, and multi-tenant constraints.

10. **Capability And Diagnostics Model**
    - Proposed fields and how unsupported behavior should reject with diagnostics.

11. **Conformance/Test Plan**
    - Minimum tests and fixtures to add before runtime implementation.

12. **ADR/Spec Patch Plan**
    - Which existing files should change (`spec/extensions.md`, `spec/data_sources.md`,
      `spec/capabilities.md`, `spec/conformance-fixtures.md`, ADRs, task files), and what each
      should contain.

13. **Stop Conditions**
    - Conditions under which implementation must stop and request another design review.

14. **Open Questions**
    - Questions that still require human/project-owner decisions.

Keep the recommendation pragmatic for a Python research prototype. Prefer a narrow, safe v0.2
pre-design over a broad platform. Do not assume cloud credentials, package-plugin execution, or
Datoviz implementation are available.

## Dependent Work Blocked Until Response

- Any implementation of remote fetch descriptors.
- Any implementation of credential references or credential resolvers.
- Any dynamic extension discovery/loading.
- Any executable manifest hooks, decoders, shader loading, or plugin entry-point integration.
- Any user-facing VisPy2 remote data API.
