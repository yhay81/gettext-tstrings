# gettext-tstrings

Safe gettext and Babel integration for Python 3.14+ t-strings.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

The catalog receives the complete sentence `Hello {name}`. A translation may
reorder or repeat `{name}`; it may not drop it, invent one, or attach formatting
of its own.

## Why t-strings

An f-string is already interpolated by the time any library sees it, so
translating one means translating a fragment. A t-string ([PEP 750]) keeps the
static text, the evaluated values, the source expressions, the conversions, and
the format specs separate — which is exactly the split a message catalog needs.

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

- **[Guide](guide.md)** — the runtime API, per-request languages, deferred
  strings, and what happens when a catalog is wrong.
- **[Extraction](extraction.md)** — the `pybabel` workflow, configuration, and
  how existing tools end up validating these catalogs for free.
- **[Specification](spec.md)** — the t-string ↔ msgid convention as a stable,
  versioned contract, with a machine-readable conformance suite.
- **[API](api.md)** — everything the package exports.

</div>

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
