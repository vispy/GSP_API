# M265 VisPy2 producer migration

Date: 2026-07-22

## Result

Migrated the semantic producer into `/Users/cyrille/GIT/Viz/vispy2` commit `99e4875`. The public
package is now `vispy2`; no compatibility alias for the unpublished `gsp_vispy2` identity was
created. `Figure.to_scene()` freezes producer state into immutable `gsp.Scene` records and rejects
unsupported multi-axes execution instead of silently dropping panels.

`Figure.savefig()` and blocking `Figure.show()` use ephemeral Matplotlib provider sessions.
Non-blocking and interactive execution require an explicit caller-owned GSP session. Producer
objects retain no backend, session, display, or native state, and the source contains no concrete
adapter imports.

Strict downstream typing exposed a missing `py.typed` marker in `gsp-core`; local GSP commit
`c76a403` adds the marker and the rebuilt wheel now exports its existing type information.

## Validation

- 10 producer tests pass from installed `vispy2` and `gsp-core` wheels with no adapter installed.
- The backend-neutral semantic example runs in that producer-only environment.
- Strict mypy passes for all three VisPy2 source files; Ruff passes.
- Installed-wheel Matplotlib `savefig()` and blocking `show()` pass under Agg.
- Installed-wheel caller-owned Datoviz non-blocking display creation passes against local Datoviz
  commit `be7f2a80354c25e85bab88c85f5ea7340975b569`.
- No source import targets `gsp_matplotlib`, `gsp_datoviz`, or `gsp_vispy2`.
- VisPy2 wheel SHA-256: `637b73fe6755b838744042024bf90e6255bc1491e342e325505fc2abd1ab9730`.
- VisPy2 sdist SHA-256: `86984d71c52a04327a98dd2a58bb732b3cacfea37cf4731be17761080d8ba3a3`.

No remote, publication, tag, or release operation occurred. M266 is approved for complete
installed-wheel qualification and S062 closeout.
