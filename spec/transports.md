# GSP Transports - Draft

Transport is not protocol semantics.

Required transport classes:

| Transport | Purpose |
|---|---|
| inproc | Local desktop fast path, direct objects/memoryviews/ctypes, no JSON/base64 |
| debug-json | Fixtures, replay, tests, simple demos |
| binary-ipc | Future shared memory or binary chunk transport |
| network | Remote renderer and server-side data fetch |

The local desktop path must not require JSON/base64 serialization.
