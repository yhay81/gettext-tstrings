---
description: "Vollständige t-string-Nachrichten sicher mit gettext und Babel übersetzen, ohne Formatierung in den Katalog zu verschieben."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Schreib den Satz einmal.<br>Übersetze ihn als Ganzes.

Sichere gettext- und Babel-Integration für Python-3.14+-t-strings — der Wert
bleibt an seinem Platz, und der Katalog sieht die ganze Nachricht:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Tutorial starten :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Warum t-strings](comparison.md){ .md-button }

Diese Website praktiziert, was sie dokumentiert: Jede Sprachausgabe —
Navigation, Beschriftungen und der pluralabhängige Build-Bericht — wird von
[`gettext-tstrings` selbst](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
aus PO-Katalogen gerendert.
{ .home-hero-note }

</div>

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

## Welches Problem wird gelöst? { #the-problem-it-solves }

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

## Die getroffenen Entscheidungen { #the-choice-it-makes }

- Vollständige Nachrichten statt Satzfragmenten übersetzen.
- Nur einfache Variablennamen wie `{name}` zulassen.
- `!r` und `:.2f` unter Kontrolle der Anwendung und außerhalb des Katalogs halten.
- Bekannte Platzhalter dürfen umgestellt und wiederholt werden; Attributzugriffe
  und zusätzliche Formatierung sind nicht erlaubt.
- Vorhandene POT-, PO- und MO-Dateien sowie deren Werkzeuge weiterverwenden.

## Installation { #install }

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

## Nächste Schritte { #where-to-go-next }

Drei Arten von Lesenden kommen hier an: jemand, der sein erstes Programm
übersetzt, jemand, der Übersetzung in ein echtes Projekt einbaut, und jemand,
der genau wissen will, warum die Maschinerie so geformt ist. Für alle gibt es
einen Weg.

**Lernen** — keine gettext-Erfahrung vorausgesetzt:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — starte hier: vom leeren Verzeichnis zu einer
  laufenden japanischen Übersetzung in fünf Schritten, jeder Befehl mit seiner
  Ausgabe.
- **[Warum t-strings](comparison.md)** — dieselbe Nachricht auf vier Arten
  geschrieben, und was `%(name)s`, `.format()` und `$`-Strings dem Katalog
  jeweils überlassen.
- **[Hintergrund](background.md)** — warum diese Bibliothek existiert:
  dreißig Jahre gettext, zwei PEPs und die stdlib-Diskussion, die ohne
  Antwort geschlossen wurde.

</div>

**Ernsthaft nutzen** — die Arbeitsreferenzen:

<div class="grid cards" markdown>

- **[Anleitung](guide.md)** — die Laufzeit-API: Pluralformen, Sprache pro
  Anfrage, verzögerte Strings und was geschieht, wenn ein Katalog fehlerhaft
  ist.
- **[Extraktion](extraction.md)** — die `pybabel`-Referenz: Konfiguration,
  eigene Funktionsnamen und wie vorhandene Werkzeuge diese Kataloge ganz
  nebenbei validieren.
- **[Im Produktivbetrieb](workflow.md)** — die Schleife, wie ein Team sie
  betreibt: der Update-Zyklus, fuzzy-Einträge, CI-Schranken,
  Übersetzungsplattformen und Sprache pro Anfrage in einer Webanwendung.
- **[API](api.md)** — alles, was das Paket exportiert, auf einer Seite.

</div>

**Verstehen** — von den Prinzipien zur Implementierung:

<div class="grid cards" markdown>

- **[Funktionsweise](internals.md)** — vom Template-Objekt aus PEP 750 zum
  gerenderten String, und die Caches, die das Prüfen billig machen.
- **[Spezifikation](spec.md)** — die t-string-↔-msgid-Konvention als stabiler,
  versionierter Vertrag mit maschinenlesbarer Konformitätssuite.

</div>

## Status { #status }

Das Projekt ist Alpha-Software. Der kleine Vertrag und die Spezifikation sollen
stabil sein; die Python-API kann sich vor einer stabilen Version noch ändern.
Benötigt werden weitere Sprachfälle, kontinuierliche Performance-Messungen und
Erfahrungen aus echten gettext- und Babel-Projekten.

[Issues und Pull Requests](https://github.com/yhay81/gettext-tstrings/issues)
sind willkommen.

## Community { #join-the-community }

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
