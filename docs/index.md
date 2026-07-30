---
description: "Translate complete t-string messages through gettext and Babel, with the formatting kept out of the catalog."
---

# gettext-tstrings

Safe gettext and Babel integration for Python 3.14+ t-strings.

Write the sentence once, in your source language, with the value in place:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

The catalog receives the complete sentence `Hello {name}`. A translation may
reorder or repeat `{name}`; it may not drop it, invent one, or attach
formatting of its own — this library checks that, and a broken catalog falls
back to the source text instead of crashing.

!!! note "New to gettext? The whole workflow in four sentences"

    **gettext** is the standard way software gets translated, in Python and
    far beyond. Your code marks translatable strings; an *extractor* collects
    them into a template file (`.pot`); a translator — usually not a
    programmer — fills in one catalog file (`.po`) per language, which is
    compiled to a binary `.mo` that your application loads at runtime. The
    conventional name for the translate function is `_`, so `_(t"Hello {name}")`
    reads as "translate this sentence". The **[tutorial](tutorial.md)** walks
    the entire path — mark, extract, translate, compile, run — in about five
    minutes.

## The problem it solves

An f-string is already interpolated by the time any library sees it —
`f"Hello {name}"` has become `"Hello Ada"`, and translating the fragments
around a value breaks the grammar of most languages. A t-string ([PEP 750])
keeps the static text, the evaluated values, the source expressions, the
conversions, and the format specs separate — which is exactly the split a
message catalog needs.
[What that changes](comparison.md), compared to `%(name)s`, `.format()`, and
`$`-strings.

Nothing in gettext or Babel says how a t-string becomes a message, though. This
library makes that choice, writes it down as a [versioned specification](spec.md),
and ships the [conformance suite](spec.md#conformance) to check it.

## The choice it makes

- Translate complete messages, never sentence fragments.
- Accept only simple variable names such as `{name}`.
- Keep `!r` and `:.2f` under application control, out of the catalog.
- Let translators reorder and repeat known placeholders — but not call
  attributes, and not add formatting behaviour.
- Reuse ordinary POT, PO, and MO files, and the tools that already read them.

## Install

```console
python -m pip install gettext-tstrings
```

Python 3.14 or newer. **Rendering has no dependencies** — it uses the standard
library's `gettext` and nothing else.

Extraction and catalog validation run through [Babel], so install that extra
wherever `pybabel` runs, which is usually a development or CI environment rather
than a production image:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Where to go next

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — start here: an empty directory to a running
  Japanese translation in five steps, every command shown with its output.
- **[Why t-strings](comparison.md)** — the same message written four ways, and
  what `%(name)s`, `.format()`, and `$`-strings each hand to the catalog.
- **[Guide](guide.md)** — the runtime API: plurals, per-request languages,
  deferred strings, and what happens when a catalog is wrong.
- **[Extraction](extraction.md)** — the `pybabel` reference: configuration,
  custom function names, and how existing tools validate these catalogs for
  free.
- **[Specification](spec.md)** — the t-string ↔ msgid convention as a stable,
  versioned contract, with a machine-readable conformance suite.
- **[API](api.md)** — everything the package exports, on one page.

</div>

## Dogfooded by this site

This documentation is not just a translated demo. Its navigation, theme
labels, copyright line, and plural-aware build report are rendered from PO
catalogs by `gettext-tstrings` itself. The
[multilingual builder](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
exercises contextual messages, named placeholders, and the plural rules of all
ten languages on every strict build.

## Status

An alpha. The contract is small on purpose and the [specification](spec.md) is
the stable part of it; the Python API may still move. Before a stable release
this needs broader language fixtures, sustained performance tracking, API review
from people who use gettext and Babel in earnest, and compatibility testing
across every supported Python and Babel release.

[Issues and pull requests](https://github.com/yhay81/gettext-tstrings/issues) are
welcome — an alpha is exactly when the interface is still worth arguing about.

## Join the community

- Pick a
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  for a bounded contribution.
- Ask usage questions in
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Bring production gettext workflows and API ideas to
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Read the
  [contribution guide](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  before opening a pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
