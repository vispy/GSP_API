# S064 - GitHub predecessor archival and fresh-root publication

Date: 2026-07-22

Status: approved; M271 is approved and M272-M273 are authorized sequential follow-ups.

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
| M271 | approved | Back up, verify, rename, and archive both predecessor repositories; disable stale GSP Pages. |
| M272 | draft | Create the fresh public repositories, add local remotes, and push the qualified `main` histories. |
| M273 | draft | Add CI, validate/push CI commits, verify repository settings and checks, and close S064. |

## Stop conditions

Stop on a failed bundle verification, unexpected repository identity or permissions, occupied
archive name, dirty local root, non-fast-forward or force-push requirement, credential problem,
unexpected public content loss, or any request for tag/release/package publication.
