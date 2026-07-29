---
description: "The same translatable message written with %-format, .format() and a t-string, and what each one lets a catalog control."
---

# Why t-strings

Every way of putting a value into a translatable message has to answer the same
question: *how much of the format language does the catalog get to control?*
The three answers below differ mostly in that.

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

The catalog string carries printf syntax, and the part a translator is most
likely to damage is the least meaningful-looking part of it — the trailing
letter that says how to render the value:

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

Better in every way a translator cares about: the placeholder is named, nothing
trails it to be lost, and reordering is free.

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

## t-strings

```python
tr(t"Hello {name}")
```

The msgid is still `Hello {name}`, so the catalog and the tooling are unchanged.
What changes is that the translation is no longer a format string. It is checked
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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| Placeholder is named | yes | yes | yes |
| Translator can reorder | yes | yes | yes |
| A dropped character breaks it | **yes** | no | no |
| Catalog controls formatting | yes | yes | **no** |
| Catalog can reach attributes | no | **yes** | **no** |
| Broken catalog raises at render | **yes** | **yes** | no, [by default](guide.md#what-happens-when-a-catalog-is-wrong) |
| Works with PO/MO and `msgfmt` | yes | yes | yes |

## What it costs

An f-string cannot be used this way at all — by the time any library sees one it
is already a finished string, so translating it means translating a fragment.
t-strings ([PEP 750]) are what make the split possible, which is why Python 3.14
is the floor.

The other cost is the restriction itself: an interpolation has to be a plain
name.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

That is a real constraint, and it is the one that buys everything above. It also
gives translators a name that means something instead of an expression they
cannot read.

  [PEP 750]: https://peps.python.org/pep-0750/
