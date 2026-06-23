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

## M033 static manifest validation

Extension manifests are validated as static protocol metadata:

- extension ids are dot-separated lowercase name segments;
- versions are numeric dot-separated components;
- the canonical capability string is `<extension-id>@<version>`;
- implementation declarations must use known statuses such as `reference`, `native`, `adapted`,
  `experimental`, or `unsupported`;
- query payload contracts must be namespaced under the manifest capability, for example
  `gsp.tiled-image@0.1.query`.

Capability snapshots may adapt a manifest directly. A backend accepts a manifest only when it
advertises both static manifest support and the manifest capability string. This does not discover,
load, or execute extension code.

## S020 dynamic extension security policy

Dynamic extension loading is deferred. Manifests remain untrusted, data-only protocol metadata used
for validation, capability advertisement, diagnostics, fixtures, and query payload contracts.

Allowed S020/v0.2 behavior:

- bundled static manifests;
- static test manifests;
- explicitly provided manifest files for validation only;
- offline manifest linting;
- capability advertisement for already-installed trusted server code.

Forbidden manifest behavior:

- Python package imports or module/class paths;
- Python entry-point discovery;
- runtime package installation or dependency solving;
- executable callbacks, hooks, transforms, or draw-call injection;
- manifest-declared decoders;
- runtime shader loading or shader source;
- shell commands;
- URLs used to load code;
- binary executable blobs;
- pickle, cloudpickle, dill, or object-representation payloads;
- auto-discovery from `site-packages`.

Static discovery sources are limited to:

- `builtin`;
- `configured-manifest-dir` for local development or test validation;
- `test-fixture`.

For every source, `manifests_are_data_only=true`, `imports_allowed=false`,
`executable_hooks_allowed=false`, and `package_resolution_allowed=false`.

Manifest validation must be strict. Unknown fields are rejected unless they live under a documented
`x-` extension namespace that is explicitly non-executable. Implementation declarations describe
already-built server capabilities; they are not instructions for loading code. A manifest can require
capabilities, but it cannot create capabilities.

Extension query payload contracts must be explicit, versioned, and bounded. Extension payloads must
not serialize arbitrary Python objects, callback references, import paths, pickle-like bytes, or
class reprs.

Security diagnostics for dynamic loading, executable fields, decoder plugins, runtime shaders, and
manifest schema violations are fatal rejects.
