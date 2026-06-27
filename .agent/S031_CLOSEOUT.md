# S031 Closeout - Release-Candidate Stabilization and Roadmap Reset

## Outcome

S031 is closed as a release-candidate stabilization pass. The repository passes the required release
validation baseline and the optional Matplotlib-path example confidence checks.

No tag was created, no package version was changed, and nothing was published.

## Validation

Required release checklist:

- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success, 206 source files.
- `PYTHONPATH=. uv run pytest -q`: 403 passed, 2 skipped.
- `uv run mkdocs build --strict`: passed; MkDocs Material emitted its upstream MkDocs 2.0 warning.
- `uv build`: built `dist/gsp-0.1.0.tar.gz` and `dist/gsp-0.1.0-py3-none-any.whl`.
- `python -m json.tool .agent/status.json >/dev/null`: passed.
- `git diff --check`: passed.

Optional release-candidate confidence checks:

- `PYTHONPATH=. uv run python tools/run_all_examples.py`: passed, 56 Matplotlib-path examples.
- `PYTHONPATH=. uv run python tools/check_expected_output.py`: passed, 3 expected files matched.

## Fixes During Stabilization

- `examples/common/example_helper.py` and `examples/common/big_tester_helper.py` now lazy-load
  optional legacy Datoviz renderer modules only when the Datoviz renderer path is selected.
- Public Matplotlib-path examples no longer eagerly import optional legacy Datoviz renderer modules.
- `examples/protocol_live_window.py` now honors `GSP_TEST=True` by closing the Matplotlib figure
  instead of opening a blocking live window.
- `tests/test_import_surface.py` covers Matplotlib example-helper import with Datoviz blocked.

## Release-Facing Docs

- `CHANGELOG.md` now includes required `Unreleased` sections for fixed items, backend support, and
  known limitations.
- `README.md` now describes GSP as backend-agnostic scene/protocol tooling with Matplotlib as the
  reference backend and Datoviz/network as optional paths.

## Decision

The tree is a valid local release candidate for review, subject to normal human inspection of the
diff and artifacts.

Before any actual release operation, the user must explicitly approve:

- target version;
- package-version update, if any;
- annotated tag creation;
- publication target, if any.

## Remaining Limitations

- Datoviz v0.4 remains capability-gated and is not a package dependency.
- Datoviz guide/View2D rows remain adapted, not strict, because panel title and guide/all-rendered
  query semantics are still unsupported.
- Optional Datoviz, network, and session replay checks require separately recorded environments.

