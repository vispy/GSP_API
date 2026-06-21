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

## M011 v0.1 decision

The first extension model is static metadata, not a dynamic plugin loader.

Implemented models:

- `ExtensionManifest`
- `ExtensionKind`
- `ExtensionSupportLevel`

The built-in reference extension is `gsp.tiled-image@0.1`. It declares a tiled virtual image data
source contract and a typed query payload. In v0.1, manifests are used only for validation,
capability advertisement, diagnostics, and fixtures. They must not load code, discover packages, or
execute user callbacks.

Explicitly out of scope:

- package entry points;
- plugin dependency solving;
- executable manifest hooks;
- runtime shader or backend extension loading;
- cloud/data credentials.
