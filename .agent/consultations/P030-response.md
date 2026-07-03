Decision:

* **Latest-only GSP adapter update now.**
* Do **not** add aliases, compatibility fallbacks, or legacy-name probes.
* Do **not** edit the Datoviz checkout for this mission unless the real generated-binding smoke shows that a current C API symbol exists but is missing from the generated Python facade.
* Treat Datoviz `v0.4-dev` at commit `f5b81a397e3be69ecfffbffa88754c1c227e6820` as the current backend contract for this work.

Required Datoviz API Contract:

| Area                                            | Required C/Python symbols                                                                                                                              | Notes                                                                                                                                                               |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Import provenance                               | `datoviz.__file__` must resolve under `/Users/cyrille/GIT/Viz/datoviz/datoviz/`                                                                        | Prevent accidentally testing against an installed stale package.                                                                                                    |
| Coordinate spaces                               | `DvzVisualCoordSpace`, `DVZ_VISUAL_COORD_VIEW`, `DVZ_VISUAL_COORD_DATA`, `DVZ_VISUAL_COORD_PANEL`                                                      | Required values: `VIEW = 0`, `DATA = 1`, `PANEL = 2`. GSP should use these directly.                                                                                |
| Scalar sampled fields / color-mapped image data | `dvz_sampled_field_desc`, `dvz_field_data_view`, `dvz_sampled_field`, `dvz_sampled_field_set_data`, `dvz_visual_set_field`                             | This should be the canonical path for scalar/image-field data, especially paths related to colormaps/colorbars.                                                     |
| Sampled-field lifecycle                         | `dvz_sampled_field_destroy` if GSP owns sampled-field handles                                                                                          | If the Python binding lacks this but GSP needs ownership cleanup, pause GSP implementation and regenerate Datoviz bindings. Do not work around with leaks or mocks. |
| Packed RGBA image data                          | `dvz_visual_set_texture_rgba8`                                                                                                                         | This is a **current API path**, not a legacy compatibility fallback. Use it for already-packed `uint8[..., 4]` RGBA images. Do not use `dvz_visual_set_texture`.    |
| View3D retained panel setup                     | `dvz_panel_view3d_desc`, `dvz_panel_set_view3d_desc`, `dvz_panel_camera`, `dvz_camera_desc`, `dvz_camera_set_orthographic_bounds`, `DvzPanelFrameInfo` | GSP should use retained panel View3D descriptors and the panel-owned camera.                                                                                        |
| Optional future direct float texture path       | `dvz_visual_set_texture_r32f`                                                                                                                          | Do not require this for M214 unless GSP intentionally adds a direct `r32f` texture path. Scalar fields should go through sampled fields for this mission.           |

Legacy Symbols To Remove From GSP:

| Legacy symbol/path                                              | Replacement                                                                                | Migration notes                                                                                          |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| `DVZ_COORD_VIEW`                                                | `DVZ_VISUAL_COORD_VIEW`                                                                    | Delete from required-symbol checks, implementation, fake facades, and error messages.                    |
| `DVZ_COORD_DATA`                                                | `DVZ_VISUAL_COORD_DATA`                                                                    | Same. No `getattr(..., fallback)` logic.                                                                 |
| Any local alias such as `DVZ_COORD_* = DVZ_VISUAL_COORD_*`      | None                                                                                       | Do not add local aliases. The adapter should speak the current Datoviz API only.                         |
| `dvz_visual_set_texture`                                        | `dvz_visual_set_texture_rgba8` for packed RGBA8; sampled-field API for scalar fields       | Delete generic/stale texture setter use.                                                                 |
| `dvz_panel_set_camera`                                          | `dvz_panel_view3d_desc`, `dvz_panel_set_view3d_desc`, `dvz_panel_camera`                   | The previous S050 blocker was a stale GSP gate. Remove it entirely.                                      |
| Fake Datoviz facades that expose old names for this path        | Real generated-binding smoke for acceptance; current-name fakes only for narrow unit tests | Unit fakes may remain elsewhere, but they must not define the acceptance outcome for this API alignment. |
| Error messages saying Datoviz is missing `dvz_panel_set_camera` | Error messages naming the retained View3D descriptor contract                              | Missing `dvz_panel_set_camera` is no longer an error.                                                    |

GSP Implementation Plan:

1. **Create a single latest-API contract module in GSP**, for example:

   `src/gsp_datoviz/latest_api_contract.py`

   It should contain only current Datoviz symbol requirements. No old-name probing, no aliases, no fallback-to-legacy behavior.

2. **Replace coordinate-space usage in `src/gsp_datoviz/protocol_renderer.py`.**

   Use:

   ```python
   dvz.DVZ_VISUAL_COORD_VIEW
   dvz.DVZ_VISUAL_COORD_DATA
   dvz.DVZ_VISUAL_COORD_PANEL
   dvz.DvzVisualCoordSpace
   ```

   Delete all references to:

   ```python
   DVZ_COORD_VIEW
   DVZ_COORD_DATA
   ```

3. **Split image handling by current Datoviz data model.**

   Use sampled fields for scalar/image-field data:

   ```text
   dvz_sampled_field_desc
   dvz_field_data_view
   dvz_sampled_field
   dvz_sampled_field_set_data
   dvz_visual_set_field
   ```

   Use `dvz_visual_set_texture_rgba8` only for true packed RGBA8 image payloads.

   This is not a compatibility shim. It is a two-path current-API design:

   ```text
   scalar field / colormapped image -> sampled-field API
   packed uint8 RGBA image          -> dvz_visual_set_texture_rgba8
   ```

   Delete all use of `dvz_visual_set_texture`.

4. **Replace View3D setup with retained panel View3D descriptors.**

   GSP should not create a detached camera and push it with `dvz_panel_set_camera`.

   The architecture should be:

   ```text
   panel -> current View3D descriptor -> dvz_panel_set_view3d_desc
         -> panel-owned camera        -> dvz_panel_camera
         -> camera configuration      -> current camera API
   ```

   Use:

   ```text
   dvz_panel_view3d_desc
   dvz_panel_set_view3d_desc
   dvz_panel_camera
   dvz_camera_desc
   dvz_camera_set_orthographic_bounds
   DvzPanelFrameInfo
   ```

   The coding agent should inspect the generated `_ctypes.py` signatures at the pinned Datoviz checkout and implement against those signatures exactly.

5. **Make missing current symbols hard failures.**

   If a required current symbol is missing from the real generated Python facade, raise an explicit backend-contract error such as:

   ```text
   Datoviz v0.4-dev generated Python binding is missing required current API symbol: <symbol>
   ```

   Do not say or imply that GSP can fall back to a legacy symbol.

6. **Update unit fakes only after the real contract is defined.**

   Fake Datoviz classes may remain for non-acceptance unit tests, but they must expose the current API names only. They should not keep old aliases alive in the test suite.

7. **Do not promote strict runtime capabilities yet.**

   The adapter alignment may allow colorbar or strict-depth cases to progress further, but do not mark Datoviz colorbar strictness or strict opaque depth as supported until fresh runtime review-pack artifacts exist and have been reviewed.

Validation Plan:

1. Generated binding smoke checks:

   From the GSP repo on branch `agentic-gsp-vispy2`:

   ```bash
   export DATOVIZ=/Users/cyrille/GIT/Viz/datoviz
   export PYTHONPATH="$DATOVIZ:${PYTHONPATH:-}"

   python - <<'PY'
   from pathlib import Path
   import datoviz as dvz

   expected_root = Path("/Users/cyrille/GIT/Viz/datoviz/datoviz").resolve()
   actual_file = Path(dvz.__file__).resolve()
   assert str(actual_file).startswith(str(expected_root)), actual_file

   required = [
       "DvzVisualCoordSpace",
       "DVZ_VISUAL_COORD_VIEW",
       "DVZ_VISUAL_COORD_DATA",
       "DVZ_VISUAL_COORD_PANEL",

       "dvz_sampled_field_desc",
       "dvz_field_data_view",
       "dvz_sampled_field",
       "dvz_sampled_field_set_data",
       "dvz_visual_set_field",

       "dvz_visual_set_texture_rgba8",

       "dvz_panel_view3d_desc",
       "dvz_panel_set_view3d_desc",
       "dvz_panel_camera",
       "dvz_camera_desc",
       "dvz_camera_set_orthographic_bounds",
       "DvzPanelFrameInfo",
   ]

   missing = [name for name in required if not hasattr(dvz, name)]
   assert not missing, f"Missing current Datoviz API symbols: {missing}"

   assert dvz.DVZ_VISUAL_COORD_VIEW == 0
   assert dvz.DVZ_VISUAL_COORD_DATA == 1
   assert dvz.DVZ_VISUAL_COORD_PANEL == 2

   enum = dvz.DvzVisualCoordSpace
   assert enum.DVZ_VISUAL_COORD_VIEW == dvz.DVZ_VISUAL_COORD_VIEW
   assert enum.DVZ_VISUAL_COORD_DATA == dvz.DVZ_VISUAL_COORD_DATA
   assert enum.DVZ_VISUAL_COORD_PANEL == dvz.DVZ_VISUAL_COORD_PANEL

   legacy = [
       "DVZ_COORD_VIEW",
       "DVZ_COORD_DATA",
       "dvz_visual_set_texture",
       "dvz_panel_set_camera",
   ]
   present_legacy = [name for name in legacy if hasattr(dvz, name)]
   assert not present_legacy, f"Unexpected legacy symbols in tested facade: {present_legacy}"

   print("Datoviz v0.4-dev generated binding smoke passed:", actual_file)
   PY
   ```

   Then verify that GSP itself no longer references stale symbols:

   ```bash
   if git grep -nE 'DVZ_COORD_(VIEW|DATA)|dvz_visual_set_texture\b|dvz_panel_set_camera' -- src tests docs; then
       echo "Stale Datoviz API symbol use remains in GSP" >&2
       exit 1
   fi
   ```

2. Runtime review-pack checks:

   Run the existing GSP review-pack runner against real Datoviz and Matplotlib, with Datoviz imported from the sibling checkout:

   ```bash
   export DATOVIZ=/Users/cyrille/GIT/Viz/datoviz
   export PYTHONPATH="$DATOVIZ:$PWD/src:${PYTHONPATH:-}"
   export GSP_DATOVIZ_REAL=1
   ```

   Required cases:

   ```bash
   python -m gsp_api.review_pack --case S028 --backend datoviz --out artifacts/M214/S028-datoviz
   python -m gsp_api.review_pack --case S028 --backend matplotlib --out artifacts/M214/S028-matplotlib
   python -m gsp_api.review_pack --case S050 --backend datoviz --out artifacts/M214/S050-datoviz
   ```

   Expected status:

   ```text
   S028 Datoviz colorbar:
   - Must render with real Datoviz.
   - Must produce fresh artifacts.
   - May be compared against Matplotlib artifacts.
   - Do not promote Datoviz colorbar strictness unless the produced artifacts are reviewed and accepted.

   S050 Datoviz View3D strict-depth:
   - Must no longer fail because of missing DVZ_COORD_* names.
   - Must no longer fail because of missing dvz_panel_set_camera.
   - If it fails later due to actual depth, opacity, camera, or rendering semantics, record that as runtime evidence.
   - Do not promote strict opaque depth until fresh visual/runtime evidence supports it.
   ```

   If the actual repo does not expose `python -m gsp_api.review_pack`, the coding agent should wire these exact cases into the existing review-pack entry point rather than replacing the acceptance with fakes.

3. Tests/docs to update:

   | File area                                              | Intent                                                                                            |
   | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
   | `src/gsp_datoviz/protocol_renderer.py`                 | Replace stale Datoviz API usage with current symbols and retained View3D setup.                   |
   | `src/gsp_datoviz/latest_api_contract.py` or equivalent | Centralize required current symbols and hard-failure messages.                                    |
   | Datoviz backend tests                                  | Update fakes to current names only; remove tests asserting legacy compatibility.                  |
   | Real Datoviz integration/smoke tests                   | Add or update a test that imports the sibling generated binding and asserts the current contract. |
   | Mission docs / review-pack notes                       | Reframe M214 as latest-binding alignment, not compatibility.                                      |
   | Support matrix docs                                    | Do not promote colorbar strictness or strict opaque depth solely from symbol/import checks.       |

M214 Rescope:

* New mission title:

  ```text
  M214 - Datoviz v0.4-dev Latest Generated-Binding Alignment
  ```

* Scope:

  ```text
  Align GSP's Datoviz adapter with the current Datoviz v0.4-dev C API and generated Python bindings at the inspected Datoviz checkout.

  Replace stale coordinate, image/texture, and View3D camera API usage.

  Validate with real generated-binding smoke and real Datoviz review-pack runs.

  Do not add local aliases, compatibility shims, or fake/mock-based acceptance.
  ```

* Stop conditions:

  ```text
  1. datoviz.__file__ does not resolve under /Users/cyrille/GIT/Viz/datoviz.
  2. A required current C/Python symbol is missing from the generated Python facade.
  3. A current C symbol exists but is not generated into Python and GSP needs it.
  4. The retained View3D descriptor/camera API cannot be driven from Python because required structs, fields, or functions are not exposed.
  5. Runtime review-pack execution reaches a real Datoviz rendering/camera/depth behavior failure unrelated to stale symbol names.
  6. Fixing the blocker would require editing the Datoviz checkout without explicit owner approval.
  ```

* Acceptance criteria:

  ```text
  1. GSP contains no implementation references to:
     - DVZ_COORD_VIEW
     - DVZ_COORD_DATA
     - dvz_visual_set_texture
     - dvz_panel_set_camera

  2. GSP uses:
     - DVZ_VISUAL_COORD_VIEW
     - DVZ_VISUAL_COORD_DATA
     - DVZ_VISUAL_COORD_PANEL
     - sampled-field API for scalar image/field data
     - dvz_visual_set_texture_rgba8 for packed RGBA8 data
     - retained View3D panel descriptor/camera API

  3. Real generated-binding smoke passes with PYTHONPATH pointing to /Users/cyrille/GIT/Viz/datoviz.

  4. S028 and S050 review-pack runs are executed against real Datoviz.

  5. S050 no longer stops at stale coordinate-space imports or missing dvz_panel_set_camera.

  6. Any remaining S050 failure is classified as runtime rendering/camera/depth evidence, not as API-symbol compatibility work.

  7. Fake/mock tests are not used as the acceptance gate for this mission.
  ```

Risks / Blockers:

* `dvz_sampled_field_destroy` may need to be present in Python if GSP owns sampled-field handles. If absent, regenerate Datoviz bindings rather than leaking or mocking around it.
* The retained View3D descriptor structs may expose different field names or ownership semantics in `_ctypes.py`; the coding agent must implement against the generated signatures, not guessed C signatures.
* `dvz_visual_set_texture_r32f` is exposed in C but not part of the required M214 Python contract unless GSP adds a direct float-texture path. Prefer sampled fields for scalar data.
* Review-pack success for import/symbol alignment does not imply strict colorbar or strict opaque-depth support.
* The Datoviz checkout has unrelated dirty state. This mission should treat it as read-only unless explicit approval is given.
* If a required current C API exists but is missing from generated Python, the correct Datoviz-side change is binding generation only: expose the current symbol in `_ctypes.py`, produce header/source evidence plus Python smoke evidence, and avoid adding legacy aliases.
