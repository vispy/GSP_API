# M002 - Protocol spine

## Goal

Create the first minimal GSP protocol spine without changing renderers.

## State

Ready for Mission Control discussion. Launch only after explicit approval.

## Expected tasks

- GSP-CORE-001: stable IDs and object references.
- GSP-CAPS-001: CapabilitySnapshot model.
- GSP-RES-001: BufferResource and AttributeSource model.
- GSP-CMD-001: CommandBatch model.
- GSP-TRANS-001: local in-process transport interface.

## Legacy inputs

- `LEGACY_MAP.md`
- `src/gsp/types/buffer.py`
- `src/gsp/types/buffer_type.py`
- `src/gsp/types/transbuf.py`
- `src/gsp/types/visual_base.py`
- `src/gsp/core/canvas.py`
- `src/gsp/core/viewport.py`
- `src/gsp/core/camera.py`
- `src/gsp/core/texture.py`
- `src/gsp_pydantic/types/pydantic_types.py`
- `src/gsp_pydantic/serializer/pydantic_serializer.py`

## Scope guard

Create the protocol spine beside the legacy object graph. Do not rewrite Matplotlib, Datoviz, Network, or VisPy2 adapters in this mission unless Mission Control explicitly expands scope.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- spec/protocol.md
- spec/transports.md
- spec/capabilities.md
- spec/resources.md

## Stop conditions

Stop for ChatGPT Pro consultation if resource semantics, transforms, or transport boundaries become unclear.
