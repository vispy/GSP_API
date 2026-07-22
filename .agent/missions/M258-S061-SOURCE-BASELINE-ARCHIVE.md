# M258 - S061 source baseline and recoverable archive

## Stage

S061 - GSP And VisPy2 Migration Foundation

## Status

Approved; M257 completed.

## Summary

Record the exact source baseline, reproduce the accepted checks, and create a checksum-verified local
Git bundle outside the working tree. This is archival preparation, not repository migration.

## Acceptance

- Exact commit, worktree state, validation results, and Datoviz provenance are recorded.
- The bundle passes `git bundle verify`, checksum verification, clean clone, and `git fsck --full`.
- The bundle path and recovery instructions are recorded without adding the bundle to Git.
- No public tag, remote mutation, deletion, or archive-mode change occurs.

## Stop conditions

Stop if the source baseline is not reproducible, the working tree contains unexplained changes, the
bundle is not independently recoverable, or storage outside the repository cannot be resolved.
