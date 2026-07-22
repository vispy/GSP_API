# M270 - S063 installed-wheel interaction qualification and closeout

## Stage

S063 - Live View2D Interaction Parity And Regression Safety

## Status

Approved; M269 completed and the project owner authorized sequential execution. Final closeout
still requires owner acceptance of both live windows.

## Summary

Rebuild every distribution, qualify live View2D behavior from clean installed wheels, rerun native
and lifecycle gates, and open both windows for final owner review.

## Acceptance

- Core-only, VisPy2-only, Matplotlib, Datoviz, and combined wheel environments pass.
- Existing test counts do not regress and new interaction tests pass.
- Equivalent actions yield matching canonical ranges across providers.
- Offscreen, query/layout, Texture2D nearest/linear, and lifecycle gates remain green.
- Both live windows demonstrate points/grid moving together and stationary NDC overlays.
- Owner accepts manual pan/zoom behavior before S063 closes.

## Stop conditions

Stop on editable/source import leakage, native instability, failed manual parity, dirty repositories,
or any required external remote/release operation.
