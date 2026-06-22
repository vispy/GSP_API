"""Static extension manifest models for the GSP protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ExtensionKind(str, Enum):
    """Extension contract families."""

    VISUAL_FAMILY = "visual-family"
    TRANSFORM = "transform"
    DATA_SOURCE = "data-source"
    FORMAT_DECODER = "format-decoder"
    QUERY_PAYLOAD = "query-payload"
    TRANSPORT = "transport"


class ExtensionSupportLevel(str, Enum):
    """How stable or central an extension contract is."""

    CORE = "core"
    REFERENCE = "reference"
    OPTIONAL = "optional"
    EXPERIMENTAL = "experimental"


@dataclass(frozen=True, slots=True)
class ExtensionManifest:
    """Static v0.1 extension manifest.

    M011 deliberately does not load code from manifests. They are metadata for
    validation, capability advertisement, diagnostics, and fixtures.
    """

    id: str
    version: str
    kind: ExtensionKind
    title: str
    support_level: ExtensionSupportLevel = ExtensionSupportLevel.EXPERIMENTAL
    requires: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    schema: Mapping[str, Any] = field(default_factory=dict)
    implementations: Mapping[str, str] = field(default_factory=dict)
    fallback_policy: str = "reject"
    diagnostics_policy: str = "explicit"
    query_contract: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("extension id must not be empty")
        if not self.version:
            raise ValueError("extension version must not be empty")
        if not self.title:
            raise ValueError("extension title must not be empty")
        if self.fallback_policy not in ("reject", "simplify", "deactivate"):
            raise ValueError("fallback_policy must be reject, simplify, or deactivate")
        if self.diagnostics_policy != "explicit":
            raise ValueError("v0.1 extension diagnostics_policy must be explicit")


TILED_IMAGE_EXTENSION_ID = "gsp.tiled-image"
TILED_IMAGE_EXTENSION_VERSION = "0.1"
TILED_IMAGE_EXTENSION_CAPABILITY = "gsp.tiled-image@0.1"
TILED_IMAGE_QUERY_PAYLOAD_KIND = f"{TILED_IMAGE_EXTENSION_CAPABILITY}.query"


def tiled_image_extension_manifest() -> ExtensionManifest:
    """Return the built-in reference tiled-image extension manifest."""
    return ExtensionManifest(
        id=TILED_IMAGE_EXTENSION_ID,
        version=TILED_IMAGE_EXTENSION_VERSION,
        kind=ExtensionKind.DATA_SOURCE,
        title="GSP tiled image data source",
        support_level=ExtensionSupportLevel.REFERENCE,
        requires=("virtual-data-source",),
        schema={"source_kind": "tiled-image", "credential_policy": "none"},
        implementations={"matplotlib": "reference", "datoviz": "unsupported"},
        query_contract={"payload": TILED_IMAGE_QUERY_PAYLOAD_KIND},
    )
