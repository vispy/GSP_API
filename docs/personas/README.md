# GSP API User Personas

This folder contains user personas that define three key stakeholder groups for the GSP API project:

## 1. Persona 1 - Dr. Alice Researcher (The Scientist Visualizing Their Data)

The end-user scientist who wants simple, fast data visualization without touching GPU internals. Uses GSP through higher-level libraries.

**Key characteristics:**
- Domain scientist comfortable with Python but not a graphics expert
- Wants fast iteration with minimal friction
- Needs publication-quality visuals that scale to large datasets

## 2. Persona 2 - Sam Framework Developer (Library Developer Building on GSP)

The library maintainer building visualization frameworks on top of GSP, needing stable APIs and clean abstractions to create tools like VisPy.

**Key characteristics:**
- Direct API consumer building interactive visualization tools
- Requires stable APIs and clear extension points
- Focuses on maintainability and community confidence

## 3. Persona 3 - Chris Backend Engineer (Backend Renderer Implementer)

The low-level graphics developer implementing GSP rendering backends (matplotlib, datoviz, WebGPU), requiring formal specs and efficient GPU pipeline mappings.

**Key characteristics:**
- Works at the lowest level of the stack
- Knows graphics APIs (OpenGL/Vulkan/WebGPU)
- Needs formal backend contracts and validation tools

---

These personas guide API design decisions by clarifying the needs, pain points, and success criteria for different user types in the GSP ecosystem.
