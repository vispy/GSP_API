# M257 - S061 architecture and naming decision

## Stage

S061 - GSP And VisPy2 Migration Foundation

## Status

Completed.

## Summary

Accept or revise ADR-0035 after recording the owner decision on separate `gsp` and `vispy2`
repositories and on the target `vispy2` distribution/import identity.

## Acceptance

- The repository and distribution topology is explicit.
- The relationship to ADR-0033 is explicit.
- Naming/governance and publication authority are not inferred.
- No repository, tag, archive, push, or release operation occurs.

## Stop conditions

Stop if the project owner does not approve the two-repository topology or if use of the `vispy2`
identity remains undecided.

## Result

The project owner approved separate fresh-root `gsp` and `vispy2` repositories, the target `vispy2`
distribution/import identity, and the bounded S061 migration-foundation stage. ADR-0035 is accepted,
ADR-0033's temporary identity is superseded for the migration target, and M258 is approved next. No
repository, tag, archive, push, release, or publication operation was performed.
