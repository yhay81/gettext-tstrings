---
description: "Tas pats verstinas pranešimas, parašytas su %-formatu, .format(), flufl.i18n $ eilutėmis ir t-eilute, įskaitant tai, kaip kiekvienas iš jų susieja reikšmes ir elgiasi su sugadintu katalogu."
---

# Kodėl t-eilutės

Keturi būdai įdėti reikšmę į verstiną pranešimą, palyginti ant to paties
sakinio. Trumpai:

- Su **%-formatu** vertėjo ištrinta viena raidė virsta lūžiu produkcijoje.
- Su **str.format** vertimas gali nuskaityti atributus iš objektų, kuriuos
  perduoda jūsų kodas — įskaitant paslaptis.
- Su **`$` eilutėmis** (flufl.i18n) reikšmės netiesiogiai traukiamos iš
  kviečiančiosios funkcijos kintamųjų, o vietaženkliai su taškais taip pat
  pasiekia atributus.
- Su **t-eilutėmis** formatavimas lieka jūsų kode, vertimai tikrinami veikimo
  metu, o sugadintas katalogas grįžta prie pirminio teksto, o ne nulūžta.

Likusi šio puslapio dalis yra įrodymai, po vieną būdą iš eilės.

!!! note "Kiekvieną išverstą pranešimą paliečia trys šalys"

    **Katalogas** yra vertimų failas — `.po`, kol jį redaguoja žmonės, ir
    sukompiliuotas į `.mo`, kad programa jį įkeltų ([pamoka](tutorial.md)
    pereina abu). Kiekvieną pranešimą paliečia trys šalys: **programuotojas**
    parašo pirminę eilutę, **vertėjas** redaguoja katalogą — dažnai išorinėje
    platformoje, toli nuo bet kokios kodo peržiūros — o **programa** veikimo
    metu abu atvaizduoja kartu. Kiekvienas žemiau esantis formatavimo stilius
    į tą patį klausimą atsako kitaip: *kiek formatavimo kalbos katalogui
    leidžiama valdyti?* Pavyzdžiuose `_` yra įprastas vertimo funkcijos
    pavadinimas, o `tr` — šios bibliotekos.

## %-formatas { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Kas gali nutikti: viena ištrinta raidė vertime nulaužia atvaizdavimą.

Katalogo eilutė neša printf sintaksę, įskaitant pabaigoje esančią tipo raidę —
tą `s` viduje `%(name)s` — kurią lengva pražiūrėti ir lengva sugadinti:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Vieno simbolio pataisa PO redaktoriuje virsta klaidos pėdsaku produkcijoje. GNU
`msgfmt --check-format` tai pagauna, bet tik pranešimams, pažymėtiems
`python-format`, ir tik jei katalogas pakeliui į jūsų programą iš tikrųjų
praeina pro msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Tai pašalina pabaigos tipo raidę, išlaikant pavadintą, laisvai perstatomą
vietaženklį. Tai, kas gali nutikti, persikelia į kitą mainų pusę: vertimas
įgyja galią jūsų objektams.

`str.format` yra nedidelė reiškinių kalba, o jos iškvietimas eilutei reiškia
tos teisės perdavimą tai eilutei:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Dabar pakeiskite tas literalines eilutes tuo, ką grąžina `_()`. Jei
`Hello {name}` vertimas grįžta kaip `{conf.api_key}`, jo atvaizdavimas
išspausdina jūsų API raktą — ką nuskaityti, nusprendė katalogas, o ne jūsų
kodas. Katalogas nėra kodas, bet jis keliauja kaip duomenys: į vertimo
platformą, per kelias rankas, atgal kaip `.po`, sukompiliuojamas į `.mo`,
kartais visai iš už jūsų projekto ribų atsineštas. `.format()` kiekvienam to
kelio žingsniui suteikia prieigą prie perduodamų objektų atributų.

## `$` eilutės ir flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Standartinės bibliotekos [`string.Template`][stdlib-template] pateikia `$name`
interpoliacijos kalbą, tačiau pati nėra vertimo API. [`flufl.i18n`][flufl-i18n]
sujungia tą stilių su gettext katalogo paieška. Atkreipkite dėmesį, kad reikšmė
niekada neperduodama: flufl.i18n sudaro pakeitimų vardų erdvę iš
kviečiančiojo globalių ir vietinių kintamųjų — pranešimui prieinami visi
kintamieji, esantys iškvietimo vietoje. Neprivaloma `extras` atvaizdis
pirmenybę turi prieš abu. Jos vertėjui matoma sintaksė neturi nei pabaigos tipo
raidės, nei formato specifikacijos, o vietaženkliai lieka laisvai perstatomi.

Neprieinamas pakeitimas nesukelia klaidos. Kai `name = "Ada"`, o
kviečiančiojo vardų erdvėje nėra `nombre`, katalogo vertimas `Hello $nombre`
atvaizduojamas kaip `Hello $nombre`: neišspręstas vietaženklis lieka matomas.
Ta [dokumentuota elgsena][documented behavior] išsaugo likusią išversto
pranešimo dalį, užuot sužlugdžiusi iškvietimą. Išimtys, kylančios sprendžiant
atributą ar konvertuojant reikšmę, vis tiek gali sklisti aukštyn.

`flufl.i18n` už plikąjį `string.Template` galingesnis vienu svarbiu aspektu.
Jo [savas Template][custom Template] priima vietaženklius su taškais, tokius
kaip `$settings.api_key`, o jo [vertėjas][translator] tuos kelius išsprendžia
pagal kviečiančiojo reikšmes. Išverstas vietaženklis gali įvardyti bet kurį
prieinamą kviečiančiojo vietinį ar globalų kintamąjį ir, su taškine sintakse,
keliauti per jo atributus. Tai patogu, kai pranešimui reikia atributo, tačiau kartu
kviečiančiojo rėmelis tampa katalogo pakeitimų vardų erdvės dalimi. Toliau
esantis palyginimas apibūdina `flufl.i18n` 6.0.0, o ne visus įmanomus
`string.Template` naudojimo būdus.

## t-eilutės { #t-strings }

```python
tr(t"Hello {name}")
```

Katalogas vis dar mato `Hello {name}` ir lieka įprastu PO/MO katalogu.
Skirtumas yra tas, ką vertimui *leidžiama pasakyti* ir kas tai tikrina.

Ši biblioteka prieš atvaizduodama patikrina kiekvieną vertimą pagal pirminio
pranešimo vietaženklius ir priima tik plikus vardus, nieko daugiau. Prieš
`t"Hello {name}"`:

| Vertimas, kuriame yra | atmetamas su |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Atmesta nereiškia sudužo: pagal nutylėjimą biblioteka užrašo įspėjimą ir
atvaizduoja pirminį tekstą, todėl blogas katalogas niekada nepargriauna
programos —
[toks pat kontraktas, kokio laikosi pats gettext](guide.md#what-happens-when-a-catalog-is-wrong).

Formatavimas lieka ten, kur buvo parašytas — kode:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` niekada nepasiekia katalogo, todėl joks vertimas negali jo pakeisti ir
jokiam vertėjui nereikia į jį žiūrėti.

Dar vienas skirtumas yra įrankiai: t-eilutės yra nauja sintaksė, todėl jų
ištraukimui į `.pot` šiuo metu reikia t-eilutes suprantančio ištraukiklio,
tokio kaip tas, kurį šis paketas [pateikia Babel'iui](extraction.md).

## Greta { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Ar vietaženklis pavadintas? | taip | taip | taip | taip |
| Ar vertėjas gali perstatyti vietaženklius? | taip | taip | taip | taip |
| Iš kur ateina reikšmės? | iš aiškaus atvaizdžio | iš aiškių argumentų | iš kviečiančiojo vietinių ir globalių kintamųjų bei neprivalomo `extras` | iš reikšmių, pagautų t-eilutės viduje |
| Ar katalogas gali pakeisti reikšmės formatavimą? | taip | taip | ne | ne |
| Ar katalogas gali siekti į objektų vidų (prieiga prie atributų)? | ne | taip | taip, su taškiniais vardais | ne |
| Vertimas *praleidžia* vietaženklį — kas atvaizduojama? | reikšmė tyliai dingsta | reikšmė tyliai dingsta | reikšmė tyliai dingsta | pirminis tekstas, su įspėjimu ([pagal nutylėjimą](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Vertimas *prideda* nežinomą vietaženklį — kas atvaizduojama? | išimtis | išimtis | vietaženklis lieka matomas kaip tekstas | pirminis tekstas, su įspėjimu ([pagal nutylėjimą](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Ar vietaženkliai tikrinami atvaizdavimo metu? | ne | ne | ne | taip (žr. žemiau) |
| Kokią PO žymą Babel nustato, kad jau turimi įrankiai galėtų tikrinti? | `python-format` | `python-brace-format` | jokios | `python-brace-format` |
| Ar naudoja įprastus PO/MO katalogus? | taip | taip | taip | taip |
| Ar reikia savo pirminio kodo ištraukiklio? | ne | ne | ne | taip, šiuo metu |

Dėl atvaizdavimo meto patikros: vienaskaitos pranešimai tikrinami dėl tikslaus
vietaženklių sutapimo. Daugiskaitos pranešimai taip pat tikrinami — pagal
[sąjungos/sankirtos taisyklę](spec.md), kuri leidžia tikslinės kalbos
daugiskaitos formoms skirtis nuo pirminės kalbos; griežtesnė kiekvienos formos
patikra vykdoma kompiliuojant katalogus ([Ištraukimas](extraction.md)).

Formato žymos eilutė kalba apie vietaženklius suprantantį tikrinimą, o ne apie
katalogų suderinamumą. `jokios` reiškia, kad standartiniai gettext įrankiai vis
tiek perskaito ir sukompiliuoja pranešimą, bet `msgfmt --check-format` neturi
jokios `$` vietaženklių gramatikos, kurią galėtų pritaikyti.

## Kiek tai kainuoja { #what-it-costs }

F-eilutės taip panaudoti apskritai neįmanoma — tuo metu, kai ją pamato bet kuri
biblioteka, ji jau yra baigta eilutė, tad jos vertimas reiškia nuotrupos
vertimą. T-eilutės ([PEP 750]) laiko statinį tekstą ir reikšmes atskirai,
išlaikydamos į f-eilutes panašią sintaksę ir aiškų reikšmių susiejimą.
`$` eilutės jau siūlo glaustą alternatyvą su kitokiu susiejimo ir gedimų
modeliu. `flufl.i18n` yra brandus paketas, veikiantis su Python 3.10 ir
naujesniais; `gettext-tstrings` šiuo metu yra alfa, o kadangi t-eilutės yra
nauja sintaksė, jam reikia Python 3.14 arba naujesnio.

Kita kaina — pats apribojimas: interpoliacija turi būti paprastas vardas.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Tai tikras apribojimas. Kartu su reikšmių susiejimu pirminiame kode ir
vietaženklių tikrinimu veikimo metu jis neleidžia katalogo eilutėms skaičiuoti
reiškinių ir išlaiko vietaženklių vardus prasmingus.

Kaip Python priėjo šią sankryžą — du PEP'ai, parašyti su dešimties metų
tarpu, ir standartinės bibliotekos diskusija, užsibaigusi be atsakymo —
papasakota su šaltiniais puslapyje [Ištakos](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
