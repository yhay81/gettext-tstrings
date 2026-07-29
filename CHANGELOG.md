# Changelog

## Unreleased

- Correct the last edges of the lenient catalog boundary: a non-string plural
  answer now falls back to the source branch selected by the count instead of
  always rendering the singular, while a real `str` subclass is normalized and
  accepted rather than mistaken for a wrong type. Diagnostics now distinguish
  a one-script non-ASCII homoglyph when it conflicts with a source name and no
  longer claim that a missing name found inside a different placeholder appears
  outside braces.
- Fix the documentation site's Markdown configuration. Declaring
  `markdown_extensions` in `zensical.toml` replaces the generator's defaults
  rather than adding to them, so nine extensions the pages were written against
  were silently off — including the one that renders `:material-…:` icons, which
  the specification page was printing as literal text. The declaration only
  reproduced those defaults, so removing it fixes the site and shortens the
  config.
- Add a *Why t-strings* page comparing `%(name)s`, `.format()` and a t-string on
  what each hands to the catalog, and tie every failure message quoted anywhere
  in the documentation back to the code with a test. The published pages had
  been quoting the previous wording of the checker's output.
- Rewrite the messages a translator sees. A missing placeholder whose name is
  visible in the text now says why it does not count — full-width braces from an
  input method, braces doubled by a round trip, or a name written outside braces
  at all. An invisible character is shown where it sits (`{name<U+00A0>}`)
  rather than described as "whitespace" in a name that reads as `{name}`. A name
  is printed as written, with an escaped form added only when it mixes writing
  systems or folds under NFKC, so `{名前}` stays readable while a Cyrillic
  lookalike does not hide. Plural messages name the `msgstr[N]` at fault, as GNU
  msgfmt does, because Babel reports the msgid's line for the whole block. And a
  diagnosis is no longer re-wrapped by this package's own generic handler, which
  had been prefixing every specific sentence and leaving a `__cause__` that
  repeated it.
- Treat a catalog that answers with the wrong type as a broken catalog rather
  than letting it end the render. The previous fix covered values the pattern
  parser rejects, but an *unhashable* one — a `Translations` implementation
  returning the list of plural forms it forgot to index, say — crashed earlier,
  in the cache lookup that happens before any validation, with a `TypeError`
  about dict keys and nothing about translation in it. Fuzzing the four
  translating functions over 20,104 catalog answers now produces no exception
  under the default lenient mode.

## 0.1.0a4 - 2026-07-29

### Breaking

- Babel is no longer a runtime dependency. Rendering never imported it — only
  the extractor and the catalog checker do — so it moved to a `babel` extra.
  Install `gettext-tstrings[babel]` wherever `pybabel` runs; a production image
  that only renders messages now installs no dependencies at all.

### Fixed

- Accept list values for the `*_functions` extraction options. A `babel.toml`
  or `pyproject.toml` mapping passes them as lists, and stringifying the list
  made every configured name fail to match, so `tr_functions = ["tr"]` silently
  dropped every t-string message — with no warning and a zero exit status, and
  without `strict` catching it either.
- Reject a translation placeholder that pads its name with whitespace
  (`{ name }`). GNU msgfmt refuses it as a python-brace-format string and
  `str.format` raises on it, so accepting it made this implementation looser
  than the standard it claims to interoperate with.
- Warn once per plan and pattern instead of on every render. A single bad
  catalog entry used to log a line each time its message was rendered, which on
  a hot page meant one line per request.
- Reject a non-`str` value returned by a `Translations` implementation as an
  invalid pattern instead of letting a bare `TypeError` escape. The protocol is
  public, and an implementation that returns `dict.get(...)` directly used to
  crash the render in both lenient and strict mode, outside the switch that is
  supposed to decide that.
- Skip Babel's ordinary-gettext pass, rather than aborting the whole
  `pybabel extract` run, when a source only `tokenize` rejects. `ast.parse`
  accepts a few files that `tokenize` does not — a form feed followed by a bare
  carriage return is one — and Babel's extractor is tokenize-based, so a single
  such file used to end the run with a `TokenError` and no POT. It now warns and
  skips like an unparsable file, keeping the t-string messages the AST pass
  already read, and `strict` still fails hard.

### Changed

- Merge extracted messages by line again, dropping the pass that rewrote every
  Babel keyword to a unique name so results could be mapped back to a column.
  That machinery bought nothing but the ordering of entries that share one
  physical line: across 4,895 files and generated programs the extracted
  messages are identical either way, and a line holding two translation calls
  occurs on roughly 0.5% of lines in a real internationalized codebase — an
  ordering `pybabel extract --sort-output` normalizes anyway. Extraction is
  about 1.5x faster and the extractor is 128 lines shorter, with one less
  dependency on Babel's internal behavior. Translator-comment ownership on a
  shared line is unchanged and still tested.
- Remove four pieces of code a mutation run proved had no effect: the
  extractor's `_uses_tstring_argument` (21 lines, no reachable influence on any
  result), the `isinstance` half of the template type guard (`Template` cannot
  be subclassed on 3.14, 3.15, or the free-threaded build), `_option_bool`'s
  `bool` special case, and one of two redundant modifier checks on translation
  patterns. Folding the modifier checks together also improves diagnostics:
  `{name:}` now names the placeholder at fault. Verified by differential
  testing — 299,593 patterns and 1,054 extraction inputs, no change in what is
  accepted, rejected, or produced.

### Documentation

- Publish `conformance/v1.json`, spec v1 in machine-readable form, so another
  extractor, IDE, type checker, or future `pygettext` can demonstrate that it
  targets the same convention. The cases name only derived msgids, accepted and
  rejected patterns, and rendered output — never an error message or an
  exception type — so an implementation in another language can run them
  unchanged. The reference implementation runs them as part of its own tests, so
  SPEC.md and the code cannot drift apart silently.
- Document `compile_template` / `CompiledTemplate`, which were exported but
  absent from the README, and state in SPEC §5 that lenient rendering is a
  property of catalog lookups: an interface handed a pattern directly always
  raises.
- Correct claims in the README and SPEC that were stronger than what the code
  guarantees.

### Testing and tooling

- Close the test gaps two audits found. Behind 100% coverage a mutation run
  still surfaced six: escaped braces beside a literal colon, `pgettext` with an
  empty msgid, a plural-branch-only placeholder on the general render path,
  **`ntr`/`ngettext`/`npgettext` resolving context-bound translations** — the
  per-request path web frameworks depend on, previously covered only for `tr` —
  the `n == 1` branch selection, and boolean options arriving as strings from an
  ini file. Earlier gaps closed alongside them: the `plain` fast path with a
  format specifier on a `str`, plural calls with one empty-msgid branch, the
  cache and pattern-record bounds, a modifier on a pattern's leading
  placeholder, the `__all__` surface, translator comments without a matching
  tag, a msgid that only escapes braces, and a plural form dropping a
  placeholder that `msgfmt --check-format` accepts but the shipped checker
  rejects.
- Drive the real toolchain end to end: `pybabel` and GNU `msgfmt` over a full
  POT round trip, the `python-brace-format` flag the interoperability claim
  rests on, and `pybabel compile` invoking the shipped checker.
- Guard the claim that the plan caches never retain interpolated values. It
  holds — all nine render paths release their values — but nothing was checking
  it: a regression that stores a template's interpolations on its cached plan
  passes every other test.
- Assert the Babel extractor and checker entry points in the built wheel's smoke
  test. Registration as a Babel plugin is the product, and the suite only ever
  resolves the editable install's entry points, never the wheel's.
- Test on the next Python (3.15) and on the free-threaded build (3.14t), where
  this package's module-level plan caches are shared across threads.
- Widen ruff from 7 rule groups to 46, with 9 ignores and 2 per-file entries,
  each justified in place. Every new group reports zero here, so they guard
  against future mistakes — including `INT`, which catches `_(f"...")`, the
  anti-pattern this library exists to replace. `S` (bandit) is deliberately not
  selected: all 194 hits are pytest's `assert`, and ignoring it wholesale would
  permanently hide the one failure mode that matters (`assert` vanishing under
  `python -O`).
- Add `ty` as a second type checker alongside mypy. It reports override
  incompatibilities mypy does not, which is how the test doubles were found
  renaming `NullTranslations`'s parameters; they now implement the published
  `Translations` protocol directly. Turn on mypy's `strict_equality_for_none`,
  which caught a declared type that was untrue: Babel's ordinary pass yields an
  entry with no line number for a nested call.
- Stop restating CI inside the release workflow; it now calls CI. The two had
  already drifted, and a release must not be checked more loosely than a pull
  request. The release also fails when `CHANGELOG.md` has no section for the
  tagged version, and never builds a published artifact from a restored cache.
- Pin every GitHub Action to a commit SHA, stop persisting credentials on
  checkout, and add Dependabot so the pins and `uv.lock` do not rot. `zizmor`
  runs in CI without a severity floor and reports no findings.
- Exercise the declared dependency lower bounds, run the microbenchmarks (no
  threshold — only bit-rot detection), type-check `tests/`, turn warnings into
  errors under pytest, and raise the coverage floor from 95% to 99% against a
  measured 100%.

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
