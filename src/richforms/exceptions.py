class RichformsError(Exception):
    """Base error for richforms."""


class SerializationError(RichformsError):
    """Raised when serialization fails."""
