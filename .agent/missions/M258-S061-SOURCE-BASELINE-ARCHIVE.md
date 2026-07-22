# M258 - S061 source baseline and recoverable archive

## Stage

S061 - GSP And VisPy2 Migration Foundation

## Status

Completed.

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

## Result

Established clean source baseline `463d34d1d6560f045e5c40af594372d0fea93ab5`, reproduced all
repository/package/native validation gates, and created a complete 42 MiB external Git bundle with
SHA-256 `4b6b8bdd0e403ea9f0ed7d169a7694ac0985e7a8906890d2f74cf1dc5c611f8b`. Bundle,
checksum, clean-clone, exact-commit, and full object-integrity checks pass. See
`.agent/S061_M258_SOURCE_BASELINE_ARCHIVE.md`.
