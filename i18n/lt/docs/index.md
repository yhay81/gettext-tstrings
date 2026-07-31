---
description: "Verskite ištisus t-eilučių pranešimus per gettext ir Babel, palikdami formatavimą už katalogo ribų."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Parašykite sakinį vieną kartą.<br>Išverskite jį visą.

Saugi gettext ir Babel integracija Python 3.14+ t-eilutėms — reikšmė lieka
savo vietoje, o katalogas mato visą pranešimą:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Pradėti pamoką :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Kodėl t-eilutės](comparison.md){ .md-button }

Ši svetainė daro tai, ką dokumentuoja: kiekvieną kalbos leidimą —
navigaciją, etiketes ir daugiskaitos formas suprantančią kūrimo ataskaitą —
iš PO katalogų atvaizduoja
[pats `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalogas gauna ištisą sakinį `Hello {name}`. Vertimas gali perstatyti ar
pakartoti `{name}`; jis negali jo praleisti, sugalvoti naujo ar prikabinti savo
formatavimo — ši biblioteka tai tikrina, o sugadintas katalogas grįžta prie
pirminio teksto, o ne nulūžta.

!!! note "Nesate susidūrę su gettext? Visa darbo eiga keturiais sakiniais"

    **gettext** yra standartinis būdas programinei įrangai išversti — tiek
    Python kalboje, tiek toli už jos ribų. Jūsų kodas pažymi verstinas
    eilutes; *ištraukiklis* surenka jas į šablono failą (`.pot`); vertėjas —
    paprastai ne programuotojas — užpildo po vieną katalogo failą (`.po`)
    kiekvienai kalbai, o šis sukompiliuojamas į dvejetainį `.mo`, kurį jūsų
    programa įkelia veikimo metu. Įprastas vertimo funkcijos pavadinimas yra
    `_`, todėl `_(t"Hello {name}")` skaitosi kaip „išversk šį sakinį“.
    **[Pamoka](tutorial.md)** pereina visą kelią — pažymėti, ištraukti,
    išversti, sukompiliuoti, paleisti — maždaug per penkias minutes.

## Problema, kurią ji sprendžia { #the-problem-it-solves }

F-eilutė būna jau interpoliuota tuo metu, kai ją pamato bet kuri biblioteka —
`f"Hello {name}"` jau tapo `"Hello Ada"`, o aplink reikšmę esančių nuotrupų
vertimas laužo daugumos kalbų gramatiką. T-eilutė ([PEP 750]) atskirai
išsaugo statinį tekstą, apskaičiuotas reikšmes, pirminius reiškinius,
konversijas ir formato specifikacijas — o būtent tokio padalijimo ir reikia
pranešimų katalogui.
[Ką tai keičia](comparison.md), palyginti su `%(name)s`, `.format()` ir
`$` eilutėmis.

Tačiau nei gettext, nei Babel nepasako, kaip t-eilutė tampa pranešimu. Ši
biblioteka tą pasirinkimą padaro, surašo jį kaip
[versijuotą specifikaciją](spec.md) ir pateikia
[atitikties rinkinį](spec.md#conformance), kad tai patikrintų.

## Pasirinkimas, kurį ji daro { #the-choice-it-makes }

- Verskite ištisus pranešimus, niekada ne sakinių nuotrupas.
- Priimkite tik paprastus kintamųjų vardus, tokius kaip `{name}`.
- Palikite `!r` ir `:.2f` programos kontrolėje, už katalogo ribų.
- Leiskite vertėjams perstatyti ir kartoti žinomus vietaženklius — bet ne
  kreiptis į atributus ir ne pridėti formatavimo elgsenos.
- Naudokite įprastus POT, PO ir MO failus bei įrankius, kurie juos jau skaito.

## Diegimas { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 arba naujesnis. **Atvaizdavimas neturi jokių priklausomybių** — jis
naudoja standartinės bibliotekos `gettext` ir nieko daugiau.

Ištraukimas ir katalogų tikrinimas vyksta per [Babel], todėl įdiekite šį
priedą ten, kur veikia `pybabel`, o tai paprastai yra kūrimo arba CI aplinka,
o ne produkcinis atvaizdis:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Kur eiti toliau { #where-to-go-next }

Čia atkeliauja trijų rūšių skaitytojai: tas, kuris verčia savo pirmą programą,
tas, kuris įpina vertimą į tikrą projektą, ir tas, kuris nori tiksliai
sužinoti, kodėl ši mechanika yra būtent tokios formos. Kiekvienas turi savo
kelią.

**Mokymuisi** — gettext patirties nereikia:

<div class="grid cards" markdown>

- **[Pamoka](tutorial.md)** — pradėkite čia: nuo tuščio katalogo iki veikiančio
  japoniško vertimo penkiais žingsniais, kiekviena komanda parodyta su savo
  išvestimi.
- **[Kodėl t-eilutės](comparison.md)** — tas pats pranešimas, parašytas
  keturiais būdais, ir tai, ką `%(name)s`, `.format()` bei `$` eilutės
  perduoda katalogui.
- **[Ištakos](background.md)** — kodėl ši biblioteka egzistuoja: trisdešimt
  metų gettext, du PEP'ai ir standartinės bibliotekos diskusija, užsibaigusi
  be atsakymo.

</div>

**Rimtam naudojimui** — darbinės žinynų dalys:

<div class="grid cards" markdown>

- **[Vadovas](guide.md)** — veikimo metu naudojama API: daugiskaita, kalbos
  pagal užklausą, atidėtos eilutės ir kas nutinka, kai katalogas klaidingas.
- **[Ištraukimas](extraction.md)** — `pybabel` žinynas: konfigūracija,
  savi funkcijų vardai ir tai, kaip jau turimi įrankiai patikrina šiuos
  katalogus be jokių pastangų.
- **[Realioje aplinkoje](workflow.md)** — ciklas taip, kaip jį sukioja
  komanda: atnaujinimo ciklas, fuzzy įrašai, CI vartai, vertimo platformos ir
  kalbos pagal užklausą žiniatinklio programoje.
- **[API](api.md)** — viskas, ką paketas eksportuoja, viename puslapyje.

</div>

**Supratimui** — nuo principų iki įgyvendinimo:

<div class="grid cards" markdown>

- **[Kaip tai veikia](internals.md)** — nuo PEP 750 šablono objekto iki
  atvaizduotos eilutės ir podėliai, dėl kurių tikrinimas kainuoja mažai.
- **[Specifikacija](spec.md)** — t-eilutės ↔ msgid susitarimas kaip stabilus,
  versijuotas kontraktas su mašininiu būdu skaitomu atitikties rinkiniu.

</div>

## Būsena { #status }

Alfa versija. Kontraktas tyčia mažas, o [specifikacija](spec.md) yra
stabilioji jo dalis; Python API dar gali keistis. Prieš stabilų leidimą reikia
platesnių kalbinių bandymų rinkinių, nuolatinio našumo stebėjimo, API
peržiūros iš žmonių, rimtai naudojančių gettext ir Babel, bei suderinamumo
testavimo su kiekviena palaikoma Python ir Babel versija.

[Problemos ir pull request'ai](https://github.com/yhay81/gettext-tstrings/issues)
yra laukiami — alfa yra kaip tik tas metas, kai dėl sąsajos dar verta ginčytis.

## Prisijunkite prie bendruomenės { #join-the-community }

- Pasirinkite
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  aiškiai apibrėžtam indėliui.
- Klauskite apie naudojimą
  [Q&A diskusijose](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Atneškite produkcines gettext darbo eigas ir API idėjas į
  [Ideas diskusijas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Perskaitykite
  [prisidėjimo vadovą](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md),
  prieš atverdami pull request'ą.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
