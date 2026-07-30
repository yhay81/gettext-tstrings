---
description: "Dieselbe übersetzbare Nachricht mit %-Format, .format(), flufl.i18n-$-Strings und einem t-String, einschließlich der Art, wie sie Werte binden und einen beschädigten Katalog behandeln."
---

# Warum t-strings?

Jede Methode, Werte in übersetzbare Nachrichten einzusetzen, beantwortet eine
Frage: *Wie viel der Formatsprache darf der Katalog kontrollieren?* Die vier
folgenden Antworten unterscheiden sich auch darin, woher Werte stammen und was
geschieht, wenn ein Katalog einen Platzhalter verändert.

## %-Formatierung

```python
_("Hello %(name)s") % {"name": name}
```

Der Katalog enthält printf-Syntax, darunter einen leicht zu übersehenden
abschließenden Typbuchstaben, der durch eine Änderung an nur einem Zeichen
beschädigt werden kann:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

`msgfmt --check-format` erkennt das, aber nur bei korrekt als
`python-format` markierten Nachrichten und nur, wenn der Katalog tatsächlich
mit msgfmt geprüft wird.

## str.format

```python
_("Hello {name}").format(name=name)
```

Der abschließende Typbuchstabe entfällt, der Platzhalter bleibt benannt und frei
umstellbar.

Das Problem liegt auf der anderen Seite. `str.format` ist eine kleine
Ausdruckssprache:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ein Katalog ist Daten und durchläuft Übersetzungsplattformen und viele Hände.
`.format()` gibt ihm trotzdem Attributzugriff auf übergebene Objekte.

## `$`-Strings und flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

Die Standardbibliothek stellt mit [`string.Template`][stdlib-template] die
`$name`-Interpolationssprache bereit, ist aber selbst keine Übersetzungs-API.
[`flufl.i18n`][flufl-i18n] verbindet diesen Stil mit der gettext-Katalogsuche. Der
Namensraum für Ersetzungen wird aus den globalen und lokalen Variablen des
Aufrufers gebildet; ein optionales `extras`-Mapping hat Vorrang vor beiden.
Die Syntax für Übersetzende hat weder einen abschließenden Typbuchstaben noch
eine Formatspezifikation, und Platzhalter bleiben frei umstellbar.

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
PO/MO-Katalog. Die Quelltextextraktion ist anders: Aktuelle Werkzeuge benötigen
einen t-String-fähigen Extraktor, etwa den dieses Pakets. Eine Übersetzung wird
gegen die Platzhalter der Quellnachricht geprüft und von dieser Bibliothek
gerendert, die ausschließlich einfache Namen akzeptiert:

| Inhalt der Übersetzung | Ablehnung |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Die Formatierung bleibt in der Anwendung:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` erreicht den Katalog nie.

## Direktvergleich

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Benannter Platzhalter | ja | ja | ja | ja |
| Von Übersetzenden umstellbar | ja | ja | ja | ja |
| Werte stammen aus | explizitem Mapping | expliziten Argumenten | globalen und lokalen Variablen des Aufrufers, mit optional überschreibendem `extras` | den vom t-String erfassten Interpolationen |
| Katalog kontrolliert Wertkonvertierung oder Formatspezifikation | ja | ja | nein | nein |
| Katalog kann Attributzugriff anfordern | nein | ja | ja, mit punktierten Namen | nein |
| Quellplatzhalter beim Rendern entfernt | stillschweigend ausgelassen | stillschweigend ausgelassen | stillschweigend ausgelassen | standardmäßig [vollständig gerendertes Quellmuster](guide.md#what-happens-when-a-catalog-is-wrong) |
| Hinzugefügter Platzhalter beim Rendern nicht verfügbar | löst Ausnahme aus | löst Ausnahme aus | bleibt sichtbar | standardmäßig [vollständig gerendertes Quellmuster](guide.md#what-happens-when-a-catalog-is-wrong) |
| Quellplatzhaltermenge zur Laufzeit geprüft (Singular) | nein | nein | nein | ja |
| Von Babel für das Beispiel abgeleitetes PO-Format-Flag | `python-format` | `python-brace-format` | keines | `python-brace-format` |
| Verwendet gewöhnliche PO/MO-Kataloge | ja | ja | ja | ja |
| Benötigt einen eigenen Quelltextextraktor | nein | nein | nein | derzeit ja |

Die Zeile zum Format-Flag betrifft die platzhalterbezogene Validierung, nicht
die Katalogkompatibilität. `keines` bedeutet, dass Standard-gettext-Werkzeuge
die Nachricht weiterhin lesen und kompilieren, `msgfmt --check-format` aber
keine Grammatik für `$`-Platzhalter anwenden kann.

## Der Preis

Ein f-String kann auf diese Weise gar nicht verwendet werden: Sobald eine
Bibliothek ihn sieht, ist er bereits eine fertige Zeichenkette, sodass eine
Übersetzung nur ein Fragment übersetzen würde. t-Strings ([PEP 750]) ermöglichen
die Trennung mit f-String-ähnlicher Syntax und expliziter Wertebindung.
`$`-Strings bieten bereits eine knappe Alternative mit einem anderen Bindungs-
und Fehlermodell. `flufl.i18n` ist ein ausgereiftes Paket, dessen aktuelle
Version Python 3.10 unterstützt; `gettext-tstrings` befindet sich derzeit im
Alpha-Stadium, und native t-Strings setzen mindestens Python 3.14 voraus.

Der andere Preis ist die Einschränkung selbst: Jede Interpolation muss ein
einfacher Name sein.

```python
tr(t"Hello {user.name}")  # rejected
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
