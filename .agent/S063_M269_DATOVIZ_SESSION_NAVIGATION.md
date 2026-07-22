# M269 Datoviz session navigation wiring

Date: 2026-07-22

Implemented and committed in fresh-root GSP commit `7738b5c`.

- Interactive 2D `display()` enables the existing canonical GSP View2D controller before running.
- `run()` also enables it when the renderer was created by a prior noninteractive `render()`.
- Activation is idempotent per retained renderer.
- File/offscreen rendering does not activate input, and View3D scenes remain excluded.
- Renderer close continues to own controller callback unsubscription.
- Existing retained navigation tests prove panel domains/axes update without visual-buffer uploads.

Validation: 451 tests passed; strict mypy passed for 51 source files; Ruff passed; the current
Datoviz source probe passed against `be7f2a80354c25e85bab88c85f5ea7340975b569`.

M270 is approved for installed-wheel and live-owner qualification.
