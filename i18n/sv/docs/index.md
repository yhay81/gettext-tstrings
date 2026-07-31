---
description: "Översätt kompletta t-string-meddelanden genom gettext och Babel, med värdena och formateringen hållna utanför katalogen."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Översätt kompletta meddelanden<br>med t-strings i Python

`gettext-tstrings` kopplar samman t-strings i Python 3.14+ med vanliga
gettext-kataloger och Babel-verktyg. Värden och formatering stannar i
applikationskoden; översättarna arbetar med kompletta meddelanden och enkla
`{name}`-platshållare:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalogen innehåller `Hello {name}`. En översättning får flytta om eller
upprepa `{name}`. Om den utelämnar, byter namn på eller formaterar om
platshållaren rapporterar katalogvalideringen felet. Om en ogiltig post ändå
når produktion loggar biblioteket en varning och renderar källmeddelandet i
stället för att krascha.

[Starta den femminuterslånga handledningen :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Jämför alternativen](comparison.md){ .md-button }

Alfa · Python 3.14+ · standardiserade PO/MO-kataloger · inga körningsberoenden från tredje part
{ .home-facts }

Den här webbplatsen praktiserar vad den dokumenterar: varje språkutgåva —
navigering, etiketter och den pluralmedvetna byggrapporten — renderas från
PO-kataloger av
[`gettext-tstrings` självt](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Är det här något för dig? { #is-this-for-you }

**Det passar redan i dag när** din applikation kör på Python 3.14 eller nyare;
du redan använder gettext och Babel, eller vill införa deras PO/MO-arbetsflöde;
och du vill ha t-string-syntax med namngivna platshållare som kontrolleras
innan de renderas.

**Det passar inte än när** du behöver Python 3.13 eller äldre; du kräver ett
stabilt Python-API — det här är en alfa, och [specifikationen](spec.md) är den
del av det som har satt sig; eller när nästan all din översättbara text bor i
ett mallspråk snarare än i Python-källkod.

Har du redan kataloger? De fortsätter att fungera.
`_("Hello {name}").format(name=name)` och `tr(t"Hello {name}")` ger samma
msgid, så befintliga översättningar överlever bytet — [Migrering](migration.md)
går igenom hela flytten.

## Vad katalogen får säga { #what-the-catalog-may-say }

**En översättning kan inte ändra strukturen på det meddelande den översätter.**
Det är hela löftet, och resten av den här webbplatsen följer av det. En
översättning får flytta om eller upprepa `{name}`, och får skriva om varenda
annat ord runt omkring. Den får inte utelämna platshållaren, hitta på en ny,
sträcka sig genom den in i dina objekt eller lägga till egen formatering.

Biblioteket kontrollerar det på vägen in — när kataloger kompileras — och igen
vid rendering, vilket är skillnaden mellan ett misstag som hittas i granskning
och ett misstag som hittas av en användare.

!!! note "Ny på gettext? Hela arbetsflödet i fyra meningar"

    **gettext** är standardsättet att översätta programvara, i Python och långt
    därbortom. Din kod markerar översättbara meddelanden; en *extraktor* samlar
    dem i en mallfil (`.pot`); en översättare — oftast inte en programmerare —
    fyller i en katalogfil (`.po`) per språk, som kompileras till en binär
    `.mo` som din applikation läser in vid körning. Det konventionella namnet
    på översättningsfunktionen är `_`, så `_(t"Hello {name}")` läses som
    "översätt det här meddelandet". **[Handledningen](tutorial.md)** går igenom
    hela vägen — markera, extrahera, översätta, kompilera, köra — på ungefär
    fem minuter.

## Problemet det löser { #the-problem-it-solves }

En f-string är redan interpolerad när något bibliotek får se den —
`f"Hello {name}"` har blivit `"Hello Ada"`, och att översätta fragmenten runt
ett värde bryter grammatiken i de flesta språk. En t-string ([PEP 750]) håller
den statiska texten, de utvärderade värdena, källuttrycken, konverteringarna
och formatspecifikationerna åtskilda — vilket är exakt den uppdelning en
meddelandekatalog behöver.
[Vad det förändrar](comparison.md), jämfört med `%(name)s`, `.format()` och
`$`-strängar.

Men ingenting i gettext eller Babel säger hur en t-string blir ett meddelande.
Det här biblioteket gör det valet, skriver ner det som en
[versionerad specifikation](spec.md) och levererar
[konformitetssviten](spec.md#conformance) som kontrollerar det.

## Designreglerna { #the-design-rules }

- Översätt kompletta meddelanden, aldrig meningsfragment.
- Acceptera endast enkla variabelnamn som `{name}`.
- Håll `!r` och `:.2f` under applikationens kontroll, utanför katalogen.
- Låt översättningar flytta om och upprepa kända platshållare, samtidigt som de
  hindras från att nå attribut eller lägga till formatering.
- Återanvänd vanliga POT-, PO- och MO-filer, och verktygen som redan läser dem.

Och den motsvarande listan över vad det avsiktligt lämnar i fred: det
lokaliserar inte tal, valutor eller datum — [formatera dem först](guide.md#locale-aware-values),
med Babel; det escapar inte renderad utdata för HTML, ett skal eller en
terminal; och det kan inte bedöma om en översättning är *korrekt*, bara om dess
platshållare är intakta.

## Installera { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 eller nyare. **Rendering har inga beroenden** — den använder
standardbibliotekets `gettext` och ingenting annat.

Extrahering och katalogvalidering går genom [Babel], så installera det extrat
överallt där `pybabel` körs, vilket vanligtvis är en utvecklings- eller
CI-miljö snarare än en produktionsavbild:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Vart härnäst { #where-to-go-next }

**Börja här** — ingen gettext-erfarenhet förutsätts:

<div class="grid cards" markdown>

- **[Handledning](tutorial.md)** — från en tom katalog till en körande japansk
  översättning i fem steg, varje kommando visat med sin utdata.
- **[Varför t-strings](comparison.md)** — samma meddelande skrivet på fyra
  sätt, och vad `%(name)s`, `.format()` och `$`-strängar var för sig lämnar
  över till katalogen.

</div>

**Använd det** — arbetsreferenserna:

<div class="grid cards" markdown>

- **[Guide](guide.md)** — körnings-API:et: vilken ingång du ska använda,
  pluralformer, språk per förfrågan, uppskjutna strängar, och vad som händer
  när en katalog är fel.
- **[Extrahering](extraction.md)** — `pybabel`-referensen: konfiguration,
  egna funktionsnamn, och hur befintliga verktyg validerar dessa kataloger
  gratis.
- **[I produktion](workflow.md)** — kretsloppet så som ett team kör det:
  uppdateringscykeln, fuzzy-poster, CI-grindar, översättningsplattformar och
  leverans.
- **[Migrering](migration.md)** — att införa det här i ett projekt som redan
  har kataloger, ett anropsställe i taget.
- **[För översättare](translators.md)** — en sida att räcka över till den som
  redigerar `.po`-filerna.

</div>

**Förstå det** — från historia till implementation:

<div class="grid cards" markdown>

- **[Bakgrund](background.md)** — varför det här biblioteket finns: trettio år
  av gettext, två PEP:ar och stdlib-diskussionen som stängdes utan svar.
- **[Fallgropar](pitfalls.md)** — vad översättningen av den här webbplatsen
  till trettiofem språk faktiskt gick sönder på, och vilken hälft ett verktyg
  hinner fånga.
- **[Så fungerar det](internals.md)** — från PEP 750:s template-objekt till den
  renderade strängen, och cacharna som gör kontrollerna billiga.

</div>

**Referens** — kontrakten:

<div class="grid cards" markdown>

- **[API](api.md)** — allt paketet exporterar, på en sida.
- **[Specifikation](spec.md)** — konventionen t-string ↔ msgid som ett
  stabilt, versionerat kontrakt, med en maskinläsbar konformitetssvit.

</div>

## Status { #status }

| | |
| --- | --- |
| Paketversion | 0.1.0a8 |
| API-stabilitet | alfa — Python-API:et kan fortfarande ändras |
| [Specifikation](spec.md) | v1, med en [konformitetssvit](spec.md#conformance) |
| Python | 3.14 och senare; testad på 3.14, 3.14t (free-threaded) och 3.15 |
| Babel | 2.18 eller senare, och endast där `pybabel` körs |
| Körtidsberoenden | inga — standardbibliotekets `gettext` |
| Katalogformat | vanlig POT, PO och MO |
| Ändringar | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

En alfa. Kontraktet är avsiktligt litet och [specifikationen](spec.md) är den
stabila delen av det; Python-API:et kan fortfarande röra sig. Före en stabil
utgåva behövs bredare språkfixturer, kontinuerlig prestandauppföljning,
API-granskning från personer som använder gettext och Babel på allvar, och
kompatibilitetstester över varje Python- och Babel-version som stöds.

[Ärenden och pull requests](https://github.com/yhay81/gettext-tstrings/issues)
är välkomna — en alfa är exakt rätt tillfälle att fortfarande diskutera
gränssnittet.

## Gå med i gemenskapen { #join-the-community }

- Välj ett
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  för ett avgränsat bidrag.
- Ställ användarfrågor i
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Ta med produktionserfarenheter av gettext-arbetsflöden och API-idéer till
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Läs
  [bidragsguiden](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  innan du öppnar en pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
