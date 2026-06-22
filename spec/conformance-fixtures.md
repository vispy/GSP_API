# GSP Conformance Fixtures - Draft

Conformance fixtures define stable semantic behavior for the v0.1 reference path.

## M036 in-process replay harness

The first S018 replay layer is Python/in-process only. It replays existing conformance fixtures
without JSON/base64 serialization and returns semantic results for:

- capability snapshot identity and advertised extension surface;
- point-over-image query frontmost behavior;
- guide tick hit and guide miss behavior;
- local tiled-source clipped mosaic and typed query payload behavior.

This harness is not a transport encoding and is not a schema authority. JSON/base64 fixture files,
debug-json replay, backend matrices, and pixel/image comparison remain follow-up S018 work.
