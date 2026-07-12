# Queries and diagnostics

GSP is bidirectional. A producer can ask what contributed under a panel coordinate and request
identity, coordinates, displayed color, depth, or feature-specific data when the backend advertises
the corresponding query capability.

A miss is different from unsupported behavior. Structured results preserve that distinction, while
diagnostics report validation failures, adaptations, unavailable capabilities, stale snapshots, and
execution errors. Rendering support never automatically implies query support.
