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
        _validate_extension_id(self.id)
        _validate_extension_version(self.version)
        if not self.title:
            raise ValueError("extension title must not be empty")
        if self.fallback_policy not in ("reject", "simplify", "deactivate"):
            raise ValueError("fallback_policy must be reject, simplify, or deactivate")
        if self.diagnostics_policy != "explicit":
            raise ValueError("v0.1 extension diagnostics_policy must be explicit")
        for requirement in self.requires + self.optional:
            if not requirement:
                raise ValueError("extension requirements must not be empty")
        for backend, status in self.implementations.items():
            if not backend:
                raise ValueError("extension implementation backend must not be empty")
            if status not in ("reference", "native", "adapted", "experimental", "unsupported"):
                raise ValueError("extension implementation status is invalid")
        if self.query_contract is not None:
            payload = self.query_contract.get("payload")
            if payload is not None and (not isinstance(payload, str) or not payload.startswith(f"{self.capability}.query")):
                raise ValueError("extension query payload must be namespaced by extension capability")

    @property
    def capability(self) -> str:
        """Return the capability string advertised by renderers for this manifest."""
        return extension_capability(self.id, self.version)


TILED_IMAGE_EXTENSION_ID = "gsp.tiled-image"
TILED_IMAGE_EXTENSION_VERSION = "0.1"
TILED_IMAGE_EXTENSION_CAPABILITY = "gsp.tiled-image@0.1"
TILED_IMAGE_QUERY_PAYLOAD_KIND = f"{TILED_IMAGE_EXTENSION_CAPABILITY}.query"


def extension_capability(extension_id: str, version: str) -> str:
    """Return the canonical extension capability string."""
    _validate_extension_id(extension_id)
    _validate_extension_version(version)
    return f"{extension_id}@{version}"


def validate_extension_manifest(manifest: ExtensionManifest) -> ExtensionManifest:
    """Return a static manifest after running v0.1 validation.

    This helper is intentionally side-effect free: it does not import modules, discover plugins, or
    execute extension code.
    """
    from .security import validate_static_manifest_security

    if manifest.capability != extension_capability(manifest.id, manifest.version):
        raise ValueError("extension capability mismatch")
    security = validate_static_manifest_security(manifest)
    if not security.accepted:
        diagnostic = security.diagnostics[0]
        raise ValueError(f"{diagnostic.code.value}: {diagnostic.message}")
    return manifest


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


def _validate_extension_id(extension_id: str) -> None:
    if not extension_id:
        raise ValueError("extension id must not be empty")
    segments = extension_id.split(".")
    if len(segments) < 2 or any(not _valid_extension_segment(segment) for segment in segments):
        raise ValueError("extension id must be dot-separated lowercase name segments")


def _validate_extension_version(version: str) -> None:
    if not version:
        raise ValueError("extension version must not be empty")
    parts = version.split(".")
    if not parts or any(not part.isdigit() for part in parts):
        raise ValueError("extension version must be numeric dot-separated components")


def _valid_extension_segment(segment: str) -> bool:
    if not segment:
        return False
    return all(character.islower() or character.isdigit() or character == "-" for character in segment)
