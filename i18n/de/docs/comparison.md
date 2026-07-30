---
description: "Dieselbe übersetzbare Nachricht mit %-Format, .format() und einer t-string — und welche Kontrolle der Katalog jeweils erhält."
---

# Warum t-strings?

Jede Methode, Werte in übersetzbare Nachrichten einzusetzen, beantwortet eine
Frage: *Wie viel der Formatsprache darf der Katalog kontrollieren?*

## %-Formatierung

```python
_("Hello %(name)s") % {"name": name}
```

Der Katalog enthält printf-Syntax. Ein einziges entferntes Zeichen kann im
Produktionsbetrieb einen Fehler verursachen:

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

Der Platzhalter ist benannt und kann frei umgestellt werden. Doch
`str.format` ist eine kleine Ausdruckssprache:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ein Katalog ist Daten und durchläuft Übersetzungsplattformen und viele Hände.
`.format()` gibt ihm trotzdem Attributzugriff auf übergebene Objekte.

## t-strings

```python
tr(t"Hello {name}")
```

Der msgid bleibt `Hello {name}`. Die Übersetzung wird aber nicht als
Format-String ausgeführt, sondern gegen die Platzhalter der Quelle geprüft.
Nur einfache Namen sind erlaubt:

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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| Benannter Platzhalter | ja | ja | ja |
| Umstellung möglich | ja | ja | ja |
| Ein verlorenes Zeichen führt zum Fehler | **ja** | nein | nein |
| Katalog kontrolliert Formatierung | ja | ja | **nein** |
| Katalog kann Attribute lesen | nein | **ja** | **nein** |
| Defekter Katalog löst beim Rendern aus | **ja** | **ja** | standardmäßig [nein](guide.md#what-happens-when-a-catalog-is-wrong) |
| PO/MO und `msgfmt` funktionieren | ja | ja | ja |

## Der Preis

f-strings sind beim Aufruf bereits fertig und eignen sich daher nicht. t-strings
([PEP 750]) erfordern Python 3.14 oder neuer. Zudem muss jede Interpolation ein
einfacher Name sein:

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Diese Einschränkung liefert die Sicherheitsgarantie und gibt Übersetzenden
zugleich verständliche Platzhalternamen.

  [PEP 750]: https://peps.python.org/pep-0750/
