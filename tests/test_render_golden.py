from pathlib import Path

from rich.console import Console

from richforms.introspection import build_model_schema
from richforms.render import render_field_card, render_path_radar, render_validation_ledger
from tests.models import Metadata


def _strip_trailing(text: str) -> str:
    """Strip trailing whitespace from each line for stable comparison."""
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def _render_text(renderable) -> str:
    console = Console(record=True, width=120)
    console.print(renderable)
    return _strip_trailing(console.export_text())


def _golden(name: str) -> str:
    raw = (Path(__file__).parent / "golden" / f"{name}.txt").read_text(encoding="utf-8")
    return _strip_trailing(raw)


def test_field_card_golden() -> None:
    schema = build_model_schema(Metadata)
    node = schema.by_path["discovery.title"]
    output = _render_text(render_field_card(node=node, index=1, total=3, current_path=node.path))
    assert output == _golden("field_card")


def test_path_radar_golden() -> None:
    schema = build_model_schema(Metadata)
    output = _render_text(
        render_path_radar(
            schema.leaf_nodes[:4],
            current_path="discovery.source",
            completed_paths={"discovery.title"},
            error_paths={"discovery.source"},
        )
    )
    assert output == _golden("path_radar")


def test_validation_ledger_golden() -> None:
    output = _render_text(
        render_validation_ledger(
            {
                "discovery.source": "Input should be a valid URL",
                "discovery.domain": "List should have at least 1 item after validation",
            }
        )
    )
    assert output == _golden("validation_ledger")
