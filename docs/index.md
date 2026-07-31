---
description: "Translate complete t-string messages through gettext and Babel, with the values and the formatting kept out of the catalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Translate whole messages,<br>not string fragments.

`gettext-tstrings` connects Python 3.14+ t-strings to standard gettext
catalogs and Babel tooling. Values and formatting stay in application code;
the catalog holds a complete message with simple `{name}` placeholders:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Start the tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Compare the alternatives](comparison.md){ .md-button }

Alpha · Python 3.14+ · ordinary PO/MO catalogs · no runtime dependencies
{ .home-facts }

This site practices what it documents: every language edition —
navigation, labels, and the plural-aware build report — is rendered from PO
catalogs by
[`gettext-tstrings` itself](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Is this for you?

**A fit today when** your application runs on Python 3.14 or newer; you
already use gettext and Babel, or want to adopt their PO/MO workflow; and you
want t-string syntax with named placeholders that are checked before they
render.

**Not yet a fit when** you need Python 3.13 or older; you require a stable
Python API — this is an alpha, and the [specification](spec.md) is the part of
it that has settled; or nearly all of your translatable text lives in a
template language rather than in Python source.

Already have catalogs? They keep working. `_("Hello {name}").format(name=name)`
and `tr(t"Hello {name}")` produce the same msgid, so existing translations
survive the switch — [Migration](migration.md) walks the whole move.

## What the catalog may say

The catalog receives the complete message `Hello {name}`. A translation may
reorder or repeat `{name}`, and may rewrite every other word around it. It may
not drop the placeholder, invent a new one, reach through it into your objects,
or attach formatting of its own.

That is the whole promise: **a translation cannot change the structure of the
message it translates.** The library checks it on the way in — when catalogs
are compiled — and again at render time; a broken entry that reaches production
anyway logs a warning and renders the source message instead of crashing.

!!! note "New to gettext? The whole workflow in four sentences"

    **gettext** is the standard way software gets translated, in Python and
    far beyond. Your code marks translatable messages; an *extractor* collects
    them into a template file (`.pot`); a translator — usually not a
    programmer — fills in one catalog file (`.po`) per language, which is
    compiled to a binary `.mo` that your application loads at runtime. The
    conventional name for the translate function is `_`, so `_(t"Hello {name}")`
    reads as "translate this message". The **[tutorial](tutorial.md)** walks
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

## The design rules

- Translate complete messages, never sentence fragments.
- Accept only simple variable names such as `{name}`.
- Keep `!r` and `:.2f` under application control, out of the catalog.
- Allow translations to reorder and repeat known placeholders, while
  preventing them from reaching attributes or adding formatting.
- Reuse ordinary POT, PO, and MO files, and the tools that already read them.

And the matching list of what it deliberately leaves alone: it does not
localize numbers, currencies, or dates — [format those first](guide.md#locale-aware-values),
with Babel; it does not escape rendered output for HTML, a shell, or a
terminal; and it cannot judge whether a translation is *correct*, only whether
its placeholders are intact.

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

**Start here** — no gettext experience assumed:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — an empty directory to a running Japanese
  translation in five steps, every command shown with its output.
- **[Why t-strings](comparison.md)** — the same message written four ways, and
  what `%(name)s`, `.format()`, and `$`-strings each hand to the catalog.

</div>

**Use it** — the working references:

<div class="grid cards" markdown>

- **[Guide](guide.md)** — the runtime API: which entry point to use, plurals,
  per-request languages, deferred strings, and what happens when a catalog is
  wrong.
- **[Extraction](extraction.md)** — the `pybabel` reference: configuration,
  custom function names, and how existing tools validate these catalogs for
  free.
- **[In production](workflow.md)** — the loop as a team runs it: the update
  cycle, fuzzy entries, CI gates, translation platforms, and shipping.
- **[Migration](migration.md)** — adopting this in a project that already has
  catalogs, one call site at a time.
- **[For translators](translators.md)** — one page to hand to whoever edits
  the `.po` files.

</div>

**Understand it** — from history to implementation:

<div class="grid cards" markdown>

- **[Background](background.md)** — why this library exists: thirty years of
  gettext, two PEPs, and the stdlib discussion that closed without an answer.
- **[Pitfalls](pitfalls.md)** — what translating this site into thirty-five
  languages actually broke, and which half a tool can catch.
- **[How it works](internals.md)** — from PEP 750's template object to the
  rendered string, and the caches that make the checking cheap.

</div>

**Reference** — the contracts:

<div class="grid cards" markdown>

- **[API](api.md)** — everything the package exports, on one page.
- **[Specification](spec.md)** — the t-string ↔ msgid convention as a stable,
  versioned contract, with a machine-readable conformance suite.

</div>

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
