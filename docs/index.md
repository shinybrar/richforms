---
hide:
  - toc
---

# `richforms`

Turn Pydantic data models into interactive terminal forms.

---

<div class="grid cards" markdown>

-   🚀 [**Get Started**](getting-started.md)

    ---

    Install `richforms`, define a model, and run your first form.

-  💻 [**Use the CLI**](cli.md)

    ---

    Use `richforms` to collect and update forms from the terminal.

-   🐍 [**Embed in Python**](python-api.md)

    ---

    Call `fill`, `edit`, and `collect_dict` directly in your tools.

-  🪤 [**Integrate with frameworks**](integrations.md)

    ---

    Plug into existing Click and Typer command options.

</div>

## What richforms gives you

You get consistent input flows across all workflows with minimal custom code.

- **Schema-first forms:** Use your existing Pydantic models as the source of
  truth.
- **Repair loops:** Re-prompt only fields that fail model validation.
- **Typed prompting:** Show required state, defaults, type hints, and choices.
- **Flexible output:** Keep values in memory or write JSON and YAML files.
