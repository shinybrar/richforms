# Releasing

`richforms` uses release-please and PyPI Trusted Publishing.

## Workflow

1. Merge conventional commits to `main`.
2. release-please updates or opens a release PR.
3. Merge release PR to create tag + GitHub release.
4. `publish.yml` builds and publishes to PyPI via OIDC.

## Local release validation

```bash
uv build
```

## Configuration files

- `.release-please-config.json`
- `.release-please-manifest.json`
- `.github/workflows/release-please.yml`
- `.github/workflows/publish.yml`
