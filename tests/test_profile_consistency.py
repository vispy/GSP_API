"""Checks for versioned GSP implementation profiles."""

from __future__ import annotations

import json
from pathlib import Path

from gsp_datoviz.capabilities import gsp_capability_snapshot_from_datoviz
from gsp_matplotlib.capabilities import capability_snapshot

from tools.profile_consistency import PROFILE_FILES, validate


def test_profiles_and_generated_matrix_are_current() -> None:
    """Every claim has evidence and the public matrix is synchronized."""
    assert validate() == []


def test_renderer_snapshots_identify_their_versioned_profiles() -> None:
    """Runtime discovery points consumers to the matching detailed profile."""
    matplotlib = capability_snapshot()
    datoviz = gsp_capability_snapshot_from_datoviz(None)
    assert matplotlib.metadata["profile_id"] == "gsp.matplotlib@0.2"
    assert datoviz.metadata["profile_id"] == "gsp.datoviz-v0.4@0.2"
    assert matplotlib.protocol_versions == ("0.2",)
    assert datoviz.protocol_versions == ("0.2",)
    assert set(matplotlib.visual_families) == {"point", "marker", "segment", "path", "image", "text", "mesh"}
    assert set(datoviz.visual_families) == set(matplotlib.visual_families)


def test_profile_ids_and_feature_ids_are_unique() -> None:
    """Machine consumers can use profile and feature identifiers as stable keys."""
    profiles = [json.loads(Path(path).read_text(encoding="utf-8")) for path in PROFILE_FILES]
    assert len({profile["profile_id"] for profile in profiles}) == len(profiles)
    for profile in profiles:
        ids = [feature["id"] for feature in profile["features"]]
        assert len(ids) == len(set(ids))
