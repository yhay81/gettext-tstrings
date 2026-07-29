# Contributing

Thanks for helping improve `gettext-tstrings`. The project is deliberately small:
it is the connection convention between Python t-strings and gettext, not a new
i18n framework. Changes are judged against that scope.

## The convention comes first

[SPEC.md](SPEC.md) defines the t-string→msgid derivation and the translation
validation rules as a versioned contract. Any change to how a msgid is derived,
or to which translations are accepted or rejected, is a change to the spec:
update `SPEC.md` in the same pull request and explain why the version does or
does not need to increment.

## Development

The project uses [uv](https://docs.astral.sh/uv/) and requires Python 3.14+.

```console
uv sync
uv run ruff format .
uv run ruff check .
uv run mypy
uv run ty check
uv run pytest --cov=gettext_tstrings --cov-report=term-missing
```

All of these must pass, matching CI. New behavior needs tests, and behavior that
touches the spec needs tests that read like executable examples of the rule.

### The documentation site

<https://gettext-tstrings.yhay81.com/> is built from `docs/` with
[Zensical](https://zensical.org/):

```console
uv run --group docs zensical serve
```

`tests/test_docs.py` ties the failure messages the pages quote back to the ones
the library raises, so rewording a message fails the suite until the page is
updated with it. Quote output; do not paraphrase it.

## Guidelines

- **Keep it narrow.** Prefer the simplest change that closes a concrete gap
  backed by a real failure, test, or user need. New configuration, layers, or
  branches need a strong justification.
- **Never evaluate a translation.** The safety guarantee — no evaluation, no
  attribute access, no calls, no translation-side formatting — is the core of
  the project. Code that renders catalog data must go through the existing
  validated path.
- **Match the surrounding code.** Everything written down here — docstrings,
  comments, documentation, commit messages — is in English. A comment says why a
  line exists, not what it does.
- **gettext parity.** The public API mirrors stdlib gettext naming and calling
  conventions; new surface should extend that, not diverge from it.
