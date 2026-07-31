---
description: "Verskite ištisus t-eilučių pranešimus per gettext ir Babel, palikdami reikšmes ir formatavimą už katalogo ribų."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Verskite ištisus pranešimus,<br>o ne eilučių nuotrupas.

`gettext-tstrings` sujungia Python 3.14+ t-eilutes su standartiniais gettext
katalogais ir Babel įrankiais. Reikšmės ir formatavimas lieka programos kode;
katalogas laiko ištisą pranešimą su paprastais `{name}` vietaženkliais:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Pradėti pamoką :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Palyginti alternatyvas](comparison.md){ .md-button }

Alfa · Python 3.14+ · įprasti PO/MO katalogai · jokių veikimo meto priklausomybių
{ .home-facts }

Ši svetainė daro tai, ką dokumentuoja: kiekvieną kalbos leidimą —
navigaciją, etiketes ir daugiskaitos formas suprantančią kūrimo ataskaitą —
iš PO katalogų atvaizduoja
[pats `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Ar tai jums? { #is-this-for-you }

**Tinka jau šiandien, kai** jūsų programa veikia su Python 3.14 ar naujesniu;
jūs jau naudojate gettext ir Babel arba norite perimti jų PO/MO darbo eigą; ir
norite t-eilučių sintaksės su vardiniais vietaženkliais, kurie patikrinami
prieš atvaizduojant.

**Kol kas netinka, kai** jums reikia Python 3.13 ar senesnio; jums reikia
stabilios Python API — tai alfa versija, o [specifikacija](spec.md) yra
nusistovėjusi jos dalis; arba beveik visas jūsų verstinas tekstas gyvena
šablonų kalboje, o ne Python pirminiame kode.

Jau turite katalogus? Jie ir toliau veiks.
`_("Hello {name}").format(name=name)` ir `tr(t"Hello {name}")` pagamina tą patį
msgid, todėl esami vertimai perėjimą išgyvena — [Migracija](migration.md)
pereina visą kelią.

## Ką katalogui leidžiama pasakyti { #what-the-catalog-may-say }

Katalogas gauna ištisą pranešimą `Hello {name}`. Vertimas gali perstatyti ar
pakartoti `{name}` ir gali perrašyti kiekvieną aplink jį esantį žodį. Jis
negali vietaženklio praleisti, sugalvoti naujo, prasibrauti pro jį į jūsų
objektus ar prikabinti savo formatavimo.

Tai ir yra visas pažadas: **vertimas negali pakeisti verčiamo pranešimo
sandaros.** Biblioteka tai patikrina įeinant — kai katalogai kompiliuojami — ir
dar kartą atvaizdavimo metu; sugadintas įrašas, vis dėlto pasiekęs produkciją,
užrašo įspėjimą ir atvaizduoja pirminį pranešimą, o ne nulūžta.

!!! note "Nesate susidūrę su gettext? Visa darbo eiga keturiais sakiniais"

    **gettext** yra standartinis būdas programinei įrangai išversti — tiek
    Python kalboje, tiek toli už jos ribų. Jūsų kodas pažymi verstinus
    pranešimus; *ištraukiklis* surenka jas į šablono failą (`.pot`); vertėjas —
    paprastai ne programuotojas — užpildo po vieną katalogo failą (`.po`)
    kiekvienai kalbai, o šis sukompiliuojamas į dvejetainį `.mo`, kurį jūsų
    programa įkelia veikimo metu. Įprastas vertimo funkcijos pavadinimas yra
    `_`, todėl `_(t"Hello {name}")` skaitosi kaip „išversk šį pranešimą“.
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

## Projektavimo taisyklės { #the-design-rules }

- Verskite ištisus pranešimus, niekada ne sakinių nuotrupas.
- Priimkite tik paprastus kintamųjų vardus, tokius kaip `{name}`.
- Palikite `!r` ir `:.2f` programos kontrolėje, už katalogo ribų.
- Leiskite vertimams perstatyti ir kartoti žinomus vietaženklius, kartu
  neleisdami jiems pasiekti atributų ar pridėti formatavimo.
- Naudokite įprastus POT, PO ir MO failus bei įrankius, kurie juos jau skaito.

Ir atitinkamas sąrašas to, ką ji sąmoningai palieka ramybėje: ji nelokalizuoja
skaičių, valiutų ar datų — [pirma suformatuokite
juos](guide.md#locale-aware-values) su Babel; ji neekranuoja atvaizduotos
išvesties nei HTML, nei apvalkalui, nei terminalui; ir ji negali nuspręsti, ar
vertimas *teisingas* — tik ar jo vietaženkliai nepažeisti.

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

**Pradėkite čia** — gettext patirties nereikia:

<div class="grid cards" markdown>

- **[Pamoka](tutorial.md)** — nuo tuščio katalogo iki veikiančio japoniško
  vertimo penkiais žingsniais, kiekviena komanda parodyta su savo išvestimi.
- **[Kodėl t-eilutės](comparison.md)** — tas pats pranešimas, parašytas
  keturiais būdais, ir tai, ką `%(name)s`, `.format()` bei `$` eilutės
  perduoda katalogui.

</div>

**Naudokite** — darbinės žinynų dalys:

<div class="grid cards" markdown>

- **[Vadovas](guide.md)** — veikimo metu naudojama API: kurią įėjimo vietą
  rinktis, daugiskaita, kalbos pagal užklausą, atidėtos eilutės ir kas nutinka,
  kai katalogas klaidingas.
- **[Ištraukimas](extraction.md)** — `pybabel` žinynas: konfigūracija,
  savi funkcijų vardai ir tai, kaip jau turimi įrankiai patikrina šiuos
  katalogus be jokių pastangų.
- **[Realioje aplinkoje](workflow.md)** — ciklas taip, kaip jį sukioja
  komanda: atnaujinimo ciklas, fuzzy įrašai, CI vartai, vertimo platformos ir
  išsiuntimas.
- **[Migracija](migration.md)** — kaip tai perimti projekte, kuris jau turi
  katalogus, po vieną iškvietimo vietą.
- **[Vertėjams](translators.md)** — vienas puslapis tam, kas redaguoja `.po`
  failus.

</div>

**Supraskite** — nuo istorijos iki įgyvendinimo:

<div class="grid cards" markdown>

- **[Ištakos](background.md)** — kodėl ši biblioteka egzistuoja: trisdešimt
  metų gettext, du PEP'ai ir standartinės bibliotekos diskusija, užsibaigusi
  be atsakymo.
- **[Spąstai](pitfalls.md)** — ką iš tikrųjų sulaužė šios svetainės vertimas į
  trisdešimt penkias kalbas ir kurią pusę to įrankis gali pagauti.
- **[Kaip tai veikia](internals.md)** — nuo PEP 750 šablono objekto iki
  atvaizduotos eilutės ir podėliai, dėl kurių tikrinimas kainuoja mažai.

</div>

**Žinynas** — kontraktai:

<div class="grid cards" markdown>

- **[API](api.md)** — viskas, ką paketas eksportuoja, viename puslapyje.
- **[Specifikacija](spec.md)** — t-eilutės ↔ msgid susitarimas kaip stabilus,
  versijuotas kontraktas su mašininiu būdu skaitomu atitikties rinkiniu.

</div>

## Būsena { #status }

| | |
| --- | --- |
| Paketo versija | 0.1.0a7 |
| API stabilumas | alfa — Python API dar gali keistis |
| [Specifikacija](spec.md) | v1 su [atitikties rinkiniu](spec.md#conformance) |
| Python | 3.14 ir naujesnis; testuota su 3.14, 3.14t (laisvųjų gijų) ir 3.15 |
| Babel | 2.18 arba naujesnis, ir tik ten, kur veikia `pybabel` |
| Veikimo meto priklausomybės | jokių — standartinės bibliotekos `gettext` |
| Katalogų formatas | įprasti POT, PO ir MO |
| Pakeitimai | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

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
