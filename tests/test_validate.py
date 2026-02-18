from richforms.validate import validate_draft
from tests.models import Metadata


def test_validate_draft_returns_error_map_for_nested_fields() -> None:
    draft = {
        "discovery": {
            "title": "Image",
            "description": "Desc",
            "source": "not-a-url",
            "version": "1.0.0",
            "created": "2024-01-01T00:00:00Z",
            "domain": [],
            "kind": ["headless"],
        }
    }

    result = validate_draft(Metadata, draft)

    assert result.model is None
    assert "discovery.source" in result.errors
    assert "discovery.domain" in result.errors
