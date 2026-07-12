# Scene model

A GSP scene is the semantic state established during a session, not a required Python object graph.

| Concept | Meaning |
|---|---|
| Panel | A presentation and query region. |
| View | A 2D mapping or 3D camera/projection associated with a panel. |
| Visual | Points, markers, segments, paths, images, text, or meshes. |
| Resource | Validated data referenced by visuals, such as buffers or textures. |
| Guide | Axis, ticks, grid, title, label, or colorbar intent. |
| Resolved layout | Concrete pixel geometry used consistently by rendering and queries. |

Visuals declare coordinate spaces explicitly. Views and transforms give those coordinates meaning;
backend code does not get to reinterpret them silently.
