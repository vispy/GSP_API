# GSP Documentation

Graphic Server Protocol — a backend-agnostic scene-description API for 2D/3D scientific visualization in Python.

GSP provides a unified, declarative interface for describing scientific visualizations across multiple rendering backends. Whether you're building interactive plots with Matplotlib, high-performance 3D scenes with Datoviz, or remote visualization systems over the network, GSP abstracts away backend-specific details. This documentation covers the core protocol, available renderers, and the architectural principles that make GSP flexible and extensible.

## Philosophy

GSP is built on a set of core design principles that prioritize clarity, flexibility, and composability. This section explores the architectural decisions, design patterns, and philosophical foundations that guide GSP's development. Whether you're contributing to GSP or simply curious about why certain decisions were made, these documents provide a comprehensive view of the project's vision and technical rationale.

- [Overview](philosophy/README.md) — Index of all philosophy and design documents
- [Whitepaper](philosophy/whitepaper.md) — High-level pitch: motivation, architecture, ecosystem positioning
- [GSP Core](philosophy/philosophy_gsp_core.md) — Deep dive on the contract layer and the five design principles behind `src/gsp/`
- [Packages](philosophy/philosophy_packages.md) — Seven packages and the three-tier layered architecture
- [Renderers](philosophy/philosophy_renderers.md) — Conventions shared across `gsp_matplotlib`, `gsp_datoviz`, and `gsp_network`
- [Examples](philosophy/philosophy_examples.md) — Pattern catalog and design principles behind the 50+ example scripts


## API Reference

GSP is organized into seven core packages, each serving a specific role in the visualization pipeline. The Core protocol provides the foundational abstractions, while specialized packages handle rendering across different backends, network communication, and high-level utilities. Each module below exposes a cohesive API designed for both simplicity and extensibility.

- [GSP](api/gsp.md) — Core protocol: canvas, viewport, camera, visuals, transforms, and utilities
- [GSP Network](api/gsp_network.md) — Network-based rendering for remote visualization and client-server architectures
- [GSP Pydantic](api/gsp_pydantic.md) — Serialization and validation of GSP objects using Pydantic models
- [GSP Matplotlib](api/gsp_matplotlib.md) — Matplotlib rendering backend
- [GSP Datoviz](api/gsp_datoviz.md) — High-performance Datoviz rendering backend
- [GSP Extra](api/gsp_extra.md) — Additional utilities, animation helpers, and high-level 3D components
- [VisPy 2](api/vispy_2.md) — Interactive axes display and pan/zoom built on top of GSP

