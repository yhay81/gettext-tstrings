---
description: "Laufzeit-API: welcher Einstiegspunkt der richtige ist, Katalogbindung, Sprache pro Anfrage, verzögerte Strings, lokalisierte Werte und Umgang mit fehlerhaften Übersetzungen."
---

# Anleitung

Diese Seite ist die Laufzeitreferenz: alles, was dein *Anwendungscode* mit
dieser Bibliothek tut, sobald Kataloge existieren. Wenn du die vollständige
Schleife — markieren, extrahieren, übersetzen, kompilieren, ausführen — noch
nicht gesehen hast, geht das [Tutorial](tutorial.md) sie einmal in fünf
Minuten durch; das Erstellen und Validieren von Katalogen behandelt die
[Extraktion](extraction.md), und wie ein Team die Schleife am Laufen hält —
Update-Zyklen, CI, Übersetzungsplattformen — zeigt
[Im Produktivbetrieb](workflow.md).

## Welchen Einstiegspunkt soll ich nehmen? { #which-entry-point-should-i-use }

Das Paket exportiert mehrere Wege, eine Nachricht zu übersetzen, weil
Anwendungen eine Sprache auf sehr unterschiedliche Weise binden. Wähle danach,
wie dein Programm entscheidet, in welcher Sprache es gerade ist:

| Deine Situation | Nimm |
| --- | --- |
| Eine Sprache für den ganzen Prozess — ein CLI, eine Desktop-App, ein Skript | `Translator`, aufgerufen als `_` |
| Eine Sprache pro Anfrage oder pro async-Task — eine Webanwendung | `use_translations()` um die Arbeit herum, dann `tr()` |
| Eine beim Import definierte Nachricht — ein Formularlabel, ein Enum, eine Konstante | `lazy_gettext()` oder `lazy_pgettext()` |
| Eine Zahl entscheidet über die Formulierung | `ngettext()` / `npgettext()`, in welcher der obigen Formen auch immer |
| Ein Pattern rendern, ohne dass ein Katalog beteiligt ist | `compile_template()` |

Alles Weitere sind diese fünf, in dieser Reihenfolge.

## Einen Katalog binden { #binding-a-catalog }

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

## Sprache pro Anfrage { #per-request-language }

Ein Web-Framework wählt die Sprache pro Anfrage. Binde die Übersetzung an den
aktuellen Kontext; dann verwenden alle Modulaufrufe diese Sprache, auch bei
gleichzeitigen Anfragen.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations()` bindet ohne Block, wenn das Framework den Lebenszyklus
selbst verwaltet; `get_translations()` liest die Bindung. Ein explizites
`translations=` hat Vorrang. Ohne Bindung dienen die globalen
gettext-Funktionen der Standardbibliothek als Fallback. Ausgearbeitete
Beispiele für Flask und ASGI-Middleware stehen auf der Seite
[Im Produktivbetrieb](workflow.md#binding-a-language-at-runtime).

## Verzögerte Übersetzung { #deferred-translation }

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

`strict` wird dort entschieden, wo die Nachricht geschrieben wird, nicht dort,
wo sie gerendert wird:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Ein verzögerter String wird dort gerendert, wo er schließlich verwendet wird —
in einem Template, einem Formular, einer Logzeile — und diese Stelle weiß
selten, ob es sich um einen Testlauf oder um den Produktivbetrieb handelt.
`strict=True` bei der Definition zu übergeben, ermöglicht dieselbe Wahl
[laut in der CI, nachsichtig im Produktivbetrieb](#what-happens-when-a-catalog-is-wrong)
auch für einen String, der nicht an seiner Aufrufstelle gerendert wird.

Pluralformen hängen von einer Zahl zur Laufzeit ab und sollten sofort mit
`ngettext` gerendert werden.

## Mehrere Sprachen gleichzeitig { #several-languages-at-once }

Eine Anfrage braucht oft mehr als eine Sprache: eine Seite, die für die lesende
Person gerendert wird und zugleich eine Benachrichtigung an ein Konto einreiht,
das auf eine andere eingestellt ist, oder eine Zusammenfassung, die jede
beteiligte Person in ihrer eigenen zitiert. Bindungen verschachteln sich, und
das Verlassen des inneren Blocks stellt den äußeren wieder her.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Über eine Liste von Empfängern hinweg erledigen verzögerte Strings die Arbeit:
Die Nachricht wird einmal geschrieben, beim Import, und einmal pro Sprache
gerendert.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Die Bindung ist eine `ContextVar` und kein Stapel auf einem geteilten Objekt,
sodass sich überlappende Anfragen einander nicht die Sprache abnehmen können —
auch dann nicht, wenn sie ihre Blöcke in derselben Reihenfolge *verlassen*, in
der sie sie betreten haben, also genau in der Verschränkung, die ein
Kellerstapel falsch macht. Einen Katalog pro Sprache zu laden ist günstig:
`gettext.translation()` parst jede `.mo` einmal und gibt Kopien heraus, die
sich den geparsten Katalog teilen.

!!! warning "Ob ein Worker-Thread die Bindung erbt, hängt vom Build ab"

    Ein einfacher `threading.Thread` oder `ThreadPoolExecutor.submit` startet
    entweder mit einer Kopie des Kontexts des Aufrufers oder mit einem leeren
    Kontext; was davon gilt, entscheidet `sys.flags.thread_inherit_context` —
    auf free-threaded Builds standardmäßig wahr, sonst überall falsch.
    Derselbe Code rendert daher auf 3.14t die gebundene Sprache und auf 3.14
    den prozessglobalen Katalog. Gib den Kontext weiter, statt dich auf die
    Vorgabe zu verlassen:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` erledigt das bereits für dich.

## Lokalisierte Werte { #locale-aware-values }

Diese Bibliothek entscheidet, *wo* ein Wert in einer übersetzten Nachricht
erscheint. Sie lokalisiert den Wert selbst nicht. `{amount:,.2f}` ist eine
Python-Formatangabe mit festem Verhalten — ein Komma alle drei Stellen und ein
Punkt vor den Nachkommastellen — und erzeugt dieselben Zeichen, in welcher
Sprache die Nachricht auch steht:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Auf Deutsch schreibt man diese Zahl `1.234,50`, auf Französisch `1 234,50`, und
Hindi gruppiert `1234567` als `12,34,567` statt als `1,234,567`. Zahlen,
Währungen, Datums- und Zeitangaben sowie Einheiten gehören zu
[Babel][babel-numbers]. Formatiere den Wert zuerst und setze dann den fertigen
String ein:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Bei einer gezählten Nachricht erledigt die Zahl zwei Aufgaben — sie wählt die
Pluralform aus und sie erscheint im Text —, und nur die zweite wird
lokalisiert. Behalte die rohe Zahl für die Auswahl und übergib den formatierten
String für die Anzeige:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Vor dem Aufruf zu formatieren hält außerdem jede Formatangabe aus dem Katalog
heraus: Was eine übersetzende Person zu sehen bekommt, ist ein fertiges Stück
Text und keine Zahl samt Anweisung, wie sie darzustellen ist.

## Wenn ein Katalog fehlerhaft ist { #what-happens-when-a-catalog-is-wrong }

Wenn die Platzhalter einer Übersetzung nicht zur Quelle passen, rendert der
Standardmodus die Quellnachricht, statt eine Exception auszulösen. Das
entspricht dem gettext-Vertrag: Ein schlechter Katalog soll die Anwendung nicht
beenden.

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

Diese Meldungen sind für die Person geschrieben, die etwas an ihnen ändern
kann, und das ist bei einem Katalogproblem häufiger eine übersetzende als eine
programmierende — wo ein Platzhalter also vorhanden *aussieht*, es aber nicht
ist, erklärt die Meldung warum, statt zu wiederholen, dass er fehlt.
Vollbreite Klammern, ein verdoppeltes `{{name}}`, ein unsichtbares geschütztes
Leerzeichen, ein kyrillischer Buchstabe unter lateinischen: Jeder Fall hat
seine eigene Formulierung, aufgelistet mit Beispielen unter
[Für Übersetzende](translators.md#reading-a-failure-message). Diese Seite ist
so geschrieben, dass man sie der Person in die Hand drücken kann, die die
`.po` bearbeitet.

## Ein Pattern ohne Katalog rendern { #rendering-a-pattern-without-a-catalog }

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

## Sicherheit und Grenzen { #safety-and-scope }

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
