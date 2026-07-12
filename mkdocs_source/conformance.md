# Testing and conformance

GSP separates protocol validity, reference behavior, backend capability claims, and visual review.
A rendered example alone is not conformance evidence.

## Validation layers

| Layer | Purpose |
| --- | --- |
| Unit and integration tests | Validate Python behavior and backend adapters. |
| Versioned fixtures | Preserve protocol records and expected outcomes. |
| Conformance replay | Compare backend results and structured diagnostics. |
| Visual QA | Produce review artifacts without silently promoting capabilities. |
| API review examples | Present small, readable scenes for human comparison. |

Run the portable baseline:

```bash
uv run pytest
uv run mypy src
uv run ruff check .
uv run mkdocs build --strict
```

Run the conformance report without requiring a local Datoviz installation:

```bash
uv run python tools/conformance_debug_report.py
```

## Normative and operational references

- [Conformance fixture specification](https://github.com/vispy/GSP_API/blob/main/spec/conformance-fixtures.md)
- [Visual QA harness specification](https://github.com/vispy/GSP_API/blob/main/spec/visual_qa_harness.md)
- [Fixture README](https://github.com/vispy/GSP_API/blob/main/fixtures/conformance/README.md)
- [API review examples](review-examples.md)
- [Historical S023 visual-QA foundation](s023_visual_qa.md)
