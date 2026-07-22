# S063 closeout - live View2D interaction parity and regression safety

Date: 2026-07-22

## Outcome

S063 is complete. The initially observed Matplotlib and Datoviz live interaction regressions are
fixed in the fresh-root GSP repository without changing the public VisPy2 producer API or adding
backend state to producer objects.

| Boundary | Commit |
|---|---|
| Red regression baseline | `0a950be` |
| Matplotlib canonical live View2D synchronization | `003e6f4` |
| Datoviz session navigation wiring | `7738b5c` |
| Qualification record | `d1daacb`, `cb10e1b` |

The VisPy2 repository required no source change and remains at `55a16b3`.

## Qualification

| Environment | Result |
|---|---|
| GSP source workspace | 451 passed |
| Core installed wheel only | 167 passed |
| VisPy2 + core installed wheels | 10 passed; semantic example passed |
| Matplotlib + VisPy2 installed wheels | 140 passed |
| Datoviz + VisPy2 installed wheels | 163 passed |
| Strict mypy | 51 GSP and 3 VisPy2 source files passed |
| Ruff | Both fresh-root repositories passed |
| Offscreen PNG | Matplotlib and Datoviz passed from `site-packages` imports |
| Live review | Owner accepted Matplotlib and Datoviz pan/zoom parity |

The live scene used DATA points, semantic axes/grid, and an NDC mesh overlay. In both windows the
DATA points and grid navigated together while the NDC overlay stayed stationary. Equivalent
semantic pan actions produced equal canonical ranges and compatible revision transitions. Existing
retained Datoviz tests preserved zero unchanged-buffer uploads, exact Texture2D nearest/linear
expectations, and deterministic callback cleanup.

## Wheel hashes

- `gsp-core`: `727ec6d12078b8abf2aa1f3eebc6373704eba6a2e17b5c98256c9e8f37e607cc`
- `gsp-matplotlib`: `cabc20ea2e56cab1a6984433f0655b8f73bbbc14bcfe1572721658a776a4b06e`
- `gsp-datoviz`: `a1f96d44d66f6981f3d6c6f019f2ff8ea3774bd05ace1f7c50f1210e35bee142`
- `vispy2`: `637b73fe6755b838744042024bf90e6255bc1491e342e325505fc2abd1ab9730`

Datoviz provenance remains `be7f2a80354c25e85bab88c85f5ea7340975b569`; its checkout was not
modified. No remote, push, tag, release, publication, or external repository operation occurred.
