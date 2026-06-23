# Remote data and extensions

GSP does not implement arbitrary remote fetch by default.

Scenes may use synthetic and in-memory data. Future remote-capable scenes may also refer to
administrator-preconfigured source handles, but the scene must not provide a URL, object-store URI,
local path, request header, cookie, signed URL, or credential.

Extension manifests are not plugins. They describe protocol contracts for validation, capabilities,
diagnostics, fixtures, and query payloads. They must not import Python packages, declare entry
points, execute hooks, load shaders, or load decoders.

Secrets do not belong in scenes, manifests, fixtures, replay logs, diagnostics, or debug JSON.
Credential use, when supported, is resolver-owned and preconfigured by the renderer administrator.

Unsafe behavior rejects fatally. GSP may simplify visual fidelity gaps, but it must not simplify
security boundary failures such as arbitrary fetch, inline credentials, path traversal, dynamic code,
resource-limit violations, cache isolation failures, or query-scope violations.
