from pathlib import Path

from richforms.serializers import serialize_result
from tests.models import Discovery


def _build_discovery() -> Discovery:
    return Discovery.model_validate(
        {
            "title": "Example",
            "description": "Example discovery",
            "source": "https://example.com/repo",
            "version": "1.0.0",
            "created": "2024-01-01T00:00:00Z",
            "domain": ["astronomy"],
            "kind": ["headless"],
        }
    )


def test_serialize_result_json_returns_string() -> None:
    model = _build_discovery()
    output = serialize_result(model, format="json")
    assert output is not None
    assert '"title": "Example"' in output


def test_serialize_result_writes_json_file(tmp_path: Path) -> None:
    model = _build_discovery()
    out_file = tmp_path / "metadata.json"

    result = serialize_result(model, format="json", path=out_file)

    assert result is None
    text = out_file.read_text()
    assert '"version": "1.0.0"' in text


def test_serialize_result_yaml_returns_string() -> None:
    model = _build_discovery()
    output = serialize_result(model, format="yaml")
    assert output is not None
    assert "title: Example" in output
