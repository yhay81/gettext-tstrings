---
description: "Y contract dalwyr lle i bwy bynnag sy'n golygu'r ffeiliau .po: beth y cewch ei newid, beth y mae'n rhaid i chi ei adael llonydd, a sut i ddarllen y gwallau."
---

# I gyfieithwyr

Mae'r dudalen hon ar gyfer y person sy'n golygu'r catalog, nid y person sy'n
ysgrifennu'r cod. Mae'n fyr yn fwriadol, a'i bwriad yw cael ei chysylltu neu ei
chopïo i mewn i gyfarwyddiadau cyfieithwyr prosiect ei hun.

Nid oes dim yma'n gofyn i chi ddarllen Python. Mae popeth yma'n ymwneud ag un
peth: darnau neges sydd mewn bracedi cyrliog.

## Beth yw daliwr lle { #what-a-placeholder-is }

Caiff neges mewn catalog gynnwys enwau mewn bracedi cyrliog:

```po
msgid "Hello {name}"
msgstr ""
```

**Daliwr lle** yw `{name}`. Pan fydd y rhaglen yn dangos y neges hon mae'n rhoi
gwerth y mae'n ei gyflenwi yn lle `{name}` — enw person, enw ffeil, rhif. Nid
gair i'w gyfieithu yw'r daliwr lle; slot ydyw.

Mae eich cyfieithiad yn mynd yn y `msgstr`, ac mae'n rhaid iddo gadw'r slot
hwnnw:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Beth y cewch ei newid, a beth na chewch { #what-you-may-change-and-what-you-may-not }

**Cewch**:

- **Symud daliwr lle** i ble bynnag y mae gramadeg yr iaith darged ei eisiau,
  gan gynnwys i flaen y neges.
- **Ailadrodd daliwr lle** os oes angen y gwerth ddwywaith ar yr iaith.
- **Ailysgrifennu pob gair arall**, gan gynnwys atalnodi, bylchu, a threfn y
  frawddeg.

**Ni chewch**:

- **Gyfieithu'r enw y tu mewn i'r bracedi.** Mae `{name}` yn aros yn `{name}`,
  hyd yn oed mewn iaith nad yw'n ysgrifennu dim byd arall mewn llythrennau
  Lladin.
- **Tynnu'r bracedi**, nac ysgrifennu'r enw hebddynt.
- **Rhoi `｛` `｝` lled-llawn yn lle'r bracedi ASCII `{` `}`.** Mae llawer o
  ddulliau mewnbwn yn cynhyrchu'r ffurfiau lled-llawn; maent yn edrych bron yn
  union yr un fath ac nid ydynt yn gweithio.
- **Ychwanegu fformatio**, megis `{name!r}` neu `{amount:.2f}`. Penderfynir sut
  y dangosir gwerth yn y rhaglen, nid yn y catalog.
- **Dyfeisio daliwr lle** nad yw yn y `msgid`.

Os oes angen gwerth ar neges nad yw'r gwreiddiol yn ei gynnig, mae honno'n neges
y mae'n rhaid i'r datblygwr ei newid. Dywedwch hynny yn hytrach na gweithio o'i
hamgylch.

## Ffurfiau lluosog { #plural-forms }

Mae neges a gyfrifir yn cyrraedd ag un slot `msgstr` fesul ffurf luosog yn eich
iaith, a'ch iaith chi sy'n penderfynu faint yw hynny — un i Japaneg, dwy i
Almaeneg, tair i Rwseg, chwech i Arabeg. Llenwch bob slot y mae'r catalog yn ei
roi i chi.

Dwy reol sy'n dal pobl allan:

- **Nid "unigol, lluosog, mwy lluosog" yw'r slotiau.** Mae pob mynegai'n golygu
  beth bynnag y mae rheol luosog eich iaith yn dweud ei fod yn ei olygu. Mae
  trydedd ffurf Latfieg ar gyfer sero'n unig; mae ail ffurf Slofeneg ar gyfer
  dau'n union; mae'r Gymraeg yn rhoi'r achos cyffredinol ym mynegai 0 a'r unigol
  ym mynegai 1.
- **Caiff dau slot yn gyfreithlon ddal yr un testun.** Mewn Twrceg, Hwngareg,
  Perseg a Bengaleg mae enw'n aros yn unigol ar ôl rhifolyn, felly mae dwy ffurf
  neges a gyfrifir yr un llinyn. Mae hynny'n gywir, nid yn llithriad copïo a
  gludo.

Mae'r rheolau dalwyr lle uchod yn berthnasol i bob ffurf yn annibynnol.

## Cofnodion fuzzy { #fuzzy-entries }

Dyfaliad peiriant yw cofnod wedi'i farcio'n `fuzzy`: newidiodd y datblygwr y
neges wreiddiol, a pharodd yr offer y testun newydd â'ch hen gyfieithiad fel bod
gennych rywle i gychwyn.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

**Nid yw'r rhaglen yn defnyddio** cofnod fuzzy — mae'n dangos y gwreiddiol heb
ei gyfieithu yn ei le — hyd nes y bydd rhywun yn diwygio'r testun ac yn tynnu'r
marciwr `fuzzy`. Mae gan y rhan fwyaf o olygyddion PO fotwm ar gyfer yr union
beth hwnnw.

## Darllen neges fethiant { #reading-a-failure-message }

Mae'r offer yn gwirio dalwyr lle pan grynhoir y catalog, ac ysgrifennwyd y neges
ar eich cyfer chi yn hytrach nag ar gyfer rhaglennydd. Mae adrodd yn unig fod
`{name}` ar goll yn ben ffordd pan allwch weld yr union nodau hynny o'ch blaen,
felly lle mae daliwr lle'n edrych yn bresennol ond nad ydyw, mae'r neges yn
dweud pam. Yn erbyn y gwreiddiol `Hello {name}`, adroddir pob un o'r rhain dan
`translation does not match the source placeholders:`

| Yr hyn y mae eich cyfieithiad yn ei ddweud | Y rheswm y mae'n ei roi |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Mae nodau na ellir eu gweld yn cael eu trin ar wahân. Mae bwlch di-dor y tu mewn
i'r bracedi'n rhywbeth y mae dull mewnbwn yn ei gynhyrchu ac nad oes yr un
golygydd yn ei ddangos, felly mae'r neges yn ei argraffu wrth ei bwynt cod yn
hytrach nag enwi nod na fyddech byth yn gallu dod o hyd iddo:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Dangosir enw y mae ei lythrennau'n cymysgu systemau ysgrifennu — yr achos
homoglyff, lle mae `а` Cyrilig yn anwahanadwy oddi wrth un Lladin — ddwywaith,
unwaith yn ddarllenadwy ac unwaith wedi'i ddianc, sef yr unig ffurf sy'n
gwahaniaethu rhwng y ddau:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Mae'r un gwahaniaethu'n berthnasol pan fo enw Groeg neu Gyrilig a ysgrifennwyd
yn gyfan gwbl mewn un sgript yn gwrthdaro ag enw ffynhonnell ASCII, gan gynnwys
achos yr un llythyren `a` Lladin / `а` Cyrilig.

Os dewch ar draws un o'r rhain ac nad yw'r ateb yn amlwg, y symudiad diogel yw
dileu'r daliwr lle a deipiwyd gennych a chopïo'r un o'r `msgid`.

## Yr hyn na all y gwiriadau ei wneud { #what-the-checks-cannot-do }

Mae'r offer yn gwirio bod eich dalwyr lle'n gyfan. Ni all ddweud a yw'r
cyfieithiad yn gywir, yn naturiol, nac yn iawn i'r cyd-destun — mae hynny'n aros
yn gyfan gwbl gyda chi.

Mae dau beth yn helpu mwy nag unrhyw wiriad:

- **Darllenwch sylw'r cyfieithydd.** Mae llinell sy'n dechrau â `#.` uwchben y
  neges yn ddatblygwr yn dweud wrthych ble mae'n ymddangos a beth y mae'n ei
  olygu.
- **Gofynnwch am `msgctxt`.** Pan fo'r un gair yn ymddangos ddwywaith â
  chyd-destunau gwahanol, mae hynny am fod angen i'r ddau gyfieithu'n wahanol —
  "Open" y botwm ac "Open" y cyflwr, er enghraifft.
