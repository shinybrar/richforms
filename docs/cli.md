# CLI Guide

## Fill

Create a new model instance interactively:

```bash
richforms fill package.models:Metadata
```

Seed defaults from file and write JSON output:

```bash
richforms fill package.models:Metadata \
  --from-file metadata.json \
  --output metadata.out.json \
  --format json
```

## Edit

Load an existing payload, edit interactively, and write YAML:

```bash
richforms edit package.models:Metadata \
  --from-file metadata.yaml \
  --output metadata.updated.yaml \
  --format yaml
```

## Interaction sample

```text
Path Radar: discovery.title ✓  discovery.source >  discovery.version ✓
Field Card: discovery.source (AnyUrl, required)
Validation Ledger:
  - discovery.source: Input should be a valid URL
```
