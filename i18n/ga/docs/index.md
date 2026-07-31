---
description: "Aistrigh teachtaireachtaí t-string iomlána trí gettext agus Babel, agus an formáidiú coinnithe amuigh as an gcatalóg."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Scríobh an abairt uair amháin.<br>Aistrigh í ina hiomláine.

Comhtháthú sábháilte le gettext agus Babel do t-strings Python 3.14+ — fanann
an luach ina áit, agus feiceann an chatalóg an teachtaireacht ina hiomláine:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Tosaigh an rang teagaisc :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Cén fáth t-strings](comparison.md){ .md-button }

Cleachtann an suíomh seo an rud a dhoiciméadaíonn sé: rindreáiltear gach
eagrán teanga — an nascleanúint, na lipéid agus an tuairisc tógála a
thuigeann an t-iolra — ó chatalóga PO le
[`gettext-tstrings` féin](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Faigheann an chatalóg an abairt iomlán `Hello {name}`. Tá cead ag aistriúchán
`{name}` a athordú nó a athdhéanamh; níl cead aige é a fhágáil ar lár, ceann
nua a chumadh, ná formáidiú dá chuid féin a cheangal leis — seiceálann an
leabharlann seo é sin, agus titeann catalóg lochtach ar ais ar an téacs
foinseach seachas tuairteáil.

!!! note "gettext nua duit? An sreabhadh oibre iomlán i gceithre abairt"

    Is é **gettext** an bealach caighdeánach a aistrítear bogearraí, i bPython
    agus i bhfad níos faide anonn. Marcálann do chód na teaghráin is féidir a
    aistriú; bailíonn *eastóscóir* iad i gcomhad teimpléid (`.pot`); líonann
    aistritheoir — nach programmer é de ghnáth — comhad catalóige (`.po`)
    amháin in aghaidh na teanga, agus tiomsaítear é sin ina `.mo` dénártha a
    luchtaíonn d'fheidhmchlár ag am rite. Is é `_` an t-ainm traidisiúnta ar an
    bhfeidhm aistriúcháin, agus mar sin léitear `_(t"Hello {name}")` mar
    "aistrigh an abairt seo". Siúlann an **[rang teagaisc](tutorial.md)** an
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

## An rogha a dhéanann sé { #the-choice-it-makes }

- Aistrigh teachtaireachtaí iomlána, riamh blúirí abairte.
- Ná glac ach le hainmneacha simplí athróg ar nós `{name}`.
- Coinnigh `!r` agus `:.2f` faoi smacht an fheidhmchláir, amuigh as an
  gcatalóg.
- Lig d'aistritheoirí sealbhóirí ionaid aitheanta a athordú agus a
  athdhéanamh — ach gan tréithe a ghairm, agus gan iompar formáidithe a chur
  leo.
- Athúsáid gnáthchomhaid POT, PO agus MO, agus na huirlisí a léann cheana iad.

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

Tagann trí chineál léitheora anseo: duine atá ag aistriú a chéad chláir,
duine atá ag ceangal an aistriúcháin le fíorthionscadal, agus duine ar mian
leis a fháil amach go beacht cén fáth a bhfuil an t-inneall múnlaithe mar
seo. Tá cosán ag gach duine acu.

**Á fhoghlaim** — ní ghlactar le haon taithí ar gettext:

<div class="grid cards" markdown>

- **[Rang teagaisc](tutorial.md)** — tosaigh anseo: ó chomhadlann fholamh go
  haistriúchán Seapáinise atá ag rith, i gcúig chéim, gach ordú á thaispeáint
  lena aschur.
- **[Cén fáth t-strings](comparison.md)** — an teachtaireacht chéanna scríofa
  ar cheithre bhealach, agus an rud a shíneann `%(name)s`, `.format()` agus
  `$`-strings chuig an gcatalóg.
- **[Cúlra](background.md)** — cén fáth a bhfuil an leabharlann seo ann:
  tríocha bliain de gettext, dhá PEP, agus an plé sa leabharlann chaighdeánach
  a dúnadh gan freagra.

</div>

**Á úsáid i ndáiríre** — na tagairtí oibre:

<div class="grid cards" markdown>

- **[Treoir](guide.md)** — an API ag am rite: iolraí, teangacha in aghaidh an
  iarratais, teaghráin iarchurtha, agus a tharlaíonn nuair a bhíonn catalóg
  mícheart.
- **[Eastóscadh](extraction.md)** — an tagairt do `pybabel`: cumraíocht,
  ainmneacha feidhme saincheaptha, agus an chaoi a mbailíochtaíonn uirlisí atá
  ann cheana na catalóga seo saor in aisce.
- **[I dtáirgeadh](workflow.md)** — an lúb mar a ritheann foireann í: an
  timthriall nuashonraithe, iontrálacha `fuzzy`, geataí CI, ardáin
  aistriúcháin, agus teangacha in aghaidh an iarratais i bhfeidhmchlár
  gréasáin.
- **[API](api.md)** — gach rud a easpórtálann an pacáiste, ar leathanach
  amháin.

</div>

**Á thuiscint** — ó na prionsabail go dtí an cur i bhfeidhm:

<div class="grid cards" markdown>

- **[Conas a oibríonn sé](internals.md)** — ó oibiacht teimpléid PEP 750 go
  dtí an teaghrán rindreáilte, agus na taiscí a fhágann go bhfuil an tseiceáil
  saor.
- **[Sonraíocht](spec.md)** — an coinbhinsiún t-string ↔ msgid mar chonradh
  cobhsaí le leagan air, agus sraith comhréireachta inléite ag meaisín leis.

</div>

## Stádas { #status }

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
