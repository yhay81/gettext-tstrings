---
description: "An teachtaireacht inaistrithe chéanna scríofa le %-format, .format(), $-strings flufl.i18n, agus le t-string, curtha i gcomparáid ar bhotúin aistritheoirí, ar údarás na catalóige, agus ar chostas an chomhtháthaithe."
---

# Cén fáth t-strings

Ceithre bhealach chun luach a chur i dteachtaireacht inaistrithe, curtha i
gcomparáid ar an teachtaireacht chéanna. Ainmníonn an ceathrar acu a gcuid
sealbhóirí ionaid agus ligeann siad d'aistritheoir iad a athordú; is é an
difríocht eatarthu ná a tharlaíonn nuair a bhíonn aistriúchán mícheart, cé
mhéad de do chlár ar féidir leis an gcatalóg dul chuige, agus cad a chosnaíonn
sé glacadh leo.

Tagann na táblaí ar dtús, ionas go bhfaighfeá an ró is cás leat agus nach
léifeá ach an rannán atá taobh thiar de.

!!! note "Baineann trí pháirtí le gach teachtaireacht aistrithe"

    Is é atá i **gcatalóg** ná comhad na n-aistriúchán — `.po` fad is atá
    daoine á chur in eagar, tiomsaithe go `.mo` le go luchtódh an feidhmchlár
    é (siúlann an [rang teagaisc](tutorial.md) tríd an dá cheann). Baineann
    trí pháirtí le gach teachtaireacht: scríobhann an **forbróir** an teaghrán
    foinseach, cuireann **aistritheoir** an chatalóg in eagar — go minic ar
    ardán seachtrach, i bhfad ó aon athbhreithniú cóid — agus rindreáileann an
    **feidhmchlár** an dá rud le chéile ag am rite. Freagraíonn gach stíl
    formáidithe thíos an cheist chéanna ar bhealach difriúil: *cé mhéad den
    teanga formáide a fhaigheann an chatalóg le rialú?* Sna samplaí, is é `_`
    an gnáthainm ar an bhfeidhm aistriúcháin, agus is le `tr` a bhaineann an
    leabharlann seo.

## Taobh le taobh { #side-by-side }

**Nuair a dhéanann aistritheoir botún.** Taistealaíonn catalóg trí mhórán lámh,
agus is de thaisme a tharlaíonn formhór na rudaí a théann amú inti:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| *Fágann* aistriúchán sealbhóir ionaid ar lár — cad a rindreáiltear? | imíonn an luach gan focal | imíonn an luach gan focal | imíonn an luach gan focal | an teachtaireacht fhoinseach, le rabhadh ([de réir réamhshocraithe](guide.md#what-happens-when-a-catalog-is-wrong)) |
| *Cuireann* aistriúchán sealbhóir ionaid anaithnid leis — cad a rindreáiltear? | eisceacht | eisceacht | fanann an sealbhóir ionaid le feiceáil mar théacs | an teachtaireacht fhoinseach, le rabhadh ([de réir réamhshocraithe](guide.md#what-happens-when-a-catalog-is-wrong)) |
| *Athfhormáidíonn* aistriúchán sealbhóir ionaid — cad a rindreáiltear? | an rud a d'iarr an chatalóg, nó eisceacht mura n-oireann an litir chineáil don luach a thuilleadh | an rud a d'iarr an chatalóg | ní féidir é a chur in iúl i `$`-strings | an teachtaireacht fhoinseach, le rabhadh |
| An seiceáiltear sealbhóirí ionaid ag am rindreála? | ní sheiceáiltear | ní sheiceáiltear | ní sheiceáiltear | seiceáiltear (féach thíos) |

**Cén t-údarás atá ag an gcatalóg.** Is sonraí ó thaobh amuigh de do stórlann é
aistriúchán, agus tugann gach stíl méid difriúil cumhachta dó:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Cad as a dtagann na luachanna? | mapáil fhollasach | argóintí follasacha | athróga áitiúla agus domhanda an ghlaoiteora, móide `extras` roghnach | na luachanna a gabhadh laistigh den t-string |
| An féidir leis an gcatalóg an chaoi a bhformáidítear luach a athrú? | is féidir | is féidir | ní féidir | ní féidir |
| An féidir leis an gcatalóg dul isteach in oibiachtaí (rochtain ar thréithe)? | ní féidir | is féidir | is féidir, le hainmneacha poncacha | ní féidir |
| Cá bhfuil "an teanga reatha" ina cónaí? | cibé áit a gcuireann an feidhmchlár í | cibé áit a gcuireann an feidhmchlár í | cruach cód teanga ar an oibiacht fheidhmchláir roinnte | `ContextVar`, in aghaidh an taisc nó an iarratais |

**Cad a chosnaíonn sé é a chomhtháthú.** Tá gach rud thuas saor in aisce má
oireann na huirlisí; seo an áit a bhféadfadh sé gan oiriúint:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python is lú | ceann ar bith | ceann ar bith | 3.10 | **3.14** |
| Aibíocht | leabharlann chaighdeánach | leabharlann chaighdeánach | eisiúint chobhsaí | **alfa** |
| An úsáideann sé gnáthchatalóga PO/MO? | úsáideann | úsáideann | úsáideann | úsáideann |
| An dteastaíonn eastóscóir foinse saincheaptha uaidh? | ní theastaíonn | ní theastaíonn | ní theastaíonn | teastaíonn, faoi láthair |
| Cén bhratach PO a thuigeann Babel, le go mbailíochtódh uirlisí atá ann cheana? | `python-format` | `python-brace-format` | ceann ar bith | `python-brace-format` |

Maidir leis an seiceáil ag am rindreála: seiceáiltear teachtaireachtaí uatha
le haghaidh meaitseála beachta ar na sealbhóirí ionaid. Seiceáiltear
teachtaireachtaí iolra freisin, i gcoinne na
[rialach aontais/trasnaithe](spec.md) a ligeann d'fhoirmeacha iolra na
sprioctheanga bheith éagsúil le foirmeacha na foinse; ritheann an tseiceáil
níos déine in aghaidh na foirme nuair a thiomsaítear catalóga
([Eastóscadh](extraction.md)).

Baineann an ró faoin mbratach formáide le bailíochtú a thuigeann sealbhóirí
ionaid, ní le comhoiriúnacht catalóige. Ciallaíonn `ceann ar bith` go léann
agus go dtiomsaíonn gnáthuirlisí gettext an teachtaireacht fós, ach níl aon
ghramadach shealbhóirí ionaid `$` ag `msgfmt --check-format` le cur i
bhfeidhm.

## Comhoiriúnacht agus aibíocht { #compatibility-and-maturity }

Is iad an chéad dá ró den tábla deireanach na cinn a shocraíonn an nglactar
leis, mar sin is fiú iad a rá go lom seachas mar chealla.

Tá `%`-format agus `.format()` tógtha isteach i bPython agus ní theastaíonn
spleáchas ar bith uathu. Is pacáiste aibí é [`flufl.i18n`][flufl-i18n], atá
eisithe agus in úsáid i dtáirgeadh, a ritheann ar Python 3.10 agus níos
déanaí. Is **alfa** é `gettext-tstrings` agus teastaíonn **Python 3.14 nó
níos nuaí** uaidh, ós comhréir nua i 3.14 iad na t-strings — níl aon
chúlphort ann agus ní féidir ceann a bheith ann. Is í a
[shonraíocht](spec.md) an chuid chobhsaí de; d'fhéadfadh an API Python bogadh
fós roimh 1.0.

Is é an rud nach gcosnaíonn ceann ar bith acu ná comhoiriúnacht catalóige.
Táirgeann an ceathrar acu gnáthchomhaid POT/PO/MO a léann gach eagarthóir PO,
gach ardán aistriúcháin agus gach uirlis GNU gettext cheana féin, mar sin tá
an rogha thíos inchúlaithe ar bhealach nach mbeadh athrú *formáide* catalóige.
Clúdaíonn [Aistriú anonn](migration.md) tionscadal atá ann cheana a bhogadh.

Taispeánann na rannáin thíos gach comhbhabhtáil go mion, modh amháin i
ndiaidh a chéile.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Cad is féidir dul amú: tuairteálann litir amháin scriosta in aistriúchán an
rindreáil.

Iompraíonn teaghrán na catalóige comhréir printf, lena n-áirítear litir
chineáil ag an deireadh — an `s` i `%(name)s` — atá éasca a ligean thar do
shúil agus éasca a mhilleadh:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Éiríonn cúlrian i dtáirgeadh as eagrán aon charachtair amháin in eagarthóir
PO. Beireann GNU `msgfmt --check-format` air, ceart go leor, ach ní bheireann
ach ar theachtaireachtaí a bhfuil an bhratach `python-format` orthu, agus sin
ach amháin má théann an chatalóg trí msgfmt i ndáiríre ar a bealach chuig
d'fheidhmchlár.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Baineann sé an litir chineáil ón deireadh agus coinníonn sé sealbhóir ionaid
ainmnithe is féidir a athordú go saor. Bogann an rud is féidir dul amú go dtí
an taobh eile den mhalartú: faigheann an t-aistriúchán cumhacht ar do chuid
oibiachtaí.

Is teanga bheag sloinn é `str.format`, agus nuair a ghairtear ar theaghrán é
tugtar don teaghrán sin an ceart chun í a úsáid:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Anois cuir cibé rud a fhilleann `_()` in ionad na dteaghrán litriúil sin. Má
fhilleann aistriúchán ar `Hello {name}` mar `{conf.api_key}`, priontálann a
rindreáil d'eochair API — is í an chatalóg, agus ní do chód, a shocraigh cad a
léadh. Ní cód í catalóg, ach taistealaíonn sí ar nós sonraí: amach chuig ardán
aistriúcháin, trí roinnt lámh, ar ais mar `.po`, tiomsaithe ina `.mo`,
uaireanta á soláthar ó thaobh amuigh de do thionscadal ar fad. Tugann
`.format()` rochtain ar thréithe na n-oibiachtaí a chuireann tú isteach do
gach céim den turas sin.

## `$`-strings agus flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Soláthraíonn [`string.Template`][stdlib-template] na leabharlainne
caighdeánaí an teanga idirshuite `$name`, ach ní API aistriúcháin é féin.
Cuireann [`flufl.i18n`][flufl-i18n] an stíl sin le cuardach catalóige gettext.
Tabhair faoi deara nach gcuirtear an luach isteach riamh: tógann flufl.i18n an
t-ainmspás ionadaíochta as athróga áitiúla agus domhanda an ghlaoiteora — tá
cibé athróga atá ann ag láthair an ghlao ar fáil don teachtaireacht. Tá
tosaíocht ag mapáil roghnach `extras` ar an dá cheann. Níl litir chineáil ná
sonraitheoir formáide ag deireadh a chomhréire don aistritheoir, agus fanann
na sealbhóirí ionaid inathordaithe go saor.

Ní ardaíonn ionadaíocht nach bhfuil ar fáil eisceacht. Le `name = "Ada"` agus
gan aon `nombre` in ainmspás an ghlaoiteora, rindreáiltear aistriúchán
catalóige ar `Hello $nombre` mar `Hello $nombre`: fanann an sealbhóir ionaid
gan réiteach le feiceáil. Caomhnaíonn an t-[iompar doiciméadaithe][documented behavior]
sin an chuid eile den teachtaireacht aistrithe in ionad teip a chur ar an nglao.
Is féidir le heisceachtaí a ardaítear agus tréith á réiteach nó luach á
thiontú leathadh fós.

Tá `flufl.i18n` níos cumasaí ná `string.Template` lom ar bhealach amháin atá
ábhartha. Glacann a [Theimpléad saincheaptha][custom Template] le sealbhóirí
ionaid le poncanna ar nós `$settings.api_key`, agus réitíonn a
[aistritheoir][translator] na cosáin sin i gcoinne luachanna an ghlaoiteora.
Féadfaidh sealbhóir ionaid aistrithe aon athróg áitiúil nó dhomhanda de chuid
an ghlaoiteora atá ar fáil a ainmniú agus, leis an gcomhréir phoncach, taisteal
trína tréithe. Tá sé sin áisiúil nuair a theastaíonn tréith ó theachtaireacht,
agus fágann sé ag an am céanna gur cuid d'ainmspás ionadaíochta na catalóige é
fráma an ghlaoiteora. Cuireann an chomparáid anseo síos ar `flufl.i18n` 6.0.0,
ní ar gach úsáid a d'fhéadfaí a bhaint as `string.Template`.

Freagraíonn sé ceist freisin a fhágann an dá stíl formáidithe eile faoin
bhfeidhmchlár ar fad: *cén* teanga atá reatha, agus conas í a athrú.
Coinníonn [oibiacht fheidhmchláir][application object] cruach teangacha,
bogann `_.push(code)` agus `_.pop()` í, neadaíonn `with _.using(code):`, agus
aimsíonn [straitéis][strategy] an chatalóg do chód teanga ionas nach
láimhseálann an feidhmchlár oibiachtaí catalóige riamh é féin. Freastalaí a
chaithfidh téacs a chur ar fáil i níos mó ná teanga amháin le linn aonad oibre
amháin — leathanach don léitheoir, fógra do dhuine a bhfuil teanga eile
socraithe ar a chuntas — sin an cás a bhfuil sé seo ann dó.

Tá an chruach ina cónaí ar an oibiacht fheidhmchláir sin, agus roinneann an
próiseas ar fad í. Roinneann dhá iarratas fhorluiteacha aon chruach amháin
dá bharr, agus tugann bloic nach bhfuil neadaithe go docht *in am* an teanga
mhícheart dá chéile:

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

Coinníonn an leabharlann seo an cumas céanna — neadaíonn ceangail agus
scaoiltear iad ar an mbealach céanna — i `ContextVar` in ionad cruaiche
roinnte, mar sin réitítear an fite fuaite thuas do gach tasc ar leith. Tá na
coibhéisí ar
[Roinnt teangacha ag an am céanna](guide.md#several-languages-at-once). Is é an
rud nach soláthraíonn sé ná an cuardach ó chód teanga go catalóg: cuireann tú
oibiacht aistriúchán isteach, rud nach bhfuil ann sa ghnáthchás ach glao amháin
`gettext.translation()`, agus taisceann an leabharlann chaighdeánach an chatalóg
pharsáilte.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

Feiceann an chatalóg `Hello {name}` fós agus fanann sí ina gnáthchatalóg
PO/MO. Is é an difríocht ná cad tá *cead* ag aistriúchán a rá, agus cé a
sheiceálann é.

Bailíochtaíonn an leabharlann seo gach aistriúchán i gcoinne shealbhóirí
ionaid na teachtaireachta foinsí roimh an rindreáil, agus ní ghlacann sí ach
le hainmneacha loma agus faic eile. I gcoinne `t"Hello {name}"`:

| Aistriúchán ina bhfuil | Diúltaítear dó leis seo |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Ní hionann diúltú agus tuairteáil: de réir réamhshocraithe logálann an
leabharlann rabhadh agus rindreáileann sí an teachtaireacht fhoinseach, mar sin
ní leagann drochchatalóg an feidhmchlár riamh —
[an conradh céanna a choinníonn gettext féin](guide.md#what-happens-when-a-catalog-is-wrong).

Fanann an formáidiú san áit ar scríobhadh é, sa chód:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

Ní shroicheann `:,.2f` an chatalóg riamh, mar sin ní féidir le haon
aistriúchán é a athrú, agus ní gá d'aon aistritheoir breathnú air. Formáid
*sheasta* atá ann, áfach, agus ní ceann logánaithe — is é
[post Babel é, roimh an nglao](guide.md#locale-aware-values), digití agus
deighilteoirí a roghnú in aghaidh na teanga.

Difríocht amháin eile is ea na huirlisí: comhréir nua iad na t-strings, mar
sin teastaíonn eastóscóir a thuigeann t-strings faoi láthair chun iad a
eastóscadh go `.pot`, ar nós an chinn a
[sholáthraíonn an pacáiste seo do Babel](extraction.md).

## Costas an tsriain { #the-cost-of-the-restriction }

Taobh amuigh den riachtanas Python, is é praghas an méid seo ar fad ná riail
amháin: caithfidh idirshuíomh a bheith ina ainm lom.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Is fíorshrian é sin, agus is é an srian céanna é a tháirgeann na ráthaíochtaí
thuas. In éineacht le ceangal na luachanna ar thaobh na foinse agus le
seiceáil na sealbhóirí ionaid ag am rite, cuireann sé cosc ar theaghráin
chatalóige sloinn a mheas agus coinníonn sé brí in ainmneacha na sealbhóirí
ionaid don duine atá á n-aistriú.

Ní féidir f-string a úsáid ar an mbealach seo ar chor ar bith — faoin am a
fheiceann leabharlann ar bith ceann acu tá sé ina theaghrán críochnaithe
cheana, mar sin ciallaíonn é a aistriú blúire a aistriú. Coinníonn t-strings
([PEP 750]) an téacs statach agus na luachanna scartha óna chéile, agus
coinníonn siad comhréir cosúil le f-string agus ceangal follasach luachanna ag
an am céanna.

Insítear le foinsí ar [Cúlra](background.md) conas a shroich Python an
crosbhóthar seo — dhá PEP deich mbliana ó chéile, agus an plé sa leabharlann
chaighdeánach a dúnadh gan freagra.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
