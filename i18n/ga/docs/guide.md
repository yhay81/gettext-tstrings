---
description: "An API ag am rite: catalóg a cheangal, teangacha in aghaidh an iarratais, teaghráin iarchurtha, agus an chaoi a dtuairiscítear aistriúchán lochtach."
---

# Treoir

Is é an leathanach seo an tagairt ama rite: gach rud a dhéanann *cód
d'fheidhmchláir* leis an leabharlann seo a luaithe is atá catalóga ann. Mura
bhfaca tú an lúb iomlán fós — marcáil, eastósc, aistrigh, tiomsaigh, rith —
siúlann an [rang teagaisc](tutorial.md) uair amháin í i gcúig nóiméad;
pléitear catalóga a chruthú agus a bhailíochtú in [Eastóscadh](extraction.md),
agus tá an chaoi a gcoinníonn foireann an lúb ag casadh — timthriallta
nuashonraithe, CI, ardáin aistriúcháin — in [I dtáirgeadh](workflow.md).

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

Braitheann foirmeacha iolra ar chomhaireamh ag am rite, mar sin rindreáil iad
sin go fonnmhar le `ngettext` san áit a bhfuil an comhaireamh ar eolas.

## A tharlaíonn nuair a bhíonn catalóg mícheart { #what-happens-when-a-catalog-is-wrong }

Mura meaitseálann sealbhóirí ionaid aistriúcháin leis an bhfoinse — réimse atá
ar iarraidh, anaithnid nó athfhormáidithe a shleamhnaigh thar an mbailíochtú,
ó MO a cuireadh in eagar de láimh, ó chatalóg díoltóra, nó ó phíblíne a
scipeálann an seiceálaí — is é an réamhshocrú an téacs foinseach a atáirgeadh
seachas eisceacht a ardú. Déanann sé sin aithris ar chonradh gettext féin nach
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

## Teachtaireacht teipe a léamh { #reading-a-failure-message }

Scríobhtar na teachtaireachtaí seo do cibé duine ar féidir leis gníomhú orthu,
agus i gcás faidhbe catalóige is aistritheoir é sin níos minice ná programmer.
Is bóthar caoch é a thuairisciú nach bhfuil ann ach go bhfuil `{name}` ar
iarraidh nuair a fheiceann an léitheoir na carachtair sin os a chomhair, mar
sin nuair a bhíonn cuma ar shealbhóir ionaid go bhfuil sé ann ach nach bhfuil,
insíonn an teachtaireacht cén fáth. I gcoinne na foinse `Hello {name}`,
tuairiscítear gach ceann díobh seo faoi
`translation does not match the source placeholders:`

| A deir an t-aistriúchán | An chúis a thugtar |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Faigheann carachtair nach féidir a fheiceáil a gcóireáil féin. Is rud é spás
gan bhriseadh laistigh de na lúibíní slabhracha a chruthaíonn modh ionchuir
agus nach dtaispeánann aon eagarthóir, mar sin priontálann an teachtaireacht
de réir a phointe cóid é seachas carachtar a ainmniú nach féidir leis an
léitheoir a aimsiú:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ainm a bhfuil córais scríbhneoireachta measctha ina litreacha — cás na
homaghlifeanna, nuair nach féidir `а` Coireallach a idirdhealú ó cheann
Laidineach — taispeántar faoi dhó é, uair amháin go hinléite agus uair amháin
éalaithe, agus is í sin an t-aon fhoirm a aithníonn an dá cheann óna chéile:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Baineann an t-idirdhealú céanna leis nuair a bhíonn ainm Gréagach nó
Coireallach atá scríofa go hiomlán in aon script amháin ag teacht salach ar
ainm foinseach ASCII, cás an aon litir amháin `a` Laidineach / `а`
Coireallach san áireamh.

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
