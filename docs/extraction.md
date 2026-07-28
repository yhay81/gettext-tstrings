# Extraction

Extraction needs the `babel` extra:

```console
python -m pip install "gettext-tstrings[babel]"
```

## The workflow

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

The `gettext_tstrings` extractor also handles ordinary `_()`, `gettext()`, and
`ngettext()` calls, so one mapping covers a mixed codebase. It recognizes `_()`,
the four standard gettext names, the `tr()` / `ntr()` aliases, and the deferred
`lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` is not optional"

    `pybabel extract` only collects translator comments when you pass
    `-c "Translators:"`, exactly as it does for ordinary gettext calls.

## Registering your own function names

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

Both spellings work: an ini file gives whitespace-separated strings, a TOML
mapping gives lists.

The options are `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions`, and `npgettext_functions`.

## Robust by default

One bad file does not end the run:

- A t-string the extractor rejects — attribute access, an expression, a wrong
  argument — is reported as a warning and skipped.
- A file that will not parse is skipped the same way.
- So is a file that only `tokenize` refuses while `ast` accepts it, which Babel's
  own pass would otherwise abort on.

Set `strict = true` in the mapping options to turn every one of those into a hard
failure instead, which is what you want in CI.

## Your existing toolchain validates these catalogs

Babel marks every extracted message `#, python-brace-format`, and that one flag
is what activates placeholder checking in the tools you already run:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:26: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate, Crowdin, Transifex, and POEditor read the same flag. No configuration is
involved.

On top of that, the package registers a Babel **checker**, so `pybabel compile`
applies the specification's rules to every message carrying the
`gettext-tstrings` marker comment:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:25: translation placeholders do not
match source: missing ['name'], unexpected ['nombre']
1 errors encountered.
```

The two are not redundant. The shipped checker is the stricter party in at least
two places:

- A msgid whose only braces are escaped (`Config {{raw}} only`) never gets the
  `python-brace-format` flag, so no external tool validates it at all.
- `msgfmt --check-format` accepts a plural form that drops a placeholder the
  other form keeps. `pybabel compile` rejects it.

## Templates and other tools

t-strings are Python syntax, so this library covers Python source. Template
languages keep using their own i18n — Jinja2's `{% trans %}`, Django's template
tags — and Babel's extractors for them. Everything feeds the same PO catalog, so
one translation workflow still covers a mixed codebase.

`pygettext` cannot parse t-strings today, which is why extraction goes through
Babel. The convention is written down in the [specification](spec.md) so that
another extractor, or a future `pygettext`, can target it.
