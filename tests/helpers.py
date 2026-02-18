from __future__ import annotations


class ScriptedInteraction:
    def __init__(self, responses: list[str], confirmations: list[bool] | None = None) -> None:
        self._responses = list(responses)
        self._confirmations = list(confirmations or [])
        self.prompts: list[str] = []
        self.confirm_prompts: list[str] = []

    def ask(self, prompt: str, default: str | None = None) -> str:
        self.prompts.append(prompt)
        if not self._responses:
            raise AssertionError(f"No scripted response available for prompt: {prompt}")
        if self._responses[0] == "__INTERRUPT__":
            self._responses.pop(0)
            raise KeyboardInterrupt
        return self._responses.pop(0)

    def confirm(self, prompt: str, default: bool = True) -> bool:
        self.confirm_prompts.append(prompt)
        if self._confirmations:
            return self._confirmations.pop(0)
        return default
