---
description: "Vollständige t-string-Nachrichten über gettext und Babel übersetzen, mit den Werten und der Formatierung außerhalb des Katalogs."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Vollständige Nachrichten übersetzen<br>mit den t-strings von Python

`gettext-tstrings` verbindet die t-strings von Python 3.14+ mit gewöhnlichen
gettext-Katalogen und dem Babel-Werkzeug. Werte und Formatierung bleiben im
Anwendungscode; übersetzende Personen arbeiten mit vollständigen Nachrichten und
einfachen `{name}`-Platzhaltern:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Der Katalog enthält `Hello {name}`. Eine Übersetzung darf `{name}` umstellen oder
wiederholen. Entfernt, benennt oder formatiert sie den Platzhalter um, meldet die
Katalogprüfung den Fehler. Schafft es ein ungültiger Eintrag trotzdem in die
Produktion, protokolliert die Bibliothek eine Warnung und rendert die
Ursprungsnachricht, statt abzustürzen.

[Das Fünf-Minuten-Tutorial starten :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Die Alternativen vergleichen](comparison.md){ .md-button }

Alpha · Python 3.14+ · standardkonforme PO/MO-Kataloge · keine Laufzeitabhängigkeiten von Dritten
{ .home-facts }

Diese Website praktiziert, was sie dokumentiert: Jede Sprachausgabe —
Navigation, Beschriftungen und der pluralabhängige Build-Bericht — wird von
[`gettext-tstrings` selbst](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
aus PO-Katalogen gerendert.
{ .home-hero-note }

</div>

## Ist das etwas für dich? { #is-this-for-you }

**Heute passend, wenn** deine Anwendung auf Python 3.14 oder neuer läuft, du
gettext und Babel bereits nutzt oder deren PO/MO-Workflow übernehmen willst, und
du t-string-Syntax mit benannten Platzhaltern möchtest, die vor dem Rendern
geprüft werden.

**Noch nicht passend, wenn** du Python 3.13 oder älter brauchst; wenn du eine
stabile Python-API benötigst — dies ist eine Alpha, und die
[Spezifikation](spec.md) ist der bereits gefestigte Teil davon; oder wenn fast
dein gesamter übersetzbarer Text in einer Template-Sprache statt im
Python-Quelltext steht.

Du hast bereits Kataloge? Sie funktionieren weiter.
`_("Hello {name}").format(name=name)` und `tr(t"Hello {name}")` erzeugen
denselben msgid, sodass vorhandene Übersetzungen den Wechsel überleben — die
[Migration](migration.md) beschreibt den ganzen Umzug.

## Was der Katalog sagen darf { #what-the-catalog-may-say }

**Eine Übersetzung kann die Struktur der Nachricht, die sie übersetzt, nicht
verändern.** Das ist das ganze Versprechen, und der Rest dieser Website folgt
daraus. Eine Übersetzung darf `{name}` umstellen oder wiederholen und darf jedes
andere Wort darum herum neu schreiben. Sie darf den Platzhalter nicht entfernen,
keinen neuen erfinden, nicht durch ihn hindurch auf deine Objekte zugreifen und
keine eigene Formatierung anhängen.

Die Bibliothek prüft das auf dem Weg hinein — wenn Kataloge kompiliert werden —
und noch einmal beim Rendern, und das ist der Unterschied zwischen einem Fehler,
der im Review gefunden wird, und einem, den eine nutzende Person findet.

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
ein Nachrichtenkatalog braucht.
[Was sich dadurch ändert](comparison.md), verglichen mit `%(name)s`, `.format()`
und `$`-Strings.

gettext und Babel definieren jedoch nicht, wie eine t-string in eine Nachricht
umgewandelt wird. Diese Bibliothek trifft diese Entscheidung, schreibt sie als
[versionierte Spezifikation](spec.md) fest und liefert die
[Konformitätssuite](spec.md#conformance) mit, um sie zu prüfen.

## Die Entwurfsregeln { #the-design-rules }

- Vollständige Nachrichten statt Satzfragmenten übersetzen.
- Nur einfache Variablennamen wie `{name}` zulassen.
- `!r` und `:.2f` unter Kontrolle der Anwendung und außerhalb des Katalogs halten.
- Bekannte Platzhalter dürfen umgestellt und wiederholt werden; Attributzugriffe
  und zusätzliche Formatierung sind nicht erlaubt.
- Vorhandene POT-, PO- und MO-Dateien sowie deren Werkzeuge weiterverwenden.

Und die dazu passende Liste dessen, was sie bewusst nicht anfasst: Sie
lokalisiert weder Zahlen noch Währungen oder Daten —
[formatiere die vorher](guide.md#locale-aware-values) mit Babel; sie maskiert
gerenderte Ausgabe nicht für HTML, eine Shell oder ein Terminal; und sie kann
nicht beurteilen, ob eine Übersetzung *richtig* ist, sondern nur, ob deren
Platzhalter unversehrt sind.

## Installation { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 oder neuer. **Das Rendern hat keine Abhängigkeiten** — es verwendet
nur `gettext` aus der Standardbibliothek und sonst nichts.

Extraktion und Katalogprüfung laufen über [Babel]. Installiere dieses Extra
überall dort, wo `pybabel` läuft, also üblicherweise in einer Entwicklungs- oder
CI-Umgebung statt in einem Produktiv-Image:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Nächste Schritte { #where-to-go-next }

**Erste Schritte** — keine gettext-Erfahrung vorausgesetzt:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — vom leeren Verzeichnis zu einer laufenden
  japanischen Übersetzung in fünf Schritten, jeder Befehl mit seiner Ausgabe.
- **[Warum t-strings](comparison.md)** — dieselbe Nachricht auf vier Arten
  geschrieben, und was `%(name)s`, `.format()` und `$`-Strings dem Katalog
  jeweils überlassen.

</div>

**Einsetzen** — die Arbeitsreferenzen:

<div class="grid cards" markdown>

- **[Anleitung](guide.md)** — die Laufzeit-API: welcher Einstiegspunkt wofür,
  Pluralformen, Sprache pro Anfrage, verzögerte Strings und was geschieht, wenn
  ein Katalog fehlerhaft ist.
- **[Extraktion](extraction.md)** — die `pybabel`-Referenz: Konfiguration,
  eigene Funktionsnamen und wie vorhandene Werkzeuge diese Kataloge ganz
  nebenbei validieren.
- **[Im Produktivbetrieb](workflow.md)** — die Schleife, wie ein Team sie
  betreibt: der Update-Zyklus, fuzzy-Einträge, CI-Schranken,
  Übersetzungsplattformen und das Ausliefern.
- **[Migration](migration.md)** — wie du das in einem Projekt einführst, das
  schon Kataloge hat, eine Aufrufstelle nach der anderen.
- **[Für Übersetzende](translators.md)** — eine Seite, die du allen in die Hand
  geben kannst, die die `.po`-Dateien bearbeiten.

</div>

**Hintergrundwissen** — von der Geschichte zur Implementierung:

<div class="grid cards" markdown>

- **[Hintergrund](background.md)** — warum diese Bibliothek existiert: dreißig
  Jahre gettext, zwei PEPs und die stdlib-Diskussion, die ohne Antwort
  geschlossen wurde.
- **[Fallstricke](pitfalls.md)** — was beim Übersetzen dieser Website in
  fünfunddreißig Sprachen tatsächlich kaputtgegangen ist, und welche Hälfte
  davon ein Werkzeug fangen kann.
- **[Funktionsweise](internals.md)** — vom Template-Objekt aus PEP 750 zum
  gerenderten String, und die Caches, die das Prüfen billig machen.

</div>

**Nachschlagen** — die Verträge:

<div class="grid cards" markdown>

- **[API](api.md)** — alles, was das Paket exportiert, auf einer Seite.
- **[Spezifikation](spec.md)** — die t-string-↔-msgid-Konvention als stabiler,
  versionierter Vertrag mit maschinenlesbarer Konformitätssuite.

</div>

## Status { #status }

| | |
| --- | --- |
| Paketversion | 0.1.0a7 |
| API-Stabilität | Alpha — die Python-API kann sich noch ändern |
| [Spezifikation](spec.md) | v1, mit einer [Konformitätssuite](spec.md#conformance) |
| Python | 3.14 und neuer; getestet auf 3.14, 3.14t (free-threaded) und 3.15 |
| Babel | 2.18 oder neuer, und nur dort, wo `pybabel` läuft |
| Laufzeitabhängigkeiten | keine — das `gettext` der Standardbibliothek |
| Katalogformat | gewöhnliches POT, PO und MO |
| Änderungen | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Eine Alpha. Der Vertrag ist absichtlich klein, und die
[Spezifikation](spec.md) ist der stabile Teil davon; die Python-API kann sich
noch bewegen. Vor einer stabilen Version braucht es breitere Sprachfixtures,
kontinuierliche Performance-Messungen, eine API-Durchsicht von Leuten, die
gettext und Babel ernsthaft einsetzen, und Kompatibilitätstests über jede
unterstützte Python- und Babel-Version.

[Issues und Pull Requests](https://github.com/yhay81/gettext-tstrings/issues)
sind willkommen — eine Alpha ist genau der Zeitpunkt, zu dem über die
Schnittstelle noch zu streiten lohnt.

## Community { #join-the-community }

- Wähle ein begrenztes
  [Good First Issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
- Stelle Nutzungsfragen in den
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Bring produktive gettext-Workflows und API-Ideen in die
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lies vor einem Pull Request den
  [Beitragsleitfaden](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
