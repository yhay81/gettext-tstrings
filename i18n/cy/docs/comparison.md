---
description: "Yr un neges gyfieithadwy wedi'i hysgrifennu â fformat-%, .format(), llinynnau-$ flufl.i18n, a llinyn-t, wedi'u cymharu ar gamgymeriadau cyfieithwyr, awdurdod y catalog, a chost integreiddio."
---

# Pam llinynnau-t

Pedair ffordd o roi gwerth i mewn i neges gyfieithadwy, wedi'u cymharu ar yr un
neges. Mae'r pedair yn enwi eu dalwyr lle ac yn gadael i gyfieithydd eu
haildrefnu; maent yn gwahaniaethu yn yr hyn sy'n digwydd pan fo cyfieithiad yn
anghywir, yn faint o'ch rhaglen y gall y catalog ei chyrraedd, ac yn yr hyn y
mae eu mabwysiadu'n ei gostio.

Daw'r tablau'n gyntaf, fel y gallwch ddod o hyd i'r rhes sydd o bwys i chi a
darllen dim ond yr adran sydd y tu ôl iddi.

!!! note "Mae tair plaid yn cyffwrdd â phob neges wedi'i chyfieithu"

    **Catalog** yw'r ffeil gyfieithiadau — `.po` tra bo pobl yn ei golygu,
    wedi'i chrynhoi'n `.mo` i'r rhaglen ei llwytho (mae'r
    [tiwtorial](tutorial.md) yn cerdded drwy'r ddau). Mae tair plaid yn
    cyffwrdd â phob neges: mae'r **datblygwr** yn ysgrifennu'r llinyn
    ffynhonnell, mae **cyfieithydd** yn golygu'r catalog — yn aml ar lwyfan
    allanol, ymhell o unrhyw adolygiad cod — ac mae'r **rhaglen** yn rendro'r
    ddau gyda'i gilydd wrth redeg. Mae pob arddull fformatio isod yn ateb yr un
    cwestiwn yn wahanol: *faint o'r iaith fformat y caiff y catalog ei rheoli?*
    Yn yr enghreifftiau, `_` yw'r enw confensiynol ar y ffwythiant cyfieithu, ac
    `tr` yw un y llyfrgell hon.

## Ochr yn ochr { #side-by-side }

**Pan fo cyfieithydd yn gwneud camgymeriad.** Mae catalog yn teithio drwy lawer
o ddwylo, ac mae'r rhan fwyaf o'r hyn sy'n mynd o'i le ynddo'n ddamweiniol:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Mae cyfieithiad yn *gollwng* daliwr lle — beth sy'n rendro? | mae'r gwerth yn diflannu'n dawel | mae'r gwerth yn diflannu'n dawel | mae'r gwerth yn diflannu'n dawel | y neges ffynhonnell, gyda rhybudd ([yn ddiofyn](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Mae cyfieithiad yn *ychwanegu* daliwr lle anhysbys — beth sy'n rendro? | eithriad | eithriad | mae'r daliwr lle'n aros yn weladwy fel testun | y neges ffynhonnell, gyda rhybudd ([yn ddiofyn](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Mae cyfieithiad yn *ailfformatio* daliwr lle — beth sy'n rendro? | yr hyn a ofynnodd y catalog amdano, neu eithriad os nad yw'r llythyren fath yn ffitio'r gwerth mwyach | yr hyn a ofynnodd y catalog amdano | ni ellir ei fynegi mewn llinynnau-`$` | y neges ffynhonnell, gyda rhybudd |
| A wirir dalwyr lle adeg rendro? | na | na | na | ie (gweler isod) |

**Pa awdurdod sydd gan y catalog.** Data o'r tu allan i'ch storfa yw cyfieithiad,
ac mae pob arddull yn rhoi swm gwahanol o rym iddo:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| O ble y daw'r gwerthoedd? | o fapio penodol | o ymresymiadau penodol | o newidynnau lleol a global y galwr, ynghyd ag `extras` dewisol | o'r gwerthoedd a ddaliwyd y tu mewn i'r llinyn-t |
| A all y catalog newid sut y caiff gwerth ei fformatio? | ie | ie | na | na |
| A all y catalog gyrraedd i mewn i wrthrychau (mynediad priodoledd)? | na | ie | ie, ag enwau dotiog | na |
| Ble mae "yr iaith gyfredol" yn byw? | lle bynnag y mae'r rhaglen yn ei roi | lle bynnag y mae'r rhaglen yn ei roi | pentwr o godau iaith ar y gwrthrych rhaglen a rennir | `ContextVar`, fesul tasg neu gais |

**Beth mae'n ei gostio i integreiddio.** Mae popeth uchod am ddim os yw'r offer
yn ffitio; dyma lle efallai nad ydynt:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python lleiaf | unrhyw un | unrhyw un | 3.10 | **3.14** |
| Aeddfedrwydd | llyfrgell safonol | llyfrgell safonol | rhyddhad sefydlog | **alffa** |
| A yw'n defnyddio catalogau PO/MO cyffredin? | ie | ie | ie | ie |
| A oes angen echdynnwr ffynhonnell pwrpasol? | na | na | na | ie, ar hyn o bryd |
| Pa faner PO y mae Babel yn ei chasglu, i offer sy'n bodoli eu dilysu? | `python-format` | `python-brace-format` | dim | `python-brace-format` |

Ynghylch y gwiriad adeg rendro: gwirir negeseuon unigol am gyfatebiaeth union o
ddalwyr lle. Gwirir negeseuon lluosog hefyd, yn erbyn y
[rheol uniad/croestoriad](spec.md) sy'n gadael i ffurfiau lluosog iaith darged
fod yn wahanol i rai'r ffynhonnell; mae'r gwiriad llymach fesul ffurf yn rhedeg
pan grynhoir catalogau ([Echdynnu](extraction.md)).

Mae rhes y faner fformat yn ymwneud â dilysu sy'n ymwybodol o ddalwyr lle, nid â
chydnawsedd catalogau. Mae `dim` yn golygu bod offer gettext safonol yn dal i
ddarllen a chrynhoi'r neges, ond nad oes gan `msgfmt --check-format` unrhyw
ramadeg dalwyr lle `$` i'w chymhwyso.

## Cydnawsedd ac aeddfedrwydd { #compatibility-and-maturity }

Dwy res gyntaf y tabl olaf yw'r rhai sy'n penderfynu mabwysiadu, felly mae'n
werth eu nodi'n blaen yn hytrach nag fel celloedd.

Mae fformat-`%` a `.format()` wedi'u hadeiladu i mewn i Python ac nid oes angen
unrhyw ddibyniaeth o gwbl arnynt. Pecyn aeddfed yw
[`flufl.i18n`][flufl-i18n], wedi'i ryddhau ac mewn defnydd cynhyrchu, sy'n
rhedeg ar Python 3.10 a diweddarach. **Alffa** yw `gettext-tstrings` ac mae
angen **Python 3.14 neu fwy newydd** arno, am fod llinynnau-t yn gystrawen
newydd yn 3.14 — nid oes ôl-borthiad ac ni all fod un. Ei
[fanyleb](spec.md) yw'r rhan sefydlog ohono; efallai y bydd yr API Python yn
symud eto cyn 1.0.

Yr hyn nad yw'r un ohonynt yn ei gostio yw cydnawsedd catalogau. Mae'r pedair yn
cynhyrchu ffeiliau POT/PO/MO cyffredin y mae pob golygydd PO, llwyfan cyfieithu,
ac offeryn gettext GNU eisoes yn eu darllen, felly mae'r dewis isod yn
gildroadwy mewn ffordd na fyddai newid *fformatau* catalog. Mae
[Mudo](migration.md) yn ymdrin â symud prosiect sy'n bodoli eisoes.

Mae'r adrannau isod yn dangos pob cyfaddawd yn fanwl, un dull ar y tro.

## fformat-% { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Beth all fynd o'i le: daw daliwr lle wedi'i niweidio'n eithriad rhedeg, oni bai
bod dilysu catalogau'n ei ddal yn gyntaf.

Mae llinyn y catalog yn cario cystrawen printf, gan gynnwys llythyren math ar y
diwedd — yr `s` yn `%(name)s` — sy'n hawdd ei hanwybyddu ac yn hawdd ei
niweidio:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Mae golygiad un nod mewn golygydd PO yn troi'n eithriad adeg rhedeg oni bai bod
dilysu catalogau'n ei ddal yn gyntaf. Mae `msgfmt --check-format` GNU yn dal hwn,
ond dim ond ar gyfer negeseuon wedi'u baneru'n `python-format`, a dim ond os yw'r
catalog yn mynd drwy msgfmt mewn gwirionedd ar ei ffordd i'ch rhaglen.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Mae'n cael gwared ar y llythyren math ar y diwedd tra'n cadw daliwr lle wedi'i
enwi y gellir ei aildrefnu'n rhydd. Mae'r hyn all fynd o'i le'n symud i ochr
arall y gyfnewidfa: mae'r cyfieithiad yn ennill grym dros eich gwrthrychau.

Iaith ymadroddion fach yw `str.format`, ac mae ei galw ar linyn yn golygu rhoi
i'r llinyn hwnnw'r hawl i'w defnyddio:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Nawr rhowch beth bynnag y mae `_()` yn ei ddychwelyd yn lle'r llinynnau
llythrennol hynny. Os daw cyfieithiad o `Hello {name}` yn ôl fel
`{conf.api_key}`, mae ei rendro'n argraffu eich allwedd API — y catalog, nid
eich cod, a benderfynodd beth a ddarllenwyd. Nid cod yw catalog, ond mae'n
teithio fel data: allan i lwyfan cyfieithu, drwy sawl pâr o ddwylo, yn ôl fel
`.po`, wedi'i grynhoi'n `.mo`, weithiau wedi'i gludo i mewn o'r tu allan i'ch
prosiect yn gyfan gwbl. Mae `.format()` yn rhoi mynediad priodoleddau at y
gwrthrychau a basiwch i mewn ym mhob cam o'r daith honno.

## Llinynnau `$` a flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Mae [`string.Template`][stdlib-template] y llyfrgell safonol yn cyflenwi'r iaith
ryngosod `$name`, ond nid yw ei hun yn API cyfieithu. Mae
[`flufl.i18n`][flufl-i18n] yn cyfuno'r arddull honno â chwilio catalog gettext.
Sylwch nad yw'r gwerth byth yn cael ei basio i mewn: mae flufl.i18n yn adeiladu'r
gofod enwau amnewid o globals a locals y galwr — mae pa newidynnau bynnag sy'n
bodoli yn safle'r alwad ar gael i'r neges. Mae mapio `extras` dewisol yn cael
blaenoriaeth dros y ddau. Nid oes gan ei chystrawen sy'n wynebu cyfieithwyr
lythyren math ar y diwedd na manyleb fformat, ac mae dalwyr lle'n aros yn rhydd
i'w haildrefnu.

Nid yw amnewidiad nad yw ar gael yn codi gwall. Gyda `name = "Ada"` a dim
`nombre` yng ngofod enwau'r galwr, mae cyfieithiad catalog o `Hello $nombre` yn
rendro fel `Hello $nombre`: mae'r daliwr lle heb ei ddatrys yn aros yn weladwy.
Mae'r [ymddygiad dogfenedig] hwnnw'n cadw gweddill y neges wedi'i chyfieithu yn
lle methu'r alwad. Gall eithriadau a godir wrth ddatrys priodoledd neu
drawsnewid gwerth ledaenu o hyd.

Mae `flufl.i18n` yn fwy galluog na `string.Template` noeth mewn un ffordd
berthnasol. Mae ei [Template pwrpasol] yn derbyn dalwyr lle dotiog megis
`$settings.api_key`, ac mae ei [chyfieithydd] yn datrys y llwybrau hynny yn
erbyn gwerthoedd y galwr. Caiff daliwr lle wedi'i gyfieithu enwi unrhyw local
neu global sydd ar gael i'r galwr ac, â chystrawen ddotiog, deithio drwy ei
briodoleddau. Mae hynny'n gyfleus pan fo neges angen priodoledd, tra hefyd yn
gwneud ffrâm y galwr yn rhan o ofod enwau amnewid y catalog. Mae'r gymhariaeth
yma'n disgrifio `flufl.i18n` 6.0.0, nid pob defnydd posibl o
`string.Template`.

Mae hefyd yn ateb cwestiwn y mae'r ddwy arddull fformatio arall yn ei adael yn
gyfan gwbl i'r rhaglen: *pa* iaith sy'n gyfredol, a sut i'w newid. Mae
[gwrthrych rhaglen][application object] yn cadw pentwr o ieithoedd, mae
`_.push(code)` a `_.pop()` yn ei symud, mae `with _.using(code):` yn nythu, ac
mae [strategaeth][strategy] yn dod o hyd i'r catalog ar gyfer cod iaith fel nad
yw'r rhaglen byth yn trin gwrthrychau catalog ei hun. Gweinydd sy'n gorfod
cynhyrchu testun mewn mwy nag un iaith yn ystod un uned waith — tudalen i'r
darllenydd, hysbysiad i rywun y mae ei gyfrif wedi'i osod yn wahanol — yw'r
achos y mae hyn yn bodoli ar ei gyfer.

Mae'r pentwr yn byw ar y gwrthrych rhaglen hwnnw, sy'n cael ei rannu gan y
broses gyfan. Felly mae dau gais sy'n gorgyffwrdd yn rhannu un pentwr, ac mae
blociau nad ydynt wedi'u nythu'n llym *mewn amser* yn rhoi'r iaith anghywir i'w
gilydd:

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

Mae'r llyfrgell hon yn cadw'r un gallu — mae rhwymiadau'n nythu ac yn dad-nythu
yn yr un modd — mewn `ContextVar` yn lle pentwr a rennir, felly mae'r cydblethu
uchod yn datrys fesul tasg. Mae'r cyfatebiaethau ar
[Sawl iaith ar unwaith](guide.md#several-languages-at-once). Yr hyn nad yw'n ei
gyflenwi yw'r chwiliad o god iaith i gatalog: rydych yn pasio gwrthrych
cyfieithiadau, sef un alwad `gettext.translation()` ar gyfer yr achos cyffredin,
ac mae'r llyfrgell safonol yn cadw'r catalog wedi'i barsio yn y storfa.

## llinynnau-t { #t-strings }

```python
tr(t"Hello {name}")
```

Mae'r catalog yn dal i weld `Hello {name}` ac yn aros yn gatalog PO/MO cyffredin.
Y gwahaniaeth yw'r hyn y *caniateir* i gyfieithiad ei ddweud, a phwy sy'n ei
wirio.

Mae'r llyfrgell hon yn dilysu pob cyfieithiad yn erbyn dalwyr lle'r neges
ffynhonnell cyn rendro, ac nid yw'n derbyn dim ond enwau noeth. Yn erbyn
`t"Hello {name}"`:

| Cyfieithiad sy'n cynnwys | caiff ei wrthod gyda |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Nid yw gwrthodwyd yn golygu chwalwyd: yn ddiofyn mae'r llyfrgell yn cofnodi
rhybudd ac yn rendro'r neges ffynhonnell, felly nid yw catalog gwael byth yn
bwrw'r rhaglen i lawr —
[yr un contract y mae gettext ei hun yn ei gadw](guide.md#what-happens-when-a-catalog-is-wrong).

Mae'r fformatio'n aros lle'r ysgrifennwyd ef, yn y cod:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

Nid yw `:,.2f` byth yn cyrraedd y catalog, felly ni all unrhyw gyfieithiad ei
newid, ac nid oes rhaid i unrhyw gyfieithydd edrych arno. Fformat *sefydlog*
ydyw, serch hynny, nid un wedi'i leoleiddio — dewis digidau a gwahanyddion fesul
iaith yw [gwaith Babel, cyn yr alwad](guide.md#locale-aware-values).

Un gwahaniaeth arall yw'r offer: cystrawen newydd yw llinynnau-t, felly mae eu
hechdynnu i mewn i `.pot` ar hyn o bryd yn gofyn am echdynnwr sy'n ymwybodol o
linynnau-t, megis yr un y mae'r pecyn hwn yn ei
[ddarparu ar gyfer Babel](extraction.md).

## Cost y cyfyngiad { #the-cost-of-the-restriction }

Y tu hwnt i ofyniad Python, un rheol yw pris hyn i gyd: rhaid i ryngosodiad fod
yn enw syml.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Cyfyngiad go iawn yw hwnnw, a dyna'r un cyfyngiad sy'n cynhyrchu'r gwarantau
uchod. Ynghyd â rhwymo gwerthoedd ar ochr y ffynhonnell a gwirio dalwyr lle wrth
redeg, mae'n atal llinynnau catalog rhag gwerthuso ymadroddion ac yn cadw enwau
dalwyr lle'n ystyrlon i'r person sy'n eu cyfieithu.

Ni ellir defnyddio llinyn-f fel hyn o gwbl — erbyn i unrhyw lyfrgell weld un
mae eisoes yn llinyn gorffenedig, felly mae ei gyfieithu'n golygu cyfieithu
darn. Mae llinynnau-t ([PEP 750]) yn cadw'r testun statig a'r gwerthoedd ar
wahân tra'n cadw cystrawen debyg i linyn-f a rhwymo gwerthoedd penodol.

Adroddir sut y cyrhaeddodd Python yma — dau PEP ddeng mlynedd ar
wahân, a'r drafodaeth am y llyfrgell safonol a gaeodd heb ateb — gyda
ffynonellau ar [Gefndir](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [ymddygiad dogfenedig]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template pwrpasol]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [chyfieithydd]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
