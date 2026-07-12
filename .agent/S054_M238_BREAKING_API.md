# S054 M238 breaking API consolidation

Date: 2026-07-12

The pre-1.0 compatibility break is intentional:

- distribution: `gsp-vispy2` 0.2.0;
- producer import: `gsp_vispy2`;
- removed import: `vispy2`;
- protocol version constant: `0.2`;
- structured `Diagnostic` records;
- explicit `CommandStatus` rather than a boolean command result;
- negotiated initialization version;
- deterministic capability snapshot identity;
- strict in-process sequence and closed-owner validation;
- canonical mesh shading vocabulary only.

The producer/session boundary from ADR-0033 is unchanged. Backend state is not stored on figures,
and a general public session/update API remains gated by lifecycle and profile work.
