# Prompt Input
based on this repository, extract the following information

Repository name: {{repo_name}}
Description: {{short_description}}
Target audience: {{audience}} (e.g. engineers, CTOs, researchers, investors)
Problem it solves: {{problem_statement}}
Key features: {{features_list}}
Tech stack: {{tech_stack}}
Differentiation: {{unique_value}}
Maturity level: {{prototype | production | research}}
Links (optional): {{repo_url, docs_url}}

---

Repository name: GSP_API

Description: A Python implementation of the Graphic Server Protocol (GSP) — a backend-agnostic scene-description API for 2D/3D scientific visualization that lets the same scene be rendered through Matplotlib, Datoviz, or a network renderer.

Target audience: Scientific Python developers and visualization researchers — particularly people building plotting tools or comparing rendering backends (matplotlib for compatibility, Datoviz for GPU performance). Less aimed at end-user analysts than at engineers/researchers building on top of a visualization stack.

Problem it solves: Scientific visualization in Python is fragmented — matplotlib is ubiquitous but slow at scale, GPU backends like Datoviz are fast but non-portable, and remote/network rendering needs yet another stack. GSP_API defines a single declarative scene model (canvas, viewport, visuals, transforms, materials, geometry) and dispatches to whichever renderer the user picks via GSP_RENDERER, so the same example script runs on all three.

Key features:
- Backend-agnostic scene API: core, geometry, transforms, materials, types, visuals
- Visual primitives: image, markers, mesh, paths, pixels, points, segments, texts (src/gsp/visuals/)
- Three pluggable renderers via separate packages: gsp_matplotlib, gsp_datoviz, gsp_network (Flask-based remote rendering)
- Animator and viewport-event subsystems shared across backends
- Pydantic-based typed scene objects (gsp_pydantic)
- Runtime backend selection via the GSP_RENDERER env var
- Large examples/ gallery covering axes, cameras, meshes, images, dynamic groups, etc.
- mkdocs-material documentation site (mkdocs.yml)

Tech stack: Python ≥3.13, NumPy, Matplotlib, Datoviz (GPU/Vulkan), Pydantic v2, Flask + requests-file (network renderer), imageio, loguru, colorama, mpl3d. Tooling: Poetry, pytest, mypy, ruff, black, pydoclint, mkdocs-material + mkdocstrings, pre-commit.

Differentiation: Unlike matplotlib, Datoviz, or VisPy — each of which owns both the API and the renderer — GSP_API is just the API layer, with three interchangeable renderers behind it (CPU/Matplotlib, GPU/Datoviz, remote/network). Switching backends is an env-var change, not a code rewrite, which makes it useful as a portability layer or as a research vehicle for studying rendering-API design across backends (an explicit goal in TODO.md: "design principles for rendering library API with multiple backends").

Maturity level: Prototype / research. Version 0.1.0, empty description field in pyproject.toml, an active TODO.md listing unresolved bugs (text anchor/rotation in datoviz, network-renderer clearing semantics, sanity-check inheritance issues), an in-flight feature branch (mesh_include_2), and an examples_nico / gsp_nico collaborator sandbox — all consistent with active R&D rather than a released product.

Links:
- Repo URL: not configured locally — no remote.origin.url is referenced in the tree; ask the maintainer for the canonical Git host
- Docs: built locally via mkdocs (mkdocs_source/, output in mkdocs_build/); no public docs URL is declared in the repo
- Related upstream: Datoviz — https://datoviz.org
