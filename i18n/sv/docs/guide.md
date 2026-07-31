---
description: "Körnings-API:et: vilken ingång du ska använda, binda en katalog, språk per förfrågan, uppskjutna strängar, lokalanpassade värden, och hur en trasig översättning rapporteras."
---

# Guide

Den här sidan är körningsreferensen: allt din *applikationskod* gör med det
här biblioteket när kataloger väl finns. Om du ännu inte sett hela
kretsloppet — markera, extrahera, översätta, kompilera, köra — går
[handledningen](tutorial.md) igenom det en gång på fem minuter; att skapa och
validera kataloger täcks i [Extrahering](extraction.md), och hur ett team
håller kretsloppet snurrande — uppdateringscykler, CI,
översättningsplattformar — är [I produktion](workflow.md).

## Vilken ingång ska jag använda? { #which-entry-point-should-i-use }

Paketet exporterar flera sätt att översätta ett meddelande, eftersom
applikationer binder ett språk på flera olika sätt. Välj utifrån hur ditt
program avgör vilket språk det befinner sig i:

| Din situation | Använd |
| --- | --- |
| Ett språk för hela processen — ett CLI, ett skrivbordsprogram, ett skript | `Translator`, anropad som `_` |
| Ett språk per förfrågan eller per async-uppgift — en webbapplikation | `use_translations()` runt arbetet, sedan `tr()` |
| Ett meddelande som definieras vid importtillfället — en formuläretikett, ett enum, en konstant | `lazy_gettext()` eller `lazy_pgettext()` |
| Ett antal avgör formuleringen | `ngettext()` / `npgettext()`, i vilken av formerna ovan som helst |
| Rendering av ett mönster utan någon katalog inblandad | `compile_template()` |

Allt nedanför är de fem, i den ordningen.

## Binda en katalog { #binding-a-catalog }

Den rekommenderade formen speglar gettexts klassbaserade användning: bind ett
standardöversättningsobjekt en gång och använd den anropbara processorn som
`_`.

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

Funktionerna på modulnivå följer standardbibliotekets namn och dess
konvention med enbart positionsargument:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` och `ntr` är exakta alias för `gettext` och `ngettext`.

## Språk per förfrågan { #per-request-language }

Ett webbramverk väljer språk per förfrågan. Bind förfrågans översättningar
till den aktuella kontexten så löses varje anrop på modulnivå upp till det
språket, säkert över samtidiga förfrågningar:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` binder utan ett `with`-block, för ramverk
som själva hanterar förfrågans livscykel; `get_translations()` läser den
aktuella bindningen. Ett explicit `translations=`-argument vinner alltid över
kontexten, och en obunden kontext faller tillbaka till standardbibliotekets
globalt installerade gettext-funktioner. Utarbetade exempel för Flask och
ASGI-middleware finns på sidan
[I produktion](workflow.md#binding-a-language-at-runtime).

## Uppskjuten översättning { #deferred-translation }

En t-string fångar sina värden ivrigt, vilket är fel för en sträng som
definieras vid importtillfället — en formuläretikett, ett enum-värde, en
modulkonstant — och som måste rendera på det språk som är aktivt när den
*används*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

En `LazyString` renderar genom `str()`, `format()` och f-strings, och jämförs
lika med sin renderade text.

!!! note "Avsiktligt ohashbar"

    En `LazyString`s text beror på det aktiva språket, så en hash skulle
    ändras vid ett språkbyte och i tysthet korrumpera varje mängd eller
    ordbok som håller den. Anropa `str()` först om du behöver en nyckel.

`strict` avgörs där meddelandet skrivs, inte där det renderas:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

En uppskjuten sträng renderas där den till slut används — inuti en mall, ett
formulär, en loggrad — och den platsen vet sällan om detta är en testkörning
eller produktion. Att skicka med `strict=True` vid definitionen är det som
låter samma val mellan
[högljutt i CI och överseende i produktion](#what-happens-when-a-catalog-is-wrong)
gälla även för en sträng som inte renderas på sin anropsplats.

Pluralformer beror på ett antal vid körning, så rendera dem ivrigt med
`ngettext` där antalet är känt.

## Flera språk samtidigt { #several-languages-at-once }

En och samma förfrågan behöver ofta mer än ett språk: en sida renderad för
läsaren som också köar en avisering till ett konto inställt på ett annat, eller
ett sammandrag som citerar varje deltagare på deras eget. Bindningar nästlar,
och att lämna det inre blocket återställer det yttre.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Över en lista av mottagare gör uppskjutna strängar jobbet: meddelandet skrivs
en gång, vid importtillfället, och renderas en gång per språk.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Bindningen är en `ContextVar`, inte en stack som hålls på ett delat objekt, så
förfrågningar som överlappar inte kan plocka upp varandras språk — inklusive
fallet där de *lämnar* sina block i den ordning de gick in i dem, vilket är den
flätning en pushdown-stack får om bakfoten. Att läsa in en katalog per språk är
billigt: `gettext.translation()` tolkar varje `.mo` en gång och delar ut kopior
som delar den tolkade katalogen.

!!! warning "Om en arbetstråd ärver bindningen beror på bygget"

    En naken `threading.Thread`, eller `ThreadPoolExecutor.submit`, startar
    antingen från en kopia av anroparens kontext eller från en tom, och vilken
    av dem det blir är `sys.flags.thread_inherit_context` — sann som standard i
    free-threaded-byggen, falsk överallt annars. Samma kod renderar därför det
    bundna språket på 3.14t och den processglobala katalogen på 3.14. Skicka
    med kontexten i stället för att förlita dig på standardvärdet:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` gör redan detta åt dig.

## Lokalanpassade värden { #locale-aware-values }

Det här biblioteket avgör *var* ett värde hamnar i ett översatt meddelande. Det
lokaliserar inte värdet självt. `{amount:,.2f}` är en Python-formatspecifikation
med fast beteende — ett komma var tredje siffra och en punkt före decimalerna —
och den ger samma tecken oavsett vilket språk meddelandet är på:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Tyskan skriver det talet `1.234,50`, franskan `1 234,50`, och hindi grupperar
`1234567` som `12,34,567` snarare än `1,234,567`. Tal, valutor, datum, tider
och enheter hör hemma hos [Babel][babel-numbers]. Formatera värdet först,
placera sedan den färdiga strängen:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

I ett räknat meddelande gör talet två jobb — det väljer pluralform och det syns
i texten — och bara det andra lokaliseras. Behåll det råa antalet för valet och
skicka in den formaterade strängen för visning:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Att formatera före anropet är också det som håller en formatspecifikation
utanför katalogen: vad en översättare ser är en färdig textbit, inte ett tal
plus instruktioner för hur det ska renderas.

## Vad som händer när en katalog är fel { #what-happens-when-a-catalog-is-wrong }

Om en översättnings platshållare inte matchar källan — ett saknat, okänt
eller omformaterat fält som slunkit förbi valideringen, från en handredigerad
MO, en leverantörskatalog eller en pipeline som hoppar över kontrollen — är
standardbeteendet att rendera källmeddelandet i stället för att kasta undantag.
Detta speglar gettexts eget kontrakt att en dålig katalog aldrig knäcker
applikationen.

Med `Hello {name}` översatt som `こんにちは {nombre}` lyckas renderingen och
en varning går till loggern `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Varningen utlöses en gång per meddelande och mönster, inte en gång per
rendering, så en trasig katalogpost översvämmar inte en logg.

Välj att fela högljutt för tester och CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Samma uppslagning kastar då undantag, med samma mening utan halvan "using
source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

De här meddelandena skrivs för den som kan agera på dem, vilket för ett
katalogproblem oftare är en översättare än en programmerare — så där en
platshållare ser ut att finnas men inte gör det förklarar meddelandet varför i
stället för att upprepa att den saknas. Klamrar i helbredd, ett dubblerat
`{{name}}`, ett osynligt hårt mellanslag, en kyrillisk bokstav bland latinska:
var och en har sin egen formulering, listade med exempel på
[För översättare](translators.md#reading-a-failure-message). Den sidan är
skriven för att räckas över till den som redigerar `.po`-filen.

## Rendera ett mönster utan katalog { #rendering-a-pattern-without-a-catalog }

`compile_template` exponerar samma maskineri en nivå ner: det förvandlar en
t-string till dess msgid plus en bunden mängd värden, och renderar vilket
mönster du än räcker det.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validerar enligt samma regler och **kastar alltid** vid en
missmatchning. Här finns inget överseende läge: överseendet finns för att en
*kataloguppslagning* ska kunna degradera till källtexten, och ett mönster du
själv skickat in har ingenting att degradera från.

## Säkerhet och räckvidd { #safety-and-scope }

Detta är giltigt:

```python
tr(t"Hello {name}")
```

Dessa avvisas med avsikt:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Beräkna ett meningsfullt värde först:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Begränsningen ger stabila katalognycklar, ger översättarna användbara namn
och hindrar en översatt sträng från att bli ett uttrycksspråk.

Garantin är avgränsad till *struktur och formatering*: en översättning
utvärderas aldrig, och kan aldrig lägga till attributåtkomst, anrop,
konverteringar eller formatspecifikationer. Två saker förblir anroparens
ansvar, precis som med stdlib-gettext — att **escapa** renderad utdata för
dess mål (HTML, skal, terminal), och **katalogintegritet**, eftersom en
fientlig katalog kan upprepa en platshållare för att förstärka
utdatastorleken, vilket är inneboende i all platshållarbaserad i18n.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
