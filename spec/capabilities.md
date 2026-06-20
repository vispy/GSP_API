# GSP Capabilities - Draft

Every renderer/server reports a CapabilitySnapshot before planning.

Capability classes:

- protocol versions;
- resource limits;
- buffer/texture formats;
- render target formats;
- shader languages;
- visual-family support;
- transform placement support;
- readback/query support;
- output/export support;
- extension support;
- determinism guarantees.

Adaptation outcomes:

- accept;
- simplify with diagnostic;
- deactivate with diagnostic;
- reject with fatal diagnostic.

Unsupported behavior must not silently degrade.

M002 implementation note: `gsp.protocol.CapabilitySnapshot` exposes advertised protocol versions, transports, buffer dtypes, visual families, transform placements, query modes, output formats, extensions, and a minimal explicit adaptation decision helper.
