# Changelog

## Unreleased

- **Breaking:** Babel is no longer a runtime dependency. Rendering never
  imported it — only the extractor and the catalog checker do — so it moved to
  a `babel` extra. Install `gettext-tstrings[babel]` wherever `pybabel` runs;
  a production image that only renders messages now installs no dependencies
  at all.

- Accept list values for the `*_functions` extraction options. A `babel.toml`
  or `pyproject.toml` mapping passes them as lists, and stringifying the list
  made every configured name fail to match, so `tr_functions = ["tr"]` silently
  dropped every t-string message — with no warning and a zero exit status, and
  without `strict` catching it either.
- Cover the `plain` rendering fast path with a source format specifier applied
  to a `str` value. Every render path shares that fast path, but no test used
  the combination, so losing it would have silently ignored format specifiers
  across the whole API.
- Assert the Babel extractor and checker entry points in the built wheel's smoke
  test. Registration as a Babel plugin is the product, and the test suite only
  ever resolves the editable install's entry points, never the wheel's.

## 0.1.0a3 - 2026-07-28

- Reject mixed plain-string/t-string plural calls during extraction instead of
  silently omitting them, including under the extractor's strict mode.
- Preserve source order and translator-comment ownership when ordinary gettext
  and t-string translation calls share one physical line, including when Babel
  suppresses a nested intermediate call or an earlier function name is
  NFKC-normalized by the AST but not recognized lexically by Babel. Rejected
  configured aliases no longer leak their comments to a later ordinary message.
- Render placeholders shared by plural source branches from the branch selected
  by the source-language plural rule, instead of always reading the singular
  t-string's captured value.
- Reject an explicit empty translation-side format specifier (`{name:}`), which
  `string.Formatter` otherwise makes indistinguishable from a bare `{name}`.
- Gate the tag-triggered PyPI release on the same formatting, lint, type, test,
  and coverage checks as CI.
- Identify translator comments with `tokenize` instead of line-prefix
  scanning. This fixes two extraction defects: a comment-looking line inside a
  string literal could corrupt the masked source and abort the whole file's
  extraction with a `TokenError`, and characters that only `str.splitlines()`
  treats as line breaks (form feed, U+2028) silently shifted comment
  attribution.
- Deduplicate the render tails: `pgettext` and the plural functions now share
  single-sourced helpers (`_render_pattern`, `_ngettext_impl`); only
  `gettext()` keeps its intentionally inlined copy, pinned by a new
  render-parity test suite that catches drift between the copies.
- Compute the translator-comment block once per extracted call and drop the
  dead wrapper and unused optional parameter around it.
- Replace `exec()`-based cache-eviction tests with direct
  `string.templatelib.Template` construction.
- Document that `pybabel extract` needs `-c "Translators:"` to collect
  translator comments, as for ordinary gettext calls.

## 0.1.0a2 - 2026-07-28

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
- Document the zero-configuration validation pipeline: Babel's automatic
  `python-brace-format` flag activates placeholder checks in GNU msgfmt,
  Weblate, Crowdin, Transifex, and POEditor.

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
