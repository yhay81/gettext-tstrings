---
description: "t-string-Nachrichten mit pybabel extrahieren und Kataloge mit msgfmt sowie dem integrierten Babel-Checker prüfen."
---

# Extraktion

Extraktion ist der Schritt, der jede markierte Nachricht aus deinem Quellcode
in eine `.pot`-Vorlage für Übersetzende einsammelt — Schritt 3 der Schleife
aus dem [Tutorial](tutorial.md). Diese Seite ist die Referenz für diesen
Schritt: Konfiguration, eigene Funktionsnamen, strikter CI-Modus und die
Prüfungen, die deine Kataloge danach absichern.

Für die Extraktion wird das `babel`-Extra benötigt:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Workflow { #the-workflow }

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

`init` läuft einmal pro Sprache; danach arbeitet `pybabel update` jede
frische Vorlage in die vorhandenen Kataloge ein. Diesen wiederkehrenden
Zyklus — und was seine `fuzzy`-Einträge für ein Release bedeuten — geht
[Im Produktivbetrieb](workflow.md#the-cycle-after-the-first-translation)
Schritt für Schritt durch.

Der Extraktor verarbeitet auch `_()`, `gettext()` und `ngettext()`. Ein Mapping
deckt daher gemischten Code einschließlich `tr()`, `ntr()`, `lazy_gettext()` und
`lazy_pgettext()` ab.

!!! warning "Hinweise für Übersetzende mit `-c` aktivieren"

    Mit `-c "Translators:"` werden Hinweise für Übersetzende wie bei normalem
    gettext eingesammelt. Lässt du die Option weg, funktioniert die Extraktion
    weiterhin — die Hinweise erreichen den Katalog dann nur nie, wo sie
    [der billigste Qualitätshebel](workflow.md#working-with-translators-and-platforms)
    des ganzen Arbeitsablaufs sind.

## Eigene Funktionsnamen { #registering-your-own-function-names }

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

## Lokal nachsichtig, in CI strikt { #lenient-locally-strict-in-ci }

Standardmäßig beendet eine fehlerhafte Datei den Lauf nicht:

- Eine abgelehnte t-string wird gemeldet und übersprungen.
- Eine nicht parsbare Datei wird genauso isoliert.
- Auch eine nur von `tokenize` abgelehnte Datei wird isoliert.

Das ist bequem, solange du gerade editierst, und gefährlich, sobald du es
nicht tust: Eine übersprungene Nachricht **fehlt schlicht in der POT**, wird
also nie übersetzt, und nichts weist darauf hin. Setze `strict = true` in den
Mapping-Optionen überall dort, wo niemand die Extraktion beobachtet:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Jede der obigen Warnungen wird damit zum harten Fehler. Behandle das als die
Einstellung für den Produktivbetrieb und die Voreinstellung als die für die
lokale Arbeit.

## Validierung mit vorhandenen Werkzeugen { #your-existing-toolchain-validates-these-catalogs }

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
[Python brace format][weblate-checks]. Jede Plattform verhält sich dabei nach
ihren eigenen Regeln; verifiziert sind hier msgfmt und der mitgelieferte
Babel-Checker.

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

    Der Fehler oben wird gemeldet, der Exitstatus ist `1` — und der defekte
    Katalog wird trotzdem kompiliert. Nur dieser Exitstatus kann eine
    Pipeline davon abhalten, ihn auszuliefern;
    [Was CI absichert](workflow.md#what-ci-gates) zeigt den Build-Schritt,
    der das leistet.

Die Prüfungen sind nicht redundant: Der Checker des Pakets ist in mindestens
zwei Fällen strenger. Er validiert maskierte Klammern und jede Pluralform
einzeln, auch wenn msgfmt die Datei akzeptiert. ASCII-Namen lassen alle
Werkzeuge mitprüfen; die Bibliothek selbst akzeptiert jedes
`str.isidentifier()`.

In einer Ausnahme sind sich beide Checker einig: Ein `fuzzy`-Eintrag wird nicht
geprüft. Er ist eine unbestätigte Vermutung, die `pybabel compile` aus der `.mo`
heraushält, kann also gar nicht bis zu einem Rendern gelangen — und den Build an
ihm scheitern zu lassen hieße, eine Schranke so lange rot zu halten, wie eine
umformulierte Nachricht auf eine übersetzende Person wartet. Das Flag zu löschen
ist das, was den Eintrag zur Prüfung anmeldet — und zur Auslieferung.

## Templates und andere Werkzeuge { #templates-and-other-tools }

t-strings sind Python-Syntax. Jinja2 (`{% trans %}`), Django und andere
Templates behalten ihre eigenen Extraktoren und schreiben dennoch in denselben
PO-Katalog.

`pygettext` kann t-strings noch nicht parsen. Die
[Spezifikation](spec.md) erlaubt anderen Extraktoren, dieselbe Konvention zu
implementieren.
