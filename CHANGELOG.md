# Changelog

## Unreleased

- Remove four pieces of code the mutation run proved had no effect. The
  extractor's `_uses_tstring_argument` (21 lines) never changed a result: a call
  whose name is also a Babel keyword always gets an entry from Babel's own pass
  on the same line, which consumes the translator comment either way. The
  `isinstance` half of the template type guard was unreachable — `Template`
  cannot be subclassed on 3.14, 3.15, or the free-threaded build. `_option_bool`
  special-cased `bool` to reach the same answer the following line already gives.
  And translation patterns were checked for modifiers twice; folding the two
  into one detector that also reports the offending name means `{name:}` now
  says which placeholder is at fault instead of falling back to a generic
  message. Verified by differential testing: 299,593 patterns and 1,054
  extraction inputs, no change in what is accepted, rejected, or produced.

- Guard the claim that the plan caches never retain interpolated values. It
  holds — all nine render paths release their values — but nothing was checking
  it: a regression that stores a template's interpolations on its cached plan
  passes all 246 other tests, and only these four fail.

- Close six detection gaps a mutation run found behind 100% coverage. Escaped
  braces beside a literal colon (`"{{{{:{a}"`) — the brace-skipping walk in the
  translation parser could take the wrong stride and reject a valid translation,
  and no test or conformance case mixed the two forms. `pgettext` with an empty
  msgid, whose reservation guard was pinned only on the `gettext` side, so a
  catalog's metadata header could reach the UI. A plural-branch-only placeholder
  rendered through the general path. **`ntr`/`ngettext`/`npgettext` resolving
  context-bound translations** — `use_translations()` was covered for `tr` and
  the lazy helpers only, leaving the per-request path that web frameworks depend
  on untested. The `n == 1` branch selection. And boolean extractor options
  arriving as strings from an ini file, where `strict = "false"` must stay false.
- Widen ruff from 7 rule groups to 46, with 9 ignores and 2 per-file entries,
  each justified in place. The additions cost nothing here (every new group
  reports zero) but they guard real classes of mistake — including `INT`, which
  catches `_(f"...")`, the anti-pattern this library exists to replace.
  `S` (bandit) is deliberately not selected: all 194 hits are pytest's `assert`,
  and ignoring it wholesale would permanently hide the one failure mode that
  matters (`assert` vanishing under `python -O`).
- Add `ty` as a second type checker. It reports override incompatibilities mypy
  does not, which is how the test doubles were found renaming
  `NullTranslations`'s parameters. They now implement the published
  `Translations` protocol directly instead of subclassing the standard library —
  the interface users actually implement, and no base class to violate.
- Turn on mypy's `strict_equality_for_none`, which caught a type that was simply
  untrue: Babel's ordinary pass yields an entry with no line number for a nested
  call, so the extractor's declared tuple type was wider in practice.
- Drop zizmor's severity floor and stop persisting credentials on checkout. The
  three `artipacked` findings were real: the release job checks out with a token
  in `.git/config` and then uploads an artifact.

- Skip Babel's ordinary-gettext pass, rather than aborting the whole
  `pybabel extract` run, when a source only `tokenize` rejects. `ast.parse`
  accepts a few files that `tokenize` does not — a form feed followed by a bare
  carriage return is one — and Babel's extractor is tokenize-based, so a single
  such file used to end the run with a `TokenError` and no POT. It now warns and
  skips like an unparsable file, keeping the t-string messages the AST pass
  already read, and `strict` still fails hard.
- Reject a non-`str` value returned by a `Translations` implementation as an
  invalid pattern instead of letting a bare `TypeError` escape. The protocol is
  public, and an implementation that returns `dict.get(...)` directly used to
  crash the render in both lenient and strict mode, outside the switch that is
  supposed to decide that.
- Document `compile_template` / `CompiledTemplate` in the README, and state in
  SPEC §5 that lenient rendering is a property of catalog lookups: an interface
  handed a pattern directly always raises.
- Close the remaining test gaps the quality audit found: plural calls where only
  one branch has an empty msgid, the pattern-record and pattern-cache bounds, a
  modifier on the *leading* placeholder of a pattern (the one position where
  `_has_explicit_field_modifier` is the sole detector), the `__all__` surface,
  translator comments without a matching tag, a msgid that only escapes braces
  (which Babel never flags `python-brace-format`, leaving the shipped checker as
  the only guard), and a plural form dropping a placeholder that
  `msgfmt --check-format` accepts but the shipped checker rejects. Coverage is
  100%; the floor moves to 99%.

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
- Merge extracted messages by line again, dropping the pass that rewrote every
  Babel keyword to a unique name so results could be mapped back to a column.
  That machinery bought nothing but the ordering of entries that share one
  physical line: across 4,895 files and generated programs the extracted
  messages are identical either way, and a line holding two translation calls
  occurs on roughly 0.5% of lines in a real internationalized codebase — an
  ordering `pybabel extract --sort-output` normalizes anyway. Extraction is
  about 1.5x faster and the extractor is 128 lines shorter, with one less
  dependency on Babel's internal behavior. Translator-comment ownership on a
  shared line, which was fixed at the same time, is unchanged and still tested.
- Publish `conformance/v1.json`, spec v1 in machine-readable form, so another
  extractor, IDE, type checker, or future `pygettext` can demonstrate that it
  targets the same convention. The cases name only derived msgids, accepted and
  rejected patterns, and rendered output — never an error message or an
  exception type — so an implementation in another language can run them
  unchanged. The reference implementation runs them as part of its own tests, so
  SPEC.md and the code cannot drift apart silently.
- Test on the next Python (3.15) and on the free-threaded build (3.14t), where
  this package's module-level plan caches are shared across threads.
- Stop restating CI inside the release workflow; it now calls CI. The two had
  already drifted, and a release must not be checked more loosely than a pull
  request. The release also fails now when `CHANGELOG.md` has no section for the
  tagged version, and it never builds a published artifact from a restored cache.
- Pin every GitHub Action to a commit SHA and add Dependabot so the pins, and
  `uv.lock`, do not rot. `zizmor` now runs in CI and reports no findings.
- Exercise the declared dependency lower bounds, run the microbenchmarks (no
  threshold — only bit-rot detection), type-check `tests/`, turn warnings into
  errors under pytest, and raise the coverage floor from 95% to 98%.

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
