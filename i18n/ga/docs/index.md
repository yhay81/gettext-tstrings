---
description: "Aistrigh teachtaireachtaí t-string iomlána trí gettext agus Babel, agus na luachanna agus an formáidiú coinnithe amuigh as an gcatalóg."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Aistrigh teachtaireachtaí iomlána<br>le t-strings Python

Ceanglaíonn `gettext-tstrings` t-strings Python 3.14+ le catalóga
caighdeánacha gettext agus le huirlisí Babel. Fanann na luachanna agus an
formáidiú i gcód an fheidhmchláir; oibríonn na haistritheoirí le
teachtaireachtaí iomlána agus le sealbhóirí ionaid shimplí `{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Tá `Hello {name}` sa chatalóg. Tá cead ag aistriúchán `{name}` a bhogadh nó a
athdhéanamh. Má bhaineann sé an sealbhóir ionaid, má athainmníonn sé é nó má
athfhormáidíonn sé é, tuairiscíonn bailíochtú na catalóige an earráid. Má
shroicheann iontráil neamhbhailí an táirgeadh mar sin féin, logálann an
leabharlann rabhadh agus rindreálann sí an teachtaireacht fhoinseach seachas
tuairteáil.

[Tosaigh an rang teagaisc cúig nóiméad :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Déan comparáid leis na roghanna eile](comparison.md){ .md-button }

Alfa · Python 3.14+ · catalóga caighdeánacha PO/MO · gan spleáchais tríú páirtí ag am rite
{ .home-facts }

Cleachtann an suíomh seo an rud a dhoiciméadaíonn sé: rindreáiltear gach
eagrán teanga — an nascleanúint, na lipéid agus an tuairisc tógála a
thuigeann an t-iolra — ó chatalóga PO le
[`gettext-tstrings` féin](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## An bhfuil sé seo duitse? { #is-this-for-you }

**Feileann sé inniu** nuair a ritheann d'fheidhmchlár ar Python 3.14 nó níos
nuaí; nuair a úsáideann tú gettext agus Babel cheana, nó nuair is mian leat
glacadh lena sreabhadh oibre PO/MO; agus nuair atá comhréir t-string uait le
sealbhóirí ionaid ainmnithe a sheiceáiltear sula rindreáiltear iad.

**Ní fheileann sé fós** nuair a theastaíonn Python 3.13 nó níos sine uait;
nuair a theastaíonn API cobhsaí Python uait — is alfa é seo, agus is í an
[tsonraíocht](spec.md) an chuid de atá socraithe; nó nuair a bhíonn beagnach
gach téacs inaistrithe agat i dteanga teimpléid seachas i bhfoinse Python.

Catalóga agat cheana? Leanann siad ag obair. Táirgeann
`_("Hello {name}").format(name=name)` agus `tr(t"Hello {name}")` an msgid
céanna, mar sin maireann na haistriúcháin atá ann tríd an athrú — siúlann
[Aistriú anonn](migration.md) an bogadh iomlán.

## A bhfuil cead ag an gcatalóg a rá { #what-the-catalog-may-say }

**Ní féidir le haistriúchán struchtúr na teachtaireachta a aistríonn sé a
athrú.** Sin an gealltanas ar fad, agus leanann an chuid eile den suíomh seo
as. Tá cead ag aistriúchán `{name}` a athordú nó a athdhéanamh, agus gach
focal eile timpeall air a athscríobh. Níl cead aige an sealbhóir ionaid a
fhágáil ar lár, ceann nua a chumadh, síneadh tríd isteach i do chuid
oibiachtaí, ná formáidiú dá chuid féin a cheangal leis.

Seiceálann an leabharlann é sin ar an mbealach isteach — nuair a thiomsaítear
na catalóga — agus arís ag am rindreála, agus sin an difríocht idir botún a
aimsítear i léirmheas agus botún a aimsíonn úsáideoir.

!!! note "gettext nua duit? An sreabhadh oibre iomlán i gceithre abairt"

    Is é **gettext** an bealach caighdeánach a aistrítear bogearraí, i bPython
    agus i bhfad níos faide anonn. Marcálann do chód na teachtaireachtaí is féidir a
    aistriú; bailíonn *eastóscóir* iad i gcomhad teimpléid (`.pot`); líonann
    aistritheoir — nach programmer é de ghnáth — comhad catalóige (`.po`)
    amháin in aghaidh na teanga, agus tiomsaítear é sin ina `.mo` dénártha a
    luchtaíonn d'fheidhmchlár ag am rite. Is é `_` an t-ainm traidisiúnta ar an
    bhfeidhm aistriúcháin, agus mar sin léitear `_(t"Hello {name}")` mar
    "aistrigh an teachtaireacht seo". Siúlann an **[rang teagaisc](tutorial.md)** an
    cosán ar fad — marcáil, eastóscadh, aistriú, tiomsú, rith — i thart ar
    chúig nóiméad.

## An fhadhb a réitíonn sé { #the-problem-it-solves }

Bíonn f-string idirshuite cheana féin faoin am a fheiceann leabharlann ar
bith é — tá `f"Hello {name}"` ina `"Hello Ada"` faoin bpointe sin, agus
briseann aistriú na mblúirí timpeall ar luach gramadach fhormhór na
dteangacha. Coinníonn t-string ([PEP 750]) an téacs statach, na luachanna
measúnaithe, na sloinn fhoinseacha, na tiontuithe agus na sonruithe formáide
scartha óna chéile — agus sin díreach an deighilt a theastaíonn ó chatalóg
teachtaireachtaí.
[Cad a athraíonn sé sin](comparison.md), i gcomparáid le `%(name)s`,
`.format()` agus `$`-strings.

Níl aon rud i gettext ná i mBabel a deir conas a éiríonn teachtaireacht as
t-string, áfach. Déanann an leabharlann seo an rogha sin, scríobhann síos í
mar [shonraíocht le leagan uirthi](spec.md), agus seolann sí an
[tsraith comhréireachta](spec.md#conformance) chun í a sheiceáil.

## Na rialacha deartha { #the-design-rules }

- Aistrigh teachtaireachtaí iomlána, riamh blúirí abairte.
- Ná glac ach le hainmneacha simplí athróg ar nós `{name}`.
- Coinnigh `!r` agus `:.2f` faoi smacht an fheidhmchláir, amuigh as an
  gcatalóg.
- Ceadaigh d'aistriúcháin sealbhóirí ionaid aitheanta a athordú agus a
  athdhéanamh, agus cosc a chur orthu ag an am céanna síneadh chuig tréithe nó
  formáidiú a chur leis.
- Athúsáid gnáthchomhaid POT, PO agus MO, agus na huirlisí a léann cheana iad.

Agus an liosta comhoiriúnach den rud a fhágann sé faoi d'aon ghnó: ní
logánaíonn sé uimhreacha, airgeadraí ná dátaí — [formáidigh iad sin ar
dtús](guide.md#locale-aware-values), le Babel; ní éalaíonn sé an t-aschur
rindreáilte le haghaidh HTML, blaoisce ná teirminéil; agus ní féidir leis a
mheas an bhfuil aistriúchán *ceart*, gan ach an bhfuil a chuid sealbhóirí
ionaid slán.

## Suiteáil { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 nó níos nuaí. **Níl aon spleáchas ag an rindreáil** — ní
úsáideann sí ach `gettext` na leabharlainne caighdeánaí agus faic eile.

Ritheann an t-eastóscadh agus bailíochtú na gcatalóg trí [Babel], mar sin
suiteáil an breiseán sin cibé áit a ritheann `pybabel`, rud is gnách a bheith
i dtimpeallacht forbartha nó CI seachas in íomhá tháirgthe:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Cá háit le dul ar aghaidh { #where-to-go-next }

**Tosaigh anseo** — ní ghlactar le haon taithí ar gettext:

<div class="grid cards" markdown>

- **[Rang teagaisc](tutorial.md)** — ó chomhadlann fholamh go haistriúchán
  Seapáinise atá ag rith, i gcúig chéim, gach ordú á thaispeáint lena aschur.
- **[Cén fáth t-strings](comparison.md)** — an teachtaireacht chéanna scríofa
  ar cheithre bhealach, agus an rud a shíneann `%(name)s`, `.format()` agus
  `$`-strings chuig an gcatalóg.

</div>

**Bain úsáid as** — na tagairtí oibre:

<div class="grid cards" markdown>

- **[Treoir](guide.md)** — an API ag am rite: cén pointe iontrála le húsáid,
  iolraí, teangacha in aghaidh an iarratais, teaghráin iarchurtha, agus a
  tharlaíonn nuair a bhíonn catalóg mícheart.
- **[Eastóscadh](extraction.md)** — an tagairt do `pybabel`: cumraíocht,
  ainmneacha feidhme saincheaptha, agus an chaoi a mbailíochtaíonn uirlisí atá
  ann cheana na catalóga seo saor in aisce.
- **[I dtáirgeadh](workflow.md)** — an lúb mar a ritheann foireann í: an
  timthriall nuashonraithe, iontrálacha `fuzzy`, geataí CI, ardáin
  aistriúcháin, agus an seoladh.
- **[Aistriú anonn](migration.md)** — é seo a ghlacadh chugat i dtionscadal a
  bhfuil catalóga aige cheana, láithreán glaonna amháin sa turas.
- **[D'aistritheoirí](translators.md)** — leathanach amháin le tabhairt do
  cibé duine a chuireann na comhaid `.po` in eagar.

</div>

**Tuig é** — ón stair go dtí an cur i bhfeidhm:

<div class="grid cards" markdown>

- **[Cúlra](background.md)** — cén fáth a bhfuil an leabharlann seo ann:
  tríocha bliain de gettext, dhá PEP, agus an plé sa leabharlann chaighdeánach
  a dúnadh gan freagra.
- **[Gaistí](pitfalls.md)** — an rud a bhris aistriú an tsuímh seo go cúig
  theanga is tríocha i ndáiríre, agus cé acu leath is féidir le huirlis a
  cheapadh.
- **[Conas a oibríonn sé](internals.md)** — ó oibiacht teimpléid PEP 750 go
  dtí an teaghrán rindreáilte, agus na taiscí a fhágann go bhfuil an tseiceáil
  saor.

</div>

**Tagairt** — na conarthaí:

<div class="grid cards" markdown>

- **[API](api.md)** — gach rud a easpórtálann an pacáiste, ar leathanach
  amháin.
- **[Sonraíocht](spec.md)** — an coinbhinsiún t-string ↔ msgid mar chonradh
  cobhsaí le leagan air, agus sraith comhréireachta inléite ag meaisín leis.

</div>

## Stádas { #status }

| | |
| --- | --- |
| Leagan an phacáiste | 0.1.0a7 |
| Cobhsaíocht an API | alfa — d'fhéadfadh an API Python athrú fós |
| [Sonraíocht](spec.md) | v1, le [sraith comhréireachta](spec.md#conformance) |
| Python | 3.14 agus níos nuaí; tástáilte ar 3.14, 3.14t (saorshnáithithe), agus 3.15 |
| Babel | 2.18 nó níos nuaí, agus ach amháin san áit a ritheann `pybabel` |
| Spleáchais ama rite | ceann ar bith — `gettext` na leabharlainne caighdeánaí |
| Formáid na catalóige | POT, PO agus MO gnáth |
| Athruithe | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Alfa atá ann. Tá an conradh beag d'aon ghnó, agus is í an
[tsonraíocht](spec.md) an chuid chobhsaí de; d'fhéadfadh an API Python bogadh
fós. Roimh eisiúint chobhsaí teastaíonn feisteáin teanga níos leithne, rianú
feidhmíochta leanúnach, athbhreithniú API ó dhaoine a úsáideann gettext agus
Babel i ndáiríre, agus tástáil chomhoiriúnachta ar gach eisiúint Python agus
Babel a dtacaítear léi.

Tá fáilte roimh
[shaincheisteanna agus iarratais tarraingthe](https://github.com/yhay81/gettext-tstrings/issues)
— is í an alfa díreach an tráth is fiú fós argóint a dhéanamh faoin
gcomhéadan.

## Bí páirteach sa phobal { #join-the-community }

- Roghnaigh
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  le haghaidh ranníocaíochta teoranta.
- Cuir ceisteanna faoin úsáid i
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Tabhair sreafaí oibre gettext ó thimpeallachtaí táirgthe agus smaointe API
  chuig
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Léigh an
  [treoir ranníocaíochta](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  sula n-osclaíonn tú iarratas tarraingthe.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
