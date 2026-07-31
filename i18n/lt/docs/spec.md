---
description: "T-eilutės ir msgid susitarimas kaip mažas versijuotas kontraktas su mašininiu būdu skaitomu atitikties rinkiniu."
---

# Specifikacija

Šią biblioteką galite naudoti ir neskaitę šio puslapio — kasdienį naudojimą
dengia [pamoka](tutorial.md) ir [vadovas](guide.md). Šis puslapis skirtas
įrankių autoriams: bibliotekos įgyvendinamas susitarimas surašytas kaip mažas,
stabilus kontraktas, kad į jį galėtų taikytis ir su juo sąveikauti kita
realizacija — ištraukiklis, IDE, tipų tikrintuvas ar būsimas `pygettext`. Kad
gautumėte tas pačias taisykles su jų priežastimis ir su tuo, kaip jas vykdo
etaloninė realizacija, pirma perskaitykite
[Kaip tai veikia](internals.md).

[Skaityti spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Taisyklės viename ekrane { #the-rules-in-one-screen }

**Msgid** yra literalių segmentų ir po vieną `{name}` leksemą kiekvienai
interpoliacijai sujungimas pirminio kodo tvarka. Literalūs riestiniai
skliaustai ekranuojami (`{` tampa `{{`). Vardas privalo būti paprastas
vietaženklio vardas — `str.isidentifier()` yra teisingas ir jis nėra Python
raktažodis. Konversijos ir formato specifikacijos **nėra** msgid dalis; jos
lieka programos kontrolėje.

| t-eilutė | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *atmesta — ne paprastas vardas* |

**Vertimas** galioja tada, kai jame yra tik pliki `{name}` vietaženkliai,
kiekvienas privalomas vardas pasitaiko bent kartą ir nepasitaiko nė vienas
vardas už leidžiamos aibės ribų. Perstatymas ir kartojimas tyčia neribojami:
abu tiksline kalba gali būti gramatiškai būtini.

Daugiskaitai *leidžiama* yra šakų vardų sąjunga, o *privaloma* — jų sankirta,
todėl `t"One file"` prieš `t"{n} files"` palieka `n` prieinamą bet kurios formos
vertėjui, bet nė vienoje neprivalomą, o tikslinės kalbos daugiskaitos taisyklės
gali skirtis nuo pirminės.

**Tuščio msgid** niekada neieškoma, nes gettext jį rezervavo katalogo
metaduomenų antraštei.

## Atitiktis { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
yra tas pats dokumentas mašininiu būdu skaitoma forma: atvejai, susiejantys
t-eilutės statinę struktūrą su msgid, ir msgid kartu su katalogo šablonu su
atvaizduota eilute arba atmetimu.

Realizacija **atitinka spec v1**, kai atkuria kiekvieną atvejį. Atvejai
įvardija tik tai, ką apibrėžia specifikacija — išvestinius msgid'us, priimtus
ir atmestus šablonus, atvaizduotą išvestį — ir niekada nei klaidos pranešimo,
nei išimties tipo, todėl realizacija kita kalba gali juos paleisti nepakeistus.

Interpoliacijos aprašomos struktūriškai, niekada kaip Python pirminis kodas:

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

Etaloninė realizacija paleidžia šį rinkinį kaip savo pačios testų rinkinio
dalį, todėl tekstas ir kodas negali tyliai išsiskirti.

## Versijavimas { #versioning }

Tai yra spec v1. Atgal nesuderinamas msgid išvedimo ar vertimo tikrinimo
pakeitimas padidina versiją ir pateikia naują `conformance/vN.json` šalia jau
esamo. Papildomi patikslinimai, nekeičiantys nei išvestinių msgid'ų, nei
priimamų šablonų, versijos nedidina.
