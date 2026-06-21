# GSP Resources - Draft

Resource kinds:

- buffer;
- texture;
- sampled field;
- virtual data source;
- parameter block;
- external/live resource handle.

A buffer resource should eventually carry:

- id;
- dtype;
- shape;
- byte length;
- usage;
- mutability;
- locality;
- update ranges;
- optional external source.

Open v0.1 question: whether to support arbitrary strides immediately or require contiguous buffers first.

M002 decision: the initial `BufferResource` model requires contiguous buffers. Strided views may be represented by `AttributeSource.stride_bytes`, but non-contiguous resource ownership is deferred until a later resource mission.

M011 decision: virtual data sources are not ordinary buffers. `TiledImageSource` describes logical
source data and tile materialization separately from eager `BufferResource` bytes. The local proof
returns direct NumPy arrays from `TileResult` and `ViewportMosaicResult` without mandatory
serialization.
