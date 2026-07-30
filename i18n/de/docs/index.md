---
description: "Vollständige t-string-Nachrichten sicher mit gettext und Babel übersetzen, ohne Formatierung in den Katalog zu verschieben."
---

# gettext-tstrings

Sichere Integration von Python-3.14+-t-strings mit gettext und Babel.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

Der Katalog erhält den vollständigen Satz `Hello {name}`. Eine Übersetzung darf
`{name}` umstellen oder wiederholen, aber weder entfernen noch neue Platzhalter
hinzufügen oder eine eigene Formatierung festlegen.

## Welches Problem wird gelöst?

Ein f-string ist bereits interpoliert, bevor ihn eine Bibliothek sieht. Eine
t-string ([PEP 750]) hält dagegen statischen Text, ausgewertete Werte,
Quellausdrücke, Konvertierungen und Formatspezifikationen getrennt — genau die
Trennung, die ein Nachrichtenkatalog braucht. Der
[Vergleich](comparison.md) zeigt die Unterschiede zu `%(name)s` und
`.format()`.

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

## Diese Website nutzt es selbst

Diese Dokumentation ist nicht nur eine übersetzte Demo. Navigation,
Theme-Beschriftungen, Copyright-Zeile und pluralabhängiger Build-Bericht werden
von `gettext-tstrings` aus PO-Katalogen gerendert. Der
[mehrsprachige Builder](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
führt bei jedem strikten Build Kontextnachrichten, benannte Platzhalter und die
Pluralregeln aller zehn Sprachen aus.

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

- **[Warum t-strings](comparison.md)** — dieselbe Nachricht auf drei Arten.
- **[Anleitung](guide.md)** — Laufzeit-API, Sprache pro Anfrage, verzögerte
  Übersetzung und fehlerhafte Kataloge.
- **[Extraktion](extraction.md)** — `pybabel`, Konfiguration und Validierung.
- **[Spezifikation](spec.md)** — stabiler Vertrag und Konformitätssuite.
- **[API](api.md)** — alle öffentlichen Exporte.

</div>

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
