# M269 - S063 Datoviz session navigation wiring

## Stage

S063 - Live View2D Interaction Parity And Regression Safety

## Status

Approved; M268 completed and the project owner authorized sequential execution.

## Summary

Connect interactive Datoviz 2D provider sessions to the existing canonical GSP View2D input
adapter, preserving retained GPU updates and deterministic lifecycle cleanup.

## Acceptance

- Interactive 2D execution enables canonical navigation exactly once.
- Drag/wheel events update canonical view/revision and native panel/axes together.
- Unchanged visual buffers are not re-uploaded.
- Offscreen output and View3D do not activate the 2D controller.
- Controller callbacks unsubscribe on close.
- Synthetic, isolated native, full Datoviz, strict mypy, and Ruff gates pass.

## Stop conditions

Stop on native crash, hidden native-only state, buffer re-upload regression, capability overclaim,
or any required edit to the sibling Datoviz repository.
