---
description: "Yr API rhedeg: pa bwynt mynediad i'w ddefnyddio, rhwymo catalog, ieithoedd fesul cais, llinynnau gohiriedig, gwerthoedd locale-ymwybodol, a sut yr adroddir cyfieithiad toredig."
---

# Canllaw

Y dudalen hon yw'r cyfeirlyfr rhedeg: popeth y mae *cod eich rhaglen* yn ei
wneud gyda'r llyfrgell hon unwaith y bydd catalogau'n bodoli. Os nad ydych eto
wedi gweld y ddolen gyfan — nodi, echdynnu, cyfieithu, crynhoi, rhedeg — mae'r
[tiwtorial](tutorial.md) yn ei cherdded unwaith mewn pum munud; ymdrinnir â
chreu a dilysu catalogau yn [Echdynnu](extraction.md), a sut y mae tîm yn cadw'r
ddolen i droi — cylchoedd diweddaru, CI, llwyfannau cyfieithu — yw
[Mewn cynhyrchu](workflow.md).

## Pa bwynt mynediad y dylwn ei ddefnyddio? { #which-entry-point-should-i-use }

Mae'r pecyn yn allforio sawl ffordd o gyfieithu neges am fod rhaglenni'n rhwymo
iaith mewn sawl ffordd wahanol. Dewiswch yn ôl sut y mae eich rhaglen yn
penderfynu pa iaith y mae ynddi:

| Eich sefyllfa | Defnyddiwch |
| --- | --- |
| Un iaith i'r broses gyfan — CLI, rhaglen bwrdd gwaith, sgript | `Translator`, wedi'i galw fel `_` |
| Un iaith fesul cais neu fesul tasg anghydamserol — rhaglen we | `use_translations()` o amgylch y gwaith, wedyn `tr()` |
| Neges a ddiffinnir adeg mewnforio — label ffurflen, enum, cysonyn | `lazy_gettext()` neu `lazy_pgettext()` |
| Cyfrif sy'n penderfynu'r geiriad | `ngettext()` / `npgettext()`, yn unrhyw un o'r ffurfiau uchod |
| Rendro patrwm heb gatalog yn y cwestiwn | `compile_template()` |

Y pump hynny, yn y drefn honno, yw popeth isod.

## Rhwymo catalog { #binding-a-catalog }

Mae'r siâp a argymhellir yn adlewyrchu defnydd dosbarth-seiliedig gettext:
rhwymwch wrthrych cyfieithu safonol unwaith a defnyddiwch y prosesydd galwadwy
fel `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Mae'r ffwythiannau ar lefel modiwl yn dilyn enwau'r llyfrgell safonol a'i
chonfensiwn galw safleol-yn-unig:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

Mae `tr` ac `ntr` yn enwau eraill union ar `gettext` ac `ngettext`.

## Iaith fesul cais { #per-request-language }

Mae fframwaith gwe'n dewis iaith fesul cais. Rhwymwch gyfieithiadau'r cais i'r
cyd-destun presennol a bydd pob galwad ar lefel modiwl yn datrys i'r iaith
honno, yn ddiogel ar draws ceisiadau cydredol:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

Mae `set_translations(translations)` yn rhwymo heb floc `with`, ar gyfer
fframweithiau sy'n rheoli cylch bywyd y cais eu hunain; mae `get_translations()`
yn darllen y rhwymiad presennol. Mae ymresymiad `translations=` penodol bob
amser yn trechu'r cyd-destun, ac mae cyd-destun heb ei rwymo'n cwympo'n ôl i
ffwythiannau gettext y llyfrgell safonol a osodwyd yn global. Mae enghreifftiau
wedi'u gweithio ar gyfer Flask a chanolwedd ASGI ar y dudalen
[Mewn cynhyrchu](workflow.md#binding-a-language-at-runtime).

## Cyfieithu gohiriedig { #deferred-translation }

Mae llinyn-t yn dal ei werthoedd yn awchus, sy'n anghywir ar gyfer llinyn a
ddiffinnir adeg mewnforio — label ffurflen, gwerth enum, cysonyn modiwl — sydd
raid iddo rendro yn ba iaith bynnag sy'n weithredol pan gaiff ei *ddefnyddio*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Mae `LazyString` yn rendro drwy `str()`, `format()`, a llinynnau-f, ac yn
cymharu'n gyfartal â'i destun wedi'i rendro.

!!! note "Yn fwriadol anhashadwy"

    Mae testun `LazyString` yn dibynnu ar yr iaith weithredol, felly byddai
    hash yn newid ar draws newid iaith ac yn llygru'n dawel unrhyw set neu
    ddict sy'n ei ddal. Galwch `str()` yn gyntaf os oes angen allwedd arnoch.

Caiff `strict` ei benderfynu lle y caiff y neges ei hysgrifennu, nid lle y mae'n
rendro:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Mae llinyn gohiriedig yn rendro lle bynnag y caiff ei ddefnyddio yn y pen draw —
y tu mewn i dempled, i ffurflen, i linell log — ac anaml y bydd y lle hwnnw'n
gwybod ai rhediad prawf ai cynhyrchu yw hwn. Pasio `strict=True` wrth y
diffiniad yw'r hyn sy'n gadael i'r un dewis
[uchel yn CI, goddefgar mewn cynhyrchu](#what-happens-when-a-catalog-is-wrong)
fod yn berthnasol i linyn nad yw'n cael ei rendro wrth ei safle galw.

Mae ffurfiau lluosog yn dibynnu ar gyfrif adeg rhedeg, felly rendrwch y rheini'n
awchus gydag `ngettext` lle gwyddys y cyfrif.

## Sawl iaith ar unwaith { #several-languages-at-once }

Yn aml mae angen mwy nag un iaith ar un cais: tudalen wedi'i rendro i'r
darllenydd sydd hefyd yn ciwio hysbysiad i gyfrif a osodwyd i un arall, neu
grynodeb sy'n dyfynnu pob cyfranogwr yn ei iaith ei hun. Mae rhwymiadau'n
nythu, ac mae gadael y bloc mewnol yn adfer yr un allanol.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Dros restr o dderbynwyr, llinynnau gohiriedig sy'n gwneud y gwaith: ysgrifennir
y neges unwaith, adeg mewnforio, ac mae'n rendro unwaith fesul iaith.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

`ContextVar` yw'r rhwymiad, nid pentwr a ddelir ar wrthrych a rennir, felly ni
all ceisiadau sy'n gorgyffwrdd godi iaith ei gilydd — gan gynnwys yr achos lle
maent yn *gadael* eu blociau yn y drefn y daethant i mewn iddynt, sef y
cydblethu y mae pentwr gwthio i lawr yn ei gael yn anghywir. Mae llwytho
catalog fesul iaith yn rhad: mae `gettext.translation()` yn parsio pob `.mo`
unwaith ac yn dosbarthu copïau sy'n rhannu'r catalog wedi'i barsio.

!!! warning "Mae p'un a yw edefyn gweithiwr yn etifeddu'r rhwymiad yn dibynnu ar yr adeiladiad"

    Mae `threading.Thread` noeth, neu `ThreadPoolExecutor.submit`, yn cychwyn
    naill ai o gopi o gyd-destun y galwr neu o un gwag, a
    `sys.flags.thread_inherit_context` sy'n penderfynu p'un — yn wir yn ddiofyn
    ar adeiladiadau edau-rydd, ac yn ffug ym mhobman arall. Felly mae'r un cod
    yn rendro'r iaith rwym ar 3.14t a chatalog global y broses ar 3.14.
    Trosglwyddwch y cyd-destun yn hytrach na dibynnu ar y diofyn:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    Mae `asyncio.to_thread` eisoes yn gwneud hyn drosoch.

## Gwerthoedd locale-ymwybodol { #locale-aware-values }

Mae'r llyfrgell hon yn penderfynu *ble* mae gwerth yn ymddangos mewn neges
wedi'i chyfieithu. Nid yw'n lleoleiddio'r gwerth ei hun. Manyleb fformat Python
ag ymddygiad sefydlog yw `{amount:,.2f}` — atalnod bob tri digid a dot o flaen y
degolion — ac mae'n cynhyrchu'r un nodau pa iaith bynnag y mae'r neges ynddi:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Mae Almaeneg yn ysgrifennu'r rhif hwnnw'n `1.234,50`, Ffrangeg yn `1 234,50`,
ac mae Hindi'n grwpio `1234567` yn `12,34,567` yn hytrach nag yn `1,234,567`.
Mae rhifau, arian, dyddiadau, amserau ac unedau'n perthyn i
[Babel][babel-numbers]. Fformatiwch y gwerth yn gyntaf, wedyn rhowch y llinyn
gorffenedig yn ei le:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Ar gyfer neges a gyfrifir mae'r rhif yn gwneud dau waith — mae'n dewis y ffurf
luosog ac mae'n ymddangos yn y testun — a dim ond yr ail a leoleiddir. Cadwch y
cyfrif crai ar gyfer y dewis a phasiwch y llinyn wedi'i fformatio i'w ddangos:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Fformatio cyn yr alwad hefyd yw'r hyn sy'n cadw manyleb fformat allan o'r
catalog: yr hyn y mae cyfieithydd yn ei weld yw darn gorffenedig o destun, nid
rhif ynghyd â chyfarwyddiadau ar gyfer ei rendro.

## Beth sy'n digwydd pan fo catalog yn anghywir { #what-happens-when-a-catalog-is-wrong }

Os nad yw dalwyr lle cyfieithiad yn cyfateb i'r ffynhonnell — maes coll,
anhysbys, neu wedi'i ailfformatio a lithrodd heibio'r dilysu, o MO a olygwyd â
llaw, o gatalog gwerthwr, neu o biblinell sy'n hepgor y gwiriwr — y rhagosodiad
yw rendro'r neges ffynhonnell yn hytrach na chodi gwall. Mae hyn yn
adlewyrchu contract gettext ei hun nad yw catalog gwael byth yn torri'r rhaglen.

Gyda `Hello {name}` wedi'i gyfieithu fel `こんにちは {nombre}`, mae'r rendro'n
llwyddo ac mae un rhybudd yn mynd i'r cofnodydd `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Mae'r rhybudd yn tanio unwaith fesul neges a phatrwm, nid unwaith fesul rendro,
felly nid yw cofnod catalog toredig yn boddi log.

Dewiswch fethu'n uchel ar gyfer profion a CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Mae'r un chwiliad wedyn yn codi gwall, gan gario'r un frawddeg heb yr hanner
"using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Ysgrifennir y negeseuon hyn ar gyfer pwy bynnag a all weithredu arnynt, sef ar
gyfer problem gatalog yn amlach cyfieithydd na rhaglennydd — felly lle mae
daliwr lle'n edrych yn bresennol ond nad ydyw, mae'r neges yn esbonio pam yn
hytrach nag ailadrodd ei fod ar goll. Bracedi lled-llawn, `{{name}}` wedi'i
ddyblu, bwlch di-dor anweledig, llythyren Gyrilig ymhlith rhai Lladin: mae gan
bob un ei eiriad ei hun, wedi'u rhestru ag enghreifftiau ar
[I gyfieithwyr](translators.md#reading-a-failure-message). Ysgrifennwyd y
dudalen honno i'w rhoi i'r person sy'n golygu'r `.po`.

## Rendro patrwm heb gatalog { #rendering-a-pattern-without-a-catalog }

Mae `compile_template` yn datgelu'r un peirianwaith un lefel yn is: mae'n troi
llinyn-t yn ei msgid ynghyd â set rwym o werthoedd, ac yn rendro unrhyw batrwm a
roddwch iddo.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

Mae `render` yn dilysu yn ôl yr un rheolau ac yn **codi gwall bob amser** os oes
anghysondeb. Nid oes modd goddefgar yma: mae goddefgarwch yn bodoli fel y gall
chwiliad *catalog* ddiraddio i'r testun ffynhonnell, ac nid oes gan batrwm a
basiwyd i mewn gennych chi eich hun ddim i ddiraddio ohono.

## Diogelwch a chwmpas { #safety-and-scope }

Mae hyn yn ddilys:

```python
tr(t"Hello {name}")
```

Caiff y rhain eu gwrthod yn fwriadol:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Cyfrifwch werth ystyrlon yn gyntaf:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Mae'r cyfyngiad yn cynhyrchu allweddi catalog sefydlog, yn rhoi enwau defnyddiol
i gyfieithwyr, ac yn atal llinyn wedi'i gyfieithu rhag dod yn iaith ymadroddion.

Mae'r warant wedi'i chwmpasu i *strwythur a fformatio*: ni chaiff cyfieithiad
byth ei werthuso, ac ni all byth ychwanegu mynediad priodoledd, galwadau,
trawsnewidiadau, na manylebau fformat. Mae dau beth yn aros yn gyfrifoldeb y
galwr, yn union fel gyda gettext y llyfrgell safonol — **dianc** allbwn wedi'i
rendro ar gyfer ei sinc (HTML, cragen, terfynell), a **chywirdeb catalogau**,
gan y gall catalog gelyniaethus ailadrodd daliwr lle i chwyddo maint yr allbwn,
sy'n gynhenid i unrhyw i18n sy'n seiliedig ar ddalwyr lle.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
