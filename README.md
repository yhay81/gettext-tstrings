# gettext-tstrings

[![CI](https://github.com/yhay81/gettext-tstrings/actions/workflows/ci.yml/badge.svg)](https://github.com/yhay81/gettext-tstrings/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/gettext-tstrings)](https://pypi.org/project/gettext-tstrings/)
[![Python](https://img.shields.io/pypi/pyversions/gettext-tstrings)](https://pypi.org/project/gettext-tstrings/)
[![License](https://img.shields.io/pypi/l/gettext-tstrings)](https://github.com/yhay81/gettext-tstrings/blob/main/LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/yhay81/gettext-tstrings/badge)](https://scorecard.dev/viewer/?uri=github.com/yhay81/gettext-tstrings)

Safe gettext integration for Python 3.14+ t-strings, with first-class
[Babel](https://babel.pocoo.org/) extraction and validation.

**Documentation:** [English](https://gettext-tstrings.yhay81.com/) ·
[日本語](https://gettext-tstrings.yhay81.com/ja/) ·
[简体中文](https://gettext-tstrings.yhay81.com/zh/) ·
[Español](https://gettext-tstrings.yhay81.com/es/) ·
[Français](https://gettext-tstrings.yhay81.com/fr/) ·
[Deutsch](https://gettext-tstrings.yhay81.com/de/) ·
[Português (Brasil)](https://gettext-tstrings.yhay81.com/pt-br/) ·
[한국어](https://gettext-tstrings.yhay81.com/ko/) ·
[Русский](https://gettext-tstrings.yhay81.com/ru/) ·
[العربية](https://gettext-tstrings.yhay81.com/ar/)

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

Python 3.14 or newer is required. Rendering has **no dependencies** — it uses
the standard library's `gettext` and nothing else.

Extraction and catalog validation run through [Babel](https://babel.pocoo.org/),
so install that extra wherever you run `pybabel` (typically a dev or CI
environment, not your production image):

```console
python -m pip install "gettext-tstrings[babel]"
```

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
translation object is omitted, module-level functions use the translations bound
to the current context (see [Per-request language](#per-request-language)), and
otherwise fall back to the standard library's globally installed gettext
functions.

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

## Per-request language

Web frameworks pick a language per request. Bind the request's translations to
the current context and the module-level functions (and any `_` that calls them)
resolve to that language, safely across concurrent requests:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)  # your gettext.translation(...)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` binds without a `with` block (for frameworks
that manage the request lifecycle themselves), and `get_translations()` reads
the current binding. An explicit `translations=` argument always wins over the
context. A bound `Translator` is the alternative when you prefer to thread one
object through your call sites explicitly.

## Deferred (lazy) translation

A t-string captures its values eagerly, which is wrong for a string defined at
import time — a form label, an enum value, a module constant — that must render
in whatever language is active when it is *used*. `lazy_gettext` defers the
catalog lookup and rendering to first use, resolving the current context:

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

A `LazyString` renders through `str()`, `format()`, and f-strings, and compares
equal to its rendered text. Plural forms depend on a runtime count, so render
those eagerly with `ngettext` where the count is known.

## Broken catalogs never crash a render

If a translation's placeholders do not match the source — a missing, unknown, or
reformatted field slipping past validation (a hand-edited MO, a vendor catalog,
a pipeline that skips the checker) — the default is to reproduce the source text
rather than raise, mirroring gettext's contract that a bad catalog never breaks
the application. A warning is logged on the `gettext_tstrings` logger.

Opt into fail-loud behavior for tests and CI:

```python
_ = Translator(translations, strict=True)  # raises InvalidTranslationError
tr(t"Hello {name}", translations=translations, strict=True)
```

## Rendering a pattern without a catalog

`compile_template` exposes the same machinery one level down: it turns a
t-string into its msgid plus a bound set of values, and renders any pattern you
hand it. Use it when the pattern comes from somewhere other than a gettext
catalog, or to see the msgid a call will produce.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validates its pattern by the same rules and **always raises**
`InvalidTranslationError` on a mismatch. There is no lenient mode here: leniency
exists so that a *catalog* lookup can degrade to the source text, and a pattern
you passed in yourself has nothing to degrade away from.

## Extract with Babel

Extraction needs the `babel` extra (`pip install "gettext-tstrings[babel]"`).
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

The extractor recognizes `_()`, the four standard gettext names, the
`tr()` / `ntr()` aliases, and the deferred `lazy_gettext()` / `lazy_pgettext()`.
Additional aliases can be configured:

```ini
[gettext_tstrings: **.py]
tr_functions = tr, translate
ntr_functions = ntr, pluralize
gettext_functions = gettext, _, lazy_gettext
ngettext_functions = ngettext
pgettext_functions = pgettext, lazy_pgettext
npgettext_functions = npgettext
```

All `Translator` methods are recognized regardless of the variable name.
Callable processors named `_` are recognized by default; add another callable
variable name to `gettext_functions` if needed.

### Registering t-string functions

t-string calls are recognized through the `*_functions` mapping options above,
**not** through Babel's `-k`/`--keyword` flag. A t-string literal cannot be read
by Babel's built-in keyword machinery, so a custom helper such as `mytr(t"...")`
must be listed in `tr_functions` (or the matching option) — `-k mytr` alone will
not extract it. The `-k` flag continues to work for ordinary (non-t-string)
gettext calls, which are extracted alongside.

Only the standard gettext argument order is supported (message first; context
then message for `pgettext`; context, singular, plural for `npgettext`). Wrappers
with non-standard argument positions are not configurable.

### Robust by default

- A t-string the extractor rejects (attribute access, an expression, a wrong
  argument) is **warned about and skipped**; it never aborts extraction of the
  rest of the project. An unparsable file is skipped the same way. Set
  `strict = true` in the mapping to fail the run instead.
- Simple messages extract under **any** keyword set, including
  `pybabel extract --no-default-keywords -k tr`. Plural and contextual messages
  need Babel's canonical keyword specs, so keep `ngettext`, `pgettext`, and
  `npgettext` in the keyword set (the default set already has them); otherwise
  those messages are skipped with a warning.

Translator comments work as usual — pass the tag to `pybabel extract` with
`-c "Translators:"`, exactly as for ordinary gettext calls:

```python
# Translators: Product name shown in the account header.
tr(t"Welcome, {product_name}")
```

Every extracted t-string message carries an automatic `gettext-tstrings`
comment. The installed Babel checker uses that marker to reject incompatible
placeholders and translation-controlled formatting during catalog validation
and compilation.

## Your existing toolchain validates these catalogs

Babel (≥2.18, the declared floor) automatically marks extracted t-string
messages with the standard `python-brace-format` flag:

```po
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

That flag is what standard gettext tooling keys on, so a broken translation is
caught without any extra configuration:

- **GNU msgfmt** (≥0.19) rejects it at compile time — verified against
  gettext-tools, and covered by this project's test suite:

  ```console
  $ msgfmt --check-format -o /dev/null ja.po
  ja.po:24: a format specification for argument 'name' doesn't exist in 'msgstr'
  msgfmt: found 1 fatal error
  ```

- **The Babel checker shipped with this package** applies the stricter t-string
  rules during `pybabel compile`: no translation-side conversions or format
  specs, and the plural required/allowed placeholder sets.

Beyond those two, the flag is a documented PO convention rather than something
this project can vouch for: Weblate documents a [Python brace format
check](https://docs.weblate.org/en/latest/user/checks.html), and the commercial
platforms have their own placeholder QA. Behavior there is theirs, not verified
here.

Note that `msgfmt` only checks placeholder names it can parse as Python brace
format. Sticking to ASCII placeholder names keeps every tool in the chain able
to validate the message.

## Performance

The overhead is sub-microsecond per call: roughly 0.4 µs for a one-field
message on Apple Silicon (including constructing the t-string itself), about
2.5× a plain `gettext(...).format(...)`. That difference buys placeholder
validation, safe rendering, and the structural guarantees above — this library
optimizes for safety per nanosecond, not for beating `str.format`.

The runtime separates static structure from dynamic values as intended by
PEP 750:

- template plans are looked up by the template's static strings with
  per-interpolation verification, so a warm call builds no cache keys;
- translated brace patterns are parsed and validated once, then cached on
  their plan;
- both caches are bounded and never retain interpolated values — with one
  documented exception: a nested format spec (`t"{x:{width}}"`) is evaluated by
  the interpreter before the library sees it, so that evaluated spec is part of
  the cached plan's identity;
- a translation that fails validation is remembered too, so a broken catalog
  entry warns once instead of re-validating on every render;
- each distinct value is formatted at most once per render, even when a
  translation repeats its placeholder;
- constant, one-field, and two-field messages use specialized rendering paths.

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

The safety guarantee is scoped to *structure and formatting*: a translation is
never evaluated, and can never add attribute access, calls, conversions, or
format specs. Two things stay the caller's responsibility, exactly as with
stdlib gettext: **escaping** rendered output for its sink (HTML, shell,
terminal), and **catalog integrity** — a hostile catalog can repeat a
placeholder to amplify output size, which is inherent to any placeholder-based
i18n and is not bounded here.

## Templates and other tools

t-strings are Python syntax, so this library covers Python source. Template
languages (Jinja2, Django templates) keep using their own `{% trans %}` /
`{{ _(...) }}` i18n and Babel's template extractors; both feed the **same** PO
catalog, so one translation workflow covers a mixed codebase.

`pygettext` cannot parse t-strings today, so extraction goes through Babel. The
t-string→msgid convention is written down as a small, versioned contract in
[SPEC.md](SPEC.md) so that other extractors, IDEs, type checkers, or a future
`pygettext` can target it.

## Status

The project is an alpha. Its core contract is small on purpose; the
[specification](SPEC.md) is the stable reference. Before a stable release it will
add broader language fixtures, sustained performance tracking, API review from
gettext/Babel users, and compatibility testing against every supported Python
and Babel release.

## Community

Contributions from gettext users, translators, framework authors, tooling
maintainers, and performance specialists are welcome.

- Start with a
  [`good first issue`](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
- Ask usage questions in
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Propose larger ideas in
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

Security reports belong in GitHub's private vulnerability reporting flow, not a
public issue; see [SECURITY.md](SECURITY.md).
