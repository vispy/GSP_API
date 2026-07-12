# Architecture and roles

```text
Producer -> transport -> GSP session -> backend adapter -> renderer
   ^                         |
   +---- results, queries, diagnostics ------------------+
```

## Producer

VisPy2, a domain library, or direct integration code creates GSP records. Producers express intent;
they do not choose backend pipelines.

## Session and server

A session scopes identifiers, resources, scene state, command ordering, queries, and diagnostics.
The server advertises a `CapabilitySnapshot` and receives ordered `CommandBatch` values. The public
Python types exist today; a complete Matplotlib/Datoviz command-executing server is not yet shipped.

## Transport

`InProcessTransport` forwards native `CommandBatch` objects to an in-process server contract. Debug
JSON supports fixtures and replay. Binary IPC and production remote transports remain architectural
directions rather than current supported deployment profiles.

## Adapter

An adapter converts supported semantic records to backend operations. It must not silently drop an
unsupported field or infer capability support from an available symbol.
