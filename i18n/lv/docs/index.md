---
description: "Tulkojiet pilnus t-virkņu ziņojumus caur gettext un Babel, vērtības un formatējumu paturot ārpus kataloga."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Tulkojiet veselus ziņojumus,<br>nevis virkņu fragmentus.

`gettext-tstrings` savieno Python 3.14+ t-virknes ar standarta gettext
katalogiem un Babel rīkiem. Vērtības un formatējums paliek lietotnes kodā;
katalogs tur pilnu ziņojumu ar vienkāršiem `{name}` vietturiem:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Sākt pamācību :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Salīdziniet alternatīvas](comparison.md){ .md-button }

Alfa · Python 3.14+ · parasti PO/MO katalogi · nav izpildlaika atkarību
{ .home-facts }

Šī vietne praktizē to, ko dokumentē: katrs valodas izdevums — navigācija,
uzraksti un daudzskaitli ievērojošā būvējuma atskaite — tiek renderēts no PO
katalogiem ar
[paša `gettext-tstrings` palīdzību](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Vai tas ir domāts jums? { #is-this-for-you }

**Piemērots jau šodien, ja** jūsu lietotne darbojas uz Python 3.14 vai
jaunāka; jūs jau lietojat gettext un Babel vai gribat pārņemt to PO/MO
darbplūsmu; un jūs gribat t-virkņu sintaksi ar nosauktiem vietturiem, kas tiek
pārbaudīti pirms renderēšanas.

**Vēl nav piemērots, ja** jums vajadzīgs Python 3.13 vai vecāks; jums
nepieciešams stabils Python API — šī ir alfa versija, un
[specifikācija](spec.md) ir tā daļa, kas ir nostabilizējusies; vai gandrīz viss
jūsu tulkojamais teksts atrodas veidņu valodā, nevis Python pirmkodā.

Jums jau ir katalogi? Tie turpina strādāt. `_("Hello {name}").format(name=name)`
un `tr(t"Hello {name}")` rada vienu un to pašu msgid, tāpēc esošie tulkojumi
pārmaiņu pārdzīvo — [Migrācija](migration.md) izstaigā visu pāreju.

## Ko katalogs drīkst pateikt { #what-the-catalog-may-say }

Katalogs saņem pilnu ziņojumu `Hello {name}`. Tulkojums drīkst `{name}`
pārkārtot vai atkārtot un drīkst pārrakstīt katru citu vārdu tam apkārt. Tas
nedrīkst vietturi nomest, izdomāt jaunu, caur to sniegties jūsu objektos vai
pievienot tam savu formatējumu.

Tāds ir viss solījums: **tulkojums nespēj mainīt tā ziņojuma struktūru, kuru
tas tulko.** Bibliotēka to pārbauda ceļā iekšā — kad katalogi tiek kompilēti —
un vēlreiz renderēšanas brīdī; sabojāts ieraksts, kas tomēr nonāk produkcijā,
ieraksta brīdinājumu un renderē avota ziņojumu, nevis avarē.

!!! note "Vai gettext jums ir jaunums? Visa darbplūsma četros teikumos"

    **gettext** ir standarta veids, kā programmatūra tiek tulkota — gan
    Python, gan tālu aiz tā. Jūsu kods atzīmē tulkojamos ziņojumus;
    *ekstraktors* savāc tās veidnes failā (`.pot`); tulkotājs — parasti nevis
    programmētājs — aizpilda vienu kataloga failu (`.po`) katrai valodai, kas
    tiek kompilēts binārā `.mo` failā, ko jūsu lietotne ielādē izpildlaikā.
    Tulkošanas funkcijas ierastais nosaukums ir `_`, tāpēc `_(t"Hello {name}")`
    lasās kā “iztulko šo ziņojumu”. **[Pamācība](tutorial.md)** izstaigā visu
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

## Dizaina noteikumi { #the-design-rules }

- Tulkot pilnus ziņojumus, nekad ne teikumu fragmentus.
- Pieņemt tikai vienkāršus mainīgo nosaukumus, tādus kā `{name}`.
- Paturēt `!r` un `:.2f` lietotnes kontrolē, ārpus kataloga.
- Ļaut tulkojumiem pārkārtot un atkārtot zināmos vietturus, vienlaikus liedzot
  tiem sniegties pie atribūtiem vai pievienot formatējumu.
- Izmantot parastos POT, PO un MO failus un rīkus, kas tos jau lasa.

Un tam atbilstošais saraksts ar to, ko tas apzināti atstāj mierā: tas
nelokalizē skaitļus, valūtas vai datumus — [noformatējiet tos vispirms](guide.md#locale-aware-values)
ar Babel; tas neekranē renderēto izvadi HTML, čaulai vai terminālim; un tas
nespēj spriest, vai tulkojums ir *pareizs*, tikai to, vai tā vietturi ir
neskarti.

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

**Sāciet šeit** — pieredze ar gettext netiek prasīta:

<div class="grid cards" markdown>

- **[Pamācība](tutorial.md)** — no tukša direktorija līdz strādājošam
  tulkojumam japāņu valodā piecos soļos, katra komanda parādīta kopā ar tās
  izvadi.
- **[Kāpēc t-virknes](comparison.md)** — viens un tas pats ziņojums, uzrakstīts
  četros veidos, un tas, ko katalogam pasniedz `%(name)s`, `.format()` un
  `$`-virknes.

</div>

**Lietojiet** — darba uzziņas:

<div class="grid cards" markdown>

- **[Ceļvedis](guide.md)** — izpildlaika API: kuru ieejas punktu lietot,
  daudzskaitļi, valodas katram pieprasījumam, atliktās virknes un tas, kas
  notiek, kad katalogs ir kļūdains.
- **[Ekstrakcija](extraction.md)** — `pybabel` uzziņa: konfigurācija, pielāgoti
  funkciju nosaukumi un tas, kā jau esošie rīki validē šos katalogus bez
  papildu pūlēm.
- **[Produkcijā](workflow.md)** — cikls tā, kā to izpilda komanda:
  atjaunināšanas cikls, fuzzy ieraksti, CI vārti, tulkošanas platformas un
  piegāde.
- **[Migrācija](migration.md)** — šī pārņemšana projektā, kuram jau ir
  katalogi, pa vienai izsaukuma vietai.
- **[Tulkotājiem](translators.md)** — viena lapa, ko iedot tam, kurš rediģē
  `.po` failus.

</div>

**Izprotiet** — no vēstures līdz implementācijai:

<div class="grid cards" markdown>

- **[Priekšvēsture](background.md)** — kāpēc šī bibliotēka pastāv: trīsdesmit
  gadi gettext, divi PEP un standarta bibliotēkas diskusija, kas noslēdzās bez
  atbildes.
- **[Kļūmes](pitfalls.md)** — ko šīs vietnes tulkošana trīsdesmit piecās
  valodās patiešām salauza un kuru pusi no tā rīks spēj noķert.
- **[Kā tas darbojas](internals.md)** — no PEP 750 šablona objekta līdz
  renderētai virknei un kešatmiņām, kas padara pārbaudi lētu.

</div>

**Atsauce** — kontrakti:

<div class="grid cards" markdown>

- **[API](api.md)** — viss, ko pakotne eksportē, vienā lapā.
- **[Specifikācija](spec.md)** — konvencija t-virkne ↔ msgid kā stabils,
  versionēts kontrakts ar mašīnlasāmu atbilstības komplektu.

</div>

## Statuss { #status }

| | |
| --- | --- |
| Pakotnes versija | 0.1.0a7 |
| API stabilitāte | alfa — Python API vēl var mainīties |
| [Specifikācija](spec.md) | v1 ar [atbilstības komplektu](spec.md#conformance) |
| Python | 3.14 un jaunāks; testēts ar 3.14, 3.14t (brīvpavedienu) un 3.15 |
| Babel | 2.18 vai jaunāks, un tikai tur, kur darbojas `pybabel` |
| Izpildlaika atkarības | nav — standarta bibliotēkas `gettext` |
| Katalogu formāts | parastie POT, PO un MO |
| Izmaiņas | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

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
