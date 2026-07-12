"""Tests for the GSP 0.2 specification traceability registry."""

from __future__ import annotations

import json

from tools import spec_traceability


def test_source_inventory_matches_repository() -> None:
    actual = json.loads(
        spec_traceability.SOURCE_INVENTORY.read_text(encoding="utf-8")
    )
    assert actual == spec_traceability.build_source_inventory()


def test_every_detailed_spec_has_a_migration_destination() -> None:
    inventory = spec_traceability.build_source_inventory()
    detailed = [
        source
        for source in inventory["sources"]
        if source["classification"] == "detailed-normative-source"
    ]
    assert detailed
    assert all(source["disposition"] == "migration-required" for source in detailed)
    assert all(source["destination"].startswith("spec/current/") for source in detailed)


def test_registry_validation_is_clean() -> None:
    assert spec_traceability.validate() == []
