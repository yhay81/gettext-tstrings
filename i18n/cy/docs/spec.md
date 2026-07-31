---
description: "Y confensiwn llinyn-t i msgid fel contract bach â fersiwn, gyda chyfres gydymffurfio y gall peiriant ei darllen."
---

# Manyleb

Gallwch ddefnyddio'r llyfrgell hon heb ddarllen y dudalen hon — mae'r
[tiwtorial](tutorial.md) a'r [canllaw](guide.md) yn ymdrin â'r defnydd
beunyddiol. Ar gyfer awduron offer y mae'r dudalen hon: caiff y confensiwn y
mae'r llyfrgell yn ei weithredu ei ysgrifennu i lawr fel contract bach sefydlog
fel y gall gweithrediad arall — echdynnwr, IDE, gwiriwr mathau, neu `pygettext`
y dyfodol — anelu ato a rhyngweithredu. Am yr un rheolau wedi'u hesbonio â'u
rhesymau, a sut y mae'r gweithrediad cyfeirio yn eu cyflawni, darllenwch
[Sut mae'n gweithio](internals.md) yn gyntaf.

[Darllen manyleb v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Y rheolau ar un sgrin { #the-rules-in-one-screen }

**Msgid** yw cydgadwyniad, yn nhrefn y ffynhonnell, y segmentau llythrennol ac
un tocyn `{name}` fesul rhyngosodiad. Caiff bracedi llythrennol eu dyblu i
ddianc (`{` yn dod yn `{{`). Rhaid i enw fod yn enw daliwr lle syml — mae
`str.isidentifier()` yn wir ac nid yw'n allweddair Python. **Nid** yw
trawsnewidiadau a manylebau fformat yn rhan o'r msgid; maent yn aros dan
reolaeth y rhaglen.

| llinyn-t | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *gwrthodwyd — nid enw syml* |

Mae **cyfieithiad** yn ddilys pan nad yw'n cynnwys ond dalwyr lle `{name}`
noeth, pan fo pob enw gofynnol yn ymddangos o leiaf unwaith, ac nad oes enw
y tu allan i'r set a ganiateir yn ymddangos. Mae aildrefnu ac ailadrodd yn
fwriadol ddigyfyngiad: gall y ddau fod yn ramadegol angenrheidiol mewn iaith
darged.

Ar gyfer lluosogion, *a ganiateir* yw uniad enwau'r canghennau ac *a ofynnir*
yw eu croestoriad — felly mae `t"One file"` yn erbyn `t"{n} files"` yn gadael
`n` ar gael i gyfieithydd y naill ffurf neu'r llall ond heb ei fynnu gan yr un
ohonynt, a gall rheolau lluosog iaith darged fod yn wahanol i rai'r ffynhonnell.

Ni chwilir byth am **msgid gwag**, am fod gettext yn ei gadw ar gyfer pennyn
metadata catalog.

## Cydymffurfio { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
yw'r un ddogfen ar ffurf y gall peiriant ei darllen: achosion sy'n mapio
strwythur statig llinyn-t i msgid, a msgid ynghyd â phatrwm catalog i linyn
wedi'i rendro neu i wrthodiad.

Mae gweithrediad yn **cydymffurfio â manyleb v1** pan fo'n atgynhyrchu pob
achos. Nid yw'r achosion yn enwi ond yr hyn y mae'r fanyleb yn ei ddiffinio —
msgidiau deilliedig, patrymau a dderbynnir ac a wrthodir, allbwn wedi'i rendro
— a byth neges gwall na math eithriad, fel y gall gweithrediad mewn iaith arall
eu rhedeg heb eu newid.

Disgrifir rhyngosodiadau'n strwythurol, byth fel cod ffynhonnell Python:

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

**Nid** fersiwn manyleb yw'r maes `"spec"` — mae pob achos yn `v1.json` yn
perthyn i fanyleb v1. Mae'n enwi'r adran o `SPEC.md` y mae'r achos yn ei
harfer, felly darllenir `"2.2"` fel §2.2, y rheol ar gyfer deillio tocyn daliwr
lle.

Mae'r gweithrediad cyfeirio yn rhedeg y gyfres fel rhan o'i gyfres brofi ei
hun, fel na all y rhyddiaith a'r cod ymwahanu'n dawel.

## Fersiynu { #versioning }

Manyleb v1 yw hon. Mae newid sy'n anghydnaws yn ôl-weithredol i ddeilliad
msgid neu i ddilysu cyfieithiadau yn cynyddu'r fersiwn ac yn cludo
`conformance/vN.json` newydd ochr yn ochr â'r un sy'n bodoli. Nid yw eglurhad
ychwanegol nad yw'n newid na'r msgidiau deilliedig na'r patrymau a dderbynnir
yn gwneud hynny.
