---
description: "De runtime-API: welk instappunt je gebruikt, een catalogus binden, talen per request, uitgestelde strings, locale-bewuste waarden, en hoe een kapotte vertaling wordt gerapporteerd."
---

# Handleiding

Deze pagina is de runtime-referentie: alles wat je *applicatiecode* met deze
bibliotheek doet zodra er catalogi bestaan. Heb je de volledige lus —
markeren, extraheren, vertalen, compileren, uitvoeren — nog niet gezien, dan
doorloopt de [tutorial](tutorial.md) hem eenmaal in vijf minuten; het
aanmaken en valideren van catalogi wordt behandeld in
[Extractie](extraction.md), en hoe een team de lus draaiende houdt —
updatecycli, CI, vertaalplatforms — staat op [In productie](workflow.md).

## Welk instappunt moet ik gebruiken? { #which-entry-point-should-i-use }

Het pakket exporteert meerdere manieren om een bericht te vertalen, omdat
applicaties op meerdere manieren een taal binden. Kies op grond van hoe jouw
programma bepaalt in welke taal het staat:

| Jouw situatie | Gebruik |
| --- | --- |
| Eén taal voor het hele proces — een CLI, een desktopapplicatie, een script | `Translator`, aangeroepen als `_` |
| Eén taal per request of per async taak — een webapplicatie | `use_translations()` om het werk heen, daarna `tr()` |
| Een bericht dat bij importtijd gedefinieerd wordt — een formulierlabel, een enum, een constante | `lazy_gettext()` of `lazy_pgettext()` |
| Een telling bepaalt de formulering | `ngettext()` / `npgettext()`, in welke vorm hierboven ook |
| Een patroon renderen zonder dat er een catalogus bij komt kijken | `compile_template()` |

Alles hieronder is die vijf, in die volgorde.

## Een catalogus binden { #binding-a-catalog }

De aanbevolen vorm spiegelt gettexts klasse-gebaseerde gebruik: bind één keer
een standaard vertaalobject en gebruik de aanroepbare processor als `_`.

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

De functies op moduleniveau volgen de namen van de standaardbibliotheek en
haar positional-only-aanroepconventie:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` en `ntr` zijn exacte aliassen van `gettext` en `ngettext`.

## Taal per request { #per-request-language }

Een webframework kiest een taal per request. Bind de vertalingen van het
request aan de huidige context en elke aanroep op moduleniveau lost op naar
die taal, veilig over gelijktijdige requests heen:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` bindt zonder `with`-blok, voor frameworks
die de request-levenscyclus zelf beheren; `get_translations()` leest de
huidige binding. Een expliciet `translations=`-argument wint altijd van de
context, en een ongebonden context valt terug op de globaal geïnstalleerde
gettext-functies van de standaardbibliotheek. Uitgewerkte voorbeelden voor
Flask en ASGI-middleware staan op de pagina
[In productie](workflow.md#binding-a-language-at-runtime).

## Uitgestelde vertaling { #deferred-translation }

Een t-string legt zijn waarden gretig vast, wat verkeerd is voor een string
die bij importtijd gedefinieerd wordt — een formulierlabel, een enum-waarde,
een moduleconstante — en die moet renderen in welke taal er ook actief is
wanneer hij *gebruikt* wordt.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Een `LazyString` rendert via `str()`, `format()` en f-strings, en is gelijk
aan zijn gerenderde tekst.

!!! note "Bewust unhashable"

    De tekst van een `LazyString` hangt af van de actieve taal, dus een hash
    zou veranderen bij een taalwissel en elke set of dict die hem bevat
    stilletjes corrumperen. Roep eerst `str()` aan als je een sleutel nodig
    hebt.

`strict` wordt beslist waar het bericht geschreven wordt, niet waar het
rendert:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Een uitgestelde string rendert waar hij uiteindelijk gebruikt wordt — in een
template, een formulier, een logregel — en die plek weet zelden of dit een
testrun of productie is. `strict=True` meegeven bij de definitie is wat
dezelfde keuze [luid in CI, mild in productie](#what-happens-when-a-catalog-is-wrong)
laat gelden voor een string die niet op zijn aanroepplek gerenderd wordt.

Meervoudsvormen hangen af van een runtime-telling, dus render die gretig met
`ngettext` waar de telling bekend is.

## Meerdere talen tegelijk { #several-languages-at-once }

Eén request heeft vaak meer dan één taal nodig: een pagina die voor de lezer
gerenderd wordt en tegelijk een melding in de wachtrij zet voor een account dat
anders is ingesteld, of een samenvatting die elke deelnemer in zijn eigen taal
citeert. Bindings nesten, en het verlaten van het binnenste blok herstelt het
buitenste.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Over een lijst ontvangers doen uitgestelde strings het werk: het bericht wordt
één keer geschreven, bij import, en rendert één keer per taal.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

De binding is een `ContextVar`, geen stapel die op een gedeeld object leeft,
dus requests die elkaar overlappen kunnen elkaars taal niet oppikken — ook niet
in het geval waarin ze hun blokken *verlaten* in de volgorde waarin ze die
binnengingen, precies de vervlechting die een pushdown-stapel fout doet. Een
catalogus per taal laden is goedkoop: `gettext.translation()` parset elke `.mo`
één keer en geeft kopieën uit die de geparste catalogus delen.

!!! warning "Of een werkthread de binding erft, hangt af van de build"

    Een kale `threading.Thread`, of `ThreadPoolExecutor.submit`, begint óf met
    een kopie van de context van de aanroeper óf met een lege, en welke van
    die twee het is, bepaalt `sys.flags.thread_inherit_context` — standaard
    waar op free-threaded builds, elders overal onwaar. Dezelfde code rendert
    dus de gebonden taal op 3.14t en de proces-globale catalogus op 3.14. Geef
    de context door in plaats van op de standaardwaarde te vertrouwen:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` doet dit al voor je.

## Locale-bewuste waarden { #locale-aware-values }

Deze bibliotheek beslist *waar* een waarde in een vertaald bericht verschijnt.
Ze lokaliseert de waarde zelf niet. `{amount:,.2f}` is een Python-format-spec
met vast gedrag — een komma per drie cijfers en een punt vóór de decimalen — en
het levert dezelfde tekens op, in welke taal het bericht ook staat:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Het Duits schrijft dat getal als `1.234,50`, het Frans als `1 234,50`, en het
Hindi groepeert `1234567` als `12,34,567` in plaats van `1,234,567`. Getallen,
valuta's, datums, tijden en eenheden horen bij [Babel][babel-numbers].
Formatteer de waarde eerst, plaats daarna de afgeronde string:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Bij een getelde zin doet het getal twee dingen — het kiest de meervoudsvorm en
het verschijnt in de tekst — en alleen het tweede wordt gelokaliseerd. Houd de
ruwe telling voor de keuze en geef de geformatteerde string door voor de
weergave:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatteren vóór de aanroep is ook wat een format-spec buiten de catalogus
houdt: wat een vertaler ziet, is een afgerond stuk tekst, geen getal plus
instructies om het te renderen.

## Wat er gebeurt als een catalogus fout is { #what-happens-when-a-catalog-is-wrong }

Als de placeholders van een vertaling niet overeenkomen met de bron — een
ontbrekend, onbekend of hervormd veld dat langs de validatie glipte, uit een
handbewerkte MO, een leverancierscatalogus of een pipeline die de checker
overslaat — is de standaard om het bronbericht te renderen in plaats van te
raisen. Dit spiegelt gettexts eigen contract dat een slechte catalogus nooit
de applicatie breekt.

Met `Hello {name}` vertaald als `こんにちは {nombre}` slaagt de render en
gaat er één waarschuwing naar de `gettext_tstrings`-logger:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

De waarschuwing vuurt één keer per bericht en patroon, niet één keer per
render, dus een kapotte catalogusentry overspoelt geen log.

Kies bewust voor luid falen in tests en CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Dezelfde opzoeking raist dan, met dezelfde zin maar zonder de helft "using
source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Deze meldingen zijn geschreven voor wie erop kan handelen, en dat is bij een
catalogusprobleem vaker een vertaler dan een programmeur — dus waar een
placeholder aanwezig lijkt maar het niet is, legt de melding uit waaróm, in
plaats van te herhalen dat hij ontbreekt. Accolades op volle breedte, een
verdubbelde `{{name}}`, een onzichtbare harde spatie, een Cyrillische letter
tussen Latijnse: elk heeft zijn eigen formulering, met voorbeelden opgesomd op
[Voor vertalers](translators.md#reading-a-failure-message). Die pagina is
geschreven om te overhandigen aan wie de `.po` bewerkt.

## Een patroon renderen zonder catalogus { #rendering-a-pattern-without-a-catalog }

`compile_template` legt dezelfde machinerie één niveau lager bloot: het zet
een t-string om in zijn msgid plus een gebonden set waarden, en rendert elk
patroon dat je het aanreikt.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` valideert volgens dezelfde regels en **raist altijd** bij een
mismatch. Er is hier geen milde modus: mildheid bestaat zodat een
*catalogus*-opzoeking kan degraderen naar de brontekst, en een patroon dat je
zelf hebt doorgegeven heeft niets om vanaf te degraderen.

## Veiligheid en reikwijdte { #safety-and-scope }

Dit is geldig:

```python
tr(t"Hello {name}")
```

Deze worden met opzet afgewezen:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Bereken eerst een betekenisvolle waarde:

```python
name = user.display_name()
tr(t"Hello {name}")
```

De beperking levert stabiele catalogussleutels op, geeft vertalers bruikbare
namen, en voorkomt dat een vertaalde string een expressietaal wordt.

De garantie is beperkt tot *structuur en opmaak*: een vertaling wordt nooit
geëvalueerd, en kan nooit attribuuttoegang, aanroepen, conversies of
format-specs toevoegen. Twee dingen blijven de verantwoordelijkheid van de
aanroeper, precies zoals bij stdlib-gettext — het **escapen** van gerenderde
uitvoer voor zijn bestemming (HTML, shell, terminal), en
**catalogusintegriteit**, aangezien een vijandige catalogus een placeholder
kan herhalen om de uitvoergrootte op te blazen, wat inherent is aan elke
placeholder-gebaseerde i18n.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
