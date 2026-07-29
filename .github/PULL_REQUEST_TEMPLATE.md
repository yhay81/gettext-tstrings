## What changed

<!-- Describe the smallest complete change. Link an issue with "Closes #123". -->

## Why

<!-- Explain the user problem or interoperability gap this solves. -->

## Evidence

<!-- Tests, benchmark results, catalog output, or screenshots as appropriate. -->

## Checklist

- [ ] The change stays within the t-string ↔ gettext scope.
- [ ] Tests cover new or changed behavior.
- [ ] Documentation and `CHANGELOG.md` are updated when users will notice.
- [ ] `SPEC.md` and the conformance suite are updated if the convention changes.
- [ ] `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy`,
      `uv run ty check`, and `uv run pytest` pass.
