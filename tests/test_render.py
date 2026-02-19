from rich.console import Console

from richforms.introspection import build_model_schema
from richforms.render import render_editor_view, render_field_card, render_path_radar
from tests.models import Manifest, Metadata


def test_render_field_card_includes_metadata() -> None:
    schema = build_model_schema(Metadata)
    node = schema.by_path["discovery.title"]
    console = Console(record=True, width=120)

    panel = render_field_card(node=node, index=1, total=3, current_path=node.path)
    console.print(panel)
    output = console.export_text()

    assert "discovery.title" in output
    assert "Type" in output
    assert "Required" in output
    assert "Human-readable title of the image." in output


def test_render_field_card_uses_human_field_label_and_optional_hint() -> None:
    schema = build_model_schema(Manifest)
    node = schema.by_path["maintainers"]
    console = Console(record=True, width=120)

    panel = render_field_card(node=node, index=1, total=2, current_path="manifest.maintainers")
    console.print(panel)
    output = console.export_text()

    assert "manifest.maintainers" in output
    assert "Field" in output
    assert "Maintainers" in output


def test_render_field_card_shows_optional_skip_hint() -> None:
    schema = build_model_schema(Manifest)
    node = schema.by_path["version"]
    console = Console(record=True, width=120)

    panel = render_field_card(node=node, index=1, total=2, current_path="manifest.version")
    console.print(panel)
    output = console.export_text()

    assert "Press Enter to skip." in output


def test_render_path_radar_shows_active_arrow_and_required_optional_markers() -> None:
    schema = build_model_schema(Manifest)
    console = Console(record=True, width=120)
    panel = render_path_radar(
        schema.leaf_nodes,
        current_path="maintainers",
        completed_paths={"version"},
        error_paths=set(),
    )
    console.print(panel)
    output = console.export_text()

    assert "→" in output
    assert "version" in output
    assert "maintainers" in output


def test_render_editor_view_includes_waypoint_strip_and_field_dossier() -> None:
    schema = build_model_schema(Metadata)
    node = schema.by_path["discovery.title"]
    console = Console(record=True, width=140)
    panel = render_editor_view(
        nodes=schema.leaf_nodes,
        node=node,
        index=1,
        total=3,
        current_path=node.path,
        completed_paths={"discovery.source"},
        error_paths=set(),
    )
    console.print(panel)
    output = console.export_text()

    assert "Waypoint Tree" in output
    assert "Field Dossier" in output
    assert "Type" in output
    assert "current" in output


def test_render_field_card_shows_examples_heading() -> None:
    schema = build_model_schema(Metadata)
    node = schema.by_path["discovery.domain"]
    console = Console(record=True, width=120)
    panel = render_field_card(node=node, index=1, total=3, current_path=node.path)
    console.print(panel)
    output = console.export_text()

    assert "Examples" in output
