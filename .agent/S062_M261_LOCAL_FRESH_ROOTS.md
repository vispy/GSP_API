# M261 local fresh-root repositories

Date: 2026-07-22

## Result

Created two local unpublished repositories from empty directories:

| Repository | Root commit | Commit count | Remotes |
|---|---|---:|---:|
| `/Users/cyrille/GIT/Viz/gsp` | `3cb9fce43985a80fb6d5c0c3b7c2b9266bee0cba` | 1 | none |
| `/Users/cyrille/GIT/Viz/vispy2` | `eb498d434e483a992e5e36b36118b0c6cf95ec42` | 1 | none |

Both roots contain the BSD license, provenance, the exact S061 component manifest, local AGENTS
rules, ignore policy, and package/workspace skeletons. Neither repository imports legacy ancestry,
contains implementation code, or configures a remote, tag, release, or publication target.

The GSP skeleton defines separate `gsp-core`, `gsp-matplotlib`, and `gsp-datoviz` distributions. The
VisPy2 skeleton defines `vispy2` with dependency direction toward `gsp-core` and optional adapter
extras. M262 may now curate and isolate the formal core.

