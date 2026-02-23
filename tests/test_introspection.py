from pydantic import BaseModel, Field

from richforms.introspection import build_model_schema
from tests.models import Metadata


class ExcludedLeafModel(BaseModel):
    name: str
    revision: int = Field(0, json_schema_extra={"richforms": {"exclude": True}})


class ExcludedSubtreeChild(BaseModel):
    name: str
    email: str


class ExcludedSubtreeModel(BaseModel):
    title: str
    owner: ExcludedSubtreeChild = Field(
        ...,
        json_schema_extra={"richforms": {"exclude": True}},
    )


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


def test_build_model_schema_excludes_leaf_paths_from_prompts() -> None:
    schema = build_model_schema(ExcludedLeafModel)
    paths = {node.path for node in schema.leaf_nodes}

    assert "name" in paths
    assert "revision" not in paths
    assert "revision" in schema.excluded_paths


def test_build_model_schema_excludes_nested_subtree_paths_from_prompts() -> None:
    schema = build_model_schema(ExcludedSubtreeModel)
    paths = {node.path for node in schema.leaf_nodes}

    assert "title" in paths
    assert "owner.name" not in paths
    assert "owner.email" not in paths
    assert schema.excluded_paths == {"owner.name", "owner.email"}
