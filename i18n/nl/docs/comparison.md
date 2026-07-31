---
description: "Hetzelfde vertaalbare bericht geschreven met %-format, .format(), flufl.i18n $-strings en een t-string, inclusief hoe elk waarden bindt en met een beschadigde catalogus omgaat."
---

# Waarom t-strings

Vier manieren om een waarde in een vertaalbaar bericht te zetten, vergeleken
op dezelfde zin. De korte versie:

- Met **%-format** wordt één door een vertaler verwijderde letter een crash
  in productie.
- Met **str.format** kan een vertaling attributen lezen van de objecten die
  je code doorgeeft — inclusief geheimen.
- Met **$-strings** (flufl.i18n) worden waarden impliciet uit de variabelen
  van de aanroepende functie gehaald, en placeholders met punten bereiken
  ook attributen.
- Met **t-strings** blijft de opmaak in je code, worden vertalingen tijdens
  runtime gecontroleerd, en valt een kapotte catalogus terug op de brontekst
  in plaats van te crashen.

De rest van deze pagina is het bewijs, methode voor methode.

!!! note "Drie partijen raken elk vertaald bericht aan"

    Een **catalogus** is het bestand met vertalingen — `.po` terwijl mensen
    het bewerken, gecompileerd tot `.mo` zodat de applicatie het kan laden
    (de [tutorial](tutorial.md) doorloopt beide). Drie partijen raken elk
    bericht aan: de **ontwikkelaar** schrijft de bronstring, een **vertaler**
    bewerkt de catalogus — vaak op een extern platform, ver van elke
    codereview — en de **applicatie** rendert de twee samen tijdens runtime.
    Elke opmaakstijl hieronder beantwoordt dezelfde vraag anders: *hoeveel
    van de formattaal mag de catalogus besturen?* In de voorbeelden is `_`
    de conventionele naam voor de vertaalfunctie, en `tr` die van deze
    bibliotheek.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Wat er mis kan gaan: één verwijderde letter in een vertaling laat het
renderen crashen.

De catalogusstring draagt printf-syntaxis, inclusief een type-letter aan het
eind — de `s` in `%(name)s` — die makkelijk over het hoofd wordt gezien en
makkelijk beschadigd raakt:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Een bewerking van één teken in een PO-editor wordt een traceback in
productie. GNU `msgfmt --check-format` vangt het wel af, maar alleen voor
berichten met de vlag `python-format`, en alleen als de catalogus op weg naar
je applicatie daadwerkelijk door msgfmt gaat.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Het verwijdert de type-letter aan het eind en behoudt een benoemde, vrij
verplaatsbare placeholder. Wat er mis kan gaan verhuist naar de andere kant
van de uitwisseling: de vertaling krijgt macht over je objecten.

`str.format` is een kleine expressietaal, en hem op een string aanroepen
betekent die string het recht geven hem te gebruiken:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Vervang nu die letterlijke strings door wat `_()` ook maar teruggeeft. Als
een vertaling van `Hello {name}` terugkomt als `{conf.api_key}`, drukt het
renderen ervan je API-sleutel af — de catalogus, niet je code, bepaalde wat
er gelezen werd. Een catalogus is geen code, maar hij reist als data: naar
een vertaalplatform, door meerdere handen, terug als een `.po`, gecompileerd
tot een `.mo`, soms geheel van buiten je project gevendord. `.format()`
geeft elke stap van die reis attribuuttoegang tot de objecten die je
doorgeeft.

## `$`-strings en flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] uit de standaardbibliotheek levert de
`$name`-interpolatietaal, maar is zelf geen vertaal-API.
[`flufl.i18n`][flufl-i18n] combineert die stijl met gettext-catalogusopzoeking.
Merk op dat de waarde nooit wordt doorgegeven: flufl.i18n bouwt de
substitutienamespace uit de globals en locals van de aanroeper — welke
variabelen er ook op de aanroepplek bestaan, ze zijn beschikbaar voor het
bericht. Een optionele `extras`-mapping krijgt voorrang boven beide. De
syntaxis richting vertalers heeft geen type-letter of format-specifier aan
het eind, en placeholders blijven vrij verplaatsbaar.

Een niet-beschikbare substitutie raist niet. Met `name = "Ada"` en geen
`nombre` in de namespace van de aanroeper rendert een catalogusvertaling van
`Hello $nombre` als `Hello $nombre`: de onopgeloste placeholder blijft
zichtbaar. Dat [gedocumenteerde gedrag][documented behavior] behoudt de rest
van het vertaalde bericht in plaats van de aanroep te laten mislukken.
Excepties die optreden bij het oplossen van een attribuut of het converteren
van een waarde kunnen nog steeds doorpropageren.

`flufl.i18n` is op één relevant punt capabeler dan een kale
`string.Template`. Zijn [aangepaste Template][custom Template] accepteert
placeholders met punten zoals `$settings.api_key`, en zijn
[translator][translator] lost die paden op tegen de waarden van de
aanroeper. Een vertaalde placeholder mag elke beschikbare local of global
van de aanroeper benoemen en, met puntsyntaxis, zijn attributen doorlopen.
Dat is handig wanneer een bericht een attribuut nodig heeft, maar maakt
tegelijk het frame van de aanroeper deel van de substitutienamespace van de
catalogus. De vergelijking hieronder beschrijft `flufl.i18n` 6.0.0, niet elk
mogelijk gebruik van `string.Template`.

Het beantwoordt ook een vraag die de andere twee opmaakstijlen volledig aan de
applicatie overlaten: *welke* taal nu actief is, en hoe je die wisselt. Een
[applicatieobject][application object] houdt een stapel talen bij,
`_.push(code)` en `_.pop()` verschuiven hem, `with _.using(code):` nest hem, en
een [strategie][strategy] vindt de catalogus bij een taalcode, zodat de
applicatie zelf nooit catalogusobjecten aanraakt. Het geval waarvoor dit
bestaat is een server die binnen één werkeenheid tekst in meer dan één taal
moet produceren — een pagina voor de lezer, een melding voor iemand wiens
account anders is ingesteld.

De stapel leeft op dat applicatieobject, dat het hele proces deelt. Twee
overlappende requests delen daardoor één stapel, en blokken die niet strikt
genest zijn *in de tijd* geven elkaar de verkeerde taal door:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Deze bibliotheek behoudt dezelfde mogelijkheid — bindings nesten en worden op
dezelfde manier afgewikkeld — maar in een `ContextVar` in plaats van een
gedeelde stapel, zodat de vervlechting hierboven per taak wordt opgelost. De
equivalenten staan op
[Meerdere talen tegelijk](guide.md#several-languages-at-once). Wat ze niet
levert is de opzoeking van taalcode naar catalogus: jij geeft een vertaalobject
door, wat in het gewone geval één aanroep van `gettext.translation()` is, en de
standaardbibliotheek cachet de geparste catalogus.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

De catalogus ziet nog steeds `Hello {name}` en blijft een gewone
PO/MO-catalogus. Het verschil is wat een vertaling *mag zeggen*, en wie dat
controleert.

Deze bibliotheek valideert elke vertaling tegen de placeholders van het
bronbericht vóór het renderen, en accepteert kale namen en niets anders.
Tegen `t"Hello {name}"`:

| Een vertaling met | wordt afgewezen met |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Afgewezen betekent niet gecrasht: standaard logt de bibliotheek een
waarschuwing en rendert ze de brontekst, zodat een slechte catalogus de
applicatie nooit neerhaalt —
[hetzelfde contract dat gettext zelf nakomt](guide.md#what-happens-when-a-catalog-is-wrong).

Opmaak blijft waar ze geschreven werd, in de code:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` bereikt de catalogus nooit, dus geen vertaling kan het veranderen,
en geen vertaler hoeft ernaar te kijken.

Nog een verschil is tooling: t-strings zijn nieuwe syntaxis, dus ze naar een
`.pot` extraheren vereist momenteel een t-string-bewuste extractor, zoals
degene die dit pakket [voor Babel levert](extraction.md).

## Naast elkaar { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Heeft de placeholder een naam? | ja | ja | ja | ja |
| Kan een vertaler placeholders verplaatsen? | ja | ja | ja | ja |
| Waar komen de waarden vandaan? | een expliciete mapping | expliciete argumenten | de lokale en globale variabelen van de aanroeper, plus optionele `extras` | de waarden die in de t-string zijn vastgelegd |
| Kan de catalogus veranderen hoe een waarde wordt opgemaakt? | ja | ja | nee | nee |
| Kan de catalogus in objecten reiken (attribuuttoegang)? | nee | ja | ja, met puntnamen | nee |
| Een vertaling *laat een placeholder vallen* — wat wordt gerenderd? | de waarde verdwijnt geruisloos | de waarde verdwijnt geruisloos | de waarde verdwijnt geruisloos | de brontekst, met een waarschuwing ([standaard](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Een vertaling *voegt* een onbekende placeholder *toe* — wat wordt gerenderd? | een exceptie | een exceptie | de placeholder blijft als tekst zichtbaar | de brontekst, met een waarschuwing ([standaard](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Worden placeholders bij het renderen gecontroleerd? | nee | nee | nee | ja (zie hieronder) |
| Welke PO-vlag leidt Babel af, zodat bestaande tools kunnen valideren? | `python-format` | `python-brace-format` | geen | `python-brace-format` |
| Gebruikt gewone PO/MO-catalogi? | ja | ja | ja | ja |
| Vereist een eigen bron-extractor? | nee | nee | nee | ja, momenteel |
| Waar leeft "de huidige taal"? | waar de applicatie hem ook neerzet | waar de applicatie hem ook neerzet | een stapel taalcodes op het gedeelde applicatieobject | een `ContextVar`, per taak of request |

Over de controle tijdens het renderen: enkelvoudige berichten worden
gecontroleerd op een exacte placeholder-overeenkomst. Meervoudsberichten
worden ook gecontroleerd, tegen de
[unie/doorsnede-regel](spec.md) die de meervoudsvormen van een doeltaal laat
afwijken van die van de bron; de striktere controle per vorm draait wanneer
catalogi worden gecompileerd ([Extractie](extraction.md)).

De rij over de format-vlag gaat over placeholder-bewuste validatie, niet
over cataloguscompatibiliteit. `geen` betekent dat standaard gettext-tools
het bericht nog steeds lezen en compileren, maar dat
`msgfmt --check-format` geen `$`-placeholder-grammatica heeft om toe te
passen.

## Wat het kost { #what-it-costs }

Een f-string kan op deze manier helemaal niet worden gebruikt — tegen de
tijd dat een bibliotheek er een ziet, is het al een afgeronde string, dus
hem vertalen betekent een fragment vertalen. t-strings ([PEP 750]) houden de
statische tekst en de waarden gescheiden, met behoud van f-string-achtige
syntaxis en expliciete waardebinding. `$`-strings bieden al een beknopt
alternatief met een ander bindings- en faalmodel. `flufl.i18n` is een
volwassen pakket dat op Python 3.10 en later draait; `gettext-tstrings` is
momenteel een alfa, en omdat t-strings nieuwe syntaxis zijn vereist het
Python 3.14 of nieuwer.

De andere kostenpost is de beperking zelf: een interpolatie moet een
gewone naam zijn.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Dat is een echte beperking. Samen met waardebinding aan de bronkant en
placeholdercontrole tijdens runtime voorkomt ze dat catalogusstrings
expressies evalueren, en houdt ze placeholdernamen betekenisvol.

Hoe Python op dit kruispunt belandde — twee PEP's met tien jaar ertussen, en
de stdlib-discussie die zonder antwoord gesloten werd — wordt met bronnen
verteld op [Achtergrond](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
