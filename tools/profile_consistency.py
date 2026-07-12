"""Validate GSP 0.2 implementation profiles and generate their public matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "profiles"
MATRIX = ROOT / "mkdocs_source" / "support" / "feature-matrix.md"
STATUSES = {"strict", "adapted", "partial", "unsupported", "blocked", "not-assessed"}
PROFILE_FILES = (
    PROFILE_DIR / "gsp-vispy2-0.2.json",
    PROFILE_DIR / "matplotlib-0.2.json",
    PROFILE_DIR / "datoviz-v0.4-0.2.json",
)


def load_profiles() -> list[dict[str, Any]]:
    """Load profiles in the stable public column order."""
    return [json.loads(path.read_text(encoding="utf-8")) for path in PROFILE_FILES]


def validate() -> list[str]:
    """Return profile consistency errors without changing files."""
    errors: list[str] = []
    seen_profiles: set[str] = set()
    for path, profile in zip(PROFILE_FILES, load_profiles(), strict=True):
        for field in ("schema", "profile_id", "kind", "protocol_version", "implementation", "features"):
            if field not in profile:
                errors.append(f"{path.name}: missing {field}")
        if profile.get("schema") != "gsp.profile@0.2" or profile.get("protocol_version") != "0.2":
            errors.append(f"{path.name}: unsupported schema or protocol version")
        profile_id = profile.get("profile_id")
        if not isinstance(profile_id, str) or profile_id in seen_profiles:
            errors.append(f"{path.name}: invalid or duplicate profile_id")
        else:
            seen_profiles.add(profile_id)
        seen_features: set[str] = set()
        for feature in profile.get("features", []):
            feature_id = feature.get("id")
            if not isinstance(feature_id, str) or feature_id in seen_features:
                errors.append(f"{path.name}: invalid or duplicate feature id {feature_id!r}")
            else:
                seen_features.add(feature_id)
            if feature.get("status") not in STATUSES:
                errors.append(f"{path.name}: invalid status for {feature_id!r}")
            if not isinstance(feature.get("scope"), str) or not feature["scope"].strip():
                errors.append(f"{path.name}: empty scope for {feature_id!r}")
            evidence = feature.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{path.name}: missing evidence for {feature_id!r}")
                continue
            for item in evidence:
                if not isinstance(item, str) or not (ROOT / item.split("::", 1)[0]).exists():
                    errors.append(f"{path.name}: missing evidence {item!r} for {feature_id!r}")
    expected = render_matrix(load_profiles())
    if not MATRIX.exists() or MATRIX.read_text(encoding="utf-8") != expected:
        errors.append("public feature matrix is stale; run tools/profile_consistency.py --write")
    return errors


def render_matrix(profiles: list[dict[str, Any]]) -> str:
    """Render a lossless reader-oriented view of every profile feature claim."""
    rows = [
        "# Feature matrix",
        "",
        "This page is generated from the versioned implementation profiles in `profiles/`. Statuses",
        "describe only the stated scope; runtime capability discovery remains authoritative for a",
        "specific process, binding, and device.",
        "",
        "| Implementation | Feature | Status | Exact scope | Limitations |",
        "|---|---|---|---|---|",
    ]
    for profile in profiles:
        for feature in profile["features"]:
            limitations = "; ".join(feature.get("limitations", ())) or "—"
            rows.append(
                f"| `{profile['profile_id']}` | `{feature['id']}` | **{feature['status']}** | "
                f"{_cell(feature['scope'])} | {_cell(limitations)} |"
            )
    rows.extend(
        [
            "",
            "## Status meanings",
            "",
            "- **strict**: the stated scope implements the normative contract without a semantic adapter.",
            "- **adapted**: the outcome is conforming within scope, but an explicit adaptation is involved.",
            "- **partial**: only the written subset is implemented; inspect limitations and runtime capabilities.",
            "- **unsupported**: the implementation rejects the feature explicitly.",
            "- **blocked**: implementation or promotion awaits named evidence; it is not a capability claim.",
            "- **not-assessed**: no conformance claim has been made.",
            "",
            "See the [backend profile interpretation rules](../specification/backend-profiles.md) and",
            "[capability contract](../specification/capabilities.md).",
            "",
        ]
    )
    return "\n".join(rows)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        MATRIX.write_text(render_matrix(load_profiles()), encoding="utf-8")
    errors = validate()
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
