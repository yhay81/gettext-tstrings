---
description: "Översätt kompletta t-string-meddelanden genom gettext och Babel, med formateringen hållen utanför katalogen."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Skriv meningen en gång.<br>Översätt den som helhet.

Säker integration av gettext och Babel för t-strings i Python 3.14+ — värdet
stannar på sin plats, och katalogen ser hela meddelandet:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Starta handledningen :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Varför t-strings](comparison.md){ .md-button }

Den här webbplatsen praktiserar vad den dokumenterar: varje språkutgåva —
navigering, etiketter och den pluralmedvetna byggrapporten — renderas från
PO-kataloger av
[`gettext-tstrings` självt](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalogen tar emot den kompletta meningen `Hello {name}`. En översättning får
flytta om eller upprepa `{name}`; den får inte utelämna platshållaren, hitta på
en ny eller lägga till egen formatering — det här biblioteket kontrollerar det,
och en trasig katalog faller tillbaka till källtexten i stället för att krascha.

!!! note "Ny på gettext? Hela arbetsflödet i fyra meningar"

    **gettext** är standardsättet att översätta programvara, i Python och långt
    därbortom. Din kod markerar översättbara strängar; en *extraktor* samlar
    dem i en mallfil (`.pot`); en översättare — oftast inte en programmerare —
    fyller i en katalogfil (`.po`) per språk, som kompileras till en binär
    `.mo` som din applikation läser in vid körning. Det konventionella namnet
    på översättningsfunktionen är `_`, så `_(t"Hello {name}")` läses som
    "översätt den här meningen". **[Handledningen](tutorial.md)** går igenom
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

## Valet det gör { #the-choice-it-makes }

- Översätt kompletta meddelanden, aldrig meningsfragment.
- Acceptera endast enkla variabelnamn som `{name}`.
- Håll `!r` och `:.2f` under applikationens kontroll, utanför katalogen.
- Låt översättare flytta om och upprepa kända platshållare — men inte anropa
  attribut, och inte lägga till formateringsbeteende.
- Återanvänd vanliga POT-, PO- och MO-filer, och verktygen som redan läser dem.

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

Tre sorters läsare kommer hit: någon som översätter sitt första program, någon
som kopplar in översättning i ett riktigt projekt, och någon som vill veta
exakt varför maskineriet är format som det är. Var och en har en väg.

**Lära sig det** — ingen gettext-erfarenhet förutsätts:

<div class="grid cards" markdown>

- **[Handledning](tutorial.md)** — börja här: från en tom katalog till en
  körande japansk översättning i fem steg, varje kommando visat med sin utdata.
- **[Varför t-strings](comparison.md)** — samma meddelande skrivet på fyra
  sätt, och vad `%(name)s`, `.format()` och `$`-strängar var för sig lämnar
  över till katalogen.
- **[Bakgrund](background.md)** — varför det här biblioteket finns: trettio år
  av gettext, två PEP:ar och stdlib-diskussionen som stängdes utan svar.

</div>

**Använda det på allvar** — arbetsreferenserna:

<div class="grid cards" markdown>

- **[Guide](guide.md)** — körnings-API:et: pluralformer, språk per anrop,
  uppskjutna strängar, och vad som händer när en katalog är fel.
- **[Extrahering](extraction.md)** — `pybabel`-referensen: konfiguration,
  egna funktionsnamn, och hur befintliga verktyg validerar dessa kataloger
  gratis.
- **[I produktion](workflow.md)** — kretsloppet så som ett team kör det:
  uppdateringscykeln, fuzzy-poster, CI-grindar, översättningsplattformar och
  språk per förfrågan i en webbapplikation.
- **[API](api.md)** — allt paketet exporterar, på en sida.

</div>

**Förstå det** — från principer till implementation:

<div class="grid cards" markdown>

- **[Så fungerar det](internals.md)** — från PEP 750:s template-objekt till den
  renderade strängen, och cacharna som gör kontrollerna billiga.
- **[Specifikation](spec.md)** — konventionen t-string ↔ msgid som ett
  stabilt, versionerat kontrakt, med en maskinläsbar konformitetssvit.

</div>

## Status { #status }

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
