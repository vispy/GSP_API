# S063 proposal - Live View2D interaction parity and regression safety

Date: 2026-07-22

Status: completed; M267-M270 passed all automated gates and owner live acceptance.

## Trigger

Manual testing of the first separated-repository VisPy2 example exposed two live interaction gaps:

- Matplotlib toolbar pan changes the grid/axes limits while DATA points remain fixed because the
  renderer eagerly maps DATA positions into axes-fraction coordinates for the initial `View2D`.
- Datoviz opens and renders a live window but the provider session does not connect the already
  implemented GSP View2D navigation input adapter, so drag and wheel input do nothing.

Static and offscreen qualification did not exercise these live behaviors. S063 makes them explicit
regression gates without broadening the producer API or weakening canonical GSP navigation.

## Authority and decision boundary

ADR-0022 already decides the relevant semantics: `View2D` is canonical, native events adapt into
semantic actions, retained GPU navigation updates small view/panel state, and hidden native state is
not strict GSP navigation unless synchronized back into canonical state. ADR-0033 assigns event-loop
and display ownership to explicit sessions and forbids backend state on VisPy2 figures and axes.

No new ChatGPT Pro consultation is required for the scoped implementation. Stop and create a
self-contained consultation packet if implementation would require a new public session API,
change protocol semantics, or expose backend-native controller state.

## Scope

- Live interactive `View2D` pan, zoom, set-view, and reset behavior.
- Matplotlib DATA versus NDC transform placement.
- Matplotlib native-toolbar-to-canonical-View2D synchronization with revision tracking.
- Datoviz session wiring to the existing GSP live View2D navigation adapter.
- Cross-backend semantic range/revision parity and installed-wheel regression qualification.

Out of scope: View3D interaction, linked views, selection, hover, gestures beyond the current
adapter, new VisPy2 public plotting methods, remote sessions, and publication.

## Mission sequence

| Mission | State | Scope | Commit boundary |
|---|---|---|---|
| M267 | approved | Freeze the interaction contract and add failing tests for the observed Matplotlib and Datoviz behavior. | Commit tests and evidence before production fixes. |
| M268 | draft | Correct Matplotlib DATA/NDC transform placement and synchronize toolbar limit changes into session-owned canonical `View2D` state. | Commit Matplotlib implementation and focused tests. |
| M269 | draft | Activate existing canonical GSP View2D navigation for interactive Datoviz sessions and prove retained updates/cleanup. | Commit Datoviz implementation and focused native tests. |
| M270 | draft | Rebuild all wheels, run full regression/parity/lifecycle gates, open both live windows, and close S063 after owner acceptance. | Commit qualification evidence and closeout. |

## Required behavior

### Matplotlib

- DATA points, markers, segments, paths, DATA text, images, and 2D meshes track the visible data
  limits and move with grid lines during native toolbar pan/zoom.
- NDC/axes-relative visuals remain stationary during DATA navigation.
- Native limit changes update canonical session-owned `View2D` ranges and revision/snapshot state.
- Applying canonical GSP view changes back to Matplotlib does not recurse through native callbacks.
- Reversed ranges and inline/named affine transforms retain their accepted behavior.
- Callback connections are disconnected during session close.

### Datoviz

- Interactive 2D execution activates `enable_gsp_view2d_navigation()` exactly once.
- Pointer drag/wheel input becomes canonical GSP actions and updates `View2D` plus native panel/axis
  state together.
- Unchanged visual, texture, and index buffers are not re-uploaded during retained navigation.
- Offscreen/file rendering does not initialize an interactive controller.
- View3D behavior is unchanged and 2D callbacks unsubscribe during cleanup.
- Hidden native-only `enable_native_panzoom()` is not substituted for canonical navigation.

### Cross-backend

- Replaying equivalent semantic pan/zoom actions yields equal canonical x/y ranges and compatible
  revision transitions; pixel identity is not required.
- Query/layout results never claim a stale view snapshot when strict navigation is advertised.
- VisPy2 figures, axes, visuals, and immutable scenes retain no backend/session/native state.

## Regression gates

1. Focused failing tests are committed before implementation and pass only after the fixes.
2. Existing core, Matplotlib, Datoviz, and VisPy2 suites remain green.
3. Strict mypy and Ruff pass in both fresh-root repositories.
4. All four distributions rebuild and tests import them from clean installed wheels.
5. Matplotlib and Datoviz offscreen PNG paths remain functional.
6. Datoviz Texture2D nearest/linear native expectations remain exact.
7. Repeated interactive create/run/close cycles clean up deterministically.
8. One unchanged VisPy2 scene passes automated parity checks and manual pan/zoom review in both
   live windows.

## Stop conditions

Stop if a proposed fix:

- treats hidden backend-native state as canonical GSP state;
- changes static pixels without an explained semantic reason;
- moves NDC overlays with DATA navigation;
- re-uploads unchanged Datoviz buffers on the strict retained path;
- requires backend state on VisPy2 producer objects;
- introduces a new public session/protocol contract without consultation;
- depends on editable/source imports for qualification;
- modifies the sibling Datoviz repository;
- requires a remote, push, tag, release, or publication operation.

## Approval boundary

The project owner explicitly approved S063 missions M267-M270 in the active Mission Control
conversation on 2026-07-22. Approval authorizes local changes and incremental commits
in `gsp`, `vispy2`, and Mission Control records, but not external repository or publication actions.
