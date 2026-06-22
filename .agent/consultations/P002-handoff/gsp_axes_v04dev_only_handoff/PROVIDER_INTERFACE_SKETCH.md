# Axis Realization Provider Interface Sketch

This sketch is not final API. It gives Codex a concrete direction.

## Capability schema

```python
@dataclass(frozen=True)
class AxisProviderCapability:
    provider_id: str
    backend_id: str
    provider_status: Literal["strict", "adapted", "experimental", "unsupported"]
    dimensions: tuple[Literal["x", "y"], ...]
    scales: tuple[Literal["linear"], ...]
    supports_explicit_ticks: bool
    supports_auto_ticks_gsp_policy: bool
    supports_backend_auto_ticks: bool
    supports_tick_labels: bool
    supports_axis_labels: bool
    supports_title: bool
    supports_grid: bool
    supports_style_basic: bool
    supports_units: bool
    supports_datetime: bool
    supports_guide_query: bool
    supports_text_query: bool
    supports_visible_domain_readback: bool
    diagnostics: tuple[str, ...]
```

## Provider IDs

Recommended initial IDs:

```text
gsp.reference.generated_primitives.v0
matplotlib.native.axes.v0
datoviz.v04.panel_axis.wip
```

Use `.wip` for Datoviz until the v0.4 C ABI and Python binding surface is stable in the project checkout.

## Provider selection policy

```python
@dataclass(frozen=True)
class AxisProviderRequest:
    policy: Literal[
        "auto",
        "prefer_native",
        "require_native",
        "require_strict_gsp",
        "generated_primitives_only",
        "disabled",
    ]
    tick_authority: Literal[
        "gsp_resolved",
        "backend_resolved",
        "explicit_only",
    ]
    query_scope_requirement: Literal[
        "none",
        "data_only",
        "guides",
        "all_rendered",
    ]
```

Provider selection rules:

1. `require_strict_gsp` chooses a provider that can exactly realize GSP-resolved guide contributions.
2. `prefer_native` may choose Matplotlib native or Datoviz native, but diagnostics must state whether the result is strict or adapted.
3. `require_native` fails if no native provider matches.
4. `generated_primitives_only` is useful for tests and debug parity.
5. `disabled` suppresses rendered guides but does not remove `View2D`.

## Diagnostic examples

```text
axis-provider-selected: datoviz.v04.panel_axis.wip
axis-provider-adapted: backend-native ticks used; explicit GSP ticks unsupported
axis-provider-fallback: datoviz native text unavailable; using generated primitives
axis-guide-query-unsupported: provider renders guide but cannot query tick labels
axis-domain-adapted: decreasing domain normalized on CPU before Datoviz upload
axis-style-partial: requested style field ignored by provider
```

## Strict versus adapted tick authority

Strict examples:

- GSP computes ticks using `auto-linear-nice-v0`; provider renders exactly those values and labels.
- User supplies explicit ticks and labels; provider renders exactly those values and labels.

Adapted examples:

- Datoviz native axis uses its own tick policy because explicit tick values are not supported.
- Matplotlib native locator is left active in non-conformance mode.

Adapted output is allowed for interactive use but should not be called conformance output.
