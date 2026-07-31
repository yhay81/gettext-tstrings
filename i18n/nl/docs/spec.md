---
description: "De t-string-naar-msgid-conventie als een klein versiebeheerd contract, met een machineleesbare conformiteitssuite."
---

# Specificatie

Je kunt deze bibliotheek gebruiken zonder deze pagina te lezen — de
[tutorial](tutorial.md) en de [handleiding](guide.md) dekken het dagelijkse
gebruik. Deze pagina is voor toolauteurs: de conventie die de bibliotheek
implementeert is vastgelegd als een klein, stabiel contract, zodat een
andere implementatie — een extractor, een IDE, een typechecker of een
toekomstige `pygettext` — haar kan aansturen en interopereren. Voor dezelfde
regels uitgelegd met hun redenen, en hoe de referentie-implementatie ze
uitvoert, lees eerst [Hoe het werkt](internals.md).

[Lees spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## De regels op één scherm { #the-rules-in-one-screen }

**Een msgid** is de aaneenschakeling, in bronvolgorde, van de letterlijke
segmenten en één `{name}`-token per interpolatie. Letterlijke accolades
worden geëscaped (`{` wordt `{{`). Een naam moet een eenvoudige
placeholdernaam zijn — `str.isidentifier()` is waar en het is geen
Python-keyword. Conversies en format-specs zijn **geen** deel van de msgid;
ze blijven onder controle van de applicatie.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *afgewezen — geen eenvoudige naam* |

**Een vertaling** is geldig wanneer ze alleen kale `{name}`-placeholders
bevat, elke vereiste naam ten minste één keer voorkomt, en er geen naam
buiten de toegestane set voorkomt. Herordening en herhaling zijn bewust
onbeperkt: beide kunnen in een doeltaal grammaticaal noodzakelijk zijn.

Voor meervouden is *toegestaan* de unie van de namen van de takken en
*vereist* hun doorsnede — dus `t"One file"` tegenover `t"{n} files"` laat
`n` beschikbaar voor een vertaler van elk van beide vormen maar vereist het
van geen van beide, en de meervoudsregels van een doeltaal kunnen afwijken
van die van de bron.

**Een lege msgid** wordt nooit opgezocht, omdat gettext hem reserveert voor
de metadata-header van een catalogus.

## Conformiteit { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
is hetzelfde document in machineleesbare vorm: gevallen die de statische
structuur van een t-string afbeelden op een msgid, en een msgid plus een
cataloguspatroon op een gerenderde string of een afwijzing.

Een implementatie **conformeert aan spec v1** wanneer ze elk geval
reproduceert. De gevallen benoemen alleen wat de specificatie definieert —
afgeleide msgids, geaccepteerde en afgewezen patronen, gerenderde uitvoer —
en nooit een foutmelding of een exceptietype, zodat een implementatie in een
andere taal ze ongewijzigd kan draaien.

Interpolaties worden structureel beschreven, nooit als Python-broncode:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Het veld `"spec"` is **geen** specificatieversie — elk geval in `v1.json`
hoort bij spec v1. Het benoemt de sectie van `SPEC.md` die het geval
uitoefent, dus `"2.2"` leest als §2.2, de regel voor het afleiden van een
placeholder-token.

De referentie-implementatie draait de suite als onderdeel van haar eigen
testsuite, zodat het proza en de code niet in stilte uit elkaar kunnen
drijven.

## Versiebeheer { #versioning }

Dit is spec v1. Een achterwaarts incompatibele wijziging aan de
msgid-afleiding of aan de vertaalvalidatie verhoogt de versie en levert een
nieuwe `conformance/vN.json` naast de bestaande. Additieve verduidelijkingen
die noch afgeleide msgids noch geaccepteerde patronen veranderen, doen dat
niet.
