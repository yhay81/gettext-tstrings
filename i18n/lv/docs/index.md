---
description: "Tulkojiet pilnus t-virkņu ziņojumus caur gettext un Babel, formatējumu paturot ārpus kataloga."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Uzrakstiet teikumu vienreiz.<br>Tulkojiet to veselu.

Droša gettext un Babel integrācija Python 3.14+ t-virknēm — vērtība paliek
savā vietā, un katalogs redz visu ziņojumu:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Sākt pamācību :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Kāpēc t-virknes](comparison.md){ .md-button }

Šī vietne praktizē to, ko dokumentē: katrs valodas izdevums — navigācija,
uzraksti un daudzskaitli ievērojošā būvējuma atskaite — tiek renderēts no PO
katalogiem ar
[paša `gettext-tstrings` palīdzību](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalogs saņem pilnu teikumu `Hello {name}`. Tulkojums drīkst `{name}`
pārkārtot vai atkārtot; tas nedrīkst to nomest, izdomāt jaunu vai pievienot
tam savu formatējumu — šī bibliotēka to pārbauda, un sabojāts katalogs
atkāpjas uz avota tekstu, nevis avarē.

!!! note "Vai gettext jums ir jaunums? Visa darbplūsma četros teikumos"

    **gettext** ir standarta veids, kā programmatūra tiek tulkota — gan
    Python, gan tālu aiz tā. Jūsu kods atzīmē tulkojamās virknes;
    *ekstraktors* savāc tās veidnes failā (`.pot`); tulkotājs — parasti nevis
    programmētājs — aizpilda vienu kataloga failu (`.po`) katrai valodai, kas
    tiek kompilēts binārā `.mo` failā, ko jūsu lietotne ielādē izpildlaikā.
    Tulkošanas funkcijas ierastais nosaukums ir `_`, tāpēc `_(t"Hello {name}")`
    lasās kā “iztulko šo teikumu”. **[Pamācība](tutorial.md)** izstaigā visu
    ceļu — atzīmēt, ekstrahēt, iztulkot, kompilēt, palaist — aptuveni piecās
    minūtēs.

## Problēma, ko tas risina { #the-problem-it-solves }

F-virkne ir jau interpolēta brīdī, kad to ierauga kāda bibliotēka —
`f"Hello {name}"` ir kļuvis par `"Hello Ada"`, un fragmentu tulkošana ap
vērtību lauž gramatiku lielākajā daļā valodu. T-virkne ([PEP 750]) tur
statisko tekstu, aprēķinātās vērtības, avota izteiksmes, konversijas un
formāta specifikācijas atsevišķi — un tieši tāds dalījums ir vajadzīgs
ziņojumu katalogam.
[Ko tas maina](comparison.md), salīdzinot ar `%(name)s`, `.format()` un
`$`-virknēm.

Tomēr ne gettext, ne Babel nepasaka, kā t-virkne kļūst par ziņojumu. Šī
bibliotēka izdara šo izvēli, pieraksta to kā [versionētu specifikāciju](spec.md)
un piegādā [atbilstības komplektu](spec.md#conformance), lai to pārbaudītu.

## Izvēle, ko tas izdara { #the-choice-it-makes }

- Tulkot pilnus ziņojumus, nekad ne teikumu fragmentus.
- Pieņemt tikai vienkāršus mainīgo nosaukumus, tādus kā `{name}`.
- Paturēt `!r` un `:.2f` lietotnes kontrolē, ārpus kataloga.
- Ļaut tulkotājiem pārkārtot un atkārtot zināmos vietturus — bet ne izsaukt
  atribūtus un ne pievienot formatēšanas uzvedību.
- Izmantot parastos POT, PO un MO failus un rīkus, kas tos jau lasa.

## Instalēšana { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 vai jaunāks. **Renderēšanai nav atkarību** — tā izmanto standarta
bibliotēkas `gettext` un neko citu.

Ekstrakcija un katalogu validācija notiek caur [Babel], tāpēc instalējiet šo
papildinājumu visur, kur darbojas `pybabel`, kas parasti ir izstrādes vai CI
vide, nevis produkcijas attēls:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Kurp doties tālāk { #where-to-go-next }

Šeit nonāk trīs veidu lasītāji: tas, kurš tulko savu pirmo programmu; tas,
kurš iebūvē tulkošanu īstā projektā; un tas, kurš grib precīzi zināt, kāpēc
mehānismam ir tieši šāda forma. Katram ir sava taka.

**Mācīties to** — pieredze ar gettext netiek prasīta:

<div class="grid cards" markdown>

- **[Pamācība](tutorial.md)** — sāciet šeit: no tukša direktorija līdz
  strādājošam tulkojumam japāņu valodā piecos soļos, katra komanda parādīta
  kopā ar tās izvadi.
- **[Kāpēc t-virknes](comparison.md)** — viens un tas pats ziņojums, uzrakstīts
  četros veidos, un tas, ko katalogam pasniedz `%(name)s`, `.format()` un
  `$`-virknes.
- **[Priekšvēsture](background.md)** — kāpēc šī bibliotēka pastāv: trīsdesmit
  gadi gettext, divi PEP un standarta bibliotēkas diskusija, kas noslēdzās bez
  atbildes.

</div>

**Lietot to nopietni** — darba uzziņas:

<div class="grid cards" markdown>

- **[Ceļvedis](guide.md)** — izpildlaika API: daudzskaitļi, valodas katram
  pieprasījumam, atliktās virknes un tas, kas notiek, kad katalogs ir kļūdains.
- **[Ekstrakcija](extraction.md)** — `pybabel` uzziņa: konfigurācija, pielāgoti
  funkciju nosaukumi un tas, kā jau esošie rīki validē šos katalogus bez
  papildu pūlēm.
- **[Produkcijā](workflow.md)** — cikls tā, kā to izpilda komanda:
  atjaunināšanas cikls, fuzzy ieraksti, CI vārti, tulkošanas platformas un
  valodas katram pieprasījumam tīmekļa lietotnē.
- **[API](api.md)** — viss, ko pakotne eksportē, vienā lapā.

</div>

**Saprast to** — no principiem līdz implementācijai:

<div class="grid cards" markdown>

- **[Kā tas darbojas](internals.md)** — no PEP 750 šablona objekta līdz
  renderētai virknei un kešatmiņām, kas padara pārbaudi lētu.
- **[Specifikācija](spec.md)** — konvencija t-virkne ↔ msgid kā stabils,
  versionēts kontrakts ar mašīnlasāmu atbilstības komplektu.

</div>

## Statuss { #status }

Alfa versija. Kontrakts ir apzināti mazs, un [specifikācija](spec.md) ir tā
stabilā daļa; Python API vēl var mainīties. Pirms stabila laidiena tam
nepieciešami plašāki valodu fixture komplekti, ilgstoša veiktspējas
uzraudzība, API pārskats no cilvēkiem, kuri gettext un Babel lieto nopietni,
un savietojamības testi visos atbalstītajos Python un Babel laidienos.

[Problēmziņojumi un pull request](https://github.com/yhay81/gettext-tstrings/issues)
ir gaidīti — alfa ir tieši tas brīdis, kad par saskarni vēl ir vērts strīdēties.

## Pievienojieties kopienai { #join-the-community }

- Izvēlieties
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  kā ierobežotu pirmo ieguldījumu.
- Uzdodiet jautājumus par lietošanu
  [Q&A diskusijās](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Atnesiet produkcijas gettext darbplūsmas un API idejas uz
  [Ideas diskusijām](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Izlasiet
  [ieguldījuma ceļvedi](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md),
  pirms atverat pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
