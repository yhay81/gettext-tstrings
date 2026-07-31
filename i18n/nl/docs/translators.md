---
description: "Het placeholder-contract voor wie de .po-bestanden bewerkt: wat je mag veranderen, wat je met rust moet laten, en hoe je de foutmeldingen leest."
---

# Voor vertalers

Deze pagina is voor wie de catalogus bewerkt, niet voor wie de code schrijft.
Ze is met opzet kort, en is bedoeld om gelinkt of overgenomen te worden in de
eigen vertaalinstructies van een project.

Niets hier vraagt van je dat je Python kunt lezen. Alles hier gaat over één
ding: de stukjes van een bericht tussen accolades.

## Wat een placeholder is { #what-a-placeholder-is }

Een bericht in een catalogus mag namen tussen accolades bevatten:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` is een **placeholder**. Wanneer het programma dit bericht toont,
vervangt het `{name}` door een waarde die het zelf aanlevert — de naam van een
persoon, een bestandsnaam, een getal. De placeholder is geen woord om te
vertalen; het is een gleuf.

Jouw vertaling komt in de `msgstr`, en die moet die gleuf behouden:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Wat je mag veranderen, en wat niet { #what-you-may-change-and-what-you-may-not }

Je **mag**:

- **Een placeholder verplaatsen** naar waar de grammatica van de doeltaal hem
  wil hebben, ook naar het begin van het bericht.
- **Een placeholder herhalen** als de taal de waarde twee keer nodig heeft.
- **Elk ander woord herschrijven**, inclusief leestekens, spatiëring en
  zinsvolgorde.

Je **mag niet**:

- **De naam tussen de accolades vertalen.** `{name}` blijft `{name}`, ook in
  een taal die verder niets in Latijnse letters schrijft.
- **De accolades weghalen**, of de naam zonder accolades schrijven.
- **De ASCII-accolades `{` `}` vervangen door `｛` `｝` op volle breedte.** Veel
  invoermethoden produceren de vormen op volle breedte; ze zien er bijna
  identiek uit en werken niet.
- **Opmaak toevoegen**, zoals `{name!r}` of `{amount:.2f}`. Hoe een waarde
  getoond wordt, wordt in het programma beslist, niet in de catalogus.
- **Een placeholder verzinnen** die niet in de `msgid` staat.

Heeft een bericht een waarde nodig die het origineel niet aanbiedt, dan is dat
een bericht dat de ontwikkelaar moet veranderen. Zeg dat, in plaats van er
omheen te werken.

## Meervoudsvormen { #plural-forms }

Een geteld bericht komt aan met één `msgstr`-gleuf per meervoudsvorm in jouw
taal, en jouw taal bepaalt hoeveel dat er zijn — één voor het Japans, twee voor
het Duits, drie voor het Russisch, zes voor het Arabisch. Vul elke gleuf in die
de catalogus je geeft.

Twee regels waar mensen over struikelen:

- **De gleuven zijn niet "enkelvoud, meervoud, nog meer meervoud".** Elke index
  betekent wat de meervoudsregel van jouw taal zegt dat hij betekent. De derde
  vorm van het Lets is alleen voor nul; de tweede van het Sloveens is voor
  precies twee; het Welsh zet het algemene geval op index 0 en het enkelvoud op
  index 1.
- **Twee gleuven mogen terecht dezelfde tekst bevatten.** In het Turks,
  Hongaars, Perzisch en Bengaals blijft een zelfstandig naamwoord na een
  telwoord in het enkelvoud, dus beide vormen van een geteld bericht zijn
  dezelfde string. Dat is juist, geen kopieer-plakfoutje.

De placeholderregels hierboven gelden voor elke vorm afzonderlijk.

## Fuzzy-entries { #fuzzy-entries }

Een entry met de markering `fuzzy` is een gok van een machine: de ontwikkelaar
heeft het oorspronkelijke bericht veranderd, en de tooling heeft de nieuwe tekst
aan jouw oude vertaling gekoppeld zodat je ergens kunt beginnen.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Een fuzzy-entry wordt **niet door het programma gebruikt** — het toont in plaats
daarvan het onvertaalde origineel — totdat iemand de tekst nakijkt en de
`fuzzy`-markering verwijdert. De meeste PO-editors hebben daar een knop voor.

## Een foutmelding lezen { #reading-a-failure-message }

De tooling controleert placeholders wanneer de catalogus gecompileerd wordt, en
de melding is voor jou geschreven en niet voor een programmeur. Alleen melden
dat `{name}` ontbreekt is een doodlopende weg wanneer je die tekens vóór je kunt
zien, dus waar een placeholder aanwezig lijkt maar het niet is, zegt de melding
waarom. Tegen het origineel `Hello {name}` wordt elk van deze gerapporteerd
onder
`translation does not match the source placeholders:`

| Jouw vertaling zegt | De reden die ze geeft |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Tekens die niet te zien zijn krijgen hun eigen behandeling. Een harde spatie
binnen de accolades is iets wat een invoermethode produceert en geen editor
toont, dus de melding drukt haar af als codepunt in plaats van een teken te
noemen dat je nooit zou kunnen vinden:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Een naam waarvan de letters schriftsystemen mengen — het homoglief-geval,
waar een Cyrillische `а` niet te onderscheiden is van een Latijnse — wordt
twee keer getoond, één keer leesbaar en één keer geëscaped, wat de enige vorm
is die de twee uit elkaar houdt:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Dezelfde disambiguatie geldt wanneer een Griekse of Cyrillische naam die
volledig in één schrift geschreven is, botst met een ASCII-bronnaam,
inclusief het geval van één letter — Latijnse `a` / Cyrillische `а`.

Kom je een van deze tegen en is de oplossing niet meteen duidelijk, dan is de
veilige zet: verwijder de placeholder die je getypt hebt en kopieer die uit de
`msgid`.

## Wat de controles niet kunnen { #what-the-checks-cannot-do }

De tooling verifieert dat je placeholders intact zijn. Ze kan niet beoordelen
of de vertaling accuraat, natuurlijk of passend voor de context is — dat blijft
volledig bij jou.

Twee dingen helpen meer dan welke controle ook:

- **Lees de vertalerscommentaar.** Een regel die met `#.` begint boven het
  bericht is de ontwikkelaar die je vertelt waar het verschijnt en wat het
  betekent.
- **Vraag naar `msgctxt`.** Wanneer hetzelfde woord twee keer verschijnt met
  verschillende contexten, is dat omdat de twee verschillend vertaald moeten
  worden — "Open" de knop en "Open" de toestand, bijvoorbeeld.
