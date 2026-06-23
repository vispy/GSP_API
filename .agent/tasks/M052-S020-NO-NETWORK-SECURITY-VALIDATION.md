# M052-S020-NO-NETWORK-SECURITY-VALIDATION - No-network security validation scaffolding

## Mission

M052

## Goal

Implement the first S020 no-network validation scaffolding and negative tests for unsafe source
descriptors, credentials, executable manifest fields, redaction, and conservative capabilities.

## Acceptance

- Protocol exposes stable S020 security diagnostic codes.
- Data-source descriptor validation rejects remote fetch descriptors, unsafe localities, URL/path
  metadata, inline secrets, unsupported credential policies, and credential refs.
- Static manifest validation rejects executable fields such as imports, entry points, hooks,
  callbacks, decoders, and runtime shader declarations.
- Redaction helpers produce deterministic placeholders for credential refs, URLs, paths, and secret
  fields.
- Capability snapshots keep remote fetch, server-side fetch, and dynamic extension loading absent by
  default.
- Negative tests cover the no-network rejection surface.

## Stop conditions

Do not add real network fetch, cloud/object-store clients, credential exchange, dynamic package
loading, runtime shader loading, custom decoder execution, or Datoviz remote-data requirements.

## Source

ADR-0008 and S020 spec patches.

## Result

Completed. Added protocol security helpers, conservative capability fields, static manifest
executable-field rejection, redaction helpers, and no-network negative tests.
