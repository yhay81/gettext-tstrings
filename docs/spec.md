---
description: "The t-string to msgid convention as a small versioned contract, with a machine-readable conformance suite."
---

# Specification

The convention this library implements is written down as a small, stable
contract so that another implementation — an extractor, an IDE, a type checker,
or a future `pygettext` — can target it and interoperate.

[Read spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## The rules in one screen

**A msgid** is the concatenation, in source order, of the literal segments and
one `{name}` token per interpolation. Literal braces are escaped (`{` becomes
`{{`). A name must be a simple placeholder name — `str.isidentifier()` is true
and it is not a Python keyword. Conversions and format specs are **not** part of
the msgid; they stay under application control.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *rejected — not a simple name* |

**A translation** is valid when it contains only bare `{name}` placeholders,
every required name appears at least once, and no name outside the allowed set
appears. Reordering and repetition are deliberately unconstrained: both can be
grammatically necessary in a target language.

For plurals, *allowed* is the union of the branches' names and *required* is
their intersection — so `t"One file"` against `t"{n} files"` leaves `n` available
to a translator of either form but required of neither, and a target language's
plural rules can differ from the source's.

**An empty msgid** is never looked up, because gettext reserves it for a
catalog's metadata header.

## Conformance

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
is the same document in machine-readable form: cases mapping a t-string's static
structure to a msgid, and a msgid plus a catalog pattern to a rendered string or
a rejection.

An implementation **conforms to spec v1** when it reproduces every case. The
cases name only what the specification defines — derived msgids, accepted and
rejected patterns, rendered output — and never an error message or an exception
type, so an implementation in another language can run them unchanged.

Interpolations are described structurally, never as Python source:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": ["Total: ", {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}],
  "msgid": "Total: {amount}"
}
```

The reference implementation runs the suite as part of its own test suite, so the
prose and the code cannot drift apart in silence.

## Versioning

This is spec v1. A backwards-incompatible change to msgid derivation or to
translation validation increments the version and ships a new
`conformance/vN.json` beside the existing one. Additive clarifications that
change neither derived msgids nor accepted patterns do not.
