---
description: "t-string-Nachrichten mit pybabel extrahieren und Kataloge mit msgfmt sowie dem integrierten Babel-Checker prüfen."
---

# Extraktion

Für die Extraktion wird das `babel`-Extra benötigt:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Workflow

Erstelle `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Danach funktionieren die üblichen Babel-Befehle:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

Der Extraktor verarbeitet auch `_()`, `gettext()` und `ngettext()`. Ein Mapping
deckt daher gemischten Code einschließlich `tr()`, `ntr()`, `lazy_gettext()` und
`lazy_pgettext()` ab.

!!! warning "`-c` ist nicht optional"

    Mit `-c "Translators:"` werden Hinweise für Übersetzende wie bei normalem
    gettext eingesammelt.

## Eigene Funktionsnamen

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

INI-Werte sind durch Leerzeichen oder Kommas getrennte Strings; TOML nimmt
Listen an. Die Optionen decken alle sechs gettext-Funktionsfamilien ab.

!!! danger "`-k` erreicht keine t-string"

    Ein Helper wie `mytr(t"…")` muss in diesen Optionen stehen. Babels
    `--keyword`-Mechanismus liest keine t-string-Literale:
    `pybabel extract -k mytr` lässt sie ohne Warnung aus.

    Nur die Standardreihenfolge der Argumente wird unterstützt.

## Standardmäßig robust

- Eine abgelehnte t-string wird gemeldet und übersprungen.
- Eine nicht parsbare Datei wird genauso isoliert.
- Auch eine nur von `tokenize` abgelehnte Datei wird isoliert.

Mit `strict = true` werden diese Warnungen in CI zu Fehlern.

## Validierung mit vorhandenen Werkzeugen

Babel fügt ein Standard-Flag hinzu:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Eine Übersetzung `こんにちは {nombre}` wird ohne zusätzliche Konfiguration
erkannt:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate dokumentiert diese Prüfung als
[Python brace format][weblate-checks]. Verifiziert sind msgfmt und der
mitgelieferte Babel-Checker.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

`pybabel compile` wendet den Checker auf jede markierte Nachricht an:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Bei Pluralformen nennt die Meldung die konkrete Form:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` schreibt die `.mo` trotzdem"

    Der Exitstatus ist `1`, der ungültige Katalog wird jedoch kompiliert.
    Eine Pipeline muss den Status als harte Schranke behandeln.

    ```yaml
    - run: pybabel compile -d locales   # non-zero exit is the gate
    ```

Die Prüfungen sind nicht redundant: Der mitgelieferte Checker validiert
maskierte Klammern und jede Pluralform einzeln, auch wenn msgfmt die Datei
akzeptiert. ASCII-Namen lassen alle Werkzeuge mitprüfen; die Bibliothek selbst
akzeptiert jedes `str.isidentifier()`.

## Templates und andere Werkzeuge

t-strings sind Python-Syntax. Jinja2 (`{% trans %}`), Django und andere
Templates behalten ihre eigenen Extraktoren und schreiben dennoch in denselben
PO-Katalog.

`pygettext` kann t-strings noch nicht parsen. Die
[Spezifikation](spec.md) erlaubt anderen Extraktoren, dieselbe Konvention zu
implementieren.
