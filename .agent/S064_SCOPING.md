# S064 - GitHub predecessor archival and fresh-root publication

Date: 2026-07-22

Status: completed; M271-M273 passed their stop conditions and acceptance gates.

## Authorization

The project owner explicitly approved this stage in the active Mission Control conversation.
Authorization covers verified backups, disabling stale predecessor Pages, renaming the public
predecessors with `-old`, archiving them, creating fresh public repositories at `vispy/gsp` and
`vispy/vispy2`, pushing the qualified local `main` histories, and adding CI.

It does not authorize force pushes, history rewrites, tags, releases, package publication, deletion
of predecessor repositories, credential changes, or changes to the sibling Datoviz repository.

## Mission sequence

| Mission | State | Scope |
|---|---|---|
| M271 | completed | Backed up, verified, renamed, and archived both predecessor repositories; relocated stale GSP Pages. |
| M272 | completed | Created fresh public repositories, added local remotes, and pushed the qualified `main` histories. |
| M273 | completed | Added CI, validated and pushed CI commits, verified settings/checks, and closed S064. |

## Stop conditions

Stop on a failed bundle verification, unexpected repository identity or permissions, occupied
archive name, dirty local root, non-fast-forward or force-push requirement, credential problem,
unexpected public content loss, or any request for tag/release/package publication.
