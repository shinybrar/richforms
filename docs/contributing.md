# Contributing

This project welcomes contributions from open source maintainers and users.
This page explains how to set up a local environment, run quality checks, and
submit changes that are easy to review.

## Development setup

You can create a local development environment with `uv`.

```bash title="install dependencies"
uv sync --dev
```

If you use pre-commit, install hooks to run checks before commits.

```bash title="optional but recommended"
uv run pre-commit install
```

## Run required checks

You must run the full check set before opening a pull request.

```bash title="format and lint"
uv run ruff format --check .
uv run ruff check .
```

```bash title="type checks and tests"
uv run ty check --output-format github .
uv run pytest -q
```

## Work on documentation

You can preview and build the documentation locally while editing pages.

```bash title="serve docs locally"
uv run zensical serve
```

```bash title="build docs"
uv run zensical build
```

!!! note
    Documentation pages are under `/docs`, and site configuration is in
    `zensical.toml`.

## Contribution expectations

Each contribution is easier to merge when it follows these principles.

- Keep pull requests focused on one user-visible change.
- Add or update tests for behavior changes.
- Keep docs in sync with CLI and API behavior.
- Prefer clear commit messages that release-please can classify.

## Pull request checklist

You can use this checklist before requesting review.

1. Confirm checks pass locally.
2. Confirm new behavior is covered by tests.
3. Confirm docs and examples are updated.
4. Confirm breaking changes are called out in the PR description.
