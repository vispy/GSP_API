# GSP Virtual Data Sources - Draft

Huge datasets should be modeled as virtual data sources, not ordinary buffers.

Examples:

- tiled image pyramids;
- cloud microscopy data;
- map tiles;
- point-cloud octrees;
- remote simulation timesteps;
- custom chunk APIs.

A data source should declare:

- logical shape;
- coordinate system;
- chunk/tile scheme;
- levels of detail;
- fetch locality;
- cache policy;
- credentials policy;
- materialization policy;
- query/readout behavior.

Remote renderers should be able to fetch data server-side when permitted, avoiding client data transfer.
