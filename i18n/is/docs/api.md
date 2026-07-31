---
description: "Every name gettext_tstrings exports: functions, the Translator, context binding, lazy strings, and the errors."
---

# API

Everything below is exported from `gettext_tstrings`. Nothing else is public.
This page is the signature reference; for worked examples of each function,
see the [guide](guide.md).

## Translating { #translating }

Each function takes its t-string positionally and accepts two keyword arguments:
`translations` (falling back to the context binding, then to the standard
library's global functions) and `strict` (see [Guide](guide.md#what-happens-when-a-catalog-is-wrong)).

| Function | Signature |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias of `gettext` |
| `ntr` | alias of `ngettext` |

### `Translator`

A frozen dataclass binding one translation object, so call sites do not repeat
it.

```python
Translator(translations, strict=False)
```

It is callable (`_(t"…")`) and carries `gettext`, `ngettext`, `pgettext`,
`npgettext`, and the `tr` / `ntr` aliases.

## Context binding { #context-binding }

| Name | Purpose |
| --- | --- |
| `use_translations(translations)` | Bind for the duration of a `with` block, then restore. |
| `set_translations(translations)` | Bind without a block, for framework-managed lifecycles. |
| `get_translations()` | Read the current binding, or `None`. |

The binding is a `ContextVar`, so it is per-context and safe under concurrency.

## Deferred strings { #deferred-strings }

| Name | Purpose |
| --- | --- |
| `lazy_gettext(template, /)` | Defer a translation to first use. |
| `lazy_pgettext(context, template, /)` | The contextual form. |
| `LazyString` | What both return. Renders through `str()` and `format()`, compares equal to its text, and is deliberately unhashable. |

## Lower-level { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compile a t-string, reusing its cached static plan.

### `CompiledTemplate`

| Member | Meaning |
| --- | --- |
| `.msgid` | The stable gettext message identifier. |
| `.placeholders` | Placeholder names in first-occurrence order. |
| `.render(pattern)` | Validate one pattern and render it. **Always raises** on a mismatch. |

## Types and errors { #types-and-errors }

### `Translations`

A `runtime_checkable` `Protocol` for the four standard methods, all
positional-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations`, and Babel's `Translations`
all satisfy it.

### Exceptions

| Class | Raised when |
| --- | --- |
| `TStringError` | Base class for both below. |
| `InvalidTemplateError` | The **source** t-string breaks the convention — a complex interpolation, or a repeated name with different formatting. |
| `InvalidTranslationError` | The **translation** does. Under the default lenient mode this is logged and the source text is rendered instead. |

## Extraction entry points { #extraction-entry-points }

Registered automatically on install; you refer to them by name, not by import.

| Group | Name | Used by |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | The `method` in `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatically. |

## Performance { #performance }

The full account — what is cached, what the caches key on, and the measured
numbers — is [The hot path](internals.md#the-hot-path). The short version:
validation is cached, never skipped, and the whole render costs a fraction of
a microsecond. Run the benchmark on your own target:

```console
uv run python benchmarks/runtime.py
```
