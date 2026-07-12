# Resources and data

## Resource contract

A resource has validated identity, locality, mutability, usage, data type, shape, and payload rules. Backends must not infer a different shape or data interpretation from raw byte length alone.

## Buffers

`BufferResource` represents ordinary finite data. The local path may carry NumPy arrays or `memoryview` values directly. JSON/base64 is permitted for fixtures, replay, debugging, and simple transport, but it is not mandatory protocol semantics.

## Texture2D

The accepted texture resource is immutable two-dimensional RGBA8 data with explicit width, height, and format. Textured meshes require:

- a declared `Texture2D` identifier;
- finite per-vertex UV coordinates shaped `(N, 2)`;
- UV topology matching mesh vertex indexing;
- the fixed accepted unlit sampling and color-combination rules.

Linear filtering, repeat wrapping, mipmaps, color management, generated UVs, and separate UV indices are outside the accepted bounded contract.

## Data locality

Locality is explicit. A backend must not perform network, filesystem, decoder, or extension execution merely because a descriptor contains a URL or path. Security and credential policies are validated before materialization.

## Virtual data sources

Data too large or dynamic for an ordinary buffer is represented by a data-source contract. Tiled and preconfigured sources expose bounded requests and availability states. Current HTTP-array work is limited and must not be described as general remote-data support.
