---
description: "Conradh na sealbhóirí ionaid do cibé duine a chuireann na comhaid .po in eagar: cad is féidir leat a athrú, cad nach mór duit a fhágáil ina aonar, agus conas na hearráidí a léamh."
---

# D'aistritheoirí

Tá an leathanach seo don duine a chuireann an chatalóg in eagar, ní don duine
a scríobhann an cód. Tá sé gearr d'aon ghnó, agus tá sé i gceist go nascfaí
nó go gcóipeálfaí é isteach i dtreoracha aistritheoirí tionscadail féin.

Ní gá duit Python a léamh d'aon rud anseo. Baineann gach rud anseo le rud
amháin: na píosaí de theachtaireacht atá idir lúibíní slabhracha.

## Cad is sealbhóir ionaid ann { #what-a-placeholder-is }

Féadfaidh ainmneacha idir lúibíní slabhracha a bheith i dteachtaireacht i
gcatalóg:

```po
msgid "Hello {name}"
msgstr ""
```

Is **sealbhóir ionaid** é `{name}`. Nuair a thaispeánann an clár an
teachtaireacht seo cuireann sé luach a sholáthraíonn sé féin in ionad
`{name}` — ainm duine, ainm comhaid, uimhir. Ní focal le haistriú é an
sealbhóir ionaid; is sliotán é.

Téann d'aistriúchán isteach sa `msgstr`, agus caithfidh sé an sliotán sin a
choinneáil:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Cad is féidir leat a athrú, agus cad nach féidir { #what-you-may-change-and-what-you-may-not }

**Is féidir** leat:

- **Sealbhóir ionaid a bhogadh** cibé áit is mian le gramadach na sprioctheanga
  é a bheith, go tosach na teachtaireachta san áireamh.
- **Sealbhóir ionaid a athdhéanamh** má theastaíonn an luach faoi dhó ón
  teanga.
- **Gach focal eile a athscríobh**, an phoncaíocht, an spásáil agus ord na
  habairte san áireamh.

**Ní mór duit gan**:

- **An t-ainm istigh sna lúibíní a aistriú.** Fanann `{name}` mar `{name}`,
  fiú i dteanga nach scríobhann rud ar bith eile i litreacha Laidineacha.
- **Na lúibíní a bhaint**, ná an t-ainm a scríobh gan iad.
- **Na lúibíní ASCII `{` `}` a chur in ionad `｛` `｝` lánleithid.** Táirgeann
  mórán modhanna ionchuir na foirmeacha lánleithid; tá cuma beagnach
  comhionann orthu agus ní oibríonn siad.
- **Formáidiú a chur leis**, ar nós `{name!r}` nó `{amount:.2f}`. Is sa chlár
  a shocraítear an chaoi a dtaispeántar luach, ní sa chatalóg.
- **Sealbhóir ionaid a chumadh** nach bhfuil sa `msgid`.

Má theastaíonn luach ó theachtaireacht nach dtairgeann an bunleagan, is
teachtaireacht í sin a chaithfidh an forbróir a athrú. Abair é sin seachas dul
timpeall air.

## Foirmeacha iolra { #plural-forms }

Tagann teachtaireacht a bhfuil comhaireamh inti le sliotán `msgstr` amháin in
aghaidh gach foirme iolra i do theanga, agus is í do theanga a shocraíonn cé
mhéad díobh sin atá ann — ceann amháin don tSeapáinis, dhá cheann don
Ghearmáinis, trí cinn don Rúisis, sé cinn don Araibis. Líon isteach gach
sliotán a thugann an chatalóg duit.

Dhá riail a mheallann daoine:

- **Ní hionann na sliotáin agus "uatha, iolra, iolra níos mó".** Ciallaíonn
  gach innéacs cibé rud a deir riail iolra do theanga a chiallaíonn sé. Is don
  nialas amháin an tríú foirm sa Laitvis; is do bheirt go díreach an dara
  ceann sa tSlóivéinis; cuireann an Bhreatnais an cás ginearálta ag innéacs 0
  agus an t-uatha ag innéacs 1.
- **Féadfaidh dhá shliotán an téacs céanna a bheith iontu go dlisteanach.** Sa
  Tuircis, san Ungáiris, sa Pheirsis agus sa Bheangáilis fanann ainmfhocal san
  uatha i ndiaidh uimhreach, mar sin is é an teaghrán céanna an dá fhoirm de
  theachtaireacht a bhfuil comhaireamh inti. Tá sin ceart, ní botún cóipeála.

Baineann rialacha na sealbhóirí ionaid thuas le gach foirm ar leith.

## Iontrálacha fuzzy { #fuzzy-entries }

Is buille faoi thuairim meaisín í iontráil atá marcáilte `fuzzy`: d'athraigh
an forbróir an bhunteachtaireacht, agus chuir na huirlisí an téacs nua le
d'aistriúchán d'fhonn go mbeadh áit tosaigh agat.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

**Ní úsáideann an clár** iontráil fuzzy — taispeánann sé an bunleagan
neamhaistrithe ina hionad — go dtí go leasaíonn duine éigin an téacs agus go
mbaineann sé an marcóir `fuzzy`. Tá cnaipe ag formhór na n-eagarthóirí PO chun
é sin díreach a dhéanamh.

## Teachtaireacht teipe a léamh { #reading-a-failure-message }

Seiceálann na huirlisí na sealbhóirí ionaid nuair a thiomsaítear an chatalóg,
agus scríobhtar an teachtaireacht duitse seachas do programmer. Is bóthar
caoch é a thuairisciú nach bhfuil ann ach go bhfuil `{name}` ar iarraidh nuair
a fheiceann tú na carachtair sin os do chomhair, mar sin nuair a bhíonn cuma
ar shealbhóir ionaid go bhfuil sé ann ach nach bhfuil, insíonn an
teachtaireacht cén fáth. I gcoinne an bhunleagain `Hello {name}`,
tuairiscítear gach ceann díobh seo faoi
`translation does not match the source placeholders:`

| A deir d'aistriúchán | An chúis a thugtar |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Faigheann carachtair nach féidir a fheiceáil a gcóireáil féin. Is rud é spás
gan bhriseadh laistigh de na lúibíní slabhracha a chruthaíonn modh ionchuir
agus nach dtaispeánann aon eagarthóir, mar sin priontálann an teachtaireacht
de réir a phointe cóid é seachas carachtar a ainmniú nach bhféadfá a aimsiú
choíche:

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

Má bhuaileann tú le ceann díobh seo agus nach léir an leigheas, is é an
beart sábháilte an sealbhóir ionaid a chlóscríobh tú a scriosadh agus an ceann
ón `msgid` a chóipeáil.

## Cad nach féidir leis na seiceálacha a dhéanamh { #what-the-checks-cannot-do }

Deimhníonn na huirlisí go bhfuil do chuid sealbhóirí ionaid slán. Ní féidir
leo a rá an bhfuil an t-aistriúchán cruinn, nádúrtha ná ceart don chomhthéacs
— fanann sin fútsa ar fad.

Cabhraíonn dhá rud níos mó ná aon seiceáil:

- **Léigh nóta tráchta an aistritheora.** Is é atá i líne a thosaíonn le `#.`
  os cionn na teachtaireachta ná an forbróir ag insint duit cá bhfeictear í
  agus cad is brí léi.
- **Fiafraigh faoi `msgctxt`.** Nuair a fheictear an focal céanna faoi dhó le
  comhthéacsanna difriúla, is amhlaidh gur gá an dá cheann a aistriú ar
  bhealaí difriúla — "Open" an cnaipe agus "Open" an staid, mar shampla.
