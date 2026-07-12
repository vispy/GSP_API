# Views, transforms, and layout

## Coordinate spaces

Visuals declare whether coordinates are data values or panel-normalized device coordinates. Conversion between spaces is defined by the associated view and transform records, not by backend convention.

## Affine transforms

The accepted 2D transform is finite and invertible. Inline and named transforms have equivalent semantics. Transform order is deterministic, and query results must report whether inverse mapping is exact, unavailable, or ambiguous.

## View2D

`View2D` defines finite non-degenerate x and y ranges. Reversed ranges are valid and reverse the corresponding mapping. Navigation is expressed through semantic pan, zoom-about, set-view, and reset actions. Input-device adapters may translate pointer events into those actions but do not define the navigation result.

## View3D

`View3D` associates a camera with an orthographic or perspective projection. Camera basis vectors and ranges must pass degeneracy and finite-value checks. Navigation actions include orbit, pan, zoom, camera replacement, projection replacement, and reset with explicit snapshot freshness.

Strict opaque depth applies only to advertised supported mesh and view combinations. Partially clipped triangles, arbitrary transparency, and backend-native camera behavior are not implicitly strict.

## Resolved layout

Resolved layout records concrete logical-pixel rectangles for panels, plot regions, and guides. The same snapshot identity must be used by rendering and layout-aware queries. Device scale and output DPI are explicit metadata. Grid lines are clipped to the plot rectangle when strict layout behavior is advertised.
