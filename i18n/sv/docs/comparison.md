---
description: "Samma översättbara meddelande skrivet med %-format, .format(), flufl.i18n $-strängar och en t-string, jämförda på översättarmisstag, katalogens befogenheter och integrationskostnad."
---

# Varför t-strings

Fyra sätt att sätta in ett värde i ett översättbart meddelande, jämförda på
samma meddelande. Alla fyra namnger sina platshållare och låter en översättare
flytta om dem; de skiljer sig i vad som händer när en översättning är fel, i
hur mycket av ditt program katalogen når, och i vad det kostar att införa dem.

Tabellerna kommer först, så att du kan hitta raden du bryr dig om och bara
läsa avsnittet bakom den.

!!! note "Tre parter rör vid varje översatt meddelande"

    En **katalog** är filen med översättningar — `.po` medan människor
    redigerar den, kompilerad till `.mo` för applikationen att läsa in
    ([handledningen](tutorial.md) går igenom båda). Tre parter rör vid varje
    meddelande: **utvecklaren** skriver källsträngen, en **översättare**
    redigerar katalogen — ofta på en extern plattform, långt från all
    kodgranskning — och **applikationen** renderar de två tillsammans vid
    körning. Varje formateringsstil nedan besvarar samma fråga olika: *hur
    mycket av formatspråket får katalogen kontrollera?* I exemplen är `_` det
    konventionella namnet på översättningsfunktionen, och `tr` är det här
    bibliotekets.

## Sida vid sida { #side-by-side }

**När en översättare gör ett misstag.** En katalog passerar genom många händer,
och det mesta som går fel i den sker av misstag:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| En översättning *tappar* en platshållare — vad renderas? | värdet försvinner tyst | värdet försvinner tyst | värdet försvinner tyst | källmeddelandet, med en varning ([som standard](guide.md#what-happens-when-a-catalog-is-wrong)) |
| En översättning *lägger till* en okänd platshållare — vad renderas? | ett undantag | ett undantag | platshållaren förblir synlig som text | källmeddelandet, med en varning ([som standard](guide.md#what-happens-when-a-catalog-is-wrong)) |
| En översättning *formaterar om* en platshållare — vad renderas? | det katalogen bad om, eller ett undantag om typbokstaven inte längre passar värdet | det katalogen bad om | går inte att uttrycka i `$`-strängar | källmeddelandet, med en varning |
| Kontrolleras platshållare vid renderingstillfället? | nej | nej | nej | ja (se nedan) |

**Vilka befogenheter katalogen har.** En översättning är data utifrån ditt
kodförråd, och varje stil ger den olika mycket makt:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Varifrån kommer värdena? | en explicit mappning | explicita argument | anroparens lokala och globala variabler, plus valfria `extras` | värdena som fångats inuti t-strängen |
| Kan katalogen ändra hur ett värde formateras? | ja | ja | nej | nej |
| Kan katalogen nå in i objekt (attributåtkomst)? | nej | ja | ja, med punktade namn | nej |
| Var bor "det aktuella språket"? | där applikationen lägger det | där applikationen lägger det | en stack av språkkoder på det delade applikationsobjektet | en `ContextVar`, per uppgift eller förfrågan |

**Vad det kostar att integrera.** Allt ovanstående är gratis om verktygen
passar; här är det de kanske inte gör:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Lägsta Python-version | vilken som helst | vilken som helst | 3.10 | **3.14** |
| Mognad | standardbiblioteket | standardbiblioteket | stabil utgåva | **alfa** |
| Använder vanliga PO/MO-kataloger? | ja | ja | ja | ja |
| Behöver en egen källextraktor? | nej | nej | nej | ja, för närvarande |
| Vilken PO-flagga härleder Babel, för befintliga verktyg att validera? | `python-format` | `python-brace-format` | ingen | `python-brace-format` |

Om kontrollen vid rendering: singularmeddelanden kontrolleras mot en exakt
platshållarmatchning. Pluralmeddelanden kontrolleras också, mot
[unions-/snittregeln](spec.md) som låter ett målspråks pluralformer skilja
sig från källans; den striktare kontrollen per form körs när kataloger
kompileras ([Extrahering](extraction.md)).

Raden om formatflaggan handlar om platshållarmedveten validering, inte om
katalogkompatibilitet. `ingen` betyder att standardverktygen för gettext
fortfarande läser och kompilerar meddelandet, men `msgfmt --check-format` har
ingen `$`-platshållargrammatik att tillämpa.

## Kompatibilitet och mognad { #compatibility-and-maturity }

Den sista tabellens två första rader är de som avgör införandet, så de är värda
att säga rakt ut i stället för som celler.

`%`-format och `.format()` är inbyggda i Python och behöver inget beroende
alls. [`flufl.i18n`][flufl-i18n] är ett moget paket, utgivet och i
produktionsbruk, som kör på Python 3.10 och senare. `gettext-tstrings` är en
**alfa** och kräver **Python 3.14 eller nyare**, eftersom t-strings är ny
syntax i 3.14 — det finns ingen bakåtport och det kan inte finnas någon. Dess
[specifikation](spec.md) är den stabila delen av det; Python-API:et kan
fortfarande röra sig före 1.0.

Vad ingen av dem kostar är katalogkompatibilitet. Alla fyra producerar vanliga
POT/PO/MO-filer som varje PO-redigerare, översättningsplattform och
GNU gettext-verktyg redan läser, så valet nedan är omvändbart på ett sätt som
ett byte av katalog*format* inte skulle vara. [Migrering](migration.md) tar upp
hur ett befintligt projekt flyttas.

Avsnitten nedan visar varje avvägning i detalj, en metod i taget.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Vad som kan gå fel: en raderad bokstav i en översättning kraschar renderingen.

Katalogsträngen bär printf-syntax, inklusive en avslutande typbokstav —
`s`:et i `%(name)s` — som är lätt att förbise och lätt att skada:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

En enteckensredigering i en PO-redigerare blir ett undantag vid körning om inte
katalogvalideringen fångar det först. GNU `msgfmt --check-format` fångar
visserligen just detta, men bara för meddelanden flaggade `python-format`, och
bara om katalogen faktiskt passerar genom msgfmt på väg till din applikation.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Det tar bort den avslutande typbokstaven men behåller en namngiven, fritt
omflyttbar platshållare. Vad som kan gå fel flyttar till andra sidan av
utbytet: översättningen får makt över dina objekt.

`str.format` är ett litet uttrycksspråk, och att anropa det på en sträng
innebär att ge strängen rätten att använda det:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ersätt nu de bokstavliga strängarna med vad `_()` än returnerar. Om en
översättning av `Hello {name}` kommer tillbaka som `{conf.api_key}`, skriver
renderingen ut din API-nyckel — katalogen, inte din kod, avgjorde vad som
lästes. En katalog är inte kod, men den reser som data: ut till en
översättningsplattform, genom flera händer, tillbaka som en `.po`, kompilerad
till en `.mo`, ibland levererad helt utifrån ditt projekt. `.format()` ger
varje steg på den resan attributåtkomst till objekten du skickar in.

## `$`-strängar och flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Standardbibliotekets [`string.Template`][stdlib-template] tillhandahåller
interpolationsspråket `$name`, men är inte i sig något översättnings-API.
[`flufl.i18n`][flufl-i18n] kombinerar den stilen med kataloguppslagning i
gettext. Lägg märke till att värdet aldrig skickas in: flufl.i18n bygger
substitutionsnamnrymden från anroparens globala och lokala variabler — vilka
variabler som än finns på anropsplatsen är tillgängliga för meddelandet. En
valfri `extras`-mappning har företräde framför båda. Dess syntax mot
översättaren har ingen avslutande typbokstav eller formatspecifikation, och
platshållarna förblir fritt omflyttbara.

En otillgänglig substitution kastar inget undantag. Med `name = "Ada"` och
ingen `nombre` i anroparens namnrymd renderas en katalogöversättning av
`Hello $nombre` som `Hello $nombre`: den oupplösta platshållaren förblir
synlig. Det [dokumenterade beteendet][documented behavior] bevarar resten av
det översatta meddelandet i stället för att låta anropet misslyckas. Undantag
som kastas medan ett attribut löses upp eller ett värde konverteras kan
fortfarande propagera.

`flufl.i18n` är mer kapabelt än en ren `string.Template` på ett relevant
sätt. Dess [anpassade Template][custom Template] accepterar punktade
platshållare som `$settings.api_key`, och dess [translator] löser upp de
sökvägarna mot anroparens värden. En översatt platshållare kan namnge vilken
tillgänglig lokal eller global variabel som helst hos anroparen och, med
punktad syntax, traversera dess attribut. Det är bekvämt när ett meddelande
behöver ett attribut, samtidigt som det gör anroparens stackram till en del
av katalogens substitutionsnamnrymd. Jämförelsen här beskriver
`flufl.i18n` 6.0.0, inte varje möjlig användning av `string.Template`.

Det besvarar också en fråga som de två andra formateringsstilarna lämnar helt
åt applikationen: *vilket* språk som är det aktuella, och hur man byter. Ett
[applikationsobjekt][application object] håller en stack av språk,
`_.push(code)` och `_.pop()` flyttar den, `with _.using(code):` nästlar, och
en [strategi][strategy] hittar katalogen för en språkkod så att applikationen
aldrig hanterar katalogobjekt själv. En server som måste producera text på mer
än ett språk under en och samma arbetsenhet — en sida för läsaren, en
avisering till någon vars konto är inställt annorlunda — är fallet det här
finns till för.

Stacken bor på det applikationsobjektet, som hela processen delar. Två
överlappande förfrågningar delar därför en och samma stack, och block som inte
är strikt nästlade *i tiden* räcker varandra fel språk:

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

Det här biblioteket behåller samma förmåga — bindningar nästlar och rullas
tillbaka på samma sätt — i en `ContextVar` i stället för i en delad stack, så
flätningen ovan löses upp per uppgift. Motsvarigheterna finns på
[Flera språk samtidigt](guide.md#several-languages-at-once). Vad det inte
tillhandahåller är uppslagningen från språkkod till katalog: du skickar in ett
översättningsobjekt, vilket i det vanliga fallet är ett enda anrop till
`gettext.translation()`, och standardbiblioteket cachar den tolkade katalogen.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

Katalogen ser fortfarande `Hello {name}` och förblir en vanlig
PO/MO-katalog. Skillnaden är vad en översättning *får säga*, och vem som
kontrollerar det.

Det här biblioteket validerar varje översättning mot källmeddelandets
platshållare före rendering, och det accepterar rena namn och ingenting
annat. Mot `t"Hello {name}"`:

| En översättning som innehåller | avvisas med |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Avvisad betyder inte kraschad: som standard loggar biblioteket en varning och
renderar källmeddelandet, så en dålig katalog fäller aldrig applikationen —
[samma kontrakt som gettext självt håller](guide.md#what-happens-when-a-catalog-is-wrong).

Formateringen stannar där den skrevs, i koden:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` når aldrig katalogen, så ingen översättning kan ändra det, och ingen
översättare behöver titta på det. Det är dock ett *fast* format, inte ett
lokaliserat — att välja siffror och avskiljare per språk är
[Babels uppgift, före anropet](guide.md#locale-aware-values).

Ytterligare en skillnad är verktygsstödet: t-strings är ny syntax, så att
extrahera dem till en `.pot` kräver för närvarande en t-string-medveten
extraktor, som den detta paket
[tillhandahåller för Babel](extraction.md).

## Vad begränsningen kostar { #the-cost-of-the-restriction }

Utöver Python-kravet är priset för allt detta en enda regel: en interpolation
måste vara ett rent namn.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Det är en verklig begränsning, och det är samma begränsning som ger garantierna
ovan. Tillsammans med värdebindning på källsidan och platshållarkontroll vid
körning hindrar den katalogsträngar från att utvärdera uttryck och håller
platshållarnamnen meningsfulla för den som översätter dem.

En f-string kan inte alls användas så här — när något bibliotek ser en är den
redan en färdig sträng, så att översätta den innebär att översätta ett
fragment. t-strings ([PEP 750]) håller den statiska texten och värdena
åtskilda med bibehållen f-string-lik syntax och explicit värdebindning.

Hur Python hamnade vid detta vägskäl — två PEP:ar med tio års mellanrum, och
stdlib-diskussionen som stängdes utan svar — berättas med källor på
[Bakgrund](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
