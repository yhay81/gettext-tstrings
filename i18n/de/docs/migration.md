---
description: "t-strings in einem Projekt einführen, das schon gettext-Kataloge hat: was unangetastet bleibt, was fuzzy wird und wie man eine Aufrufstelle nach der anderen umstellt."
---

# Migration

Wenn dein Projekt schon gettext verwendet, sind die Fragen, die über die
Einführbarkeit dieser Bibliothek entscheiden, eng umrissen: Entwertet sie die
Kataloge, die du hast? Kann sie neben dem Code bestehen, den du noch nicht
ändern willst? Und wie viel von der Umstellung muss auf einmal geschehen? Die
Antworten, die kürzeste zuerst:

| Frage | Antwort |
| --- | --- |
| Funktionieren vorhandene `.po`- und `.mo`-Dateien weiter? | Ja. Dieselben Dateien, dieselben Werkzeuge. |
| Dürfen alte und neue Aufrufe in einer Datei stehen? | Ja, und ein Extraktor-Mapping deckt beide ab. |
| Ändert sich der msgid? | Aus `.format()` nicht. Aus `%`-Format schon. |
| Muss das ganze Projekt auf einmal umziehen? | Nein. Eine einzige Aufrufstelle ist eine gültige Änderung. |
| Und Jinja, Django-Templates, JavaScript? | Unberührt, dieselben Kataloge. |

Der Rest dieser Seite ist das Detail hinter jeder dieser Antworten.

## Aus `.format()`: der msgid ändert sich nicht { #from-format-the-msgid-does-not-change }

Das ist der Fall, in dem die Migration fast nichts kostet. Eine
`str.format`-Nachricht und eine t-string-Nachricht leiten *denselben*
Katalogschlüssel ab, denn der Schlüssel ist so oder so der Text mit dem darin
verbliebenen `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Die vorhandene Übersetzung bleibt also daran hängen. Ausgehend von einem
Katalog mit

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

änderst du den Aufruf, extrahierst neu und aktualisierst:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Der Eintrag, der zurückkommt, unterscheidet sich in zwei Zeilen Metadaten und
sonst in nichts — ein Markierungskommentar, der ihn als t-string-Nachricht
ausweist, und eine Quellzeilennummer:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Kein `fuzzy`-Flag, keine Neuübersetzung, in keiner Sprache. Die Nachricht
rendert sofort:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` wird die Kataloge als veraltet melden"

    Dieser Markierungskommentar und die verschobenen Zeilennummern genügen
    schon, damit `pybabel update --check` sagt, ein Katalog müsse neu erzeugt
    werden, denn es vergleicht den ganzen Eintrag und nicht nur die
    Übersetzung. Führe das echte `pybabel update` im selben Commit wie die
    Codeänderung aus und committe die Kataloge mit — dieselbe Gewohnheit, um
    die die [CI-Schranke](workflow.md#what-ci-gates) ohnehin bittet.

## Aus `%`-Format: der msgid ändert sich, also werden Übersetzungen fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf-Syntax steht *innerhalb* der Nachricht, sie zu ersetzen schreibt also
den Katalogschlüssel um. Daran führt kein Weg vorbei, und das ist der ehrliche
Preis dafür, `%(name)s` hinter sich zu lassen:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` erkennt die neue Nachricht als nahe Verwandte der entfernten
und trägt die alte Übersetzung hinüber, markiert als fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Drei Dinge, die man über diesen Zustand wissen sollte:

- **Zur Laufzeit geht nichts kaputt.** fuzzy-Einträge sind von der
  kompilierten `.mo` ausgeschlossen, die Anwendung rendert also die
  Quellnachricht, bis ein Mensch das Paar bestätigt —
  [dieselbe Degradation](workflow.md#the-cycle-after-the-first-translation),
  die jede umformulierte Nachricht durchläuft.
- **Die CI bleibt grün, solange sie fuzzy sind.** Der Platzhalter-Checker
  überspringt fuzzy-Einträge, genau wie `msgfmt --check-format` es tut, denn
  ein Eintrag, der die Laufzeit gar nicht erreichen kann, sollte keinen Build
  scheitern lassen. Sobald eine übersetzende Person das Flag entfernt, wird der
  Eintrag geprüft wie jeder andere — ein in einer bestätigten Übersetzung
  stehengebliebenes `%(name)s` wird also genau dann gefunden, wenn es sonst
  anfinge zu rendern.
- **Das alte `python-format`-Flag reist mit** und sollte zusammen mit dem
  `fuzzy`-Flag gelöscht werden, sonst wendet `msgfmt --check-format` weiterhin
  Printf-Regeln auf eine brace-format-Nachricht an.

Bei benannten Printf-Platzhaltern ist die Bearbeitung mechanisch — aus
`%(name)s` wird `{name}`, und sonst bewegt sich nichts —, ein großer Katalog
ist also ein skriptgesteuerter Durchlauf mit anschließendem Review durch eine
übersetzende Person und keine Neuübersetzung. Positionsbezogenes `%s` ist
nicht mechanisch: Es hat keinen Namen, den man übernehmen könnte, und genau
diesen zu wählen ist der Zweck der Änderung.

Die Migration kann deshalb in dem Tempo laufen, das das Review zulässt: Ein
noch nicht umgestellter fuzzy-Eintrag ist ein sichtbares Stück Arbeit im
Katalog und kein kaputter Build.

## Alte und neue Aufrufe nebeneinander { #old-and-new-calls-coexist }

Der Extraktor, der t-strings liest, liest auch gewöhnliche gettext-Aufrufe;
ein Mapping deckt also eine Datei mitten in der Migration ab:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Beide Nachrichten landen in derselben Vorlage, und nur die t-string-Nachricht
trägt den Markierungskommentar, der die zusätzliche Prüfung dieser Bibliothek
einschaltet:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Erkannt werden `_()`, die vier Standard-gettext-Namen, die Aliase `tr()` /
`ntr()` sowie die verzögerten `lazy_gettext()` / `lazy_pgettext()`. Ein
eigener Helper muss
[im Mapping benannt werden](extraction.md#registering-your-own-function-names).

Zur Laufzeit sind die beiden Stile gleichermaßen unabhängig:
`gettext.translation()` liefert ein Übersetzungsobjekt, und sowohl `_` als
auch die Einstiegspunkte dieser Bibliothek lesen daraus.

## Was sich nicht bewegt { #what-does-not-move }

- **Template-Sprachen.** Jinja2s `{% trans %}`, die Template-Tags von Django
  und ihre Babel-Extraktoren arbeiten unverändert weiter und speisen dieselben
  PO-Kataloge. t-strings sind Python-Syntax; sie gelten für Python-Quelltext.
- **Deine Katalogdateien.** Kein Formatwechsel, keine neue Datei, kein
  Konvertierungsschritt.
- **Deine Übersetzungsplattform.** Der `.po`-Austausch ist identisch, und das
  `python-brace-format`-Flag, das eine t-string-Nachricht trägt, ist dasselbe
  Flag, das eine `.format()`-Nachricht trägt — die Platzhalter-QA funktioniert
  also weiter.
- **Nicht-Python-Code.** Ein JavaScript- oder C-Katalog im selben Projekt
  bleibt unberührt.

## Eine Migrations-Checkliste { #a-migration-checklist }

1. Füge das `babel`-Extra dort hinzu, wo `pybabel` läuft, und stelle das
   `python`-Mapping in `babel.cfg` auf die Methode `gettext_tstrings` um — ein
   Mapping deckt dann beide Stile ab, und `-k` funktioniert für die
   gewöhnlichen Aufrufe weiter.
2. Stelle zuerst die `.format()`-Aufrufstellen um. Neu extrahieren,
   `pybabel update` laufen lassen und die Kataloge mit dem Code committen; es
   sind keine fuzzy-Einträge zu erwarten.
3. Stelle die `%`-Format-Aufrufstellen in Portionen um, die du reviewen lassen
   kannst, schreibe dabei die übernommenen Platzhalter um und entferne die
   Flags `fuzzy` und `python-format`.
4. Repariere, was die Einschränkung ablehnt: Eine Interpolation muss ein
   einfacher Name sein, aus `t"Hello {user.name}"` wird also zuerst eine lokale
   Variable. Das ist eine Änderung an der Aufrufstelle, nicht am Katalog.
5. Schalte `strict = true` im Extraktor-Mapping ein, sobald der Durchlauf
   erledigt ist, damit eine nicht extrahierbare Nachricht
   [den Build](extraction.md#lenient-locally-strict-in-ci) scheitern lässt,
   statt aus der Vorlage zu verschwinden.
6. Ergänze die Laufzeitprüfung aus
   [Im Produktivbetrieb](workflow.md#what-ci-gates): eine Nachricht pro
   ausgelieferter Sprache durch einen strikten `Translator` rendern.

Die Schritte 2 und 3 sind gewöhnliche Commits. Nichts auf dieser Liste
braucht einen Stichtag.
