"""Structured protocol diagnostics shared by commands, planning, and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .ids import validate_id


class DiagnosticSeverity(str, Enum):
    """Severity of a structured GSP diagnostic."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class DiagnosticCategory(str, Enum):
    """Stable top-level diagnostic category."""

    VALIDATION = "validation"
    CAPABILITY = "capability"
    ADAPTATION = "adaptation"
    STALE = "stale"
    EXECUTION = "execution"
    SECURITY = "security"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Machine-readable protocol diagnostic.

    Applications branch on ``code`` and typed ``data`` rather than parsing ``message``.
    """

    code: str
    severity: DiagnosticSeverity
    category: DiagnosticCategory
    message: str
    operation_id: str | None = None
    entity_id: str | None = None
    feature_id: str | None = None
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code or any(character.isspace() for character in self.code):
            raise ValueError("diagnostic code must be non-empty and contain no whitespace")
        if not isinstance(self.severity, DiagnosticSeverity):
            raise TypeError("severity must be a DiagnosticSeverity")
        if not isinstance(self.category, DiagnosticCategory):
            raise TypeError("category must be a DiagnosticCategory")
        if not self.message:
            raise ValueError("diagnostic message must not be empty")
        for value in (self.operation_id, self.entity_id):
            if value is not None:
                validate_id(value)
        if self.feature_id is not None and not self.feature_id:
            raise ValueError("feature_id must not be empty")
