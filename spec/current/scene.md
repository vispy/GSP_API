# Scene model

## Identity

Every addressable protocol entity uses a non-empty validated identifier. References must resolve within the relevant session state. Missing, duplicate, stale, or wrong-kind references must produce deterministic validation errors.

## Panels

A panel is a rectangular presentation and query region. It associates views, visuals, and guides with resolved layout geometry. Panel coordinates are the common boundary for rendering, navigation, and queries.

## Views

`View2D` maps two-dimensional data domains into a panel. `View3D` combines a camera and projection with a panel. A visual in data coordinates requires the appropriate view; a visual already expressed in panel NDC does not acquire data meaning implicitly.

## Visuals

A visual is a semantic family, not a backend draw call. Accepted families are points, markers, segments, paths, images, text, and triangle meshes. Each declares its coordinate space, geometry, styling inputs, and referenced resources explicitly.

## Guides

Guides express semantic annotation intent:

- `AxisGuide` defines an axis dimension, side, label, tick intent, grid intent, and style.
- `PanelTextGuide` defines panel-level text roles such as a title.
- `ColorbarGuide` represents the display of a scalar color scale.

Guides are not pre-rendered decorations. Query geometry and exact layout require separate backend capabilities.

## State relationships

Resources must exist before visuals that reference them are executed. Views and transforms used by a visual must be valid for its coordinate space. Layout, view, and resource revisions that affect a query must participate in snapshot freshness checks.
