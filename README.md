# gettext-tstrings

Safe gettext integration for Python 3.14+ t-strings, with first-class
[Babel](https://babel.pocoo.org/) extraction and validation.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

The catalog receives the complete sentence `Hello {name}`. A translation may
reorder or repeat `{name}`, while the runtime rejects missing, unknown, or
modified placeholders.

## Why

Python t-strings preserve the static text, evaluated values, source expressions,
conversions, and format specifications separately. That makes them a useful
boundary for internationalization, but gettext and Babel do not define how a
t-string becomes a catalog message.

`gettext-tstrings` makes one deliberately narrow choice:

- translate complete messages, never sentence fragments;
- accept only simple variable names such as `{name}`;
- keep `!r` and `:.2f` formatting under application control;
- let translators reorder and repeat known placeholders, but not execute
  attribute access or add formatting behavior;
- reuse normal POT, PO, and MO files.

## Install

```console
python -m pip install gettext-tstrings
```

Python 3.14 or newer is required.

## Pythonic runtime API

The recommended API mirrors gettext's class-based usage. Bind a standard
translation object once and use the callable processor as `_`:

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation(
    "messages",
    localedir="locales",
    languages=["ja"],
)

_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))

n = 3
print(_.ngettext(t"One file", t"{n} files", n))

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))
```

The module-level API follows the standard library names and positional-only
calling convention:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext(
    "inbox",
    t"One message",
    t"{n} messages",
    n,
    translations=translations,
)
```

`tr` and `ntr` are exact aliases of `gettext` and `ngettext`. When an explicit
translation object is omitted, module-level functions use the standard
library's globally installed gettext functions.

Plural branches may expose different values. This common form is valid:

```python
ngettext(t"One file", t"{n} files", n)
```

Fields present in both source branches are required in every translated plural
form. A field present in only one branch is available but optional, allowing a
language's plural rules to differ from the source language.

Conversions and format specs stay outside the catalog:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")
# msgid: "Total: {amount}"
```

## Extract with Babel

Create `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Then use the normal Babel workflow:

```console
pybabel extract -F babel.cfg -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

The `gettext_tstrings` extractor also extracts ordinary `_()`, `gettext()`,
and `ngettext()` calls, so one mapping can cover mixed codebases.

The extractor recognizes `_()`, the four standard gettext names, and the
`tr()` / `ntr()` aliases. Additional aliases can be configured:

```ini
[gettext_tstrings: **.py]
tr_functions = tr, translate
ntr_functions = ntr, pluralize
gettext_functions = gettext, _
ngettext_functions = ngettext
pgettext_functions = pgettext
npgettext_functions = npgettext
```

All `Translator` methods are recognized regardless of the variable name.
Callable processors named `_` are recognized by default; add another callable
variable name to `gettext_functions` if needed.

Translator comments work as usual:

```python
# Translators: Product name shown in the account header.
tr(t"Welcome, {product_name}")
```

Every extracted t-string message carries an automatic `gettext-tstrings`
comment. The installed Babel checker uses that marker to reject incompatible
placeholders and translation-controlled formatting during catalog validation
and compilation.

## Performance

The runtime separates static structure from dynamic values as intended by
PEP 750:

- template plans are cached by static strings, expressions, conversions, and
  format specifications;
- translated brace patterns are parsed and validated once;
- both caches are bounded and never retain interpolated values;
- each distinct value is formatted at most once per render, even when a
  translation repeats its placeholder;
- one-field and constant messages use specialized rendering paths.

Run the reproducible microbenchmark on your target interpreter and hardware:

```console
uv run python benchmarks/runtime.py
```

## Safety and scope

This is valid:

```python
tr(t"Hello {name}")
```

These are intentionally rejected:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # function call
```

Compute a meaningful value first:

```python
name = user.display_name()
tr(t"Hello {name}")
```

This restriction produces stable catalog keys, gives translators useful names,
and prevents translated strings from becoming an expression language.

## Status

The project is an alpha. Its core contract is small on purpose. Before a stable
release it will add broader language fixtures, sustained performance tracking,
API review from gettext/Babel users, and compatibility testing against every
supported Python and Babel release.
