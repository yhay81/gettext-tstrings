# Contributing

Thanks for helping improve `gettext-tstrings`. The project is deliberately small:
it is the connection convention between Python t-strings and gettext, not a new
i18n framework. Changes are judged against that scope.

## Find the right place

- Pick a [`good first issue`](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  for a bounded first contribution.
- Use [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)
  for setup help and usage questions.
- Open a bug report when you have a reproducible failure.
- Start an [Ideas Discussion](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)
  before implementing a new API or changing the specification.
- Report security problems privately as described in [SECURITY.md](SECURITY.md).

You do not need permission to work on an unassigned issue. Leave a short comment
so that another contributor does not duplicate the work. If an issue is already
assigned, ask before starting.

## Your first pull request

1. Fork the repository and create a focused branch.
2. Run the development checks below before changing anything.
3. Make the smallest change that satisfies the issue's acceptance criteria.
4. Add or update tests and documentation when behavior changes.
5. Open a draft pull request early if you want feedback.

The pull request template explains the evidence reviewers need. A perfect first
draft is not expected: maintainers will explain requested changes and the reason
behind scope decisions. No contributor license agreement is required.

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

To run only the real-catalog integration tests:

```console
uv run pytest tests/test_gettext_integration.py
```

### The documentation site

<https://gettext-tstrings.yhay81.com/> is built with
[Zensical](https://zensical.org/) in ten languages: English, Japanese,
Simplified Chinese, Spanish, French, German, Brazilian Portuguese, Korean,
Russian, and Arabic. Build the exact site that CI and Cloudflare use:

```console
./scripts/build-docs.sh
uv run python -m http.server --directory site 8000
```

English pages live in `docs/`. Translated pages live in
`i18n/<language>/docs/`, and their navigation and theme strings live in the
adjacent `LC_MESSAGES/site.po`. All languages deliberately keep the same
Markdown filenames and Python examples so the language selector can stay on the
current page and copied examples never drift.

The multilingual builder compiles the PO files and renders each localized
Zensical configuration through `gettext-tstrings` itself. Add or change site
chrome messages in `scripts/build_multilingual_docs.py`, then update every
catalog. The build runs Zensical in strict mode, so broken links and translated
anchors fail before deployment. Its site chrome deliberately exercises
contextual messages, named placeholders, and each language's plural rules;
Arabic also keeps the right-to-left rendering path under test.

`tests/test_docs.py` ties the failure messages the pages quote back to the ones
the library raises, checks that every language has the same pages and Python
examples, and rejects incomplete site catalogs. Rewording a message fails the
suite until every quoted page is updated. Quote output; do not paraphrase it.

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

## Review and recognition

Every contribution is reviewed for correctness, safety, API consistency, and
scope. Reviews discuss the change, never the contributor. Substantial design
changes use an issue or Discussion first so that decisions are visible and can
be challenged.

Contributors are credited through the repository history, release notes, and
GitHub's contributor graph. Repeated contributors who want to take on review or
maintenance work can follow the path described in [GOVERNANCE.md](GOVERNANCE.md).
