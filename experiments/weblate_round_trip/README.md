# A round trip through Weblate

**The claim.** This package writes ordinary GNU gettext catalogs and marks every
message that has placeholders with the `python-brace-format` flag. A
translation platform should therefore be able to take such a catalog, check the
translations against the flag, and give the catalog back intact.
[*Extraction*](../../docs/extraction.md#your-existing-toolchain-validates-these-catalogs)
pointed at Weblate's documentation for that, and nothing had verified it
([#15](https://github.com/yhay81/gettext-tstrings/issues/15)).

## Run it

From the repository root:

```console
uv run experiments/weblate_round_trip/run.py
```

It needs uv and a PostgreSQL 13 or newer server installation that includes the
contrib extensions Weblate's migrations create, `pg_trgm` and `btree_gin`.
Homebrew's `postgresql@18` and Debian's `postgresql` packages both qualify.
`weblate_side.py` looks for one in the usual places; set `PG_BIN` to its `bin`
directory if it does not find yours.

Nothing is installed or left running. Weblate runs in a Python 3.12
environment of its own, which uv builds from the inline metadata and lock of
`weblate_side.py`. It uses a database cluster created in a temporary directory,
which listens only on a Unix socket in a directory no other user can enter,
needs no password, and is stopped when the run ends. Celery tasks run in place, so no Redis or worker is involved. The one
dependency Weblate declares that the environment leaves out is `borgbackup`,
which only Weblate's backup feature uses and which has no wheel for every
platform. A run takes about 30 seconds, most of them Weblate's database
migrations, and exits non-zero if any expectation below fails.

## What it does

1. **Extract.** `messages.py` holds one message of each shape a catalog has: a
   singular with a translator comment, a plural, two messages that differ only
   by `msgctxt`, a message whose two placeholders a translation reorders, and a
   message whose source repeats a placeholder. The package's Babel extractor
   turns it into `catalogs/messages.pot`, with the `#. gettext-tstrings` marker
   and the `python-brace-format` flag.
2. **Import.** The template and an empty Polish catalog from `pybabel init` go
   into a Weblate project as a gettext component with no remote repository. This
   is the path Weblate's "upload translation files" form and its REST API take
   (`create_component_from_zip`), and it uses default settings throughout. Polish
   is the target because it has three plural forms, the first of them used for
   n = 1 alone.
3. **Translate broken, then export.** Four broken translations are entered
   through `Unit.translate`, the method Weblate's editor and REST API call, and
   what Weblate's checks said about each is recorded. Weblate then commits, and
   its file becomes `catalogs/pl.unchecked.po`: what a translator who ignored
   the checks would hand back.
4. **Translate valid, then export again.** Seven valid translations replace
   them, one of which repeats a placeholder more often than its source does.
   Weblate's file becomes `catalogs/pl.po`.
5. **Compare** `pl.po` with the template, message by message.
6. **Compile** both exports with `pybabel compile`, this package's checker
   included, and with GNU `msgfmt --check-format`.
7. **Render** the calls in `messages.py` against the compiled exports, for
   n = 1, 2 and 5.

`catalogs/weblate-results.json` records the versions, the component settings,
and every check Weblate reported.

## Result

### What each tool said about each translation

| Translation entered | Weblate's Python brace format check | GNU `msgfmt --check-format` | `pybabel compile` with this package's checker |
| --- | --- | --- | --- |
| renamed placeholder, `Witaj ponownie, {imie}` | missing `{name}`, extra `{imie}` | fatal error | error |
| conversion added, `Cześć, {name!r}` | missing `{name}`, extra `{name!r}` | fatal error: not a valid Python brace format string | error: adds formatting |
| second plural form drops `{n}`, `pliki` | missing `{n}` | not exported; *Extraction* already records that msgfmt accepts a form that drops a placeholder its siblings keep | not exported |
| **first plural form drops `{n}`**, `plik` for n = 1 | **nothing** | **nothing** | error: `msgstr[0]`, `{n}` is missing |
| reordered, `Do folderu {folder} przeniesiono {item}` | nothing | nothing | nothing |
| repeated as often as in the source | nothing | nothing | nothing |
| **repeated more often than in the source**, `Cześć, {name}! Miło cię znowu widzieć, {name}` | **extra `{name}`** | nothing | nothing |

The bold rows are where Weblate's check and this package's rules
([SPEC §4](../../SPEC.md)) disagree:

- **Weblate counts occurrences.** It compares the placeholders of source and
  translation as multisets, so a value used once in the source and twice in the
  translation is reported as an extra placeholder. This package lets a
  translation repeat a value freely, so that catalog compiles and renders. In
  Weblate the check has to be dismissed for that string.
- **Weblate lets the first plural form drop a placeholder** when that form is
  used for exactly one number, or for 0 and 1 only. Its own source calls this
  technically wrong but kept to avoid false positives. This package requires
  `{n}` in every form whenever both source branches contain it, so `plik` is
  rejected here. If a language's form for 1 should not show the number, write
  the singular source without it (`t"One file"`); then neither tool requires
  it.

Neither difference loses data, and the second is caught before release, by the
checker in the compile step. That step is the one that saw all three broken
translations; Weblate missed one and `msgfmt` missed the same one.

### What the round trip kept

Every one of the 7 messages came back with its `#. gettext-tstrings` marker,
its translator comment, its `python-brace-format` flag, its `msgctxt`, its
location, and, for the plural, three Polish forms. Weblate changed only the
header: it set `PO-Revision-Date`, `Last-Translator` and `Language-Team`, added
`X-Generator`, and rewrote the `Plural-Forms` expression without its outer
parentheses. That expression still picks the same form as Babel's for every n
from 0 to 1000.

Compiled, the valid export rendered all 7 calls in Polish for n = 1, 2 and 5
without a single warning. The unchecked export compiled too: `pybabel` writes
the `.mo` while it reports the errors and exits 1. At runtime, each of its three
broken messages rendered its source text and logged one warning, and its valid
plural forms still rendered for n = 2 and 5.

### Recorded output

Recorded on 2026-10-18 on macOS 27.0.1, arm64, with uv 0.13.1:

```text
command            uv run experiments/weblate_round_trip/run.py
python             3.14.8 (cpython)
gettext-tstrings   0.1.0a8
babel              2.18.0
weblate's python   3.12.15
weblate            2026.10.1
django             6.0.9
translate-toolkit  3.20.0
postgresql         postgres (PostgreSQL) 18.6 (Homebrew)
msgfmt             msgfmt (GNU gettext-tools) 1.0
component          file_format='po', vcs='local', filemask='locale/*/LC_MESSAGES/messages.po', new_base='locale/messages.pot', source_language='en', check_flags='', enforced_checks=[], language='pl', plural_formula='n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2', plural_forms=3

ok    Weblate's Python brace format check on broken translations: it caught a renamed placeholder, an added conversion, and a plural form that drops {n}
ok    DIFFERENCE, a plural form used for one number only may drop {n} in Weblate: Polish 'plik' for n == 1, without {n}, raised no check; this package requires {n} in every form
ok    valid translations, reordered and repeated as in the source: no check fired on 6 of them
ok    DIFFERENCE, repeating a placeholder more often than the source does: Weblate flagged the second {name} as extra; this package allows a value to repeat
ok    what the export kept: all 7 messages came back with their marker and translator comments, flags, msgctxt, locations, and three Polish plural forms
ok    the rewritten Plural-Forms header: Weblate wrote 'n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2', which picks the same form as Babel's for n = 0..1000
ok    pybabel compile, with this package's checker: the valid export compiled cleanly; the unchecked one exited 1 with an error for each of its three broken translations, the plural form Weblate let through included
        error: experiments/weblate_round_trip/catalogs/pl.unchecked.po:29: translation does not match the source placeholders: {name} is missing; {imie} is not in the source message
        error: experiments/weblate_round_trip/catalogs/pl.unchecked.po:35: msgstr[0]: translation does not match the source placeholders: {n} is missing
        error: experiments/weblate_round_trip/catalogs/pl.unchecked.po:68: placeholder {name} adds formatting; write {name} on its own, because the source message decides how the value is formatted
ok    GNU msgfmt --check-format: the valid export passed; the unchecked one failed on the renamed placeholder and the conversion, and let the plural form without {n} through
        experiments/weblate_round_trip/catalogs/pl.unchecked.po:30: a format specification for argument 'imie', as in 'msgstr', doesn't exist in 'msgid'
        experiments/weblate_round_trip/catalogs/pl.unchecked.po:69: 'msgstr' is not a valid Python brace format string, unlike 'msgid'. Reason: The directive number 0 is unterminated.
        /opt/homebrew/bin/msgfmt: found 2 fatal errors
ok    rendering messages.py against Weblate's export: all 7 calls rendered in Polish for n = 1, 2 and 5, with no warning
ok    rendering the unchecked export: the three broken messages rendered their source text with one warning each, and the Polish plural forms that are valid still rendered for n = 2 and 5

all expectations held
```

Three runs printed exactly this. The files in `catalogs/` differ from run to run
only in their header dates.

## What this does not cover

- **Weblate's web layer.** Translations went in through `Unit.translate`, which
  the editor and the REST API call, not through HTTP. Nothing ran in a browser.
- **Other configurations.** Only one Weblate version, 2026.10.1, was tested,
  with default component settings: no enforced checks, no extra check flags, and
  no add-ons. The "Update PO files to match POT" add-on, for example, was not
  enabled.
- **Other platforms.** Crowdin, Transifex and the rest key their own QA on the
  same flag; how they behave is not verified here.
