from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from rich.console import Console
from rich.prompt import Confirm, Prompt


class Interaction(Protocol):
    def ask(self, prompt: str, default: str | None = None) -> str: ...

    def confirm(self, prompt: str, default: bool = True) -> bool: ...


@dataclass(slots=True)
class ThemeTokens:
    ink: str = "white"
    alloy: str = "grey50"
    paper: str = "white"
    probe: str = "cyan"
    caution: str = "yellow"
    fault: str = "red"
    verify: str = "green"


class RichInteraction:
    def __init__(self, console: Console) -> None:
        self.console = console

    def ask(self, prompt: str, default: str | None = None) -> str:
        value = Prompt.ask(prompt, default=default, console=self.console)
        return value if value is not None else ""

    def confirm(self, prompt: str, default: bool = True) -> bool:
        return Confirm.ask(prompt, default=default, console=self.console)


@dataclass(slots=True)
class FormConfig:
    interaction: Interaction | None = None
    console: Console | None = None
    theme: ThemeTokens = field(default_factory=ThemeTokens)
    confirm_before_return: bool = True
    save_draft_on_interrupt: Literal["prompt", "always", "never"] = "prompt"
    draft_directory: Path | None = None
    interrupt_message_style: str = "yellow"
