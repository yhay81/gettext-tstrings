---
description: "Laufzeit-API: Katalogbindung, Sprache pro Anfrage, verzögerte Strings und Umgang mit fehlerhaften Übersetzungen."
---

# Anleitung

Diese Seite ist die Laufzeitreferenz: alles, was dein *Anwendungscode* mit
dieser Bibliothek tut, sobald Kataloge existieren. Wenn du die vollständige
Schleife — markieren, extrahieren, übersetzen, kompilieren, ausführen — noch
nicht gesehen hast, geht das [Tutorial](tutorial.md) sie einmal in fünf
Minuten durch; das Erstellen und Validieren von Katalogen behandelt die
[Extraktion](extraction.md).

## Einen Katalog binden

Die empfohlene Form entspricht der objektorientierten gettext-Nutzung: Binde
ein Standard-Übersetzungsobjekt einmal und verwende den aufrufbaren Prozessor
als `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Die Modulfunktionen folgen den Namen und Positionsargumenten der
Standardbibliothek:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` und `ntr` sind exakte Aliase für `gettext` und `ngettext`.

## Sprache pro Anfrage

Ein Web-Framework wählt die Sprache pro Anfrage. Binde die Übersetzung an den
aktuellen Kontext; dann verwenden alle Modulaufrufe diese Sprache, auch bei
gleichzeitigen Anfragen.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations()` bindet ohne Block, wenn das Framework den Lebenszyklus
selbst verwaltet; `get_translations()` liest die Bindung. Ein explizites
`translations=` hat Vorrang. Ohne Bindung dienen die globalen
gettext-Funktionen der Standardbibliothek als Fallback.

## Verzögerte Übersetzung

Eine t-string erfasst ihre Werte sofort. Für Labels, Enums oder Konstanten, die
beim Import definiert, aber erst bei der *Nutzung* in der aktiven Sprache
gerendert werden, gibt es verzögerte Strings.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` rendert über `str()`, `format()` und f-strings und vergleicht sich
mit seinem Text.

!!! note "Absichtlich nicht hashbar"

    Sein Text hängt von der Sprache ab. Ein sich ändernder Hash würde Sets und
    Dictionaries unbemerkt beschädigen. Für Schlüssel zuerst `str()` aufrufen.

Pluralformen hängen von einer Zahl zur Laufzeit ab und sollten sofort mit
`ngettext` gerendert werden.

## Wenn ein Katalog fehlerhaft ist { #what-happens-when-a-catalog-is-wrong }

Wenn die Platzhalter einer Übersetzung nicht zur Quelle passen, rendert der
Standardmodus den Quelltext, statt eine Exception auszulösen. Das entspricht
dem gettext-Vertrag: Ein schlechter Katalog soll die Anwendung nicht beenden.

Ist `Hello {name}` als `こんにちは {nombre}` übersetzt, gelingt das Rendern und
der Logger `gettext_tstrings` erhält eine Warnung:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Die Warnung erscheint nur einmal pro Nachricht und Pattern, nicht einmal pro
Rendern; ein fehlerhafter Katalogeintrag flutet also kein Log. In Tests und CI
sollte
der strikte Modus aktiv sein:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Dann löst dieselbe Suche aus:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Fehlermeldungen lesen

Die Meldungen erklären auch, warum ein sichtbarer Platzhalter ungültig ist:

| Übersetzung enthält | Grund |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Ein unsichtbares geschütztes Leerzeichen wird als Codepoint dargestellt:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ein Homoglyph aus einem anderen Alphabet erscheint lesbar und zusätzlich
maskiert:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Das gilt auch für Konflikte zwischen rein griechischen oder kyrillischen Namen
und ihren ASCII-Pendants.

## Ein Pattern ohne Katalog rendern

`compile_template` erzeugt den msgid und bindet Werte; anschließend kann ein
Pattern gerendert werden:

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validiert nach denselben Regeln und **löst bei Abweichungen immer
aus**. Ohne Katalogsuche gibt es keinen Fallback.

## Sicherheit und Grenzen

Gültig:

```python
tr(t"Hello {name}")
```

Absichtlich abgelehnt:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Werte vorher explizit berechnen:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Eine Übersetzung wird nie ausgewertet und kann weder Attributzugriffe noch
Aufrufe, Konvertierungen oder Formate hinzufügen. Wie bei normalem gettext
bleibt die Anwendung für **Escaping am Ausgabeziel** und
**Katalogintegrität** verantwortlich.
