# Image Visual - Draft

Semantic purpose: display 2D sampled fields or textures in a panel.

First-slice concepts:

- sampled field or texture source;
- placement rectangle;
- coordinate interpretation;
- interpolation;
- color role;
- optional scalar-to-color mapping.

Open questions:

- row-major upload convention;
- data-coordinate origin;
- texture-coordinate origin;
- vector export fallback.

Query payload first slice:

- visual id;
- texel id or coordinate;
- data coordinate;
- displayed RGBA;
- source value if available.
