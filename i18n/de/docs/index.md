---
description: "Vollständige t-string-Nachrichten sicher mit gettext und Babel übersetzen, ohne Formatierung in den Katalog zu verschieben."
---

# gettext-tstrings

Sichere Integration von Python-3.14+-t-strings mit gettext und Babel.

Schreib den Satz einmal, in deiner Quellsprache, mit dem Wert an seinem Platz:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Der Katalog erhält den vollständigen Satz `Hello {name}`. Eine Übersetzung darf
`{name}` umstellen oder wiederholen, aber weder entfernen noch neue Platzhalter
erfinden oder eine eigene Formatierung anhängen — diese Bibliothek prüft das,
und ein fehlerhafter Katalog fällt auf den Quelltext zurück, statt abzustürzen.

!!! note "Neu bei gettext? Der ganze Workflow in vier Sätzen"

    **gettext** ist der Standardweg, auf dem Software übersetzt wird, in
    Python und weit darüber hinaus. Dein Code markiert übersetzbare Strings;
    ein *Extraktor* sammelt sie in eine Vorlagendatei (`.pot`); eine
    übersetzende Person — meist keine Programmiererin — füllt pro Sprache eine
    Katalogdatei (`.po`) aus, die zu einer binären `.mo` kompiliert wird, die
    deine Anwendung zur Laufzeit lädt. Der konventionelle Name der
    Übersetzungsfunktion ist `_`, sodass sich `_(t"Hello {name}")` als
    „übersetze diesen Satz“ liest. Das **[Tutorial](tutorial.md)** geht den
    gesamten Weg — markieren, extrahieren, übersetzen, kompilieren, ausführen
    — in etwa fünf Minuten durch.

## Welches Problem wird gelöst?

Ein f-string ist bereits interpoliert, bevor ihn eine Bibliothek sieht — aus
`f"Hello {name}"` ist `"Hello Ada"` geworden, und das Übersetzen der Fragmente
um einen Wert herum zerstört die Grammatik der meisten Sprachen. Eine t-string
([PEP 750]) hält dagegen statischen Text, ausgewertete Werte, Quellausdrücke,
Konvertierungen und Formatspezifikationen getrennt — genau die Trennung, die
ein Nachrichtenkatalog braucht. Der [Vergleich](comparison.md) zeigt, was sich
dadurch gegenüber `%(name)s`, `.format()` und `$`-Strings ändert.

gettext und Babel definieren jedoch nicht, wie eine t-string in eine Nachricht
umgewandelt wird. Diese Bibliothek legt eine
[versionierte Spezifikation](spec.md) fest und liefert eine
[Konformitätssuite](spec.md#conformance) mit.

## Die getroffenen Entscheidungen

- Vollständige Nachrichten statt Satzfragmenten übersetzen.
- Nur einfache Variablennamen wie `{name}` zulassen.
- `!r` und `:.2f` unter Kontrolle der Anwendung und außerhalb des Katalogs halten.
- Bekannte Platzhalter dürfen umgestellt und wiederholt werden; Attributzugriffe
  und zusätzliche Formatierung sind nicht erlaubt.
- Vorhandene POT-, PO- und MO-Dateien sowie deren Werkzeuge weiterverwenden.

## Installation

```console
python -m pip install gettext-tstrings
```

Erfordert Python 3.14 oder neuer. Das Rendern hat **keine Abhängigkeiten** und
verwendet nur `gettext` aus der Standardbibliothek.

Extraktion und Katalogprüfung laufen über [Babel]. Installiere dafür im
Entwicklungs- oder CI-System:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Nächste Schritte

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — starte hier: vom leeren Verzeichnis zu einer
  laufenden japanischen Übersetzung in fünf Schritten, jeder Befehl mit seiner
  Ausgabe.
- **[Warum t-strings](comparison.md)** — dieselbe Nachricht auf vier Arten
  geschrieben, und was `%(name)s`, `.format()` und `$`-Strings dem Katalog
  jeweils überlassen.
- **[Anleitung](guide.md)** — die Laufzeit-API: Pluralformen, Sprache pro
  Anfrage, verzögerte Strings und was geschieht, wenn ein Katalog fehlerhaft
  ist.
- **[Extraktion](extraction.md)** — die `pybabel`-Referenz: Konfiguration,
  eigene Funktionsnamen und wie vorhandene Werkzeuge diese Kataloge ganz
  nebenbei validieren.
- **[Spezifikation](spec.md)** — die t-string-↔-msgid-Konvention als stabiler,
  versionierter Vertrag mit maschinenlesbarer Konformitätssuite.
- **[API](api.md)** — alles, was das Paket exportiert, auf einer Seite.

</div>

## Diese Website nutzt es selbst

Diese Dokumentation ist nicht nur eine übersetzte Demo. Navigation,
Theme-Beschriftungen, Copyright-Zeile und pluralabhängiger Build-Bericht werden
von `gettext-tstrings` aus PO-Katalogen gerendert. Der
[mehrsprachige Builder](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
führt bei jedem strikten Build Kontextnachrichten, benannte Platzhalter und die
Pluralregeln aller zehn Sprachen aus.

## Status

Das Projekt ist Alpha-Software. Der kleine Vertrag und die Spezifikation sollen
stabil sein; die Python-API kann sich vor einer stabilen Version noch ändern.
Benötigt werden weitere Sprachfälle, kontinuierliche Performance-Messungen und
Erfahrungen aus echten gettext- und Babel-Projekten.

[Issues und Pull Requests](https://github.com/yhay81/gettext-tstrings/issues)
sind willkommen.

## Community

- Wähle ein begrenztes
  [Good First Issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
- Stelle Nutzungsfragen in den
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Diskutiere API-Ideen in den
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lies vor einem Pull Request den
  [Beitragsleitfaden](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
