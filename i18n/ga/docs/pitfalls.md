---
description: "An rud a bhriseann aistriú suímh bhig amháin go cúig theanga is tríocha i ndáiríre, cé acu díobh is féidir leis an leabharlann a cheapadh duit, agus cé acu nach féidir."
---

# Gaistí

Tá an suíomh seo aistrithe go cúig theanga is tríocha, agus táirgeadh gach
eagrán acu tríd an lúb a mhúineann an doiciméadú seo a rith. Is corpas beag é
sin de réir chaighdeáin an tionscail, agus mar sin féin ba leor é chun titim i
bhformhór na ngaistí a fhágann go bhfuil i18n níos deacra ná mar a fheictear.

Rud a chuaigh amú anseo i ndáiríre atá i ngach alt thíos: an chuma a bhí air
ag an am, agus an áit a dtiteann an líne idir an rud a sheiceálann an
leabharlann duit agus an rud a fhanann faoi do bhreithiúnas féin.

## Nuair a athainmnítear athróg, athaistrítear abairt { #renaming-a-variable-retranslates-a-sentence }

Is í an msgid eochair na catalóige, agus tá ainm idirshuite *istigh* inti.
Nuair a bogadh tairiseach amháin go scóip an mhodúil agus é a scríobh le
ceannlitreacha mar a iarrann stíl Python — `author` go `AUTHOR` — rinneadh
teachtaireacht nach bhfaca catalóg ar bith riamh de
`Copyright © 2026 {author} · MIT License`. Bheadh gach aistriúchán ar an líne
sin tar éis dul siar tríd an timthriall fuzzy, i ngach teanga, mar gheall ar
athainmniú nár athraigh aon rud a d'fheicfeadh léitheoir.

Ní stopfaidh an leabharlann thú: is ainmneacha bailí sealbhóra ionaid iad an
dá litriú. Ach is é a dhéanann sí ná an t-ainm a dhéanamh *fiúntach* le
cosaint — caithfidh idirshuíomh a bheith ina
[ghnáthainm](internals.md#from-template-to-msgid), agus mar sin is focal is
féidir le haistritheoir a léamh atá in eochair na catalóige, ní slonn.

Tá an cás contrártha sábháilte ó nádúr. Níl na tiontuithe ná na sonruithe
formáide ina gcuid den msgid, mar sin ní athraíonn géarú `{amount:,.2f}` go
`{amount:,.0f}` aon eochair agus ní chuireann sé aistriúchán ar bith ó bhail
in aon áit.

## Ní chiallaíonn `nplurals=2` dhá theaghrán éagsúla { #nplurals-2-does-not-mean-two-different-strings }

Fógraíonn an Tuircis, an Ungáiris, an Pheirsis agus an Bheangáilis dhá fhoirm
iolra an ceann, agus sna ceithre theanga sin is é an *teaghrán céanna* go
dlisteanach an dá fhoirm de theachtaireacht chomhairthe — fanann an
t-ainmfhocal san uatha i ndiaidh uimhreach, mar sin tá `{n} sayfa` ceart do
leathanach amháin agus do dheich gcinn. Briseann athbhreithneoir a
"cheartaíonn" an dúbailt an t-aistriúchán.

Tá an botún contrártha chomh furasta céanna. Níl tríú foirm na Laitvise ann
ach do **nialas amháin**; is **déach** í an dara foirm sa tSlóivéinis, do dhá
cheann go beacht; teastaíonn an focal `de` ó fhoirm dheireanach na Rómáinise,
focal nach mór don dá fhoirm eile a sheachaint. Má líontar na sliotáin sin le
huatha agus le hiolra, gheofar catalóg nach bhfuil mícheart ach do na
comhairimh nach dtástálann aon duine.

Níos measa fós, níl *ord* na sliotán séimeantach. Innéacsaíonn an Bhreatnais a
cúig fhoirm sa chaoi gurb é `msgstr[0]` an cás ginearálta agus gurb é
`msgstr[1]` an t-uatha. Má líontar iad san ord is dealraithí, fágtar an
t-uatha san áit a bhfaighidh gach teachtaireacht neamhchomhairthe é.

Ní ghlacann an leabharlann aon chuid de seo uirthi féin, agus sin é an pointe:
tá riail iolra na sprioctheanga ina ceanntásc catalóige féin, agus ligeann an
[riail aontais/trasnaithe](spec.md) d'aistriúchán níos mó foirmeacha, nó níos
lú, a bheith aige ná mar atá ag an bhfoinse. Is é a sheiceálann sí an t-aon
rud is féidir léi a sheiceáil gan an teanga a bheith ar eolas aici — go
gcoinníonn gach foirm na sealbhóirí ionaid a theastaíonn uaithi.

## Is féidir le dhá fhoirm a bheith comhionann ar chúis mhaith { #two-forms-can-be-identical-for-a-reason }

Tá cúig fhoirm iolra ag an nGaeilge, agus i dtuairisc thógála an tsuímh seo
litrítear roinnt acu ar aon dul. Ní botún cóipeála is cúis leis sin: tosaíonn
*leathanach* le `l`, agus ní scríobhtar ceachtar den dá athrú tosaigh a
spreagann uimhreacha na Gaeilge ar `l`. Déanann na foirmeacha obair
fhírinneach mar sin féin — malartaíonn an gas idir *leathanach* agus
*leathanaigh*, agus filleann comhairimh os cionn a deich ar an uatha — ach ní
thaispeánfadh ainmfhocal ar bith a chiallaíonn "leathanach" an chodarsnacht.

Aon seiceáil a chuireann foirmeacha dúblacha in amhras, cuirfidh sí Gaeilge
cheart in amhras. Níl d'athbhreithneoir ann dó seo ach duine a bhfuil an
teanga aige.

## Ní féidir le teachtaireacht réiteach ach le comhaireamh amháin { #a-message-can-only-agree-with-one-count }

Insíonn tuairisc thógála an tsuímh seo cé mhéad leathanach a rindreáladh agus
cé chomh fada a thóg sé. Tá cuma neamhurchóideach ar
"Rendered {n} pages in {seconds} seconds" mar scríbhinn, agus níl sé
inaistrithe: roghnaíonn gettext foirm amháin as comhaireamh amháin, agus is é
`n` an comhaireamh sin. Bheadh ar an bhfocal *seconds* réiteach le huimhir
nach bhfeiceann meaisínre an iolra riamh.

Is é an leigheas an dara cainníocht a dhéanamh ina siombail aonaid seachas ina
focal, agus logánaítear siombailí aonaid iad féin: iompraíonn catalóga an
tsuímh seo `s`, `с`, `ث`, `שנ׳` agus `mp`, agus teastaíonn spás roimh an
tsiombail ó chló-eagar na Fraincise, na Spáinnise agus na Sualainnise san áit
nach dteastaíonn ón mBéarla. Ní gnó don leabharlann aon chuid de sin — ach is
gnó di a thabhairt faoi deara go dteastaíonn *dhá* réiteach ó theachtaireacht,
agus níl d'uirlis chuige sin ach an teachtaireacht a scríobh ar bhealach eile.

## Nuair a chuirtear abairt Bhéarla in eagar, cuirtear gramadach iasachta in eagar { #editing-an-english-sentence-edits-foreign-grammar }

Deireadh an leathanach baile "all ten language editions" tráth. Nuair a
baineadh an uimhir as — eagarthóireacht aon fhocail sa Bhéarla, a rinneadh mar
go raibh an uimhir ag dul as dáta i gcónaí — rinneadh ainmní uatha d'ainmní
iolra. B'éigean don Spáinnis, don Iodáilis, don Phortaingéilis, don Rúisis,
don Úcráinis, don Ghréigis, don Ollainnis agus don Eabhrais an briathar a
réiteach as an nua; theastaigh athrú ar an rangabháil freisin i roinnt acu.

Níl eagarthóireacht foinse a léitear mar mhionrud sa Bhéarla ina mionrud níos
faide síos an sruth. Is é an marcáil fuzzy, rud a dhéanann `pybabel update`,
an mheicníocht a thugann an deis do gach aistritheoir é a thabhairt faoi
deara.

## Maireann difríochtaí dofheicthe trí gach cóipeáil is greamú { #invisible-differences-survive-every-copy-paste }

Luann an treoir diagnóisic ina bhfuil `(nаme)` — éalú d'aon ghnó, mar gur `а`
Coireallach an carachtar a ainmníonn sí, ceann nach féidir le léitheoir ar
bith a idirdhealú ón gceann Laidineach. D'iompaigh aistritheoirí an tsuímh seo
an t-éalú sin ina charachtar iarbhír **cúig huaire ar leith**, i gcúig theanga
éagsúla, agus leathanach á tháirgeadh acu gach uair a raibh cuma cheart air
agus a bhí mícheart.

Ceapann an leabharlann an ceann seo, agus is é sin an fáth a bhfuil na
diagnóisicí múnlaithe mar atá siad: sealbhóir ionaid a bhfuil córais
scríbhneoireachta measctha ina litreacha,
[tuairiscítear faoi dhó é](internals.md#diagnostics-are-part-of-the-design),
uair amháin go hinléite agus uair amháin éalaithe, mar is í an fhoirm éalaithe
an t-aon litriú a aithníonn óna chéile iad. Priontáiltear spás gan bhriseadh
taobh istigh de lúibíní de réir pointe cóid ar an gcúis chéanna. Diúltaíonn
seiceálaí na catalóige don teachtaireacht sula bhféadfaí í a sheoladh.

## Ní ionann neamhfholamh agus aistrithe { #non-empty-is-not-translated }

Éiríonn le catalóg a scafláladh trína msgids a chóipeáil isteach sna msgstrs i
ngach seiceáil shoineanta: níl aon rud folamh, níl aon rud fuzzy, agus
meaitseálann an tacar teachtaireachtaí go beacht. Seoladh eagrán amháin den
suíomh seo mar sin ar feadh roinnt uaireanta an chloig. Mar an gcéanna d'ocht
leathanach d'eagrán eile ar chóipeanna comhionanna beart ar bheart den fhoinse
Bhéarla iad — rud a éiríonn le seiceáil a chuireann na bloic chóid eatarthu i
gcomparáid, mar gurb ionann comhad dóibh.

Ní féidir le leabharlann aistriúcháin ceachtar acu a fheiceáil. Tá an dá cheann
saor le tástáil, ach ní trína éileamh go mbeadh gach iontráil difriúil óna
foinse: aistríonn `OK`, ainmneacha táirgí, ainmneacha daoine, acrainmneacha
agus aitheantóirí cóid go léir mar iad féin, agus tugann seiceáil a chuireann
cosc air sin torthaí bréagdhearfacha go deo.

Tomhais an *ráta* ina ionad sin, thar chatalóg iomlán nó thar leathanach
iomlán, agus cuir na heisceachtaí chuig duine daonna. Déanann tástáil an tsuímh
seo féin díreach é sin — cuireann sí línte próis gach eagráin i gcomparáid leis
an bhfoinse Bhéarla agus teipeann uirthi os cionn 25% comhionann. Bhí an
t-eagrán bréige ag 87%; luíonn gach fíoraistriúchán idir 4% agus 8%, is é sin an
t-eireaball beag de línte a chomhtharlaíonn go dlisteanach, ar nós URLanna agus
aschur cláir a luaitear. Tá an dá dhaonra sách fada óna chéile nach gá don
tairseach a bheith beacht.

## Ní hí an chatalóg an t-aon rud a aistrítear { #the-catalog-is-not-the-only-translated-thing }

Ní raibh baint ar bith ag dhá theip anseo le gettext.

Nuair a aistrítear ceannteideal athraítear an t-ancaire a ghintear uaidh, agus
mar sin briseann gach nasc trasleathanaigh isteach sa rannán sin — go ciúin,
sa teanga sin amháin. Greamaíonn an suíomh seo an t-ancaire Béarla de gach
ceannteideal, agus díorthaíonn tástáil an liosta a bhfuiltear ag súil leis ón
leathanach Béarla.

Agus seolann gineadóir an tsuímh aistriúcháin chomhéadain do sheasca a hocht
de theangacha, nach n-áirítear an tSvahaílis ná an Ghaeilge orthu. Gan ceann
acu ní thiteann an tógáil ar ais go Béarla; teipeann ar áireamh an teimpléid
agus ní féidir an t-eagrán a thógáil ar chor ar bith. Tá dhá cheann de
chomhaid na stórlainne seo féin ann chun an bhearna sin a líonadh.

## Tá fabhtanna i d'uirlisí féin freisin { #your-tools-have-bugs-too }

An chéim CI a mholann an doiciméadú seo chun catalóga atá as dáta a cheapadh,
`pybabel update --check`, ní féidir léi an obair sin a dhéanamh d'aon
tionscadal a úsáideann `pgettext` ná `npgettext`. Ar Babel 2.18.0
tuairiscíonn sí gach catalóg a bhfuil `msgctxt` inti mar cheann atá as dáta,
ar gach rith. Ritheann an chomparáid trí `Catalog.is_identical`, a
chuardaíonn gach teachtaireacht de réir na heochrach faoina stóráiltear í —
agus i gcás teachtaireachta comhthéacsúla is í an eochair sin an péire
`(id, context)`, rud nach nglacann `Catalog.get` leis. Ní fhilleann an
cuardach faic, agus ní bhíonn na catalóga cothrom lena chéile riamh:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Fuarthas anseo é trí iarracht a dhéanamh é a úsáid, tuairiscíodh in aghaidh an
tsrutha é, agus tá an tseiceáil ionaid
[ar an leathanach táirgthe](workflow.md#what-ci-gates).

Is é an ceacht ginearálta an ceann míchompordach: is measa geata atá dearg i
gcónaí ná gan geata ar bith, mar múchann foireann é. Deimhnigh gur féidir le
do sheiceáil CI éirí léi i ndáiríre sula gcuirfidh tú muinín inti chun
teipeadh.

## Cad chuige an leabharlann, in aon líne amháin { #what-the-library-is-for-in-one-line }

Is breithiúnas nach féidir le huirlis ar bith a ghlacadh uirthi féin formhór
an leathanaigh seo. Is é an rud is *féidir* le huirlis a dhéanamh ná a ráthú
nach féidir le haistriúchán struchtúr na habairte a aistríonn sé a athrú —
nach féidir leis luach a fhágáil ar lár, ceann a chumadh, ceann a
athfhormáidiú, ná lámh a chur i do chuid oibiachtaí — agus é sin a rá in
abairt ar féidir leis an duine a chaithfidh é a dheisiú gníomhú uirthi. Sin a
bhfuil á ghealladh ag an leabharlann seo, agus is é an chuid eile den suíomh
seo an chaoi a gcoinníonn sí é.
