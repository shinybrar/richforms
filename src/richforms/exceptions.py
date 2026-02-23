from __future__ import annotations

from collections.abc import Mapping


class RichformsError(Exception):
    """Base error for richforms."""


class SerializationError(RichformsError):
    """Raised when serialization fails."""


class ExcludedFieldResolutionError(RichformsError):
    """Raised when excluded fields fail validation and cannot be prompted."""

    def __init__(self, errors: Mapping[str, str]) -> None:
        self.errors = dict(errors)
        details = "; ".join(f"{path}: {message}" for path, message in sorted(self.errors.items()))
        message = (
            "Excluded fields failed validation and cannot be prompted. "
            "Provide values via initial data or define defaults/default_factory. "
            f"Fields: {details}"
        )
        super().__init__(message)
