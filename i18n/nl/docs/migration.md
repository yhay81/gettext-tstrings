---
description: "T-strings invoeren in een project dat al gettext-catalogi heeft: wat onaangeroerd blijft, wat fuzzy wordt, en hoe je één aanroepplek tegelijk verhuist."
---

# Migratie

Gebruikt je project al gettext, dan zijn de vragen die bepalen of deze
bibliotheek bruikbaar is smalle vragen: maakt ze de catalogi die je hebt
ongeldig, kan ze samenleven met de code die je nog niet wilt veranderen, en
hoeveel van de verhuizing moet in één keer gebeuren. De antwoorden, het kortste
eerst:

| Vraag | Antwoord |
| --- | --- |
| Werken bestaande `.po`- en `.mo`-bestanden nog? | Ja. Dezelfde bestanden, dezelfde tools. |
| Kunnen oude en nieuwe aanroepen in één bestand samenleven? | Ja, en één extractor-mapping dekt beide. |
| Verandert de msgid? | Niet vanuit `.format()`. Wel vanuit `%`-format. |
| Moet het hele project in één keer over? | Nee. Eén aanroepplek is een geldige wijziging. |
| En Jinja, Django-templates, JavaScript? | Onaangeroerd, dezelfde catalogi. |

De rest van deze pagina is het detail achter elk van die antwoorden.

## Vanuit `.format()`: de msgid verandert niet { #from-format-the-msgid-does-not-change }

Dit is het geval waarin migreren vrijwel niets kost. Een `str.format`-bericht en
een t-string-bericht leiden *dezelfde* catalogussleutel af, omdat de sleutel in
beide gevallen de tekst is met `{name}` er nog in:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

De bestaande vertaling blijft er dus aan hangen. Uitgaande van een catalogus met

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

verander je de aanroep, extraheer je opnieuw, en werk je bij:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

De entry die terugkomt verschilt in twee regels metadata en verder in niets —
een markeringscommentaar dat hem als t-string-bericht aanwijst, en een
bronregelnummer:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Geen `fuzzy`-vlag, geen hervertaling, in geen enkele taal. Het bericht rendert
meteen:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` meldt de catalogi als verouderd"

    Dat markeringscommentaar en de verschoven regelnummers zijn genoeg voor
    `pybabel update --check` om te zeggen dat een catalogus opnieuw gegenereerd
    moet worden, want het vergelijkt de hele entry en niet alleen de vertaling.
    Draai de echte `pybabel update` in dezelfde commit als de codewijziging, en
    commit de catalogi ermee — dezelfde gewoonte die de
    [CI-poort](workflow.md#what-ci-gates) al vraagt.

## Vanuit `%`-format: de msgid verandert, dus vertalingen worden fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf-syntaxis leeft *binnen* het bericht, dus haar vervangen herschrijft de
catalogussleutel. Daar is geen ontkomen aan, en het is de eerlijke prijs van het
achterlaten van `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` herkent het nieuwe bericht als een naaste verwant van het
verwijderde en neemt de oude vertaling mee, gemarkeerd als fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Drie dingen om over die toestand te weten:

- **Er breekt tijdens runtime niets.** Fuzzy-entries worden uit de
  gecompileerde `.mo` weggelaten, dus de applicatie rendert het bronbericht
  totdat een mens het paar bevestigt —
  [dezelfde degradatie](workflow.md#the-cycle-after-the-first-translation) die
  elk geherformuleerd bericht doormaakt.
- **`pybabel compile` meldt er elk van**, omdat de meegenomen `%(name)s` geen
  geldige accolade-placeholder is, en eindigt met een niet-nul exitcode. Die
  lijst is je werkvoorraad, geen vals alarm; de entries erin moeten echt
  bewerkt worden.
- **De oude `python-format`-vlag lift mee** en hoort samen met de
  `fuzzy`-vlag verwijderd te worden, anders blijft `msgfmt --check-format`
  printf-regels toepassen op een brace-format-bericht.

Voor benoemde printf-placeholders is de bewerking mechanisch — `%(name)s` wordt
`{name}` en verder verschuift er niets — dus een grote catalogus is een
geautomatiseerde doorloop gevolgd door de review van een vertaler, en geen
hervertaling. Positionele `%s` is niet mechanisch: er is geen naam om mee te
nemen, en er een kiezen is juist de kern van de wijziging.

Daarom is de praktische volgorde om `%`-format-berichten weloverwogen te
migreren — een module, een release, een taal tegelijk — in plaats van in één
veeg die elke catalogus tegelijk rood kleurt.

## Oude en nieuwe aanroepen leven samen { #old-and-new-calls-coexist }

De extractor die t-strings leest, leest ook gewone gettext-aanroepen, dus één
mapping dekt een bestand middenin de migratie:

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

Beide berichten belanden in hetzelfde sjabloon, en alleen dat van de t-string
draagt het markeringscommentaar dat de extra controle van deze bibliotheek
inschakelt:

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

Ze herkent `_()`, de vier standaard gettext-namen, de aliassen `tr()` / `ntr()`,
en de uitgestelde `lazy_gettext()` / `lazy_pgettext()`. Een eigen hulpfunctie
moet [in de mapping benoemd worden](extraction.md#registering-your-own-function-names).

Tijdens runtime zijn de twee stijlen even onafhankelijk:
`gettext.translation()` geeft één vertaalobject terug, en zowel `_` als de
instappunten van deze bibliotheek lezen daaruit.

## Wat niet verhuist { #what-does-not-move }

- **Sjabloontalen.** Jinja2's `{% trans %}`, de templatetags van Django en hun
  Babel-extractors blijven ongewijzigd werken en blijven dezelfde PO-catalogi
  voeden. T-strings zijn Python-syntaxis; ze gelden voor Python-broncode.
- **Je catalogusbestanden.** Geen formaatwijziging, geen nieuw bestand, geen
  conversiestap.
- **Je vertaalplatform.** De `.po`-uitwisseling is identiek, en de vlag
  `python-brace-format` die een t-string-bericht draagt is dezelfde vlag die een
  `.format()`-bericht draagt — dus placeholder-QA blijft werken.
- **Code die geen Python is.** Een JavaScript- of C-catalogus in hetzelfde
  project blijft onaangeroerd.

## Een migratiechecklist { #a-migration-checklist }

1. Voeg de `babel`-extra toe waar `pybabel` draait, en verander de
   `python`-mapping in `babel.cfg` naar de methode `gettext_tstrings` — één
   mapping dekt dan beide stijlen, en `-k` blijft werken voor de gewone
   aanroepen.
2. Zet eerst de `.format()`-aanroepplekken om. Extraheer opnieuw, draai
   `pybabel update`, en commit de catalogi met de code; verwacht geen
   fuzzy-entries.
3. Zet de `%`-format-aanroepplekken om in porties die je gereviewd krijgt,
   herschrijf de meegenomen placeholders en wis de vlaggen `fuzzy` en
   `python-format`.
4. Repareer wat de beperking afwijst: een interpolatie moet een gewone naam
   zijn, dus `t"Hello {user.name}"` wordt eerst een lokale variabele. Dat is een
   bewerking op de aanroepplek, niet in de catalogus.
5. Zet `strict = true` aan in de extractor-mapping zodra de doorloop klaar is,
   zodat een bericht dat niet geëxtraheerd kan worden
   [de build](extraction.md#lenient-locally-strict-in-ci) laat falen in plaats
   van uit het sjabloon te verdwijnen.
6. Voeg de runtime-controle uit [In productie](workflow.md#what-ci-gates) toe:
   render één bericht per uitgeleverde taal via een strikte `Translator`.

Stap 2 en 3 zijn gewone commits. Niets in deze lijst vereist een grote
omschakeldag.
