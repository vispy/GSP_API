# M033-STATIC-EXTENSION-MANIFEST-VALIDATION - Static extension manifest validation

## Mission

M033

## Goal

Harden v0.1 extension manifests and tiled-source linkage without introducing runtime plugin loading.

## Acceptance

- Extension manifests expose a canonical capability string.
- Static manifest validation rejects malformed extension ids, versions, implementation statuses, and
  query payloads outside the manifest capability namespace.
- Capability snapshots can adapt a static manifest and reject unadvertised manifests explicitly.
- `TiledImageSource` can validate that its extension id/version and schema contract match a static
  data-source manifest.

## Stop conditions

Stop before package discovery, plugin execution, dynamic manifest hooks, dependency solving, remote
fetch, credentials, or backend runtime extension loading.

## Result

Completed. Static manifests remain pure metadata. Tiled-source linkage is now explicit and covered
by tests.
