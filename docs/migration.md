---
description: "Adopting t-strings in a project that already has gettext catalogs: what survives untouched, what goes fuzzy, and how to move one call site at a time."
---

# Migration

If your project already uses gettext, the questions that decide whether this
library is adoptable are narrow ones: does it invalidate the catalogs you
have, can it coexist with the code you are not ready to change, and how much
of the move has to happen at once. The answers, shortest first:

| Question | Answer |
| --- | --- |
| Do existing `.po` and `.mo` files still work? | Yes. Same files, same tools. |
| Can old and new calls live in one file? | Yes, and one extractor mapping covers both. |
| Does the msgid change? | Not from `.format()`. Yes from `%`-format. |
| Must the whole project move at once? | No. One call site is a valid change. |
| What about Jinja, Django templates, JavaScript? | Untouched, same catalogs. |

The rest of this page is the detail behind each of those.

## From `.format()`: the msgid does not change

This is the case where migration costs almost nothing. A `str.format` message
and a t-string message derive the *same* catalog key, because the key is the
text with `{name}` left in it either way:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

So the existing translation stays attached. Starting from a catalog holding

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

change the call, re-extract, and update:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

The entry that comes back differs in two lines of metadata and nothing else —
a marker comment identifying it as a t-string message, and a source line
number:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

No `fuzzy` flag, no re-translation, in any language. The message renders
immediately:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` will report the catalogs as out of date"

    That marker comment and the moved line numbers are enough for
    `pybabel update --check` to say a catalog needs regenerating, because it
    compares the whole entry and not only the translation. Run the real
    `pybabel update` in the same commit as the code change, and commit the
    catalogs with it — the same habit the
    [CI gate](workflow.md#what-ci-gates) already asks for.

## From `%`-format: the msgid changes, so translations go fuzzy

Printf syntax lives *inside* the message, so replacing it rewrites the catalog
key. There is no way around that, and it is the honest cost of leaving
`%(name)s` behind:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` recognizes the new message as a close relative of the removed
one and carries the old translation across, marked fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Three things to know about that state:

- **Nothing breaks at runtime.** Fuzzy entries are excluded from the compiled
  `.mo`, so the application renders the source message until a human confirms
  the pair — [the same degradation](workflow.md#the-cycle-after-the-first-translation)
  any reworded message goes through.
- **`pybabel compile` reports each one**, because the carried-over `%(name)s`
  is not a valid brace placeholder, and exits non-zero. That list is your work
  queue, not a false alarm; the entries in it genuinely need editing.
- **The old `python-format` flag rides along** and should be deleted with the
  `fuzzy` flag, or `msgfmt --check-format` will keep applying printf rules to
  a brace-format message.

For named printf placeholders the edit is mechanical — `%(name)s` becomes
`{name}` and nothing else moves — so a large catalog is a scripted pass
followed by a translator's review, rather than a re-translation. Positional
`%s` is not mechanical: it has no name to carry over, and choosing one is the
point of the change.

Because of this, the practical order is to migrate `%`-format messages
deliberately — a module, a release, a language at a time — rather than in one
sweep that turns every catalog red at once.

## Old and new calls coexist

The extractor that reads t-strings also reads ordinary gettext calls, so one
mapping covers a file in mid-migration:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Both messages land in the same template, and only the t-string one carries the
marker comment that turns on this library's extra checking:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

It recognizes `_()`, the four standard gettext names, the `tr()` / `ntr()`
aliases, and the deferred `lazy_gettext()` / `lazy_pgettext()`. A helper of
your own has to be [named in the mapping](extraction.md#registering-your-own-function-names).

At runtime the two styles are equally independent: `gettext.translation()`
returns one translations object, and both `_` and this library's entry points
read from it.

## What does not move

- **Template languages.** Jinja2's `{% trans %}`, Django's template tags, and
  their Babel extractors keep working unchanged and keep feeding the same PO
  catalogs. t-strings are Python syntax; they apply to Python source.
- **Your catalog files.** No format change, no new file, no conversion step.
- **Your translation platform.** The `.po` interchange is identical, and the
  `python-brace-format` flag that a t-string message carries is the same flag
  a `.format()` message carries — so placeholder QA keeps working.
- **Non-Python code.** A JavaScript or C catalog in the same project is
  unaffected.

## A migration checklist

1. Add the `babel` extra where `pybabel` runs, and change the `python` mapping
   in `babel.cfg` to the `gettext_tstrings` method — one mapping then covers
   both styles, and `-k` keeps working for the ordinary calls.
2. Convert `.format()` call sites first. Re-extract, run `pybabel update`, and
   commit the catalogs with the code; expect no fuzzy entries.
3. Convert `%`-format call sites in batches you can get reviewed, rewriting
   the carried-over placeholders and clearing the `fuzzy` and `python-format`
   flags.
4. Fix what the restriction rejects: an interpolation must be a plain name, so
   `t"Hello {user.name}"` becomes a local variable first. This is a call-site
   edit, not a catalog one.
5. Turn on `strict = true` in the extractor mapping once the sweep is done, so
   a message that cannot be extracted fails
   [the build](extraction.md#lenient-locally-strict-in-ci) rather than
   disappearing from the template.
6. Add the runtime check from [In production](workflow.md#what-ci-gates):
   render one message per shipped language through a strict `Translator`.

Steps 2 and 3 are ordinary commits. Nothing in this list needs a flag day.
