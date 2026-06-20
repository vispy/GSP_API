# GSP Extensions - Draft

Extensions may define:

- visual families;
- transforms;
- data sources;
- data formats/decoders;
- query/readout payloads;
- transports.

Every extension needs:

- id;
- semantic version;
- kind;
- schema;
- capability requirements;
- implementation declarations;
- fallback policy;
- diagnostics policy;
- query contract where applicable.

Unsupported extensions must produce explicit diagnostics.
