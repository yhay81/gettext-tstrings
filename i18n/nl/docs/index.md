---
description: "Vertaal volledige t-string-berichten via gettext en Babel, met de opmaak buiten de catalogus gehouden."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Schrijf de zin één keer.<br>Vertaal hem als geheel.

Veilige gettext- en Babel-integratie voor Python 3.14+-t-strings — de waarde
blijft op haar plaats, en de catalogus ziet het volledige bericht:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Begin de tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Waarom t-strings](comparison.md){ .md-button }

Deze site brengt in praktijk wat ze documenteert: elke taaleditie —
navigatie, labels en het meervoudsbewuste buildrapport — wordt uit
PO-catalogi gerenderd door
[`gettext-tstrings` zelf](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

De catalogus ontvangt de volledige zin `Hello {name}`. Een vertaling mag
`{name}` verplaatsen of herhalen; ze mag hem niet weglaten, er een verzinnen
of eigen opmaak toevoegen — deze bibliotheek controleert dat, en een kapotte
catalogus valt terug op de brontekst in plaats van te crashen.

!!! note "Nieuw bij gettext? De hele workflow in vier zinnen"

    **gettext** is de standaardmanier waarop software vertaald wordt, in
    Python en ver daarbuiten. Je code markeert vertaalbare strings; een
    *extractor* verzamelt ze in een sjabloonbestand (`.pot`); een vertaler —
    meestal geen programmeur — vult per taal één catalogusbestand (`.po`) in,
    dat gecompileerd wordt tot een binaire `.mo` die je applicatie tijdens
    runtime laadt. De conventionele naam voor de vertaalfunctie is `_`, zodat
    `_(t"Hello {name}")` leest als "vertaal deze zin". De
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
[gedocumenteerde, versiebeheerde specificatie](spec.md), en levert de
[conformiteitssuite](spec.md#conformance) om haar te controleren.

## De keuze die het maakt { #the-choice-it-makes }

- Vertaal volledige berichten, nooit zinsfragmenten.
- Accepteer alleen eenvoudige variabelenamen zoals `{name}`.
- Houd `!r` en `:.2f` onder controle van de applicatie, buiten de catalogus.
- Laat vertalers bekende placeholders verplaatsen en herhalen — maar geen
  attributen aanroepen, en geen opmaakgedrag toevoegen.
- Hergebruik gewone POT-, PO- en MO-bestanden, en de tools die ze al lezen.

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

Drie soorten lezers komen hier aan: iemand die zijn eerste programma vertaalt,
iemand die vertaling in een echt project inbouwt, en iemand die precies wil
weten waarom de machinerie zo gevormd is. Voor elk is er een pad.

**Het leren** — geen gettext-ervaring verondersteld:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — begin hier: van een lege map naar een
  werkende Japanse vertaling in vijf stappen, elk commando getoond met zijn
  uitvoer.
- **[Waarom t-strings](comparison.md)** — hetzelfde bericht op vier manieren
  geschreven, en wat `%(name)s`, `.format()` en `$`-strings elk aan de
  catalogus overhandigen.
- **[Achtergrond](background.md)** — waarom deze bibliotheek bestaat: dertig
  jaar gettext, twee PEP's, en de stdlib-discussie die zonder antwoord
  gesloten werd.

</div>

**Het serieus gebruiken** — de werkreferenties:

<div class="grid cards" markdown>

- **[Handleiding](guide.md)** — de runtime-API: meervouden, talen per
  request, uitgestelde strings, en wat er gebeurt als een catalogus fout is.
- **[Extractie](extraction.md)** — de `pybabel`-referentie: configuratie,
  eigen functienamen, en hoe bestaande tools deze catalogi gratis valideren.
- **[In productie](workflow.md)** — de lus zoals een team hem draait: de
  updatecyclus, fuzzy-entries, CI-poorten, vertaalplatforms en talen per
  request in een webapplicatie.
- **[API](api.md)** — alles wat het pakket exporteert, op één pagina.

</div>

**Het begrijpen** — van principes tot implementatie:

<div class="grid cards" markdown>

- **[Hoe het werkt](internals.md)** — van het template-object uit PEP 750
  naar de gerenderde string, en de caches die het controleren goedkoop maken.
- **[Specificatie](spec.md)** — de t-string-↔-msgid-conventie als een
  stabiel, versiebeheerd contract, met een machineleesbare
  conformiteitssuite.

</div>

## Status { #status }

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
