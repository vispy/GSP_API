# Protocol lifecycle

## Roles

A **producer** submits operations. A **GSP server** owns session state and executes accepted operations through a backend adapter. A **transport** connects them without changing protocol meaning.

## Initialization

Initialization must return a validated session identifier and a `CapabilitySnapshot`. All subsequent command batches must target that active session.

```python
result = transport.initialize()
session_id = result.session_id
capabilities = result.capabilities
```

## Commands and batches

A `ProtocolCommand` has a `kind`, optional target identifier, and typed or structured payload. Accepted command categories include initialization, capability queries, resource and visual creation or update, transform state, panel state, frame submission, panel queries, and shutdown.

A `CommandBatch` must:

- carry one valid session identifier;
- have a non-negative sequence number;
- contain at least one command;
- preserve command order.

The server must reject a batch for another session. A rejected `CommandResult` must include diagnostics; rejection must not be encoded as a successful no-op.

## Execution

Scene mutations establish semantic state. A frame operation requests execution or presentation of that state. Rendering must not silently reinterpret unsupported fields. Implementations may lower records eagerly or retain them internally, provided advertised semantics remain stable.

## Shutdown

Shutdown closes the active session and releases its session-scoped state. Further submission requires a new initialization.

!!! note "Current implementation boundary"
    The Python package implements these records and the in-process transport contract. It does not yet ship a complete Matplotlib or Datoviz server that executes every command category end to end.
