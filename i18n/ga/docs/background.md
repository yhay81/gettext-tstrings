---
description: "Tríocha bliain de gettext, dhá PEP deich mbliana ó chéile, agus an plé sa leabharlann chaighdeánach a dúnadh mar rud nach raibh beartaithe: cén fáth a bhfuil an leabharlann seo ann, le naisc chuig na foinsí."
---

# Cúlra

Suíonn an leabharlann seo ag pointe teagmhála dhá scéal fhada — ceann faoin
gcaoi a n-aistrítear bogearraí, ceann faoin gcaoi a n-idirshuíonn Python
teaghráin — a thrasnaigh a chéile faoi dheireadh in 2025 agus a stad ansin
díreach ag an bpointe ina raibh gá le coinbhinsiún beag cúramach. Insíonn an
leathanach seo an dá scéal, le naisc chuig na foinsí, mar is fusa breithiúnas
a thabhairt ar chinntí deartha an tsuímh seo nuair a fheiceann tú na ceisteanna
a fhreagraíonn siad.

## An t-éiceachóras gettext { #the-gettext-ecosystem }

Is trí [GNU gettext] a aistrítear bogearraí saora ó lár na 1990idí: marcáil na
teaghráin sa chód, eastósc go teimpléad iad, tabhair comhad catalóige amháin
in aghaidh na teanga do na haistritheoirí, tiomsaigh, luchtaigh ag am rite.
Timpeall na lúibe sin d'fhás éiceachóras iomlán — eagarthóirí PO, sreafaí
oibre athbhreithnithe, agus ardáin aistriúcháin a labhraíonn an fhormáid
chomhaid chéanna — agus tá [modúl `gettext`][stdlib-gettext] á sheoladh ag
Python ina leabharlann chaighdeánach le breis is fiche bliain. Níorbh í leath
ama rite an aistriúcháin an fhadhb riamh.

Ba í an leath neamhshocraithe i gcónaí ná *cén chuma atá ar theaghrán na
catalóige*. Síneann teachtaireacht `%(name)s` comhréir printf chuig
aistritheoirí, comhréir a n-iompaíonn litir amháin scriosta ina tuairteáil
táirgthe; síneann teachtaireacht `.format()` rochtain ar thréithe oibiachtaí
beo chuig an gcatalóg. (Siúlann [Cén fáth t-strings](comparison.md) tríd an dá
cheann, agus na teipeanna ar taispeáint.) Agus na f-strings — an chomhréir is
fearr le formhór an chóid Python inniu — ní féidir leo páirt a ghlacadh ar
chor ar bith: faoin am a fheiceann leabharlann ar bith ceann acu, tá sé ina
theaghrán críochnaithe cheana. Bíonn daoine á thriail mar sin féin, chomh
minic sin go mbailíonn rianaitheoir saincheisteanna Babel na hiarrachtaí
([#594][babel-594], [#715][babel-715]); teip struchtúrtha atá inti, ní gné
atá ar iarraidh.

## Dhá PEP, deich mbliana ó chéile { #two-peps-ten-years-apart }

In 2015 scríobh Alyssa Coghlan agus Nick Humrich [PEP 501], ag moladh
teimpléad idirshuite arbh é i18n an chéad spreagadh a luadh dóibh —
"providing a cleaner syntax for i18n translation", i bhfocail an PEP féin.
Cuireadh an moladh ar athló, go páirteach mar gur léirigh an plé go raibh
nithe suntasacha breise le cur san áireamh i gcás i18n nach raibh i gceist le
cásanna úsáide níos simplí.

Deich mbliana ina dhiaidh sin, thug [PEP 750] — le Jim Baker, Guido van
Rossum, Paul Everitt, Koudai Aono, Lysandros Nikolaou agus Dave Peck — an
smaoineamh ar ais mar t-strings, [glacadh leis in Aibreán 2025][sc-resolution],
agus seoladh é le [Python 3.14] i nDeireadh Fómhair 2025. Tarraingíodh PEP 501
siar ansin ina fhabhar. Tá mionsonra amháin tábhachtach don leathanach seo:
*níl* i18n i measc na spreagthaí a luaitear i PEP 750. Rinne an PEP an
mheicníocht a ghinearálú — cineál teimpléid is féidir le leabharlann ar bith a
ídiú — agus d'fhág sé ceist an aistriúcháin díreach san áit inar pháirceáil
PEP 501 í deich mbliana roimhe sin: oscailte.

Mar sin, ó Python 3.14 amach, bhí díreach an struchtúr sonraí a theastaíonn ó
chatalóg teachtaireachtaí ag an teanga, agus gan aon choinbhinsiún chun é a
úsáid mar cheann.

## An plé sa leabharlann chaighdeánach { #the-stdlib-discussion }

Dhá mhí sular seoladh 3.14, mhol Adrian Mönnich (ThiefMaster, duine de
chothaitheoirí thionscadal Indico) an bhearna sin a dhúnadh sa leabharlann
chaighdeánach féin: tháinig an snáithe
[Support t-strings in gettext][discuss-thread] ar discuss.python.org, a
osclaíodh i Lúnasa 2025, le [hiarratas tarraingthe][cpython-pr] a bhí ag obair
agus a chuir tacaíocht do t-strings le `gettext` agus le `pygettext` araon.

Is fiú an snáithe a léamh ina iomláine, mar tugann sé chun solais gach ceist
chrua a bhí ar an leabharlann seo a fhreagairt níos déanaí:

- **Cad is féidir a bheith in idirshuíomh?** Ainm simplí amháin, nó tréithe
  agus glaonna le hainm sealbhóra ionaid díorthaithe? Malartaíonn gach freagra
  áisiúlacht ar chobhsaíocht msgid agus ar shábháilteacht catalóige.
- **Cad a éilíonn foirmeacha iolra,** nuair a bhíonn córas iolra na
  sprioctheanga difriúil le córas na foinse?
- **An é gettext an sprioc cheart ar chor ar bith?** Dhírigh Barry Warsaw — a
  d'áitigh le linn fhorbairt PEP 750 nach raibh t-strings oiriúnach do i18n —
  ar a [`flufl.i18n`][flufl-i18n] féin agus ar a stíl `$`-string mar an uirlis
  ba chairdiúla; d'áitigh daoine eile gettext a fhágáil ina ndiaidh ar fad i
  bhfabhar córas níos nuaí ar nós [Fluent].
- **Agus an mheiteacheist:** cibé rud a sheolann an leabharlann chaighdeánach,
  ní féidir é a athrú go bunúsach choíche. Is baolach an rud é coinbhinsiún a
  bhfuil an oiread seo roghanna oscailte ann a reo ar an gcéad iarracht.

Níor tháinig comhthoil ar bith chun cinn.
[Dúnadh saincheist CPython mar "not planned"][cpython-issue] agus dúnadh an
t-iarratas tarraingthe gan é a chumasc i nDeireadh Fómhair 2025, cúpla lá tar
éis eisiúint 3.14. Bhí an cumas ann sa teanga; ní raibh baile ar bith ag an
gcoinbhinsiún.

## Cén fáth pacáiste ar dtús { #why-a-package-first }

Sin an bhearna a roghnaigh an tionscadal seo a líonadh ó thaobh amuigh den
leabharlann chaighdeánach, ar gheall d'aon ghnó: aibíonn coinbhinsiún níos
tapúla san áit ar féidir leis leaganacha a chur amach go saor agus glacadh
leis a thuilleamh cás ar chás, agus is í an leabharlann chaighdeánach — a
chaithfidh a bheith ceart ón gcéad uair — an áit ar cheart do choinbhinsiún
teacht i dtír sa deireadh, ní an áit inar cheart é a shaothrú.

Go nithiúil, tá freagra scríofa anseo ar gach ceist chonspóideach sa snáithe,
gach ceann ar a leathanach féin:

- Ní féidir le hidirshuímh a bheith ach ina **n-ainmneacha simplí**, ionas go
  bhfanann msgids cobhsaí agus fiúntach — taispeánann
  [an treoir](guide.md#safety-and-scope) an riail, agus
  [Conas a oibríonn sé](internals.md#from-template-to-msgid) na cúiseanna.
- **Fanann an formáidiú amuigh as an gcatalóg** ar fad
  ([Cén fáth t-strings](comparison.md)).
- Leanann **iolraí** riail aontais/trasnaithe a ligeann do chóras iolra na
  sprioctheanga bheith difriúil le córas na foinse ([sonraíocht §4](spec.md)).
- **Titeann catalóg lochtach ar ais in ionad tuairteála**, agus coinníonn sí
  conradh gettext féin
  ([an treoir](guide.md#what-happens-when-a-catalog-is-wrong)).
- Agus is [sonraíocht le leagan uirthi](spec.md) an coinbhinsiún ar fad,
  agus sraith comhréireachta inléite ag meaisín léi — scríofa ionas go
  bhféadfadh cur i bhfeidhm eile, ceann sa leabharlann chaighdeánach amach
  anseo san áireamh, glacadh léi gan athrú agus idir-inoibriú.

Níl deireadh leis an bplé, agus is rannpháirtí ann é an tionscadal seo, ní
breithiúnas air. Má tá taithí agat ar gettext i dtimpeallachtaí táirgthe a
bhaineann leis na roghanna seo, is sa [snáithe céanna][discuss-thread] agus i
[nDíospóireachtaí][gh-discussions] na stórlainne seo a phléitear í.

## Amlíne { #timeline }

| Cathain | Cad a tharla |
| --- | --- |
| lár na 1990idí | Bunaíonn GNU gettext an sreabhadh oibre PO/POT/MO a labhraíonn aistritheoirí agus ardáin fós. |
| 2015 | Molann [PEP 501] teimpléid idirshuite, le i18n mar an chéad spreagadh; cuirtear ar athló é. |
| 2016 | Seoltar f-strings i bPython 3.6 — faigheann an t-idirshuíomh a chomhréir, agus ní féidir leis an aistriúchán í a úsáid. |
| Iúil 2024 | Molann [PEP 750] t-strings. |
| Aibreán 2025 | [Glactar][sc-resolution] le PEP 750; tarraingítear PEP 501 siar ina fhabhar. |
| Lúnasa 2025 | Osclaítear an snáithe [Support t-strings in gettext][discuss-thread], le [hiarratas tarraingthe][cpython-pr] don leabharlann chaighdeánach. |
| Deireadh Fómhair 2025 | Seolann [Python 3.14] t-strings; dúntar saincheist na leabharlainne caighdeánaí mar [not planned][cpython-issue]. |
| 2026 | Seoltar `gettext-tstrings` mar alfa, le [sonraíocht v1](spec.md) agus a sraith comhréireachta. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
