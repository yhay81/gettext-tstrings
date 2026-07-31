---
description: "Extracting t-string messages with pybabel, and how msgfmt and the bundled Babel checker validate the catalogs."
---

# Extraction

Extraction is the step that collects every marked message out of your source
code into a `.pot` template for translators — step 3 of the
[tutorial](tutorial.md)'s loop. This page is the reference for that step:
configuration, custom function names, strict CI mode, and the checks that
guard your catalogs afterwards.

Extraction needs the `babel` extra:

```console
python -m pip install "gettext-tstrings[babel]"
```

## The workflow { #the-workflow }

Create `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Then use the ordinary Babel commands:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` runs once per language; after that, `pybabel update` folds each fresh
template into the existing catalogs. That recurring cycle — and what its
`fuzzy` entries mean for a release — is walked through in
[In production](workflow.md#the-cycle-after-the-first-translation).

The `gettext_tstrings` extractor also handles ordinary `_()`, `gettext()`, and
`ngettext()` calls, so one mapping covers a mixed codebase. It recognizes `_()`,
the four standard gettext names, the `tr()` / `ntr()` aliases, and the deferred
`lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` is not optional"

    `pybabel extract` only collects translator comments when you pass
    `-c "Translators:"`, exactly as it does for ordinary gettext calls.

## Registering your own function names { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

An ini file gives one string, a TOML mapping gives a list, and within a string
either whitespace or commas separate the names. All four spellings work.

The options are `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions`, and `npgettext_functions`.

!!! danger "`-k` does not reach a t-string"

    A custom helper such as `mytr(t"…")` has to be named in one of the options
    above. Babel's `--keyword` machinery cannot read a t-string literal, so
    `pybabel extract -k mytr` finds nothing and says nothing — the messages are
    simply absent from the POT. `-k` keeps working for the ordinary gettext
    calls extracted alongside.

    Only the standard argument order is supported: message first, context then
    message for `pgettext`, context then singular then plural for `npgettext`.

## Robust by default { #robust-by-default }

One bad file does not end the run:

- A t-string the extractor rejects — attribute access, an expression, a wrong
  argument — is reported as a warning and skipped.
- A file that will not parse is skipped the same way.
- So is a file that only `tokenize` refuses while `ast` accepts it, which Babel's
  own pass would otherwise abort on.

Set `strict = true` in the mapping options to turn every one of those into a hard
failure instead, which is what you want in CI.

## Your existing toolchain validates these catalogs { #your-existing-toolchain-validates-these-catalogs }

Babel marks every extracted message with a standard flag, and that one line is
what activates placeholder checking in the tools you already run:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Translate it as `こんにちは {nombre}` and the mistake is caught without any
configuration:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documents the same check as [Python brace format][weblate-checks], and
the commercial platforms have their own placeholder QA keyed on the same flag.
Their behaviour is theirs; the two tools below are the ones verified here.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

On top of that, the package registers a Babel **checker**, so `pybabel compile`
applies the specification's rules to every message carrying the
`gettext-tstrings` marker comment:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

For a plural message the pointer names the form, because the line number Babel
reports is the msgid's and a Russian block has three `msgstr` below it:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` still writes the `.mo`"

    The error above is reported, the exit status is `1` — and the broken
    catalog is compiled anyway. Only that exit status can stop a pipeline
    from shipping it; [What CI gates](workflow.md#what-ci-gates) shows the
    build step that lets it.

The two checks are not redundant. The shipped checker is the stricter party in at
least two places:

- A msgid whose only braces are escaped (`Config {{raw}} only`) never gets the
  `python-brace-format` flag, so no external tool validates it at all.
- Plural forms are checked one by one. `msgfmt --check-format` reads the very
  file above and exits `0`; a form that drops a placeholder its siblings keep is
  accepted there and rejected here.

`msgfmt` only checks placeholder names it can parse as Python brace format, so
ASCII names keep every tool in the chain able to validate the message. The
library itself accepts any `str.isidentifier()` name.

## Templates and other tools { #templates-and-other-tools }

t-strings are Python syntax, so this library covers Python source. Template
languages keep using their own i18n — Jinja2's `{% trans %}`, Django's template
tags — and Babel's extractors for them. Everything feeds the same PO catalog, so
one translation workflow still covers a mixed codebase.

`pygettext` cannot parse t-strings today, which is why extraction goes through
Babel. The convention is written down in the [specification](spec.md) so that
another extractor, or a future `pygettext`, can target it.
