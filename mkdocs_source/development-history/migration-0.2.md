# Migrating to GSP 0.2

GSP 0.2 intentionally removes ambiguous compatibility surfaces while the project is pre-1.0.

| Before | GSP 0.2 | Action |
|---|---|---|
| `import vispy2` | `import gsp_vispy2` | Rename the import; no alias is provided. |
| `GSP_RENDERER=...` | explicit producer/reference call or protocol transport | Select execution explicitly. |
| `Canvas` / `Viewport` object graph | `Panel`, `View2D`/`View3D`, visuals, attachments | Build semantic protocol records. |
| `RendererBase` / registry lookup | capability snapshot plus protocol transport | Negotiate support; do not infer it from class presence. |
| string diagnostics | `Diagnostic` with category, severity, code, message, context | Branch on stable fields, not message text. |
| implicit command success | `CommandResult.status` and diagnostics | Handle applied/rejected/failed explicitly. |
| assumed backend parity | runtime snapshot plus versioned profile | Gate every optional feature. |

The legacy code remains available for repository maintenance, but new code should not mix old object
graph instances with 0.2 records. Convert at an explicit boundary or migrate the whole path.

For session ownership, figures retain semantic producer state only. Do not cache backend handles on
`Figure` or `Axes`; the accepted ownership model is recorded in ADR-0033.
