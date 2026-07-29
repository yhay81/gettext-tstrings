---
description: "The runtime API: binding a catalog, per-request languages, deferred strings, and how a broken translation is reported."
---

# Guide

## Binding a catalog

The recommended shape mirrors gettext's class-based usage: bind a standard
translation object once and use the callable processor as `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation(
    "messages", localedir="locales", languages=["ja"]
)
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))

n = 3
print(_.ngettext(t"One file", t"{n} files", n))

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))
```

The module-level functions follow the standard library's names and its
positional-only calling convention:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext(
    "inbox", t"One message", t"{n} messages", n, translations=translations
)
```

`tr` and `ntr` are exact aliases of `gettext` and `ngettext`.

## Per-request language

A web framework picks a language per request. Bind the request's translations to
the current context and every module-level call resolves to that language, safely
across concurrent requests:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` binds without a `with` block, for frameworks
that manage the request lifecycle themselves; `get_translations()` reads the
current binding. An explicit `translations=` argument always wins over the
context, and an unbound context falls back to the standard library's globally
installed gettext functions.

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

Plural forms depend on a runtime count, so render those eagerly with `ngettext`
where the count is known.

## What happens when a catalog is wrong

If a translation's placeholders do not match the source — a missing, unknown, or
reformatted field that slipped past validation, from a hand-edited MO, a vendor
catalog, or a pipeline that skips the checker — the default is to reproduce the
source text rather than raise. This mirrors gettext's own contract that a bad
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

The warning fires once per plan and pattern, not once per render, so a broken
catalog entry does not flood a log.

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

## Reading a failure message

These messages are written for whoever can act on them, which for a catalog
problem is a translator more often than a programmer. Reporting only that
`{name}` is missing is a dead end when the reader can see those characters in
front of them, so where a placeholder looks present but is not, the message says
why. Against the source `Hello {name}`, each of these is reported under
`translation does not match the source placeholders:`

| The translation says | The reason it gives |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Characters that cannot be seen get their own treatment. A no-break space inside
the braces is something an input method produces and no editor shows, so the
message prints it by code point rather than naming a character the reader cannot
find:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

A name whose letters mix writing systems — the homoglyph case, where a Cyrillic
`а` is indistinguishable from a Latin one — is shown twice, once readably and
once escaped, which is the only form that tells the two apart:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

The same disambiguation applies when a Greek or Cyrillic name written entirely
in one script conflicts with an ASCII source name, including the one-letter
Latin `a` / Cyrillic `а` case.

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
