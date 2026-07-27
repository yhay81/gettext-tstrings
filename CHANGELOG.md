# Changelog

## Unreleased

- Rework the rendering hot path for roughly 1.7x lower overhead, measured on
  CPython 3.14: plans are looked up by the template's `strings` tuple with
  per-interpolation metadata verification instead of rebuilding an `lru_cache`
  key per call, validated translation patterns are cached on their plan, and
  constant/one-field/two-field messages render through specialized
  concatenation paths. Safety validation is unchanged — unvalidated patterns
  always pass through the same parser and placeholder checks.
- Skip `format()` for plain `str` values with no conversion or format spec
  (behavior-identical; `str` subclasses still take the `format()` path).
- Bound every plan-cache dimension: a template shape whose format spec varies
  at runtime (e.g. a nested `t"{x:{width}}"` spec) can no longer grow a cache
  bucket without limit, and bare-placeholder shapes that share static strings
  (`t"{name}"`, `t"{count}"`) are looked up by their leading expression instead
  of a linear scan.
- Skip the catalog for plural calls with an empty-msgid branch, matching the
  empty-msgid rule of SPEC §2 (`ngettext(t"", t"", n)` renders `""`, never the
  catalog header).
- Benchmark the bound `Translator` and `ngettext` paths in
  `benchmarks/runtime.py`.

## 0.1.0a1 - 2026-07-28

First public release.

- Add safe `tr()` and `ntr()` runtimes for Python t-strings.
- Add a Babel extractor that coexists with ordinary gettext calls.
- Add strict placeholder validation as a Babel checker.
- Preserve source-controlled conversions and format specifications.
- Add canonical `gettext`, `ngettext`, `pgettext`, and `npgettext` APIs.
- Cache static template and translated-pattern plans on the runtime hot path.
- Support branch-specific plural placeholders and safe translated repetition.
- Lenient runtime rendering: a catalog whose placeholders do not match the source falls back to the source text instead of raising; `strict=True` restores the raising behavior (on `Translator` and every module function).
- Guard the empty-msgid trap so `t""` renders as `""` instead of returning the catalog header.
- Extraction does not abort the whole run on one rejected t-string or one unparsable file; such calls warn and are skipped, with an opt-in `strict` extractor option.
- Emit simple t-string messages with no funcname so extraction works under custom Babel keyword sets (e.g. `--no-default-keywords -k tr`); plural/contextual messages without the standard gettext keywords are skipped with a warning.
- Add context-scoped current translations (`use_translations`, `set_translations`, `get_translations`) for per-request language selection.
- Add deferred translation (`lazy_gettext`, `lazy_pgettext`, `LazyString`) for module-level translatable strings, extracted by default with an example-driven extraction-to-runtime round-trip test.
- Make `LazyString` unhashable: its rendered text depends on the active language, so a hash would silently break sets and dict keys across switches.
- Make the `Translations` protocol `runtime_checkable`.
- Improve confusable-placeholder diagnostics with escaped names.
- Document the t-string→msgid convention as a versioned contract (SPEC.md).
- State the measured sub-microsecond overhead instead of claiming "fast".
- Run CI on Linux, macOS, and Windows, and smoke-test the built wheel in a clean environment.
- Add a tag-triggered release workflow using PyPI Trusted Publishing (see RELEASING.md).
