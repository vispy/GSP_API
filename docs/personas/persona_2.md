## 🔹 Persona 2 — *Library Developer Building on GSP*

**Name:** Sam Framework Developer

**Role:** Maintainer of VisPy-like library / scientific viz framework integrator

**Background:**

* Strong Pythonist, knows NumPy, events, data models
* Good understanding of rendering layers but not full GPU stack

**Goals:**

* Build interactive visualization tools on top of GSP
* Have stable APIs to rely on for years
* Extend visuals (markers, meshes, volumes…) without rewriting backend code

**Tasks:**

* Design scene graphs, markers, layers
* Bind high-level API to low-level GSP primitives
* Handle user-facing features (colormaps, axes, labels)

**Motivations:**

* Wants a backend that provides predictable performance
* Clean abstractions, modularity & plugin friendliness
* Community confidence and maintainability

**Pain Points:**

* Backend fragmentation (OpenGL, Vulkan, WebGPU)
* Keeping rendering code maintainable across versions
* Performance issues with large dynamic scenes

**Interaction with GSP:**

* Direct API consumer
* Creates "visuals" that map to GSP rendering primitives
* Cares about documentation, stability, unit tests

**Must haves:**

* Stable API
* Clear extension points
* Good error messages & debugging tools

**Nice to haves:**

* Profiling hooks
* Support for multiple rendering backends out-of-the-box

**Success looks like:** "I built features fast, didn't fight the backend, performance is great."
