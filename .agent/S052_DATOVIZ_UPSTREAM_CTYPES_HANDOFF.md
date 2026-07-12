# Datoviz v0.4 RC1 ctypes panel-frame handoff

## Environment

- Datoviz branch: `v0.4-dev`
- Datoviz commit: `ff62b3256f1de7dd2df2ee890c99968715789a27`
- Python: 3.12 arm64 macOS
- GSP execution: isolated Datoviz offscreen child

## Defect

The generated Python facade exports `DvzPanelFrameInfo`, `DvzGuideLayout`, and `DvzGuideHit`, but
they are zero-byte `ctypes.Structure` forward declarations with no `_fields_`. Symbol-based feature
checks therefore pass even though the structures cannot receive native copy output safely.

Minimal inspection:

```python
import ctypes
import datoviz

for name in ("DvzPanelFrameInfo", "DvzGuideLayout", "DvzGuideHit"):
    record = getattr(datoviz, name)
    print(name, ctypes.sizeof(record), getattr(record, "_fields_", None))
```

Observed output:

```text
DvzPanelFrameInfo 0 None
DvzGuideLayout 0 None
DvzGuideHit 0 None
```

Calling `dvz_panel_frame_info(snapshot, pointer(DvzPanelFrameInfo()))` from the GSP panel-frame
snapshot path caused a native segmentation fault before the case report was written.

## Requested upstream validation

1. Generate complete ctypes layouts for all public panel-frame copy records.
2. Add binding tests asserting non-zero `ctypes.sizeof()` and expected field names.
3. Add a native/Python smoke that resolves a panel frame, copies frame info, enumerates guide layout
   and rendered contributions, performs a guide hit, unreferences the snapshot, and exits cleanly.
4. Treat incomplete generated record layouts as binding-generation failures rather than exported
   capabilities.

GSP now guards zero-size ctypes records and reports snapshot readback unavailable instead of making
the unsafe native call. No Datoviz source was modified by M234.
