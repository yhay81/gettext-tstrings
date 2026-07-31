---
description: "Staðgengilssáttmálinn fyrir þann sem ritstýrir .po-skránum: hverju þú mátt breyta, hverju þú verður að láta ósnert og hvernig á að lesa villurnar."
---

# Fyrir þýðendur

Þessi síða er ætluð þeim sem ritstýrir þýðingaskránni, ekki þeim sem skrifar
kóðann. Hún er stutt af ásettu ráði og henni er ætlað að vera tengd í eða
afrituð inn í eigin þýðendaleiðbeiningar verkefnis.

Ekkert hér krefst þess að þú lesir Python. Allt hér snýst um eitt: bútana í
skilaboðum sem standa innan slaufusviga.

## Hvað staðgengill er { #what-a-placeholder-is }

Skilaboð í þýðingaskrá mega innihalda nöfn innan slaufusviga:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` er **staðgengill**. Þegar forritið birtir þessi skilaboð skiptir það
`{name}` út fyrir gildi sem það leggur til — nafn manneskju, skráarnafn, tölu.
Staðgengillinn er ekki orð til að þýða; hann er hólf.

Þýðingin þín fer í `msgstr` og hún verður að halda því hólfi:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Hverju þú mátt breyta og hverju ekki { #what-you-may-change-and-what-you-may-not }

Þú **mátt**:

- **Færa staðgengil** hvert sem málfræði markmálsins vill hafa hann, þar á
  meðal fremst í skilaboðin.
- **Endurtaka staðgengil** ef tungumálið þarf gildið tvisvar.
- **Umskrifa hvert annað orð**, þar með talið greinarmerki, bil og
  setningaskipan.

Þú **mátt ekki**:

- **Þýða nafnið innan slaufusviganna.** `{name}` er áfram `{name}`, jafnvel í
  tungumáli sem skrifar ekkert annað með latínuletri.
- **Fjarlægja slaufusvigana** eða skrifa nafnið án þeirra.
- **Skipta ASCII-slaufusvigunum `{` `}` út fyrir breiðu `｛` `｝`.** Margar
  innsláttaraðferðir framleiða breiðu myndirnar; þær líta næstum eins út og
  virka ekki.
- **Bæta við sniði**, svo sem `{name!r}` eða `{amount:.2f}`. Hvernig gildi er
  birt er ákveðið í forritinu, ekki í þýðingaskránni.
- **Finna upp staðgengil** sem er ekki í `msgid`.

Þarfnist skilaboð gildis sem frumtextinn býður ekki upp á eru það skilaboð sem
þróandinn verður að breyta. Segðu frá því fremur en að fara í kringum það.

## Fleirtölumyndir { #plural-forms }

Skilaboð sem telja berast með einu `msgstr`-hólfi fyrir hverja fleirtölumynd í
tungumálinu þínu, og tungumálið þitt ræður hversu margar þær eru — ein fyrir
japönsku, tvær fyrir þýsku, þrjár fyrir rússnesku, sex fyrir arabísku. Fylltu í
hvert hólf sem þýðingaskráin gefur þér.

Tvær reglur sem koma fólki í opna skjöldu:

- **Hólfin eru ekki „eintala, fleirtala, meiri fleirtala“.** Hvert sætisnúmer
  merkir það sem fleirtölureglan í þínu tungumáli segir að það merki. Þriðja
  mynd lettnesku er eingöngu fyrir núll; önnur mynd slóvensku er fyrir nákvæmlega
  tvö; velska setur almenna tilvikið í sæti 0 og eintöluna í sæti 1.
- **Tvö hólf mega með réttu geyma sama textann.** Í tyrknesku, ungversku,
  persnesku og bengölsku stendur nafnorð áfram í eintölu á eftir töluorði, svo
  báðar myndir skilaboða sem telja eru sami strengurinn. Það er rétt, ekki
  afrita-og-líma-mistök.

Staðgengilsreglurnar hér að ofan gilda um hverja mynd fyrir sig.

## Óskýrar færslur { #fuzzy-entries }

Færsla sem merkt er `fuzzy` er ágiskun vélar: þróandinn breytti upprunalegu
skilaboðunum og tólin pöruðu nýja textann við gömlu þýðinguna þína svo að þú
hefðir einhvern stað til að byrja á.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Óskýr færsla er **ekki notuð af forritinu** — það sýnir óþýdda frumtextann í
staðinn — fyrr en einhver endurskoðar textann og fjarlægir `fuzzy`-merkið.
Flestir PO-ritlar eru með hnapp fyrir einmitt það.

## Að lesa villuskilaboð { #reading-a-failure-message }

Tólin athuga staðgengla þegar þýðingaskráin er vistþýdd og skilaboðin eru
skrifuð fyrir þig fremur en fyrir forritara. Að tilkynna eingöngu að `{name}`
vanti er blindgata þegar þú sérð þessa stafi fyrir framan þig, svo þar sem
staðgengill sýnist vera til staðar en er það ekki segja skilaboðin hvers vegna.
Gagnvart frumtextanum `Hello {name}` er hvert eftirfarandi tilkynnt undir
`translation does not match the source placeholders:`

| Þýðingin þín segir | Ástæðan sem hún gefur |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Stafir sem ekki sjást fá sína eigin meðferð. Óskiptanlegt bil innan
slaufusviganna er eitthvað sem innsláttaraðferð framleiðir og enginn ritill
sýnir, svo skilaboðin prenta það eftir kóðapunkti fremur en að nefna staf sem
þú gætir aldrei fundið:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nafn þar sem stafirnir blanda saman ritkerfum — samstæðutilvikið, þar sem
kýrillískt `а` er óaðgreinanlegt frá latnesku — er sýnt tvisvar, einu sinni
læsilega og einu sinni með escape-ritun, sem er eina myndin sem greinir þau tvö
að:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Sama aðgreining gildir þegar grískt eða kýrillískt nafn, skrifað alfarið í einu
ritkerfi, stangast á við ASCII-nafn í frumtextanum, þar á meðal tilvikið með
eins stafs latnesku `a` og kýrillísku `а`.

Rekist þú á eitthvert þessara og lagfæringin er ekki augljós er öruggasta
leiðin að eyða staðgenglinum sem þú slóst inn og afrita þann úr `msgid`.

## Hvað athuganirnar geta ekki gert { #what-the-checks-cannot-do }

Tólin staðfesta að staðgenglarnir þínir séu heilir. Þau geta ekki sagt til um
hvort þýðingin sé nákvæm, eðlileg eða rétt fyrir samhengið — það hvílir alfarið
á þér.

Tvennt hjálpar meira en nokkur athugun:

- **Lestu athugasemd þýðanda.** Lína sem hefst á `#.` fyrir ofan skilaboðin er
  þróandinn að segja þér hvar þau birtast og hvað þau merkja.
- **Spurðu um `msgctxt`.** Þegar sama orðið birtist tvisvar með ólíku samhengi
  er það vegna þess að þau tvö þurfa að þýðast ólíkt — „Opna“ hnappurinn og
  „Opið“ ástandið, svo dæmi sé tekið.
