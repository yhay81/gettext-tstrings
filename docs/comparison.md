---
description: "The same translatable message written with %-format, .format(), flufl.i18n $-strings, and a t-string, compared on translator mistakes, catalog authority, and integration cost."
---

# Why t-strings

Four ways to put a value into a translatable message, compared on the same
message. All four name their placeholders and let a translator reorder them;
they differ in what happens when a translation is wrong, in how much of your
program the catalog can reach, and in what adopting them costs.

The tables come first, so you can find the row you care about and read only
the section behind it.

!!! note "Three parties touch every translated message"

    A **catalog** is the file of translations — `.po` while humans edit it,
    compiled to `.mo` for the application to load (the [tutorial](tutorial.md)
    walks through both). Three parties touch every message: the **developer**
    writes the source string, a **translator** edits the catalog — often on an
    external platform, far from any code review — and the **application**
    renders the two together at runtime. Each formatting style below answers
    the same question differently: *how much of the format language does the
    catalog get to control?* In the examples, `_` is the conventional name for
    the translate function, and `tr` is this library's.

## Side by side

**When a translator makes a mistake.** A catalog travels through many hands,
and most of what goes wrong in it is accidental:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| A translation *drops* a placeholder — what renders? | the value silently disappears | the value silently disappears | the value silently disappears | the source message, with a warning ([by default](guide.md#what-happens-when-a-catalog-is-wrong)) |
| A translation *adds* an unknown placeholder — what renders? | an exception | an exception | the placeholder stays visible as text | the source message, with a warning ([by default](guide.md#what-happens-when-a-catalog-is-wrong)) |
| A translation *reformats* a placeholder — what renders? | what the catalog asked for, or an exception if the type letter no longer fits the value | what the catalog asked for | not expressible in `$`-strings | the source message, with a warning |
| Are placeholders checked at render time? | no | no | no | yes (see below) |

**What authority the catalog has.** A translation is data from outside your
repository, and each style hands it a different amount of power:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Where do values come from? | an explicit mapping | explicit arguments | the caller's local and global variables, plus optional `extras` | the values captured inside the t-string |
| Can the catalog change how a value is formatted? | yes | yes | no | no |
| Can the catalog reach into objects (attribute access)? | no | yes | yes, with dotted names | no |
| Where does "the current language" live? | wherever the application puts it | wherever the application puts it | a stack of language codes on the shared application object | a `ContextVar`, per task or request |

**What it costs to integrate.** Everything above is free if the tooling fits;
this is where it might not:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Minimum Python | any | any | 3.10 | **3.14** |
| Maturity | standard library | standard library | stable release | **alpha** |
| Uses ordinary PO/MO catalogs? | yes | yes | yes | yes |
| Needs a custom source extractor? | no | no | no | yes, currently |
| Which PO flag does Babel infer, for existing tools to validate? | `python-format` | `python-brace-format` | none | `python-brace-format` |

On the render-time check: singular messages are checked for an exact
placeholder match. Plural messages are checked too, against the
[union/intersection rule](spec.md) that lets a target language's plural forms
differ from the source's; the stricter per-form check runs when catalogs are
compiled ([Extraction](extraction.md)).

The format-flag row is about placeholder-aware validation, not catalog
compatibility. `none` means standard gettext tools still read and compile the
message, but `msgfmt --check-format` has no `$`-placeholder grammar to apply.

## Compatibility and maturity

The last table's first two rows are the ones that decide adoption, so they are
worth stating plainly rather than as cells.

`%`-format and `.format()` are built into Python and need no dependency at all.
[`flufl.i18n`][flufl-i18n] is a mature package, released and in production use,
that runs on Python 3.10 and later. `gettext-tstrings` is an **alpha** and
requires **Python 3.14 or newer**, because t-strings are new syntax in 3.14 —
there is no back-port and there cannot be one. Its [specification](spec.md) is
the stable part of it; the Python API may still move before 1.0.

What none of them costs is catalog compatibility. All four produce ordinary
POT/PO/MO files that every PO editor, translation platform, and GNU gettext
tool already reads, so the choice below is reversible in a way that changing
catalog *formats* would not be. [Migration](migration.md) covers moving an
existing project.

The sections below show each trade-off in detail, one method at a time.

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

What can go wrong: one deleted letter in a translation crashes the render.

The catalog string carries printf syntax, including a trailing type letter —
the `s` in `%(name)s` — that is easy to overlook and easy to damage:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

A one-character edit in a PO editor becomes a runtime exception unless catalog
validation catches it first. GNU `msgfmt --check-format` does catch this one,
but only for messages flagged `python-format`, and only if the catalog actually
passes through msgfmt on its way to your application.

## str.format

```python
_("Hello {name}").format(name=name)
```

It removes the trailing type letter while keeping a named, freely reorderable
placeholder. What can go wrong moves to the other side of the exchange: the
translation gains power over your objects.

`str.format` is a small expression language, and calling it on a string means
handing that string the right to use it:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Now replace those literal strings with whatever `_()` returns. If a
translation of `Hello {name}` comes back as `{conf.api_key}`, rendering it
prints your API key — the catalog, not your code, decided what got read. A
catalog is not code, but it travels like data: out to a translation platform,
through several hands, back as a `.po`, compiled into a `.mo`, sometimes
vendored from outside your project entirely. `.format()` gives every step of
that trip attribute access on the objects you pass in.

## `$`-strings and flufl.i18n

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

The standard library's [`string.Template`][stdlib-template] supplies the
`$name` interpolation language, but is not itself a translation API.
[`flufl.i18n`][flufl-i18n] combines that style with gettext catalog lookup.
Notice that the value is never passed in: flufl.i18n builds the substitution
namespace from the caller's globals and locals — whatever variables exist at
the call site are available to the message. An optional `extras` mapping takes
precedence over both. Its translator-facing syntax has no trailing type letter
or format specifier, and placeholders remain freely reorderable.

An unavailable substitution does not raise. With `name = "Ada"` and no
`nombre` in the caller's namespace, a catalog translation of `Hello $nombre`
renders as `Hello $nombre`: the unresolved placeholder stays visible. That
[documented behavior] preserves the rest of the translated message instead of
failing the call. Exceptions raised while resolving an attribute or converting
a value can still propagate.

`flufl.i18n` is more capable than a bare `string.Template` in one relevant
way. Its [custom Template] accepts dotted placeholders such as
`$settings.api_key`, and its [translator] resolves those paths against the
caller's values. A translated placeholder may name any available caller local
or global and, with dotted syntax, traverse its attributes. That is convenient
when a message needs an attribute, while also making the caller's frame part
of the catalog's substitution namespace. The comparison here describes
`flufl.i18n` 6.0.0, not every possible use of `string.Template`.

It also answers a question the other two formatting styles leave entirely to
the application: *which* language is current, and how to change it. An
[application object] keeps a stack of languages, `_.push(code)` and `_.pop()`
move it, `with _.using(code):` nests, and a [strategy] finds the catalog for a
language code so the application never handles catalog objects itself. A server
that has to produce text in more than one language during a single unit of work
— a page for the reader, a notification for someone whose account is set
differently — is the case this exists for.

The stack lives on that application object, which the whole process shares. Two
overlapping requests therefore share one stack, and blocks that are not
strictly nested *in time* hand each other the wrong language:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

This library keeps the same capability — bindings nest and unwind the same way
— in a `ContextVar` instead of a shared stack, so the interleaving above
resolves per task. The equivalents are on
[Several languages at once](guide.md#several-languages-at-once). What it does
not supply is the language-code-to-catalog lookup: you pass a translations
object, which for the common case is one `gettext.translation()` call, and the
standard library caches the parsed catalog.

## t-strings

```python
tr(t"Hello {name}")
```

The catalog still sees `Hello {name}` and remains an ordinary PO/MO catalog.
The difference is what a translation is *allowed to say*, and who checks it.

This library validates every translation against the source message's
placeholders before rendering, and it accepts bare names and nothing else.
Against `t"Hello {name}"`:

| A translation containing | is rejected with |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Rejected does not mean crashed: by default the library logs a warning and
renders the source message, so a bad catalog never takes the application down —
[the same contract gettext itself keeps](guide.md#what-happens-when-a-catalog-is-wrong).

Formatting stays where it was written, in the code:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` never reaches the catalog, so no translation can change it, and no
translator has to look at it. It is a *fixed* format, though, not a localized
one — choosing digits and separators per language is
[Babel's job, before the call](guide.md#locale-aware-values).

One more difference is tooling: t-strings are new syntax, so extracting them
into a `.pot` currently requires a t-string-aware extractor, such as the one
this package [provides for Babel](extraction.md).

## The cost of the restriction

Beyond the Python requirement, the price of all this is one rule: an
interpolation has to be a plain name.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

That is a real constraint, and it is the same constraint that produces the
guarantees above. Together with source-side value binding and runtime
placeholder checking, it prevents catalog strings from evaluating expressions
and keeps placeholder names meaningful to the person translating them.

An f-string cannot be used this way at all — by the time any library sees one
it is already a finished string, so translating it means translating a
fragment. t-strings ([PEP 750]) keep the static text and the values separate
while keeping f-string-like syntax and explicit value binding.

How Python arrived at this crossroads — two PEPs ten years apart, and the
stdlib discussion that closed without an answer — is told with sources on
[Background](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
