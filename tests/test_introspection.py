from richforms.introspection import build_model_schema
from tests.models import Metadata


def test_build_model_schema_extracts_leaf_paths_and_metadata() -> None:
    schema = build_model_schema(Metadata)
    paths = {node.path: node for node in schema.leaf_nodes}

    assert "discovery.title" in paths
    assert "discovery.source" in paths
    assert "discovery.keywords" in paths
    assert "discovery.kind" in paths

    source = paths["discovery.source"]
    assert source.required is True
    assert source.description == "URL to get source code for building the image"
    assert source.type_label == "AnyUrl"

    keywords = paths["discovery.keywords"]
    assert keywords.required is False
    assert keywords.examples == ["astronomy", "analysis", "python"]

    deprecated = paths["discovery.deprecated"]
    assert deprecated.required is False
    assert deprecated.default is False


def test_build_model_schema_marks_literal_choices() -> None:
    schema = build_model_schema(Metadata)
    paths = {node.path: node for node in schema.leaf_nodes}
    kind = paths["discovery.kind"]

    assert kind.choices == ["notebook", "headless", "carta", "firefly", "contributed"]
