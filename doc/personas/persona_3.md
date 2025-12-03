## 🔹 Persona 3 — *Backend Renderer Implementer*

**Name:** Chris Backend Engineer

**Role:** Low-level graphics developer, contributor of new renderer backends

**Background:**

* Knows graphics APIs (OpenGL/Vulkan/WebGPU)
* Familiar with GLSL/SPIR-V, GPU memory, render passes
* Comfortable in Python + C/C++/Rust bindings

**Goals:**

* Implement efficient GSP backends (matplotlib, datoviz, maybe WebGPU next)
* Map GSP's intermediate representation into native rendering pipelines

**Tasks:**

* Implement rendering primitives (points, meshes, images)
* Optimize GPU usage, batching, memory transfers
* Benchmark performance across hardware

**Motivations:**

* Loves efficiency and clean architecture
* Wants a backend system that is extensible and predictable

**Pain Points:**

* Poorly defined data flow between layers
* Hard-to-test rendering pipelines
* API ambiguity makes implementation brittle

**Interaction with GSP:**

* Works at the lowest level of the stack
* Needs spec-level interface: "If user draws X → backend must do Y"
* Wants test harnesses, IR diagrams, examples

**Must haves:**

* Formal backend contract/spec
* Validation tools, debugging utilities
* Low overhead between core + backend

**Nice to haves:**

* Hot-reload shaders
* Reference backend sample implementation

**Success looks like:** "I implemented a backend cleanly, passed the test suite, and performance is solid."
