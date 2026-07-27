# Changelog

## Unreleased

- Lenient runtime rendering: a catalog whose placeholders do not match the source now falls back to the source text instead of raising; `strict=True` restores the raising behavior (on `Translator` and every module function).
- Guard the empty-msgid trap so `t""` renders as `""` instead of returning the catalog header.
- Extraction no longer aborts the whole run on one rejected t-string or one unparsable file; such calls warn and are skipped, with an opt-in `strict` extractor option.
- Emit simple t-string messages with no funcname so extraction works under custom Babel keyword sets (e.g. `--no-default-keywords -k tr`); plural/contextual messages without the standard gettext keywords are skipped with a warning.
- Add context-scoped current translations (`use_translations`, `set_translations`, `get_translations`) for per-request language selection.
- Add deferred translation (`lazy_gettext`, `lazy_pgettext`, `LazyString`) for module-level translatable strings.
- Make the `Translations` protocol `runtime_checkable`.
- Improve confusable-placeholder diagnostics with escaped names.
- Extract `lazy_gettext` and `lazy_pgettext` by default, with an example-driven
  extraction-to-runtime round-trip test.
- Make `LazyString` unhashable: its rendered text depends on the active
  language, so a hash would silently break sets and dict keys across switches.
- State the measured sub-microsecond overhead instead of claiming "fast".
- Run CI on Linux, macOS, and Windows, and smoke-test the built wheel in a
  clean environment.
- Add a tag-triggered release workflow using PyPI Trusted Publishing
  (see RELEASING.md).

## 0.1.0a1 - Unreleased

- Add safe `tr()` and `ntr()` runtimes for Python t-strings.
- Add a Babel extractor that coexists with ordinary gettext calls.
- Add strict placeholder validation as a Babel checker.
- Preserve source-controlled conversions and format specifications.
- Add canonical `gettext`, `ngettext`, `pgettext`, and `npgettext` APIs.
- Cache static template and translated-pattern plans on the runtime hot path.
- Support branch-specific plural placeholders and safe translated repetition.
