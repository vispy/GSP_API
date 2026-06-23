# S022 HTTP access and decoder architecture note

S022 starts from a narrower decision than "implement remote data": use HTTP as the first real access
mechanism to test the architecture. HTTP is not itself the source type.

## Starting position

The first HTTP proof does not need to be a tile pyramid. A tile pyramid is only one possible source
contract. Simpler first candidates include:

- an administrator-configured HTTP URL for a JPEG/PNG texture or image;
- an administrator-configured HTTP URL for a `.npy` typed array;
- a deterministic mock of either shape before production network I/O.

The key architecture requirement is to separate the access mechanism from the logical source and
decoder model.

## Layer separation

| Layer | Responsibility | Examples |
|---|---|---|
| Access/fetch | How bytes are obtained | HTTP, S3, GCS, local sandbox, in-memory |
| Source contract | What logical data is represented | image, texture, array, tiled image, volume, point chunks |
| Decoder | How bytes become typed data | JPEG/PNG, `.npy`, Zarr chunk, custom binary |
| Resolver policy | Who is allowed to fetch/decode what | admin allowlist, opaque handles, limits, credentials |
| Renderer adapter | How typed data becomes visuals/resources | image visual, texture resource, array resource, tiled source |

Protocol payloads should refer to stable data identifiers and declared contracts. They must not carry
arbitrary executable decoder code, Python import paths, callbacks, or package installation
instructions.

## Pluggability model

Pluggable and user-specific behavior is allowed only through trusted server configuration:

- fetchers and decoders are installed/configured out of band by the server or resolver
  administrator;
- capability snapshots advertise supported access schemes, source contracts, and decoder IDs;
- scenes refer to `source_id`, `source_kind`, `format`, or `decoder_id` names that the resolver
  already knows;
- manifests describe static contracts and requirements, not executable implementation loading;
- resolver policy binds source handles to allowed access mechanism, decoder, resource limits,
  credential policy, cache policy, and diagnostics.

This keeps the extension model pluggable without making protocol payloads executable.

## Recommended first proof

The first S022 consultation should evaluate an HTTP single-resource proof before tile pyramids:

- opaque handle: `source_id="demo-http-jpeg-texture"` or `source_id="demo-http-npy-array"`;
- resolver-owned URL, never client-supplied;
- bounded HTTP fetcher, initially mock/no-network if possible;
- built-in decoder, for example JPEG/PNG or `.npy`;
- output as an image/texture resource or typed array resource;
- conformance fixture covering capability advertisement, successful decode, rejection, redaction,
  and cache-key shape.

HTTP tile pyramids, Zarr/OME-Zarr, COG, map tiles, STAC, and point-cloud octrees can build on the
same fetch/resolver/decoder spine later. They should not be the first implementation unless the
consultation shows that the extra complexity is necessary to validate the architecture.

## Consultation goal

The next ChatGPT Pro consultation should not ask for a broad remote-data architecture. It should ask:

- whether HTTP single-resource is the right first architecture test;
- whether JPEG/PNG texture or `.npy` array is the better first source contract;
- what descriptor fields, capability fields, diagnostics, cache keys, and fixtures are needed;
- how to support trusted pluggable decoders without protocol-level executable code;
- what stop conditions should halt implementation before production network I/O.
