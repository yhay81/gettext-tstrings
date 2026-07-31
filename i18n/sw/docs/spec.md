---
description: "Makubaliano ya t-string kwenda msgid kama mkataba mdogo wenye matoleo, pamoja na seti ya utiifu inayosomeka na mashine."
---

# Ainisho

Unaweza kutumia maktaba hii bila kusoma ukurasa huu — [mafunzo](tutorial.md) na
[mwongozo](guide.md) hufunika matumizi ya kila siku. Ukurasa huu ni kwa ajili
ya waandishi wa zana: makubaliano ambayo maktaba huyatekeleza yameandikwa kama
mkataba mdogo na thabiti ili utekelezaji mwingine — kitoaji, IDE, kikaguzi cha
aina, au `pygettext` ya siku zijazo — uweze kuyalenga na kushirikiana. Kwa
kanuni zilezile zikielezwa pamoja na sababu zake, na jinsi utekelezaji wa
marejeo unavyozitekeleza, soma [Jinsi inavyofanya kazi](internals.md) kwanza.

[Soma ainisho v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Kanuni katika skrini moja { #the-rules-in-one-screen }

**msgid** ni muunganiko, kwa mpangilio wa chanzo, wa vipande halisi pamoja na
alama moja ya `{name}` kwa kila kiingizio. Mabano halisi hukwepeshwa (`{` huwa
`{{`). Jina lazima liwe jina rahisi la kishika nafasi — `str.isidentifier()` ni
kweli nalo si neno la msingi la Python. Ubadilishaji na maainisho ya umbizo
**si** sehemu ya msgid; hubaki chini ya udhibiti wa programu.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *imekataliwa — si jina rahisi* |

**Tafsiri** ni halali inapokuwa na vishika nafasi vya `{name}` tupu pekee, kila
jina linalohitajika linaonekana angalau mara moja, na hakuna jina lililo nje ya
seti inayoruhusiwa linaloonekana. Kupanga upya na kurudia hakuna vizuizi kwa
makusudi: vyote viwili vinaweza kuwa vya lazima kisarufi katika lugha lengwa.

Kwa wingi, *kinachoruhusiwa* ni muungano wa majina ya matawi nacho
*kinachohitajika* ni mwingiliano wao — hivyo `t"One file"` dhidi ya
`t"{n} files"` huacha `n` ikipatikana kwa mfasiri wa umbo lolote lakini
haihitajiki katika lolote, na kanuni za wingi za lugha lengwa zinaweza
kutofautiana na za chanzo.

**msgid tupu** haitafutwi kamwe, kwa sababu gettext huihifadhi kwa kichwa cha
metadata cha katalogi.

## Utiifu { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
ni hati ileile katika umbo linalosomeka na mashine: kesi zinazoramanisha muundo
tuli wa t-string kwenda msgid, na msgid pamoja na muundo wa katalogi kwenda
mfuatano ulioonyeshwa au kukataliwa.

Utekelezaji **hutii ainisho v1** unapozalisha tena kila kesi. Kesi hutaja tu
kile ainisho hulibainisha — msgid zilizotokezwa, miundo iliyokubaliwa na
iliyokataliwa, matokeo yaliyoonyeshwa — na kamwe si ujumbe wa hitilafu au aina
ya hitilafu, hivyo utekelezaji katika lugha nyingine unaweza kuziendesha bila
kuzibadilisha.

Viingizio huelezwa kimuundo, kamwe si kama msimbo chanzo wa Python:

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

Utekelezaji wa marejeo huendesha seti hiyo kama sehemu ya seti yake ya
majaribio, hivyo maandishi na msimbo haviwezi kutengana kimyakimya.

## Utoaji wa matoleo { #versioning }

Hili ni ainisho v1. Mabadiliko yasiyooana na ya nyuma katika utokezaji wa msgid
au katika uthibitishaji wa tafsiri huongeza toleo na husafirisha
`conformance/vN.json` mpya kando ya iliyopo. Ufafanuzi wa nyongeza usiobadilisha
wala msgid zilizotokezwa wala miundo inayokubaliwa haufanyi hivyo.
