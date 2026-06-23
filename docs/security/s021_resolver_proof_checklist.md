# S021 resolver proof checklist

S021 completed the no-network `preconfigured-source` resolver proof. It proved that GSP can accept
opaque administrator/test source handles, validate them against the S020 security posture, and
materialize deterministic local tiled data without introducing remote fetch behavior.

## Completed S021 artifacts

- Protocol `NoNetworkPreconfiguredSourceResolver`.
- Deterministic `gsp.test.synthetic-resolver` handle for `public-demo-pyramid`.
- Stable rejection diagnostics for unknown handles, fetch descriptors, credentialed descriptors,
  and unsafe URL metadata.
- Resolver capability metadata with `network_io=false`.
- JSON conformance fixture records for known-handle materialization and rejection cases.
- Package-data inclusion for the S021 fixture.

## Preserved boundaries

The proof does not:

- fetch HTTP, object-store, Zarr, OME-Zarr, COG, map-tile, STAC, DVID, TileDB, or custom chunk data;
- resolve DNS, inspect hosts, follow redirects, open files, or access local paths;
- use raw secrets, signed URLs, authorization headers, cookies, credential refs, cloud SDK chains,
  or resolver outputs;
- load Python packages, entry points, callbacks, shaders, decoders, or backend extensions;
- add Datoviz remote-data requirements.

## Allowed next work

Only planning and consultation work is allowed before real remote-source implementation:

- choose the first remote source family to design;
- prepare a self-contained ChatGPT Pro consultation packet;
- define source-family-specific descriptors, validation, diagnostics, cache keys, fixture strategy,
  and stop conditions;
- decide whether the first runtime proof can remain no-network or needs a tightly bounded mock.

## Hard stops

Stop and request design review before any change that requires:

- direct client-supplied URLs or object-store URIs;
- production HTTP/object-store/cloud fetch clients;
- signed URLs or credentials in scenes, manifests, diagnostics, fixtures, or replay;
- DNS, redirect, allowlist, private-address, timeout, retry, decompression, or cache policy
  enforcement;
- external decoder execution or remote format parsing beyond deterministic local mocks;
- browser-origin fetch, server-side production fetch, or multi-tenant renderer behavior.

## S022 opening decision

Open S022 for remote-source family selection and consultation. The next mission should prepare a
self-contained ChatGPT Pro packet before any real remote fetch family is implemented.
