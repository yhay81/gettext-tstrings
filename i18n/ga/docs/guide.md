---
description: "An API ag am rite: cén pointe iontrála le húsáid, catalóg a cheangal, teangacha in aghaidh an iarratais, teaghráin iarchurtha, luachanna a thuigeann an logán, agus an chaoi a dtuairiscítear aistriúchán lochtach."
---

# Treoir

Is é an leathanach seo an tagairt ama rite: gach rud a dhéanann *cód
d'fheidhmchláir* leis an leabharlann seo a luaithe is atá catalóga ann. Mura
bhfaca tú an lúb iomlán fós — marcáil, eastósc, aistrigh, tiomsaigh, rith —
siúlann an [rang teagaisc](tutorial.md) uair amháin í i gcúig nóiméad;
pléitear catalóga a chruthú agus a bhailíochtú in [Eastóscadh](extraction.md),
agus tá an chaoi a gcoinníonn foireann an lúb ag casadh — timthriallta
nuashonraithe, CI, ardáin aistriúcháin — in [I dtáirgeadh](workflow.md).

## Cén pointe iontrála ba chóir dom a úsáid? { #which-entry-point-should-i-use }

Easpórtálann an pacáiste roinnt bealaí chun teachtaireacht a aistriú toisc go
gceanglaíonn feidhmchláir teanga ar roinnt bealaí éagsúla. Roghnaigh de réir
mar a shocraíonn do chlár cén teanga ina bhfuil sé:

| Do chás | Úsáid |
| --- | --- |
| Teanga amháin don phróiseas ar fad — CLI, feidhmchlár deisce, script | `Translator`, á ghairm mar `_` |
| Teanga amháin in aghaidh an iarratais nó in aghaidh an tasc aisioncrónaigh — feidhmchlár gréasáin | `use_translations()` timpeall na hoibre, ansin `tr()` |
| Teachtaireacht a shainítear ag am iompórtála — lipéad foirme, áireamh, tairiseach | `lazy_gettext()` nó `lazy_pgettext()` |
| Socraíonn comhaireamh an fhoclaíocht | `ngettext()` / `npgettext()`, i cibé foirm thuas |
| Patrún á rindreáil gan chatalóg ar bith i gceist | `compile_template()` |

Is iad an cúigear sin, san ord sin, atá thíos ar fad.

## Catalóg a cheangal { #binding-a-catalog }

Déanann an cruth molta aithris ar úsáid ranga-bhunaithe gettext: ceangail
gnáthoibiacht aistriúcháin uair amháin agus úsáid an próiseálaí inghairthe mar
`_`.

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

Leanann na feidhmeanna ar leibhéal an mhodúil ainmneacha na leabharlainne
caighdeánaí agus a coinbhinsiún glaonna suímh amháin:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

Is leasainmneacha cruinne ar `gettext` agus `ngettext` iad `tr` agus `ntr`.

## Teanga in aghaidh an iarratais { #per-request-language }

Roghnaíonn creat gréasáin teanga in aghaidh an iarratais. Ceangail
aistriúcháin an iarratais leis an gcomhthéacs reatha agus réitíonn gach glao
ar leibhéal an mhodúil chuig an teanga sin, go sábháilte thar iarratais
chomhuaineacha:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

Ceanglaíonn `set_translations(translations)` gan bhloc `with`, do chreataí a
bhainistíonn timthriall saoil an iarratais iad féin; léann
`get_translations()` an ceangal reatha. Bíonn an lámh in uachtar i gcónaí ag
argóint fhollasach `translations=` ar an gcomhthéacs, agus titeann comhthéacs
gan cheangal ar ais ar na feidhmeanna gettext atá suiteáilte go domhanda sa
leabharlann chaighdeánach. Tá samplaí oibrithe do Flask agus do bhogearraí
lárnacha ASGI ar an leathanach
[I dtáirgeadh](workflow.md#binding-a-language-at-runtime).

## Aistriúchán iarchurtha { #deferred-translation }

Gabhann t-string a chuid luachanna go fonnmhar, rud atá mícheart do theaghrán
a shainítear ag am iompórtála — lipéad foirme, luach áirimh, tairiseach modúil
— a chaithfidh rindreáil i cibé teanga atá gníomhach nuair a *úsáidtear* é.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Rindreáileann `LazyString` trí `str()`, `format()` agus f-strings, agus bíonn
sé cothrom lena théacs rindreáilte i gcomparáid.

!!! note "Gan hais, d'aon ghnó"

    Braitheann téacs `LazyString` ar an teanga ghníomhach, mar sin d'athródh
    hais nuair a athrófaí an teanga agus thruailleodh sí go ciúin aon tacar nó
    foclóir ina bhfuil sé. Glaoigh ar `str()` ar dtús má theastaíonn eochair
    uait.

Socraítear `strict` san áit a scríobhtar an teachtaireacht, ní san áit a
rindreáiltear í:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Rindreáiltear teaghrán iarchurtha cibé áit a n-úsáidtear ar deireadh é — istigh
i dteimpléad, i bhfoirm, i líne loga — agus is annamh a bhíonn a fhios ag an
áit sin an rith tástála nó táirgeadh atá i gceist. Is é `strict=True` a chur ar
aghaidh ag an sainmhíniú a ligeann don rogha chéanna
[os ard i CI, bog i dtáirgeadh](#what-happens-when-a-catalog-is-wrong) a bheith
i bhfeidhm ar theaghrán nach rindreáiltear ag a láithreán glaonna é.

Braitheann foirmeacha iolra ar chomhaireamh ag am rite, mar sin rindreáil iad
sin go fonnmhar le `ngettext` san áit a bhfuil an comhaireamh ar eolas.

## Roinnt teangacha ag an am céanna { #several-languages-at-once }

Is minic a bhíonn níos mó ná teanga amháin ag teastáil ó iarratas amháin:
leathanach a rindreáiltear don léitheoir agus a chuireann fógra i scuaine ag
an am céanna chuig cuntas atá socraithe ar theanga eile, nó achoimre a luann
gach rannpháirtí ina theanga féin. Neadaíonn ceangail, agus nuair a fhágtar an
bloc istigh cuirtear an ceann amuigh ar ais.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Thar liosta faighteoirí is iad na teaghráin iarchurtha a dhéanann an obair:
scríobhtar an teachtaireacht uair amháin, ag am iompórtála, agus rindreáiltear
í uair amháin in aghaidh na teanga.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Is `ContextVar` é an ceangal, agus ní cruach atá á coinneáil ar oibiacht
roinnte, mar sin ní féidir le hiarratais fhorluiteacha teanga a chéile a
phiocadh suas — an cás ina *bhfágann* siad a mbloic san ord inar tháinig siad
isteach iontu san áireamh, agus sin é an fite fuaite nach n-éiríonn le cruach a
láimhseáil i gceart. Níl sé costasach catalóg a lódáil in aghaidh na teanga:
parsálann `gettext.translation()` gach `.mo` uair amháin agus tugann sé amach
cóipeanna a roinneann an chatalóg pharsáilte.

!!! warning "Braitheann oidhreacht an cheangail i snáithe oibre ar an tógáil"

    Tosaíonn `threading.Thread` lom, nó `ThreadPoolExecutor.submit`, ó chóip
    de chomhthéacs an ghlaoiteora nó ó chomhthéacs folamh, agus is é
    `sys.flags.thread_inherit_context` a shocraíonn cé acu — fíor de réir
    réamhshocraithe ar thógálacha saorshnáithithe, bréagach i ngach áit eile.
    Rindreálann an cód céanna, dá bhrí sin, an teanga cheangailte ar 3.14t
    agus an chatalóg atá domhanda don phróiseas ar 3.14. Seachaid an
    comhthéacs seachas a bheith ag brath ar an réamhshocrú:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    Déanann `asyncio.to_thread` é seo duit cheana féin.

## Luachanna a thuigeann an logán { #locale-aware-values }

Socraíonn an leabharlann seo *cén áit* a bhfeictear luach i dteachtaireacht
aistrithe. Ní logánaíonn sí an luach féin. Is sonrú formáide Python é
`{amount:,.2f}` a bhfuil iompar seasta aige — camóg gach trí dhigit agus ponc
roimh na deachúlacha — agus táirgeann sé na carachtair chéanna cibé teanga ina
bhfuil an teachtaireacht:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Scríobhann an Ghearmáinis an uimhir sin mar `1.234,50`, an Fhraincis mar
`1 234,50`, agus grúpálann an Hiondúis `1234567` mar `12,34,567` seachas
`1,234,567`. Baineann uimhreacha, airgeadraí, dátaí, amanna agus aonaid le
[Babel][babel-numbers]. Formáidigh an luach ar dtús, ansin cuir an teaghrán
críochnaithe san áit:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

I gcás teachtaireachta a bhfuil comhaireamh ann déanann an uimhir dhá phost —
roghnaíonn sí an fhoirm iolra agus feictear sa téacs í — agus ní logánaítear
ach an dara ceann. Coinnigh an comhaireamh amh don roghnú agus seachaid an
teaghrán formáidithe le taispeáint:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Is é an formáidiú roimh an nglao a choinníonn sonrú formáide amuigh as an
gcatalóg freisin: is píosa téacs críochnaithe a fheiceann aistritheoir, ní
uimhir móide treoracha lena rindreáil.

## A tharlaíonn nuair a bhíonn catalóg mícheart { #what-happens-when-a-catalog-is-wrong }

Mura meaitseálann sealbhóirí ionaid aistriúcháin leis an bhfoinse — réimse atá
ar iarraidh, anaithnid nó athfhormáidithe a shleamhnaigh thar an mbailíochtú,
ó MO a cuireadh in eagar de láimh, ó chatalóg díoltóra, nó ó phíblíne a
scipeálann an seiceálaí — is é an réamhshocrú an teachtaireacht fhoinseach a
rindreáil seachas eisceacht a ardú. Déanann sé sin aithris ar chonradh gettext féin nach
mbriseann drochchatalóg an feidhmchlár riamh.

Nuair a aistrítear `Hello {name}` mar `こんにちは {nombre}`, éiríonn leis an
rindreáil agus téann rabhadh amháin chuig an logálaí `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Scaoiltear an rabhadh uair amháin in aghaidh na teachtaireachta agus an
phatrúin, ní uair amháin in aghaidh na rindreála, mar sin ní chuireann
iontráil chatalóige lochtach loga thar maoil.

Roghnaigh teip os ard le haghaidh tástálacha agus CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Ardaíonn an cuardach céanna eisceacht ansin, agus an abairt chéanna á hiompar
aige gan an leath "using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Scríobhtar na teachtaireachtaí seo do cibé duine ar féidir leis gníomhú orthu,
agus i gcás faidhbe catalóige is aistritheoir é sin níos minice ná programmer —
mar sin nuair a bhíonn cuma ar shealbhóir ionaid go bhfuil sé ann ach nach
bhfuil, míníonn an teachtaireacht cén fáth seachas a rá arís go bhfuil sé ar
iarraidh. Lúibíní lánleithid, `{{name}}` dúblaithe, spás gan bhriseadh
dofheicthe, litir Choireallach i measc litreacha Laidineacha: tá a fhoclaíocht
féin ag gach ceann acu, liostaithe le samplaí ar
[D'aistritheoirí](translators.md#reading-a-failure-message). Scríobhadh an
leathanach sin le tabhairt don duine a chuireann an `.po` in eagar.

## Patrún a rindreáil gan chatalóg { #rendering-a-pattern-without-a-catalog }

Nochtann `compile_template` an t-inneall céanna leibhéal amháin níos ísle:
iompaíonn sé t-string ina msgid móide tacar luachanna ceangailte, agus
rindreáileann sé aon phatrún a shíneann tú chuige.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

Bailíochtaíonn `render` de réir na rialacha céanna agus **ardaíonn sé
eisceacht i gcónaí** nuair nach meaitseálann rud. Níl aon mhód bog anseo: tá
an bhoige ann le go bhféadfadh cuardach *catalóige* dul in olcas go dtí an
téacs foinseach, agus níl aon rud ag patrún a chuir tú féin isteach le dul in
olcas uaidh.

## Sábháilteacht agus raon feidhme { #safety-and-scope }

Tá sé seo bailí:

```python
tr(t"Hello {name}")
```

Diúltaítear dóibh seo d'aon ghnó:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Ríomh luach fiúntach ar dtús:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Táirgeann an srian eochracha catalóige cobhsaí, tugann sé ainmneacha
úsáideacha d'aistritheoirí, agus coinníonn sé teaghrán aistrithe ó bheith ina
theanga sloinn.

Baineann an ráthaíocht le *struchtúr agus formáidiú* amháin: ní mheastar
aistriúchán riamh, agus ní féidir leis rochtain ar thréithe, glaonna,
tiontuithe ná sonruithe formáide a chur leis riamh. Fanann dhá rud faoi chúram
an ghlaoiteora, díreach mar atá le gettext na leabharlainne caighdeánaí —
**éalú** an aschuir rindreáilte dá cheann scríbe (HTML, blaosc, teirminéal),
agus **iomláine na catalóige**, mar go bhféadfadh catalóg naimhdeach sealbhóir
ionaid a athdhéanamh chun méid an aschuir a mhéadú, rud atá dúchasach in aon
i18n atá bunaithe ar shealbhóirí ionaid.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
