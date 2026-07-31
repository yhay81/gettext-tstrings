---
description: "Viens un tas pats tulkojamais ziņojums, uzrakstīts ar %-formātu, .format(), flufl.i18n $-virknēm un t-virkni, salīdzināts pēc tulkotāju kļūdām, kataloga varas un integrācijas cenas."
---

# Kāpēc t-virknes

Četri veidi, kā ielikt vērtību tulkojamā ziņojumā, salīdzināti uz viena un tā
paša ziņojuma. Visi četri savus vietturus nosauc un ļauj tulkotājam tos
pārkārtot; tie atšķiras ar to, kas notiek, kad tulkojums ir kļūdains, ar to,
cik tālu jūsu programmā katalogs spēj sniegties, un ar to, cik maksā to
pārņemšana.

Vispirms nāk tabulas, lai jūs varētu atrast sev svarīgo rindu un izlasīt tikai
to sadaļu, kas aiz tās stāv.

!!! note "Katram iztulkotam ziņojumam pieskaras trīs puses"

    **Katalogs** ir tulkojumu fails — `.po`, kamēr to rediģē cilvēki, un
    kompilēts uz `.mo`, lai lietotne to ielādētu ([pamācība](tutorial.md)
    izstaigā abus). Katram ziņojumam pieskaras trīs puses: **izstrādātājs**
    uzraksta avota virkni, **tulkotājs** rediģē katalogu — bieži vien ārējā
    platformā, tālu no jebkādas koda pārskatīšanas —, un **lietotne**
    izpildlaikā renderē abus kopā. Katrs no zemāk aprakstītajiem formatēšanas
    stiliem atbild uz vienu un to pašu jautājumu citādi: *cik daudz no
    formāta valodas katalogs drīkst kontrolēt?* Piemēros `_` ir ierastais
    tulkošanas funkcijas nosaukums, bet `tr` — šīs bibliotēkas nosaukums.

## Blakus salikts { #side-by-side }

**Kad tulkotājs kļūdās.** Katalogs iziet caur daudzām rokām, un lielākā daļa
no tā, kas tajā noiet greizi, ir nejaušība:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Tulkojums *nomet* vietturi — kas tiek renderēts? | vērtība klusējot pazūd | vērtība klusējot pazūd | vērtība klusējot pazūd | avota ziņojums, ar brīdinājumu ([pēc noklusējuma](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Tulkojums *pievieno* nezināmu vietturi — kas tiek renderēts? | izņēmums | izņēmums | vietturis paliek redzams kā teksts | avota ziņojums, ar brīdinājumu ([pēc noklusējuma](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Tulkojums *pārformatē* vietturi — kas tiek renderēts? | tas, ko prasīja katalogs, vai izņēmums, ja tipa burts vairs neder vērtībai | tas, ko prasīja katalogs | `$`-virknēs nav izsakāms | avota ziņojums, ar brīdinājumu |
| Vai vietturi tiek pārbaudīti renderēšanas brīdī? | nē | nē | nē | jā (skatiet zemāk) |

**Kāda vara ir katalogam.** Tulkojums ir dati no ārpuses jūsu repozitorijam, un
katrs stils tam iedod atšķirīgu varas daudzumu:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| No kurienes nāk vērtības? | no skaidra attēlojuma | no skaidriem argumentiem | no izsaucēja lokālajiem un globālajiem mainīgajiem, plus neobligātā `extras` | no vērtībām, kas notvertas t-virknē |
| Vai katalogs var mainīt to, kā vērtība tiek formatēta? | jā | jā | nē | nē |
| Vai katalogs var sniegties objektos (piekļuve atribūtiem)? | nē | jā | jā, ar nosaukumiem caur punktu | nē |
| Kur dzīvo “tekošā valoda”? | tur, kur to noliek lietotne | tur, kur to noliek lietotne | valodu kodu steks uz koplietotā lietotnes objekta | `ContextVar`, katram uzdevumam vai pieprasījumam |

**Cik maksā integrācija.** Viss augšminētais ir bez maksas, ja rīki der; tieši
šeit tie var arī nederēt:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Minimālais Python | jebkurš | jebkurš | 3.10 | **3.14** |
| Briedums | standarta bibliotēka | standarta bibliotēka | stabils laidiens | **alfa** |
| Vai izmanto parastus PO/MO katalogus? | jā | jā | jā | jā |
| Vai vajadzīgs pielāgots pirmkoda ekstraktors? | nē | nē | nē | pašlaik jā |
| Kādu PO karogu izsecina Babel, lai esošie rīki varētu validēt? | `python-format` | `python-brace-format` | nekādu | `python-brace-format` |

Par pārbaudi renderēšanas brīdī: vienskaitļa ziņojumiem tiek pārbaudīta precīza
vietturu sakritība. Daudzskaitļa ziņojumi arī tiek pārbaudīti — pret
[apvienojuma/šķēluma likumu](spec.md), kas ļauj mērķa valodas daudzskaitļa
formām atšķirties no avota valodas formām; stingrākā pārbaude katrai formai
notiek, kad katalogi tiek kompilēti ([Ekstrakcija](extraction.md)).

Rinda par formāta karogu ir par vietturus ievērojošu validāciju, nevis par
katalogu savietojamību. `nekādu` nozīmē, ka standarta gettext rīki ziņojumu
joprojām nolasa un kompilē, taču `msgfmt --check-format` nav nekādas
`$`-vietturu gramatikas, ko piemērot.

## Savietojamība un briedums { #compatibility-and-maturity }

Pēdējās tabulas pirmās divas rindas ir tās, kas izlemj pārņemšanu, tāpēc tās ir
vērts pateikt skaidri, nevis atstāt šūnās.

`%`-formāts un `.format()` ir iebūvēti Python un tiem nav vajadzīga nekāda
atkarība. [`flufl.i18n`][flufl-i18n] ir nobriedusi pakotne — izlaista un
produkcijā lietota —, kas darbojas uz Python 3.10 un jaunākiem.
`gettext-tstrings` ir **alfa**, un tam vajadzīgs **Python 3.14 vai jaunāks**,
jo t-virknes ir jauna sintakse 3.14 versijā — atpakaļpārneses nav un nevar būt.
Tā [specifikācija](spec.md) ir tā stabilā daļa; Python API pirms 1.0 vēl var
mainīties.

Ko neviens no tiem nemaksā, ir katalogu savietojamība. Visi četri rada parastus
POT/PO/MO failus, ko jau lasa katrs PO redaktors, tulkošanas platforma un GNU
gettext rīks, tāpēc zemāk aprakstītā izvēle ir atgriezeniska tā, kā katalogu
*formātu* maiņa nebūtu. [Migrācija](migration.md) apraksta esoša projekta
pārcelšanu.

Sadaļas zemāk parāda katru kompromisu detalizēti, pa vienai metodei.

## %-formāts { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Kas var noiet greizi: sabojāts vietturis kļūst par izpildlaika izņēmumu, ja vien
kataloga validācija to nenoķer agrāk.

Kataloga virkne nes printf sintaksi, ieskaitot beigu tipa burtu — to `s`
virknē `%(name)s` —, ko ir viegli nepamanīt un viegli sabojāt:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Viena rakstzīmes labojums PO redaktorā kļūst par izpildlaika izņēmumu, ja vien
to iepriekš nenoķer katalogu validācija. GNU `msgfmt --check-format` šo gan
pamana, taču tikai ziņojumiem ar karogu `python-format` un tikai tad, ja
katalogs ceļā uz jūsu lietotni patiešām iziet cauri msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Tas atbrīvojas no beigu tipa burta, paturot nosauktu, brīvi pārkārtojamu
vietturi. Tas, kas var noiet greizi, pārvietojas uz otru maiņas pusi:
tulkojums iegūst varu pār jūsu objektiem.

`str.format` ir maza izteiksmju valoda, un tās izsaukšana uz virknes nozīmē
šai virknei piešķirt tiesības to lietot:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Tagad aizstājiet šīs literālās virknes ar to, ko atgriež `_()`. Ja `Hello
{name}` tulkojums atnāk atpakaļ kā `{conf.api_key}`, tā renderēšana izdrukā
jūsu API atslēgu — nolasāmo izlēma katalogs, nevis jūsu kods. Katalogs nav
kods, taču tas ceļo kā dati: prom uz tulkošanas platformu, caur vairākām
rokām, atpakaļ kā `.po`, kompilēts par `.mo`, dažkārt pilnībā ievests no
ārpuses jūsu projektam. `.format()` piešķir katram šī ceļojuma posmam piekļuvi
padoto objektu atribūtiem.

## `$`-virknes un flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Standarta bibliotēkas [`string.Template`][stdlib-template] piegādā `$name`
interpolācijas valodu, bet pats par sevi nav tulkošanas API.
[`flufl.i18n`][flufl-i18n] savieno šo stilu ar gettext kataloga meklēšanu.
Ievērojiet, ka vērtība nekad netiek padota: flufl.i18n izveido aizstāšanas
vārdtelpu no izsaucēja globālajiem un lokālajiem mainīgajiem — ziņojumam ir
pieejami visi mainīgie, kas eksistē izsaukuma vietā. Neobligāts `extras`
attēlojums ir pārāks par abiem. Tā tulkotājam redzamajā sintaksē nav ne beigu
tipa burta, ne formāta specifikatora, un vietturi paliek brīvi pārkārtojami.

Nepieejama aizstāšana neizraisa kļūdu. Ja `name = "Ada"` un izsaucēja
vārdtelpā nav nekāda `nombre`, kataloga tulkojums `Hello $nombre` tiek
renderēts kā `Hello $nombre`: neatrisinātais vietturis paliek redzams. Šī
[dokumentētā uzvedība][documented behavior] saglabā pārējo iztulkotā ziņojuma
daļu, nevis liek izsaukumam neizdoties. Izņēmumi, kas rodas, atrisinot
atribūtu vai konvertējot vērtību, joprojām var izplatīties tālāk.

`flufl.i18n` vienā būtiskā ziņā spēj vairāk nekā kails `string.Template`. Tā
[pielāgotais Template][custom Template] pieņem vietturus ar punktiem, tādus kā
`$settings.api_key`, un tā [tulkotājs][translator] atrisina šos ceļus pret
izsaucēja vērtībām. Iztulkots vietturis drīkst nosaukt jebkuru pieejamu
izsaucēja lokālo vai globālo mainīgo un, ar punktu sintaksi, izstaigāt tā
atribūtus. Tas ir ērti, kad ziņojumam ir vajadzīgs atribūts, bet vienlaikus
padara izsaucēja frame par kataloga aizstāšanas vārdtelpas daļu. Šeit
esošais salīdzinājums apraksta `flufl.i18n` 6.0.0, nevis katru iespējamo
`string.Template` lietojumu.

Tā atbild arī uz jautājumu, ko pārējie divi formatēšanas stili pilnībā atstāj
lietotnes ziņā: *kura* valoda ir tekošā un kā to nomainīt. [Lietotnes
objekts][application object] uztur valodu steku, `_.push(code)` un `_.pop()` to
pārvieto, `with _.using(code):` ļauj tos iegult vienu otrā, un
[stratēģija][strategy] atrod katalogu attiecīgajam valodas kodam, tā ka lietotne
pati nekad nedarbojas ar kataloga objektiem. Serveris, kuram vienas darba
vienības laikā jāsagatavo teksts vairāk nekā vienā valodā — lapa lasītājam,
paziņojums kādam, kura konts ir iestatīts citādi —, ir tieši tas gadījums, kura
dēļ tas pastāv.

Steks dzīvo uz šī lietotnes objekta, ko dala viss process. Divi pārklājušies
pieprasījumi tādējādi dala vienu steku, un bloki, kas nav strikti iegulti
*laikā*, pasniedz cits citam nepareizo valodu:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Šī bibliotēka saglabā to pašu spēju — piesaistes iegulst un attinas tieši
tāpat —, bet tur to `ContextVar`, nevis koplietotā stekā, tāpēc augstāk
redzamā pārklāšanās atrisinās katram uzdevumam atsevišķi. Ekvivalenti ir lapā
[Vairākas valodas vienlaikus](guide.md#several-languages-at-once). Ko tā
nepiedāvā, ir meklēšana no valodas koda uz katalogu: jūs padodat tulkojumu
objektu, kas parastajā gadījumā ir viens `gettext.translation()` izsaukums, un
standarta bibliotēka kešo parsēto katalogu.

## t-virknes { #t-strings }

```python
tr(t"Hello {name}")
```

Katalogs joprojām redz `Hello {name}` un paliek parasts PO/MO katalogs.
Atšķirība ir tajā, ko tulkojumam *ir atļauts teikt*, un tajā, kas to pārbauda.

Šī bibliotēka pirms renderēšanas validē katru tulkojumu pret avota ziņojuma
vietturiem, un tā pieņem kailus nosaukumus un neko citu. Pret
`t"Hello {name}"`:

| Tulkojums, kas satur | tiek noraidīts ar |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Noraidīts nenozīmē avarējis: pēc noklusējuma bibliotēka ieraksta žurnālā
brīdinājumu un renderē avota ziņojumu, tāpēc slikts katalogs nekad nenogāž
lietotni —
[tas pats kontrakts, ko ievēro pats gettext](guide.md#what-happens-when-a-catalog-is-wrong).

Formatējums paliek tur, kur tas uzrakstīts, — kodā:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nekad nenonāk katalogā, tāpēc neviens tulkojums to nevar mainīt un
nevienam tulkotājam uz to nav jāskatās. Tomēr tas ir *fiksēts* formāts, nevis
lokalizēts — ciparu un atdalītāju izvēle katrai valodai ir
[Babel darbs, pirms izsaukuma](guide.md#locale-aware-values).

Vēl viena atšķirība ir rīki: t-virknes ir jauna sintakse, tāpēc to
ekstrahēšanai `.pot` failā pašlaik ir vajadzīgs t-virknes pratējs ekstraktors,
piemēram, tāds, kādu šī pakotne [piedāvā Babel](extraction.md).

## Ierobežojuma cena { #the-cost-of-the-restriction }

Bez Python prasības visa tā cena ir viens noteikums: interpolācijai jābūt
kailam nosaukumam.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Tas ir īsts ierobežojums, un tas ir tas pats ierobežojums, kas rada augšminētās
garantijas. Kopā ar vērtību piesaisti avota pusē un vietturu pārbaudi
izpildlaikā tas neļauj kataloga virknēm izvērtēt izteiksmes un saglabā vietturu
nosaukumus jēgpilnus tam, kurš tos tulko.

F-virkni šādi izmantot nav iespējams vispār — brīdī, kad kāda bibliotēka to
ierauga, tā jau ir pabeigta virkne, tāpēc tās tulkošana nozīmē fragmenta
tulkošanu. T-virknes ([PEP 750]) tur statisko tekstu un vērtības atsevišķi,
vienlaikus saglabājot f-virknei līdzīgu sintaksi un skaidru vērtību piesaisti.

Kā Python šeit nonāca — divi PEP ar desmit gadu starpību un
standarta bibliotēkas diskusija, kas noslēdzās bez atbildes — ir izstāstīts ar
avotiem [Priekšvēsturē](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
