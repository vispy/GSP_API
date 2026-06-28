"""Artifact writers for visual QA runs."""

from __future__ import annotations

import json
from pathlib import Path
import platform
import sys
from typing import Any, Mapping, cast

import numpy as np

from gsp.protocol import (
    AffineTransform2DResource,
    AxisGuide,
    ColorScale,
    ColorbarGuide,
    ImageVisual,
    InlineAffineTransform2D,
    MeshVisual,
    MarkerVisual,
    PanelTextGuide,
    PathVisual,
    PointVisual,
    ScalarColorEncoding,
    SegmentVisual,
    TextVisual,
    TransformRef,
    View2D,
    VisualTransformBinding,
)
from gsp.qa.visual.backend_ids import DATOVIZ_BACKEND_ID
from gsp.qa.visual.case_spec import ProtocolVisual, VisualQAScene
from gsp.qa.visual.cases import case_slug
from gsp.qa.visual.datoviz_probe import DatovizV04ProbeReport


def ensure_run_dirs(out_dir: Path) -> None:
    """Create the visual QA artifact directory layout."""
    for relative in (
        "scenes",
        "backends/matplotlib",
        f"backends/{DATOVIZ_BACKEND_ID}",
        "contact_sheets",
        "notes",
    ):
        (out_dir / relative).mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    """Write deterministic JSON."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_scene_artifacts(out_dir: Path, scene: VisualQAScene) -> tuple[Path, Path]:
    """Write a scene JSON file and NumPy sidecar arrays."""
    slug = case_slug(scene.case_id)
    scene_path = out_dir / "scenes" / f"{slug}.scene.json"
    arrays_path = out_dir / "scenes" / f"{slug}.arrays.npz"
    write_json(scene_path, _scene_json(scene))
    np.savez(arrays_path, **cast(Any, scene.arrays))
    return scene_path, arrays_path


def write_environment(out_dir: Path, probe_report: DatovizV04ProbeReport) -> Path:
    """Write the environment summary for a run."""
    path = out_dir / "environment.json"
    payload = {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "datoviz": {
            "path": probe_report.installed_package.get("path"),
            "imported": probe_report.imports["datoviz"].imported,
            "raw_imported": probe_report.imports["datoviz.raw"].imported,
            "minimal_point_supported": probe_report.minimal_point_scene.supported,
        },
    }
    write_json(path, payload)
    return path


def write_run_manifest(out_dir: Path, payload: Mapping[str, object]) -> Path:
    """Write the run manifest."""
    path = out_dir / "run_manifest.json"
    write_json(path, payload)
    return path


def write_manual_notes(out_dir: Path, case_ids: tuple[str, ...]) -> Path:
    """Write the manual review notes template."""
    path = out_dir / "manual_notes.yaml"
    lines = ["schema_version: 1", "cases:"]
    for case_id in case_ids:
        lines.extend(
            [
                f"  - case_id: {case_id}",
                "    status: pending",
                "    notes: ''",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_case_note(
    out_dir: Path, case_id: str, title: str, notes: tuple[str, ...]
) -> Path:
    """Write a per-case manual review note."""
    path = out_dir / "notes" / f"{case_slug(case_id)}.md"
    body = [f"# {title}", "", f"Case: `{case_id}`", "", "## Review Notes", ""]
    body.extend(f"- {note}" for note in notes)
    body.extend(["", "## Decision", "", "- [ ] pass", "- [ ] needs follow-up", ""])
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def write_summary(out_dir: Path, report: Mapping[str, object]) -> Path:
    """Write a Markdown summary for a run."""
    path = out_dir / "summary.md"
    cases = report["cases"]
    assert isinstance(cases, list)
    lines = [
        f"# {str(report['stage'])} Visual QA Run",
        "",
        f"Run id: `{report['run_id']}`",
        "",
        "| Case | Matplotlib | Datoviz |",
        "|---|---|---|",
    ]
    for entry in cases:
        assert isinstance(entry, dict)
        backends = entry["backends"]
        assert isinstance(backends, dict)
        matplotlib_status = _backend_status(backends, "matplotlib")
        datoviz_status = _backend_status(backends, DATOVIZ_BACKEND_ID)
        lines.append(
            f"| `{entry['case_id']}` | {matplotlib_status} | {datoviz_status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _backend_status(backends: Mapping[str, object], backend_id: str) -> str:
    entry = backends.get(backend_id)
    if not isinstance(entry, dict):
        return "not-run"
    status = entry.get("status")
    return str(status)


def _scene_json(scene: VisualQAScene) -> dict[str, object]:
    return {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.scene",
        "case_id": scene.case_id,
        "axis_guides": [_axis_guide_json(guide) for guide in scene.axis_guides],
        "panel_text_guides": [
            _panel_text_guide_json(guide) for guide in scene.panel_text_guides
        ],
        "color_scales": [_color_scale_json(scale) for scale in scene.color_scales],
        "colorbar_guides": [
            _colorbar_guide_json(guide) for guide in scene.colorbar_guides
        ],
        "transform_resources": [
            _transform_resource_json(transform)
            for transform in scene.transform_resources
        ],
        "views": [_view2d_json(view) for view in scene.views],
        "visuals": [_visual_json(visual) for visual in scene.visuals],
        "arrays": {
            name: {
                "path": f"{case_slug(scene.case_id)}.arrays.npz",
                "key": name,
                "shape": list(array.shape),
                "dtype": str(array.dtype),
            }
            for name, array in scene.arrays.items()
        },
    }


def _visual_json(visual: ProtocolVisual) -> dict[str, Any]:
    if isinstance(visual, PointVisual):
        sizes = visual.sizes
        size_shape: list[int] = (
            list(sizes.shape) if isinstance(sizes, np.ndarray) else []
        )
        payload: dict[str, Any] = {
            "family": "point",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "sizes": {
                "shape": size_shape,
                "dtype": str(sizes.dtype) if isinstance(sizes, np.ndarray) else "float",
            },
        }
        if visual.colors is not None:
            payload["colors"] = {
                "shape": list(visual.colors.shape),
                "dtype": str(visual.colors.dtype),
            }
        if visual.color_encoding is not None:
            payload["color_encoding"] = _scalar_color_encoding_json(
                visual.color_encoding
            )
        _add_transform_json(payload, visual.transform)
        return payload
    if isinstance(visual, MarkerVisual):
        sizes = visual.sizes
        size_shape = list(sizes.shape) if isinstance(sizes, np.ndarray) else []
        angle = visual.angle
        angle_shape = list(angle.shape) if isinstance(angle, np.ndarray) else []
        shape = visual.shape
        payload = {
            "family": "marker",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "shape": [value.value for value in shape]
            if isinstance(shape, tuple)
            else shape.value,
            "sizes": {
                "shape": size_shape,
                "dtype": str(sizes.dtype) if isinstance(sizes, np.ndarray) else "float",
            },
            "angle": {
                "shape": angle_shape,
                "dtype": str(angle.dtype) if isinstance(angle, np.ndarray) else "float",
            },
            "stroke_color": {
                "shape": list(visual.stroke_color.shape),
                "dtype": str(visual.stroke_color.dtype),
            },
            "stroke_width": visual.stroke_width,
        }
        if visual.fill_colors is not None:
            payload["fill_colors"] = {
                "shape": list(visual.fill_colors.shape),
                "dtype": str(visual.fill_colors.dtype),
            }
        if visual.fill_color_encoding is not None:
            payload["fill_color_encoding"] = _scalar_color_encoding_json(
                visual.fill_color_encoding
            )
        _add_transform_json(payload, visual.transform)
        return payload
    if isinstance(visual, SegmentVisual):
        widths = visual.widths
        width_shape = list(widths.shape) if isinstance(widths, np.ndarray) else []
        payload = {
            "family": "segment",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "start_positions": {
                "shape": list(visual.start_positions.shape),
                "dtype": str(visual.start_positions.dtype),
            },
            "end_positions": {
                "shape": list(visual.end_positions.shape),
                "dtype": str(visual.end_positions.dtype),
            },
            "colors": {
                "shape": list(visual.colors.shape),
                "dtype": str(visual.colors.dtype),
            },
            "widths": {
                "shape": width_shape,
                "dtype": str(widths.dtype)
                if isinstance(widths, np.ndarray)
                else "float",
            },
            "cap": visual.cap.value,
        }
        _add_transform_json(payload, visual.transform)
        return payload
    if isinstance(visual, PathVisual):
        widths = visual.widths
        width_shape = list(widths.shape) if isinstance(widths, np.ndarray) else []
        payload = {
            "family": "path",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "path_lengths": list(visual.path_lengths),
            "colors": {
                "shape": list(visual.colors.shape),
                "dtype": str(visual.colors.dtype),
            },
            "widths": {
                "shape": width_shape,
                "dtype": str(widths.dtype)
                if isinstance(widths, np.ndarray)
                else "float",
            },
            "cap": visual.cap.value,
            "join": visual.join.value,
            "miter_limit": visual.miter_limit,
        }
        _add_transform_json(payload, visual.transform)
        return payload

    if isinstance(visual, TextVisual):
        font_size = visual.font_size_px
        font_size_shape = (
            list(font_size.shape) if isinstance(font_size, np.ndarray) else []
        )
        rotation = visual.rotation_rad
        rotation_shape = (
            list(rotation.shape) if isinstance(rotation, np.ndarray) else []
        )
        payload = {
            "family": "text",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "texts": list(visual.texts),
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "rgba": {
                "shape": list(visual.rgba.shape),
                "dtype": str(visual.rgba.dtype),
            },
            "font_size_px": {
                "shape": font_size_shape,
                "dtype": str(font_size.dtype)
                if isinstance(font_size, np.ndarray)
                else "float",
            },
            "font_role": visual.font_role.value,
            "anchor_x": [value.value for value in visual.anchor_x]
            if isinstance(visual.anchor_x, tuple)
            else visual.anchor_x.value,
            "anchor_y": [value.value for value in visual.anchor_y]
            if isinstance(visual.anchor_y, tuple)
            else visual.anchor_y.value,
            "rotation_rad": {
                "shape": rotation_shape,
                "dtype": str(rotation.dtype)
                if isinstance(rotation, np.ndarray)
                else "float",
            },
            "z_order": visual.z_order,
        }
        _add_transform_json(payload, visual.transform)
        return payload
    if isinstance(visual, MeshVisual):
        payload = {
            "family": "mesh",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "positions": {
                "shape": list(visual.positions.shape),
                "dtype": str(visual.positions.dtype),
            },
            "faces": {
                "shape": list(visual.faces.shape),
                "dtype": str(visual.faces.dtype),
            },
            "color_mode": visual.resolved_color_mode().value,
            "normal_mode": visual.resolved_normal_mode().value,
            "normal_generation": visual.normal_generation.value,
            "shading": visual.shading.value,
            "face_culling": visual.face_culling.value,
            "depth_test": visual.depth_test.value,
            "depth_write": visual.depth_write.value,
            "order": visual.order,
            "opacity_policy": visual.opacity_policy.value,
        }
        if visual.color is not None:
            payload["color"] = {
                "shape": list(visual.color.shape),
                "dtype": str(visual.color.dtype),
            }
        if visual.face_color_encoding is not None:
            payload["face_color_encoding"] = _scalar_color_encoding_json(
                visual.face_color_encoding
            )
        _add_transform_json(payload, visual.transform)
        return payload

    if isinstance(visual, ImageVisual):
        return {
            "family": "image",
            "id": visual.id,
            "coordinate_space": visual.coordinate_space.value,
            "image": {
                "shape": list(visual.image.shape),
                "dtype": str(visual.image.dtype),
            },
            "extent": list(visual.extent),
            "interpolation": visual.interpolation.value,
            "origin": visual.origin.value,
            "colormap": visual.colormap.value if visual.colormap is not None else None,
            "clim": list(visual.clim) if visual.clim is not None else None,
            "color_scale_id": visual.color_scale_id,
        }
    raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _add_transform_json(
    payload: dict[str, Any], binding: VisualTransformBinding | None
) -> None:
    if binding is not None:
        payload["transform"] = _transform_binding_json(binding)


def _transform_resource_json(
    transform: AffineTransform2DResource,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": transform.id,
        "kind": transform.kind.value,
        "matrix": np.asarray(transform.matrix, dtype=np.float64).tolist(),
        "label": transform.label,
    }
    if transform.metadata is not None:
        payload["metadata"] = transform.metadata
    return payload


def _transform_binding_json(binding: VisualTransformBinding) -> dict[str, object]:
    if binding.ref is not None:
        return {"ref": _transform_ref_json(binding.ref)}
    assert binding.inline is not None
    return {"inline": _inline_affine_json(binding.inline)}


def _transform_ref_json(ref: TransformRef) -> dict[str, object]:
    return {"id": ref.id, "required": ref.required}


def _inline_affine_json(transform: InlineAffineTransform2D) -> dict[str, object]:
    return {
        "kind": transform.kind.value,
        "matrix": np.asarray(transform.matrix, dtype=np.float64).tolist(),
    }


def _view2d_json(view: View2D) -> dict[str, object]:
    return {
        "id": view.id,
        "panel_id": view.panel_id,
        "kind": view.kind.value,
        "x_range": list(view.x_range),
        "y_range": list(view.y_range),
        "aspect_policy": view.aspect_policy.value,
        "clip": view.clip,
    }


def _axis_guide_json(guide: AxisGuide) -> dict[str, object]:
    return {
        "id": guide.id,
        "view_id": guide.view_id,
        "dimension": guide.dimension.value,
        "side": guide.side.value,
        "visible": guide.visible,
        "label_text": guide.label_text,
        "spine_visible": guide.spine_visible,
        "grid_visible": guide.grid_visible,
        "tick_spec": {
            "kind": guide.tick_spec.kind.value,
            "explicit_values": list(guide.tick_spec.explicit_values),
            "explicit_labels": list(guide.tick_spec.explicit_labels)
            if guide.tick_spec.explicit_labels is not None
            else None,
            "target_count": guide.tick_spec.target_count,
        },
        "query_policy": guide.query_policy.value,
        "style": {
            "axis_label_font_size_px": guide.style.axis_label_font_size_px,
            "tick_label_font_size_px": guide.style.tick_label_font_size_px,
            "tick_length_px": guide.style.tick_length_px,
            "tick_width_px": guide.style.tick_width_px,
            "tick_label_padding_px": guide.style.tick_label_padding_px,
            "axis_label_padding_px": guide.style.axis_label_padding_px,
            "grid_width_px": guide.style.grid_width_px,
            "guide_margin_px": guide.style.guide_margin_px,
        },
    }


def _panel_text_guide_json(guide: PanelTextGuide) -> dict[str, object]:
    return {
        "id": guide.id,
        "panel_id": guide.panel_id,
        "role": guide.role.value,
        "text": guide.text,
        "query_policy": guide.query_policy.value,
        "style": {
            "title_font_size_px": guide.style.title_font_size_px,
            "guide_margin_px": guide.style.guide_margin_px,
        },
    }


def _color_scale_json(scale: ColorScale) -> dict[str, object]:
    return {
        "id": scale.id,
        "colormap": {
            "id": scale.colormap.id.value,
            "kind": scale.colormap.kind.value,
        },
        "normalize": {
            "kind": scale.normalize.kind.value,
            "vmin": scale.normalize.vmin,
            "vmax": scale.normalize.vmax,
            "clip": scale.normalize.clip,
        },
        "description": scale.description,
    }


def _colorbar_guide_json(guide: ColorbarGuide) -> dict[str, object]:
    return {
        "id": guide.id,
        "panel_id": guide.panel_id,
        "color_scale_id": guide.color_scale_id,
        "linked_visual_ids": list(guide.linked_visual_ids),
        "orientation": guide.orientation.value,
        "placement": guide.placement.value if guide.placement is not None else None,
        "label": guide.label,
        "ticks": list(guide.ticks),
        "tick_labels": list(guide.tick_labels)
        if guide.tick_labels is not None
        else None,
    }


def _scalar_color_encoding_json(
    encoding: ScalarColorEncoding,
) -> dict[str, object]:
    return {
        "slot": encoding.slot.value,
        "values": {
            "shape": list(encoding.values.shape),
            "dtype": str(encoding.values.dtype),
        },
        "color_scale_id": encoding.color_scale_id,
        "alpha": encoding.alpha,
        "domain": encoding.domain.value if encoding.domain is not None else None,
    }
