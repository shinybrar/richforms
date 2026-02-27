from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt


class Interaction(Protocol):
    def ask(self, prompt: str, default: str | None = None) -> str: ...

    def confirm(self, prompt: str, default: bool = True) -> bool: ...

    def choose(self, prompt: str, *, choices: set[str], default: str = "") -> str: ...


@dataclass(slots=True)
class ThemeTokens:
    ink: str = "white"
    alloy: str = "grey50"
    paper: str = "white"
    probe: str = "cyan"
    caution: str = "yellow"
    fault: str = "red"
    verify: str = "green"


_PROMPT_PREFIX = "[bold cyan]▸[/bold cyan]"


class RichInteraction:
    def __init__(self, console: Console) -> None:
        self.console = console

    def ask(self, prompt: str, default: str | None = None) -> str:
        value = Prompt.ask(f"{_PROMPT_PREFIX} {prompt}", default=default, console=self.console)
        return value if value is not None else ""

    def confirm(self, prompt: str, default: bool = True) -> bool:
        return Confirm.ask(f"{_PROMPT_PREFIX} {prompt}", default=default, console=self.console)

    def choose(self, prompt: str, *, choices: set[str], default: str = "") -> str:
        allowed = {choice.lower() for choice in choices}
        if not self.console.is_terminal:
            response = self.ask(prompt, default=default)
            normalized = response.strip().lower()
            return normalized or default

        while True:
            self.console.print(f"{_PROMPT_PREFIX} {prompt}", end="")
            key = click.getchar()
            self.console.print()
            if key in {"\x03", "\x04"}:
                raise KeyboardInterrupt
            if key in {"\r", "\n"}:
                return default
            normalized = key.strip().lower()
            if normalized in allowed:
                return normalized
            options = ", ".join(sorted(allowed))
            self.console.print(f"[red]Choose one of: {options}, or press Enter.[/red]")


@dataclass(slots=True)
class FormConfig:
    interaction: Interaction | None = None
    console: Console | None = None
    theme: ThemeTokens = field(default_factory=ThemeTokens)
    confirm_before_return: bool = True
    save_draft_on_interrupt: Literal["prompt", "always", "never"] = "prompt"
    draft_directory: Path | None = None
    interrupt_message_style: str = "yellow"
    clear_on_step: bool = True
