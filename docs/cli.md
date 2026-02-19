# CLI Guide

## Fill

Create a new model instance interactively:

```bash
richforms fill richforms.example.model:Family
```

Seed defaults from file and write JSON output:

```bash
richforms fill richforms.example.model:Family \
  --from-file metadata.json \
  --output metadata.out.json \
  --format json
```

## Edit

Load an existing payload, edit interactively, and write YAML:

```bash
richforms edit richforms.example.model:Family \
  --from-file metadata.yaml \
  --output metadata.updated.yaml \
  --format yaml
```

## Live redraw mode

Interactive terminals now default to live in-place cockpit rendering.

Use `--no-live` to force static transcript output, or `--live` to force live mode.
Use `--clear/--no-clear` to control static redraw behavior.

Example forcing live mode:

```bash
richforms fill richforms.example.model:Family --live --clear
```

## Interaction sample

```text
Waypoint Tree: discovery.title ✓  discovery.source >  discovery.version ✓
Legend: → current  ✓ done  ! error  · pending  ● required  ○ optional
Field Dossier: discovery.source (AnyUrl, required)
Validation Logbook:
  - discovery.source: Input should be a valid URL
```
