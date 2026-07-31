---
description: "Vertaal volledige t-string-berichten via gettext en Babel, met de waarden en de opmaak buiten de catalogus gehouden."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Vertaal hele berichten,<br>geen tekstfragmenten.

`gettext-tstrings` verbindt de t-strings van Python 3.14+ met standaard
gettext-catalogi en Babel-gereedschap. Waarden en opmaak blijven in de code van
de applicatie; de catalogus bevat een volledig bericht met eenvoudige
`{name}`-placeholders:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Begin de tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Vergelijk de alternatieven](comparison.md){ .md-button }

Alfa · Python 3.14+ · gewone PO/MO-catalogi · geen runtime-dependencies
{ .home-facts }

Deze site brengt in praktijk wat ze documenteert: elke taaleditie —
navigatie, labels en het meervoudsbewuste buildrapport — wordt uit
PO-catalogi gerenderd door
[`gettext-tstrings` zelf](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Is dit iets voor jou? { #is-this-for-you }

**Vandaag een goede keuze wanneer** je applicatie op Python 3.14 of nieuwer
draait; je gettext en Babel al gebruikt, of hun PO/MO-workflow wilt overnemen;
en je t-string-syntaxis wilt met benoemde placeholders die gecontroleerd worden
voordat ze gerenderd worden.

**Nog geen goede keuze wanneer** je Python 3.13 of ouder nodig hebt; je een
stabiele Python-API vereist — dit is een alfa, en de [specificatie](spec.md) is
het deel ervan dat wél bezonken is; of vrijwel al je vertaalbare tekst in een
sjabloontaal staat in plaats van in Python-broncode.

Heb je al catalogi? Die blijven werken. `_("Hello {name}").format(name=name)` en
`tr(t"Hello {name}")` leveren dezelfde msgid op, zodat bestaande vertalingen de
overstap overleven — [Migratie](migration.md) loopt de hele verhuizing door.

## Wat de catalogus mag zeggen { #what-the-catalog-may-say }

De catalogus ontvangt het volledige bericht `Hello {name}`. Een vertaling mag
`{name}` verplaatsen of herhalen, en mag elk ander woord eromheen herschrijven.
Ze mag de placeholder niet weglaten, er geen nieuwe verzinnen, er niet doorheen
grijpen naar je objecten, en er geen eigen opmaak aan hangen.

Dat is de hele belofte: **een vertaling kan de structuur van het bericht dat ze
vertaalt niet veranderen.** De bibliotheek controleert dat aan de poort — bij
het compileren van catalogi — en nog eens bij het renderen; een kapotte entry
die tóch in productie belandt, logt een waarschuwing en rendert het bronbericht
in plaats van te crashen.

!!! note "Nieuw bij gettext? De hele workflow in vier zinnen"

    **gettext** is de standaardmanier waarop software vertaald wordt, in
    Python en ver daarbuiten. Je code markeert vertaalbare berichten; een
    *extractor* verzamelt ze in een sjabloonbestand (`.pot`); een vertaler —
    meestal geen programmeur — vult per taal één catalogusbestand (`.po`) in,
    dat gecompileerd wordt tot een binaire `.mo` die je applicatie tijdens
    runtime laadt. De conventionele naam voor de vertaalfunctie is `_`, zodat
    `_(t"Hello {name}")` leest als "vertaal dit bericht". De
    **[tutorial](tutorial.md)** doorloopt het hele pad — markeren, extraheren,
    vertalen, compileren, uitvoeren — in ongeveer vijf minuten.

## Het probleem dat het oplost { #the-problem-it-solves }

Een f-string is al geïnterpoleerd tegen de tijd dat een bibliotheek hem ziet —
`f"Hello {name}"` is `"Hello Ada"` geworden, en het vertalen van de fragmenten
rond een waarde breekt de grammatica van de meeste talen. Een t-string
([PEP 750]) houdt de statische tekst, de geëvalueerde waarden, de
bronexpressies, de conversies en de format-specs gescheiden — precies de
splitsing die een berichtencatalogus nodig heeft.
[Wat dat verandert](comparison.md), vergeleken met `%(name)s`, `.format()` en
`$`-strings.

Niets in gettext of Babel zegt echter hoe een t-string een bericht wordt. Deze
bibliotheek maakt die keuze, legt haar vast als een
[versiebeheerde specificatie](spec.md), en levert de
[conformiteitssuite](spec.md#conformance) om haar te controleren.

## De ontwerpregels { #the-design-rules }

- Vertaal volledige berichten, nooit zinsfragmenten.
- Accepteer alleen eenvoudige variabelenamen zoals `{name}`.
- Houd `!r` en `:.2f` onder controle van de applicatie, buiten de catalogus.
- Laat vertalingen bekende placeholders verplaatsen en herhalen, maar belet ze
  attributen te bereiken of opmaak toe te voegen.
- Hergebruik gewone POT-, PO- en MO-bestanden, en de tools die ze al lezen.

En de bijbehorende lijst van wat het bewust met rust laat: het lokaliseert geen
getallen, valuta's of datums — [formatteer die eerst](guide.md#locale-aware-values),
met Babel; het escapet gerenderde uitvoer niet voor HTML, een shell of een
terminal; en het kan niet beoordelen of een vertaling *juist* is, alleen of haar
placeholders intact zijn.

## Installatie { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 of nieuwer. **Renderen heeft geen dependencies** — het gebruikt
`gettext` uit de standaardbibliotheek en niets anders.

Extractie en catalogusvalidatie lopen via [Babel]; installeer die extra
overal waar `pybabel` draait, wat meestal een ontwikkel- of CI-omgeving is en
geen productie-image:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Waar nu heen { #where-to-go-next }

**Begin hier** — geen gettext-ervaring verondersteld:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — van een lege map naar een werkende Japanse
  vertaling in vijf stappen, elk commando getoond met zijn uitvoer.
- **[Waarom t-strings](comparison.md)** — hetzelfde bericht op vier manieren
  geschreven, en wat `%(name)s`, `.format()` en `$`-strings elk aan de
  catalogus overhandigen.

</div>

**Aan de slag** — de werkreferenties:

<div class="grid cards" markdown>

- **[Handleiding](guide.md)** — de runtime-API: welk instappunt je gebruikt,
  meervouden, talen per request, uitgestelde strings, en wat er gebeurt als een
  catalogus fout is.
- **[Extractie](extraction.md)** — de `pybabel`-referentie: configuratie,
  eigen functienamen, en hoe bestaande tools deze catalogi gratis valideren.
- **[In productie](workflow.md)** — de lus zoals een team hem draait: de
  updatecyclus, fuzzy-entries, CI-poorten, vertaalplatforms en uitleveren.
- **[Migratie](migration.md)** — dit invoeren in een project dat al catalogi
  heeft, één aanroep tegelijk.
- **[Voor vertalers](translators.md)** — één pagina om te overhandigen aan wie
  de `.po`-bestanden bewerkt.

</div>

**Het begrijpen** — van geschiedenis tot implementatie:

<div class="grid cards" markdown>

- **[Achtergrond](background.md)** — waarom deze bibliotheek bestaat: dertig
  jaar gettext, twee PEP's, en de stdlib-discussie die zonder antwoord
  gesloten werd.
- **[Valkuilen](pitfalls.md)** — wat het vertalen van deze site naar
  vijfendertig talen werkelijk brak, en welke helft een tool kan vangen.
- **[Hoe het werkt](internals.md)** — van het template-object uit PEP 750
  naar de gerenderde string, en de caches die het controleren goedkoop maken.

</div>

**Naslag** — de contracten:

<div class="grid cards" markdown>

- **[API](api.md)** — alles wat het pakket exporteert, op één pagina.
- **[Specificatie](spec.md)** — de t-string-↔-msgid-conventie als een
  stabiel, versiebeheerd contract, met een machineleesbare
  conformiteitssuite.

</div>

## Status { #status }

| | |
| --- | --- |
| Pakketversie | 0.1.0a7 |
| API-stabiliteit | alfa — de Python-API kan nog veranderen |
| [Specificatie](spec.md) | v1, met een [conformiteitssuite](spec.md#conformance) |
| Python | 3.14 en nieuwer; getest op 3.14, 3.14t (free-threaded) en 3.15 |
| Babel | 2.18 of nieuwer, en alleen waar `pybabel` draait |
| Runtime-afhankelijkheden | geen — de `gettext` van de standaardbibliotheek |
| Catalogusformaat | gewone POT, PO en MO |
| Wijzigingen | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Een alfa. Het contract is met opzet klein en de [specificatie](spec.md) is er
het stabiele deel van; de Python-API kan nog bewegen. Vóór een stabiele
release zijn er bredere taalfixtures nodig, doorlopende
performancemonitoring, API-review door mensen die gettext en Babel serieus
gebruiken, en compatibiliteitstests over elke ondersteunde Python- en
Babel-release.

[Issues en pull requests](https://github.com/yhay81/gettext-tstrings/issues)
zijn welkom — een alfa is precies het moment waarop de interface nog het
bediscussiëren waard is.

## Doe mee met de community { #join-the-community }

- Kies een
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  voor een afgebakende bijdrage.
- Stel gebruiksvragen in de
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Breng productie-gettext-workflows en API-ideeën naar de
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lees de
  [bijdragehandleiding](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  voordat je een pull request opent.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
