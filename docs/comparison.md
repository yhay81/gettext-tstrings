---
description: "The same translatable message written with %-format, .format(), flufl.i18n $-strings, and a t-string, including how each one binds values and handles a damaged catalog."
---

# Why t-strings

Every way of putting a value into a translatable message has to answer the same
question: *how much of the format language does the catalog get to control?*
The four answers below also differ in where values come from and what happens
when a catalog changes a placeholder.

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

The catalog string carries printf syntax, including a trailing type letter that
is easy to overlook and can be damaged by a one-character edit:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

A one-character edit in a PO editor becomes a traceback in production. GNU
`msgfmt --check-format` does catch it, but only for messages flagged
`python-format`, and only if the catalog actually passes through msgfmt on its
way to your application.

## str.format

```python
_("Hello {name}").format(name=name)
```

It removes the trailing type letter while keeping a named, freely reorderable
placeholder.

The problem is on the other side. `str.format` is a small expression language,
and calling it on a string means handing that string the right to use it:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

A catalog is not code, but it travels like data — out to a translation platform,
through several hands, back as a `.po`, compiled into a `.mo`, sometimes vendored
from outside your project entirely. `.format()` gives every step of that trip
attribute access on the objects you pass in.

## `$`-strings and flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

The standard library's [`string.Template`][stdlib-template] supplies the `$name`
interpolation language, but is not itself a translation API.
[`flufl.i18n`][flufl-i18n] combines that style with gettext catalog lookup. It
builds the substitution namespace from the caller's globals and locals; an
optional `extras` mapping takes precedence over both. Its translator-facing
syntax has no trailing type letter or format specifier, and placeholders remain
freely reorderable.

An unavailable substitution does not raise. With `name = "Ada"` and no
`nombre` in the caller's namespace, a catalog translation of `Hello $nombre`
renders as `Hello $nombre`: the unresolved placeholder stays visible. That
[documented behavior] preserves the rest of the translated message instead of
failing the call. Exceptions raised while resolving an attribute or converting
a value can still propagate.

`flufl.i18n` is more capable than a bare `string.Template` in one relevant way.
Its [custom Template] accepts dotted placeholders such as `$settings.api_key`,
and its [translator] resolves those paths against the caller's values. A
translated placeholder may name any available caller local or global and, with
dotted syntax, traverse its attributes. That is convenient when a message needs
an attribute, while also making the caller's frame part of the catalog's
substitution namespace. The comparison below describes `flufl.i18n` 6.0.0, not
every possible use of `string.Template`.

## t-strings

```python
tr(t"Hello {name}")
```

The catalog still sees `Hello {name}` and remains an ordinary PO/MO catalog.
Source extraction is different: current tools require a t-string-aware
extractor, such as the one provided by this package. A translation is checked
against the source message's placeholders and rendered by this library, which
accepts bare names and nothing else. Against `t"Hello {name}"`:

| A translation containing | is rejected with |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

The formatting stays where it was written:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` never reaches the catalog, so no translation can change it, and no
translator has to look at it.

## Side by side

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Placeholder is named | yes | yes | yes | yes |
| Translator can reorder | yes | yes | yes | yes |
| Values come from | explicit mapping | explicit arguments | caller's globals and locals, with optional overriding `extras` | the t-string's captured interpolations |
| Catalog controls value conversion / format specifier | yes | yes | no | no |
| Catalog can request attribute access | no | yes | yes, with dotted names | no |
| Source placeholder dropped at render | silently omitted | silently omitted | silently omitted | fully rendered source pattern [by default](guide.md#what-happens-when-a-catalog-is-wrong) |
| Added placeholder unavailable at render | raises | raises | remains visible | fully rendered source pattern [by default](guide.md#what-happens-when-a-catalog-is-wrong) |
| Source placeholder set checked at runtime (singular) | no | no | no | yes |
| PO format flag inferred by Babel for the example | `python-format` | `python-brace-format` | none | `python-brace-format` |
| Uses ordinary PO/MO catalogs | yes | yes | yes | yes |
| Needs a custom source extractor | no | no | no | yes, currently |

The format-flag row is about placeholder-aware validation, not catalog
compatibility. `none` means standard gettext tools still read and compile the
message, but `msgfmt --check-format` has no `$`-placeholder grammar to apply.

## What it costs

An f-string cannot be used this way at all — by the time any library sees one it
is already a finished string, so translating it means translating a fragment.
t-strings ([PEP 750]) provide the split while keeping f-string-like syntax and
binding values explicitly. `$`-strings already provide a concise alternative
with a different binding and failure model. `flufl.i18n` is a mature package
whose current release supports Python 3.10; `gettext-tstrings` is currently an
alpha and native t-strings make Python 3.14 its floor.

The other cost is the restriction itself: an interpolation has to be a plain
name.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

That is a real constraint. Together with source-side value binding and runtime
placeholder checking, it prevents catalog strings from evaluating expressions
and keeps placeholder names meaningful.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
