---
description: "An coinbhinsiún t-string go msgid mar chonradh beag le leagan air, agus sraith comhréireachta inléite ag meaisín leis."
---

# Sonraíocht

Is féidir leat an leabharlann seo a úsáid gan an leathanach seo a léamh —
clúdaíonn an [rang teagaisc](tutorial.md) agus an [treoir](guide.md) an
ghnáthúsáid. Tá an leathanach seo do lucht scríofa uirlisí: tá an coinbhinsiún
a chuireann an leabharlann i bhfeidhm scríofa síos mar chonradh beag cobhsaí
ionas go bhféadfadh cur i bhfeidhm eile — eastóscóir, IDE, seiceálaí
cineálacha, nó `pygettext` amach anseo — é a spriocdhíriú agus idir-inoibriú.
Chun na rialacha céanna a fheiceáil mínithe lena gcúiseanna, agus conas a
chuireann an cur i bhfeidhm tagartha i gcrích iad, léigh
[Conas a oibríonn sé](internals.md) ar dtús.

[Léigh sonraíocht v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Na rialacha ar aon scáileán { #the-rules-in-one-screen }

Is é **msgid** comhcheangal, in ord na foinse, na mírean litriúla agus
comhartha `{name}` amháin in aghaidh gach idirshuímh. Éalaítear lúibíní
litriúla (éiríonn `{{` as `{`). Caithfidh ainm a bheith ina ainm shealbhóra
ionaid shimplí — tá `str.isidentifier()` fíor agus ní eochairfhocal Python é.
**Ní cuid** den msgid iad tiontuithe ná sonruithe formáide; fanann siad faoi
smacht an fheidhmchláir.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *diúltaithe — ní ainm simplí é* |

Tá **aistriúchán** bailí nuair nach bhfuil ann ach sealbhóirí ionaid loma
`{name}`, nuair a bhíonn gach ainm riachtanach le feiceáil uair amháin ar a
laghad, agus nuair nach mbíonn aon ainm lasmuigh den tacar ceadaithe le
feiceáil. Tá an t-athordú agus an t-athdhéanamh gan srian d'aon ghnó: is féidir
leis an dá cheann a bheith riachtanach ó thaobh na gramadaí de i sprioctheanga.

I gcás iolraí, is é *ceadaithe* aontas ainmneacha na mbrainsí agus is é
*riachtanach* a dtrasnú — mar sin fágann `t"One file"` i gcoinne
`t"{n} files"` `n` ar fáil d'aistritheoir ceachtar foirme ach gan é a bheith
riachtanach do cheachtar acu, agus is féidir le rialacha iolra na
sprioctheanga bheith difriúil le rialacha na foinse.

**Ní lorgaítear msgid folamh** riamh, mar go gcoinníonn gettext é do
cheanntásc meiteashonraí catalóige.

## Comhréireacht { #conformance }

Is é
[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
an doiciméad céanna i bhfoirm atá inléite ag meaisín: cásanna a mhapálann
struchtúr statach t-string go msgid, agus msgid móide patrún catalóige go
teaghrán rindreáilte nó go diúltú.

**Comhlíonann cur i bhfeidhm sonraíocht v1** nuair a atáirgeann sé gach cás.
Ní ainmníonn na cásanna ach an méid a shainíonn an tsonraíocht — msgids
díorthaithe, patrúin a nglactar leo agus a ndiúltaítear dóibh, aschur
rindreáilte — agus ní ainmníonn siad riamh teachtaireacht earráide ná cineál
eisceachta, mar sin is féidir le cur i bhfeidhm i dteanga eile iad a rith gan
athrú.

Déantar cur síos struchtúrtha ar idirshuímh, riamh mar fhoinse Python:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Ritheann an cur i bhfeidhm tagartha an tsraith mar chuid dá shraith tástála
féin, mar sin ní féidir leis an bprós agus leis an gcód imeacht óna chéile ina
dtost.

## Leaganú { #versioning }

Is é seo sonraíocht v1. Ardaíonn athrú nach bhfuil comhoiriúnach siar ar
dhíorthú msgid nó ar bhailíochtú aistriúcháin an leagan agus seolann sé
`conformance/vN.json` nua taobh leis an gceann atá ann cheana. Ní ardaíonn
soiléirithe breise nach n-athraíonn msgids díorthaithe ná patrúin a nglactar
leo é.
