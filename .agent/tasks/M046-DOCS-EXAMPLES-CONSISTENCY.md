# M046-DOCS-EXAMPLES-CONSISTENCY - Docs/examples consistency cleanup

## Mission

M046

## Goal

Repair user-facing README, MkDocs, and examples documentation drift found by M044.

## Acceptance

- README and example docs use one canonical backend selection story or explicitly document aliases.
- Stale documentation links are replaced with existing repo paths or MkDocs entry points.
- Example README filenames match the files present under `examples/`.
- Example backend support claims distinguish Matplotlib, legacy Datoviz, Datoviz v0.4 protocol work,
  network, internal examples, and VisPy2 producer examples where needed.
- User-facing docs refer to repository commands, not agent-only skills.

## Stop conditions

Stop before rewriting the full documentation site, creating new examples, or changing runtime
backend selection behavior without tests.

## Source

M044 packaging/import/docs audit.

## Result

Completed. README links now point at existing philosophy markdowns, `examples/README.md` documents
`GSP_RENDERER` as the source-of-truth backend selector, stale session example filenames were fixed,
agent-only skill references were removed from user docs, and backend support language now
distinguishes Matplotlib, optional legacy Datoviz, network, and Datoviz v0.4 protocol work. M047 was
queued to tackle the strict mypy type-surface failures left outside M045.
