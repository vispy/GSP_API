# M263 provider SPI and Matplotlib adapter

Date: 2026-07-22

## Result

Implemented the backend-neutral scene/session surface and lazy `gsp.backends` entry-point provider
SPI in `/Users/cyrille/GIT/Viz/gsp` commit `bd115d1`. Curated the formal Matplotlib renderer,
layout, guide, navigation, query, transform, tiled-image, capability, and color-mapping modules into
the independent `gsp-matplotlib==0.2.0a1` distribution.

Discovery without probing reads only installed entry-point metadata. Provider loading checks plugin
API and GSP protocol compatibility, rejects duplicate backend names, and requires either an explicit
backend or an ordered caller policy. Capability requirements and adaptation policy are explicit.

## Validation

- 167 core tests pass.
- 126 Matplotlib adapter tests pass from source and again against installed wheels.
- Strict mypy passes for all 43 core and Matplotlib source files.
- Ruff passes for both packages.
- Both wheel and sdist builds succeed.
- Installed-wheel discovery does not import `matplotlib.pyplot`.
- Installed-wheel session rendering writes a non-empty PNG.
- Core wheel SHA-256: `d56d44d4218fd66e2c413506f29d9c07da576c77f282ee1df081c93a12b8334f`.
- Matplotlib wheel SHA-256: `5935b2bb5845449d3ba63391c68d29492a89dd458ae224ead85f99e336eade6b`.

The new repository remains local, unpublished, and has no remote. M264 is approved for the Datoviz
provider migration under the existing no-sibling-edit and native-isolation constraints.
