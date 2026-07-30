---
description: "Dieselbe übersetzbare Nachricht mit %-Format, .format(), flufl.i18n-$-Strings und einem t-String, einschließlich der Art, wie sie Werte binden und einen beschädigten Katalog behandeln."
---

# Warum t-strings?

Vier Methoden, einen Wert in eine übersetzbare Nachricht einzusetzen, am
selben Satz verglichen. Die Kurzfassung:

- Bei **%-Format** wird ein einziger in der Übersetzung gelöschter Buchstabe
  zu einem Absturz in Produktion.
- Bei **str.format** kann eine Übersetzung Attribute der Objekte lesen, die
  dein Code übergibt — einschließlich Geheimnissen.
- Bei **$-Strings** (flufl.i18n) werden Werte implizit aus den Variablen der
  aufrufenden Funktion gezogen, und punktierte Platzhalter erreichen ebenfalls
  Attribute.
- Bei **t-strings** bleibt die Formatierung in deinem Code, Übersetzungen
  werden zur Laufzeit geprüft, und ein fehlerhafter Katalog fällt auf den
  Quelltext zurück, statt abzustürzen.

Der Rest dieser Seite ist der Beleg dafür, eine Methode nach der anderen.

!!! note "Drei Parteien berühren jede übersetzte Nachricht"

    Ein **Katalog** ist die Datei mit den Übersetzungen — `.po`, solange
    Menschen sie bearbeiten, kompiliert zu `.mo`, damit die Anwendung sie
    laden kann (das [Tutorial](tutorial.md) führt durch beide). Drei Parteien
    berühren jede Nachricht: Der **Entwickler** schreibt den Quellstring, eine
    **übersetzende Person** bearbeitet den Katalog — oft auf einer externen
    Plattform, weit weg von jedem Code-Review — und die **Anwendung** rendert
    beides zusammen zur Laufzeit. Jeder Formatierungsstil unten beantwortet
    dieselbe Frage anders: *Wie viel der Formatsprache darf der Katalog
    kontrollieren?* In den Beispielen ist `_` der konventionelle Name der
    Übersetzungsfunktion und `tr` der Name dieser Bibliothek.

## %-Formatierung

```python
_("Hello %(name)s") % {"name": name}
```

Was schiefgehen kann: Ein gelöschter Buchstabe in einer Übersetzung lässt das
Rendern abstürzen.

Der Katalogstring enthält printf-Syntax, darunter einen abschließenden
Typbuchstaben — das `s` in `%(name)s` —, der leicht zu übersehen und leicht zu
beschädigen ist:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Eine Änderung an einem einzigen Zeichen in einem PO-Editor wird zu einem
Traceback in Produktion. GNU `msgfmt --check-format` erkennt das zwar, aber
nur bei Nachrichten mit dem Flag `python-format` und nur, wenn der Katalog auf
dem Weg in deine Anwendung tatsächlich msgfmt durchläuft.

## str.format

```python
_("Hello {name}").format(name=name)
```

Der abschließende Typbuchstabe entfällt, der Platzhalter bleibt benannt und frei
umstellbar. Was schiefgehen kann, wandert auf die andere Seite des Austauschs:
Die Übersetzung gewinnt Macht über deine Objekte.

`str.format` ist eine kleine Ausdruckssprache, und sie auf einen String
anzuwenden heißt, diesem String das Recht zu geben, sie zu benutzen:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ersetze diese Literalstrings nun durch das, was `_()` zurückgibt. Kommt eine
Übersetzung von `Hello {name}` als `{conf.api_key}` zurück, gibt das Rendern
deinen API-Schlüssel aus — der Katalog, nicht dein Code, hat entschieden, was
gelesen wurde. Ein Katalog ist kein Code, aber er reist wie Daten: hinaus zu
einer Übersetzungsplattform, durch viele Hände, zurück als `.po`, kompiliert
zu einer `.mo`, manchmal komplett von außerhalb des Projekts übernommen.
`.format()` gibt jeder Station dieser Reise Attributzugriff auf die
übergebenen Objekte.

## `$`-Strings und flufl.i18n

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Die Standardbibliothek stellt mit [`string.Template`][stdlib-template] die
`$name`-Interpolationssprache bereit, ist aber selbst keine Übersetzungs-API.
[`flufl.i18n`][flufl-i18n] verbindet diesen Stil mit der gettext-Katalogsuche.
Beachte, dass der Wert nie übergeben wird: flufl.i18n bildet den Namensraum
für Ersetzungen aus den globalen und lokalen Variablen des Aufrufers — jede am
Aufrufort vorhandene Variable steht der Nachricht zur Verfügung. Ein
optionales `extras`-Mapping hat Vorrang vor beiden. Die Syntax für
Übersetzende hat weder einen abschließenden Typbuchstaben noch eine
Formatspezifikation, und Platzhalter bleiben frei umstellbar.

Eine nicht verfügbare Ersetzung löst keine Ausnahme aus. Bei `name = "Ada"` und
ohne `nombre` im Namensraum des Aufrufers wird die Katalogübersetzung
`Hello $nombre` als `Hello $nombre` gerendert: Der nicht aufgelöste Platzhalter
bleibt sichtbar. Dieses [dokumentierte Verhalten] erhält den Rest der
übersetzten Nachricht, statt den Aufruf scheitern zu lassen. Ausnahmen beim
Auflösen eines Attributs oder beim Konvertieren eines Werts können sich
weiterhin fortpflanzen.

In einem relevanten Punkt kann `flufl.i18n` mehr als ein unverändertes
`string.Template`. Sein [angepasstes Template] akzeptiert punktierte Platzhalter
wie `$settings.api_key`, und sein [Übersetzer] löst diese Pfade anhand der Werte
des Aufrufers auf. Ein übersetzter Platzhalter kann jede verfügbare lokale oder
globale Variable des Aufrufers benennen und mit Punktsyntax ihre Attribute
durchlaufen. Das ist praktisch, wenn eine Nachricht ein Attribut benötigt,
macht aber zugleich den Frame des Aufrufers zum Teil des
Ersetzungsnamensraums des Katalogs. Der folgende Vergleich beschreibt
`flufl.i18n` 6.0.0, nicht jede mögliche Verwendung von `string.Template`.

## t-strings

```python
tr(t"Hello {name}")
```

Der Katalog sieht weiterhin `Hello {name}` und bleibt ein gewöhnlicher
PO/MO-Katalog. Der Unterschied liegt darin, was eine Übersetzung *sagen darf* —
und wer das prüft.

Diese Bibliothek validiert jede Übersetzung vor dem Rendern gegen die
Platzhalter der Quellnachricht und akzeptiert ausschließlich einfache Namen.
Gegen `t"Hello {name}"`:

| Inhalt der Übersetzung | Ablehnung |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Abgelehnt heißt nicht abgestürzt: Standardmäßig protokolliert die Bibliothek
eine Warnung und rendert den Quelltext, sodass ein schlechter Katalog die
Anwendung nie zu Fall bringt —
[derselbe Vertrag, den gettext selbst einhält](guide.md#what-happens-when-a-catalog-is-wrong).

Die Formatierung bleibt, wo sie geschrieben wurde — im Code:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` erreicht den Katalog nie, keine Übersetzung kann es also ändern, und
niemand muss es beim Übersetzen ansehen.

Ein weiterer Unterschied ist das Tooling: t-strings sind neue Syntax, ihre
Extraktion in eine `.pot` benötigt daher derzeit einen t-string-fähigen
Extraktor, etwa den, den dieses Paket
[für Babel bereitstellt](extraction.md).

## Direktvergleich

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Ist der Platzhalter benannt? | ja | ja | ja | ja |
| Können Übersetzende Platzhalter umstellen? | ja | ja | ja | ja |
| Woher stammen die Werte? | aus einem expliziten Mapping | aus expliziten Argumenten | aus den lokalen und globalen Variablen des Aufrufers, plus optionalem `extras` | aus den im t-String erfassten Werten |
| Kann der Katalog ändern, wie ein Wert formatiert wird? | ja | ja | nein | nein |
| Kann der Katalog in Objekte hineingreifen (Attributzugriff)? | nein | ja | ja, mit punktierten Namen | nein |
| Eine Übersetzung *entfernt* einen Platzhalter — was wird gerendert? | der Wert verschwindet stillschweigend | der Wert verschwindet stillschweigend | der Wert verschwindet stillschweigend | der Quelltext, mit einer Warnung ([standardmäßig](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Eine Übersetzung *fügt* einen unbekannten Platzhalter hinzu — was wird gerendert? | eine Ausnahme | eine Ausnahme | der Platzhalter bleibt als Text sichtbar | der Quelltext, mit einer Warnung ([standardmäßig](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Werden Platzhalter beim Rendern geprüft? | nein | nein | nein | ja (siehe unten) |
| Welches PO-Flag leitet Babel ab, damit vorhandene Werkzeuge validieren können? | `python-format` | `python-brace-format` | keines | `python-brace-format` |
| Verwendet gewöhnliche PO/MO-Kataloge? | ja | ja | ja | ja |
| Benötigt einen eigenen Quelltextextraktor? | nein | nein | nein | derzeit ja |

Zur Prüfung beim Rendern: Singularnachrichten werden auf eine exakte
Übereinstimmung der Platzhalter geprüft. Pluralnachrichten werden ebenfalls
geprüft, gegen die [Vereinigungs-/Schnittmengenregel](spec.md), die den
Pluralformen der Zielsprache erlaubt, von denen der Quellsprache abzuweichen;
die strengere Prüfung pro Form läuft beim Kompilieren der Kataloge
([Extraktion](extraction.md)).

Die Zeile zum Format-Flag betrifft die platzhalterbezogene Validierung, nicht
die Katalogkompatibilität. `keines` bedeutet, dass Standard-gettext-Werkzeuge
die Nachricht weiterhin lesen und kompilieren, `msgfmt --check-format` aber
keine Grammatik für `$`-Platzhalter anwenden kann.

## Der Preis

Ein f-String kann auf diese Weise gar nicht verwendet werden: Sobald eine
Bibliothek ihn sieht, ist er bereits eine fertige Zeichenkette, sodass eine
Übersetzung nur ein Fragment übersetzen würde. t-Strings ([PEP 750]) halten
statischen Text und Werte getrennt, bei f-String-ähnlicher Syntax und
expliziter Wertebindung. `$`-Strings bieten bereits eine knappe Alternative mit
einem anderen Bindungs- und Fehlermodell. `flufl.i18n` ist ein ausgereiftes
Paket, das auf Python 3.10 und neuer läuft; `gettext-tstrings` befindet sich
derzeit im Alpha-Stadium und setzt, weil t-strings neue Syntax sind,
Python 3.14 oder neuer voraus.

Der andere Preis ist die Einschränkung selbst: Jede Interpolation muss ein
einfacher Name sein.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Das ist eine echte Einschränkung. Zusammen mit der quellseitigen Wertebindung
und der Laufzeitprüfung der Platzhalter verhindert sie, dass Katalogstrings
Ausdrücke auswerten, und hält die Platzhalternamen aussagekräftig.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [dokumentierte Verhalten]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [angepasstes Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [Übersetzer]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
