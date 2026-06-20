# GSP Protocol Spec - Draft

GSP is a Graphics Server Protocol for semantic scientific visualization.

The protocol defines a session between a producer/client and a renderer/server. The server may be local/in-process or remote.

Minimum command categories:

- initialize/session;
- capability query;
- resource creation/update;
- visual creation/update;
- transform creation/update;
- panel/camera/controller state;
- frame submission;
- panel query/readback;
- diagnostics/events;
- shutdown.

The protocol semantics are independent from the transport encoding.

The first implementation should prove:

1. local in-process point/image scene;
2. Matplotlib reference rendering;
3. Datoviz v0.4 mapping assessment;
4. one panel-query proof.
