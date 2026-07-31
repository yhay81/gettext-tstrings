---
description: "The runtime API: which entry point to use, binding a catalog, per-request languages, deferred strings, locale-aware values, and how a broken translation is reported."
---

# Guide

This page is the runtime reference: everything your *application code* does
with this library once catalogs exist. If you have not yet seen the full loop
— mark, extract, translate, compile, run — the [tutorial](tutorial.md) walks
it once in five minutes; creating and validating catalogs is covered in
[Extraction](extraction.md), and how a team keeps the loop turning — update
cycles, CI, translation platforms — is [In production](workflow.md).

## Which entry point should I use?

The package exports several ways to translate a message because applications
bind a language in several different ways. Pick by how your program decides
what language it is in:

| Your situation | Use |
| --- | --- |
| One language for the whole process — a CLI, a desktop app, a script | `Translator`, called as `_` |
| One language per request or per async task — a web application | `use_translations()` around the work, then `tr()` |
| A message defined at import time — a form label, an enum, a constant | `lazy_gettext()` or `lazy_pgettext()` |
| A count decides the wording | `ngettext()` / `npgettext()`, in whichever form above |
| Rendering a pattern with no catalog involved | `compile_template()` |

Everything below is those five, in that order.

## Binding a catalog

The recommended shape mirrors gettext's class-based usage: bind a standard
translation object once and use the callable processor as `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

The module-level functions follow the standard library's names and its
positional-only calling convention:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` and `ntr` are exact aliases of `gettext` and `ngettext`.

## Per-request language

A web framework picks a language per request. Bind the request's translations to
the current context and every module-level call resolves to that language, safely
across concurrent requests:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` binds without a `with` block, for frameworks
that manage the request lifecycle themselves; `get_translations()` reads the
current binding. An explicit `translations=` argument always wins over the
context, and an unbound context falls back to the standard library's globally
installed gettext functions. Worked examples for Flask and ASGI middleware
are on the [In production](workflow.md#binding-a-language-at-runtime) page.

## Deferred translation

A t-string captures its values eagerly, which is wrong for a string defined at
import time — a form label, an enum value, a module constant — that has to render
in whatever language is active when it is *used*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

A `LazyString` renders through `str()`, `format()`, and f-strings, and compares
equal to its rendered text.

!!! note "Deliberately unhashable"

    A `LazyString`'s text depends on the active language, so a hash would change
    across a language switch and quietly corrupt any set or dict holding it.
    Call `str()` first if you need a key.

`strict` is decided where the message is written, not where it renders:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

A deferred string renders wherever it is finally used — inside a template, a
form, a log line — and that place rarely knows whether this is a test run or
production. Passing `strict=True` at the definition is what lets the same
[loud-in-CI, lenient-in-production](#what-happens-when-a-catalog-is-wrong)
choice apply to a string that is not rendered at its call site.

Plural forms depend on a runtime count, so render those eagerly with `ngettext`
where the count is known.

## Several languages at once

One request often needs more than one language: a page rendered for the reader
that also queues a notification to an account set to a different one, or a
digest that quotes each participant in their own. Bindings nest, and leaving
the inner block restores the outer one.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Over a list of recipients, deferred strings do the work: the message is written
once, at import, and renders once per language.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

The binding is a `ContextVar`, not a stack held on a shared object, so requests
that overlap cannot pick up each other's language — including the case where
they *leave* their blocks in the order they entered them, which is the
interleaving a pushdown stack gets wrong. Loading a catalog per language is
cheap: `gettext.translation()` parses each `.mo` once and hands out copies that
share the parsed catalog.

!!! warning "Whether a worker thread inherits the binding depends on the build"

    A bare `threading.Thread`, or `ThreadPoolExecutor.submit`, starts either
    from a copy of the caller's context or from an empty one, and which of
    those is `sys.flags.thread_inherit_context` — true by default on
    free-threaded builds, false everywhere else. The same code therefore
    renders the bound language on 3.14t and the process-global catalog on
    3.14. Pass the context rather than depending on the default:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` already does this for you.

## Locale-aware values

This library decides *where* a value appears in a translated message. It does
not localize the value itself. `{amount:,.2f}` is a Python format spec with
fixed behavior — a comma every three digits and a dot before the decimals — and
it produces the same characters whatever language the message is in:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

German writes that number `1.234,50`, French `1 234,50`, and Hindi groups
`1234567` as `12,34,567` rather than `1,234,567`. Numbers, currencies, dates,
times, and units belong to [Babel][babel-numbers]. Format the value first, then
place the finished string:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

For a counted message the number does two jobs — it selects the plural form and
it appears in the text — and only the second one is localized. Keep the raw
count for the selection and pass the formatted string for display:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatting before the call is also what keeps a format spec out of the catalog:
what a translator sees is a finished piece of text, not a number plus
instructions for rendering it.

## What happens when a catalog is wrong

If a translation's placeholders do not match the source — a missing, unknown, or
reformatted field that slipped past validation, from a hand-edited MO, a vendor
catalog, or a pipeline that skips the checker — the default is to render the
source message rather than raise. This mirrors gettext's own contract that a bad
catalog never breaks the application.

With `Hello {name}` translated as `こんにちは {nombre}`, the render succeeds and
one warning goes to the `gettext_tstrings` logger:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

The warning fires once per message and pattern, not once per render, so a
broken catalog entry does not flood a log.

Opt into failing loudly for tests and CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

The same lookup then raises, carrying the same sentence without the "using source
text" half:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

These messages are written for whoever can act on them, which for a catalog
problem is a translator more often than a programmer — so where a placeholder
looks present but is not, the message explains why rather than repeating that
it is missing. Full-width braces, a doubled `{{name}}`, an invisible no-break
space, a Cyrillic letter among Latin ones: each has its own wording, listed
with examples on
[For translators](translators.md#reading-a-failure-message). That page is
written to be handed to the person editing the `.po`.

## Rendering a pattern without a catalog

`compile_template` exposes the same machinery one level down: it turns a t-string
into its msgid plus a bound set of values, and renders any pattern you hand it.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validates by the same rules and **always raises** on a mismatch. There
is no lenient mode here: leniency exists so a *catalog* lookup can degrade to the
source text, and a pattern you passed in yourself has nothing to degrade from.

## Safety and scope

This is valid:

```python
tr(t"Hello {name}")
```

These are rejected on purpose:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Compute a meaningful value first:

```python
name = user.display_name()
tr(t"Hello {name}")
```

The restriction produces stable catalog keys, gives translators useful names, and
keeps a translated string from becoming an expression language.

The guarantee is scoped to *structure and formatting*: a translation is never
evaluated, and can never add attribute access, calls, conversions, or format
specs. Two things stay the caller's responsibility, exactly as with stdlib
gettext — **escaping** rendered output for its sink (HTML, shell, terminal), and
**catalog integrity**, since a hostile catalog can repeat a placeholder to
amplify output size, which is inherent to any placeholder-based i18n.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
