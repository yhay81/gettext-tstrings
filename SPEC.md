# The t-string ↔ gettext convention (spec v1)

This document defines how `gettext-tstrings` turns a Python 3.14 t-string into a
gettext message and how it validates a translation of that message. The rules
are small and stable on purpose: another implementation, an IDE, a type checker,
or a future `pygettext` can target "spec v1" and interoperate with the catalogs
this library produces and consumes.

The reference implementation lives in `src/gettext_tstrings/`. Where prose and
code disagree, the code is authoritative and the prose is a bug.

## 1. Terms

- **t-string** — a `string.templatelib.Template` produced by a `t"..."` literal
  (PEP 750). It exposes `strings` (the literal segments), `interpolations`
  (each with `expression`, `conversion`, `format_spec`, and a runtime `value`).
- **msgid** — the gettext message key derived from a t-string.
- **pattern** — a translated string retrieved from a catalog (PO/MO), or the
  source msgid itself when no translation applies.
- **placeholder** — a `{name}` field in a msgid or pattern.

## 2. msgid derivation

A msgid is the concatenation, in source order, of the transformed `strings`
segments and one placeholder token per interpolation.

1. **Literal segments** are brace-escaped: every `{` becomes `{{` and every `}`
   becomes `}}`. (So a literal brace survives round-tripping through a
   brace-format pattern.)
2. **Each interpolation** contributes the token `{name}`, where `name` is the
   interpolation's `expression` with surrounding whitespace stripped.
   - `name` **must** be a simple placeholder name: `str.isidentifier()` is true
     and it is not a Python keyword. Any other expression — attribute access
     (`user.name`), a call (`f()`), subscription (`a[0]`), an operator — is
     rejected. The value must be computed before the t-string.
   - The interpolation's `conversion` (`!r`, `!s`, `!a`) and `format_spec`
     (`:.2f`, `:{width}`, …) are **not** part of the msgid. They stay under
     application control and never reach the catalog.
3. **Repeated names.** The same `name` may appear more than once. Every
   occurrence must carry the identical `conversion` and `format_spec`; a repeat
   with different formatting is an error (the msgid would be ambiguous).

Examples:

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"{first}, {second}, {first}"` | `{first}, {second}, {first}` |
| `t"Hello {user.name}"` | *(rejected — not a simple name)* |

An **empty msgid** (only `t""` produces one) is never looked up in a catalog,
because gettext reserves the empty msgid for a catalog's metadata header. `t""`
renders as `""`.

## 3. Plurals and context

- **Plural** messages derive two msgids, one from the singular t-string and one
  from the plural t-string, following §2. A placeholder that appears in **both**
  branches must carry identical `conversion`/`format_spec` in both.
- **Context** (`pgettext`/`npgettext`) is a plain string literal supplied at the
  call site. It is the gettext `msgctxt` and is not derived from a t-string.

## 4. Translation validation

A pattern retrieved from a catalog is validated against the source before
rendering. A pattern is **valid** when:

1. It contains only bare placeholders `{name}`. A translation placeholder **must
   not** carry a conversion or a format spec, and `name` must be a simple
   placeholder name (§2.2). Positional (`{0}`, `{}`), attribute, and index
   fields are rejected. Formatting is the source's responsibility, never the
   translator's.
2. Its placeholder set satisfies the source contract:
   - **allowed** = the union of the placeholder names across the source
     branches (for a singular message, simply the source's names).
   - **required** = the intersection of the placeholder names across the source
     branches (for a singular message, all of the source's names).
   - Every `required` name must appear at least once; no name outside `allowed`
     may appear.
3. Placeholders **may be reordered and repeated freely.** Reordering is often
   grammatically necessary, and a language may need to repeat a value. Occurrence
   counts are deliberately unconstrained.

The `required = intersection` rule lets a plural branch expose a value the other
branch does not (e.g. `t"One file"` vs `t"{n} files"`): `n` is *available* to
translators of either form but *required* of neither, so a target language's
plural rules can differ from the source's.

## 5. Rendering

Given a valid pattern and the t-string's runtime values:

- Literal `{{`/`}}` in the pattern render as literal `{`/`}`.
- Each placeholder renders its value formatted with that field's source-side
  `conversion` then `format_spec` (equivalent to `format(convert(value, conv),
  spec)`).
- Each distinct value is formatted **at most once** per render, even when a
  translation repeats its placeholder.
- On a validation failure at render time, the behavior is caller-selected:
  lenient (default) reproduces the source text; strict re-raises. This mirrors
  gettext's contract that a broken catalog never crashes an application.

## 6. Extraction marker

Every message extracted from a t-string call carries the automatic translator
comment `gettext-tstrings`. Catalog checkers use this marker to apply §4 during
`pybabel` validation and compilation; messages without the marker are ignored by
the checker.

## 7. Non-goals (explicitly out of scope)

- **Translation-side formatting or logic.** A translation is data, never an
  expression language: no evaluation, attribute access, calls, or format specs.
- **Output escaping.** Rendered output is a plain `str`; HTML/shell/terminal
  escaping is the responsibility of the sink, exactly as with stdlib gettext.
- **Output-size bounds.** Catalog integrity is assumed. A hostile catalog can
  repeat a placeholder to amplify output size; this is inherent to every
  placeholder-substituting i18n layer and is not bounded here.

## 8. Versioning

This is **spec v1**. Backwards-incompatible changes to msgid derivation or
translation validation will increment the version. Additive clarifications that
do not change derived msgids or accepted/rejected patterns will not.
