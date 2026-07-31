---
description: "Konvencija t-virkne → msgid kā mazs versionēts kontrakts ar mašīnlasāmu atbilstības komplektu."
---

# Specifikācija

Šo bibliotēku varat lietot, šo lapu nemaz nelasot — ikdienas lietojumu sedz
[pamācība](tutorial.md) un [ceļvedis](guide.md). Šī lapa ir rīku autoriem:
konvencija, ko bibliotēka implementē, ir pierakstīta kā mazs, stabils
kontrakts, lai to varētu mērķēt un ar to savietoties cita implementācija —
ekstraktors, IDE, tipu pārbaudītājs vai nākotnes `pygettext`. Ja gribat tos
pašus likumus izskaidrotus kopā ar to iemesliem un to, kā tos izpilda atsauces
implementācija, vispirms izlasiet [Kā tas darbojas](internals.md).

[Lasīt spec. v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Likumi vienā ekrānā { #the-rules-in-one-screen }

**Msgid** ir literālo segmentu un pa vienam `{name}` tokenam katrai
interpolācijai savienojums avota secībā. Literālas figūriekavas tiek atsoļotas
(`{` kļūst par `{{`). Nosaukumam jābūt vienkāršam viettura nosaukumam —
`str.isidentifier()` ir patiess, un tas nav Python atslēgvārds. Konversijas un
formāta specifikācijas **nav** msgid daļa; tās paliek lietotnes kontrolē.

| t-virkne | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *noraidīts — nav vienkāršs nosaukums* |

**Tulkojums** ir derīgs, ja tas satur tikai kailus `{name}` vietturus, katrs
obligātais nosaukums parādās vismaz vienreiz un neparādās neviens nosaukums
ārpus atļautās kopas. Pārkārtošana un atkārtošana ir apzināti neierobežota:
abas mērķa valodā var būt gramatiski nepieciešamas.

Daudzskaitļiem *atļauts* ir zaru nosaukumu apvienojums un *obligāts* ir to
šķēlums — tāpēc `t"One file"` pret `t"{n} files"` atstāj `n` pieejamu jebkuras
formas tulkotājam, bet neprasa to nevienā, un mērķa valodas daudzskaitļa likumi
drīkst atšķirties no avota valodas likumiem.

**Tukša msgid** nekad netiek meklēta, jo gettext to rezervē kataloga metadatu
galvenei.

## Atbilstība { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
ir tas pats dokuments mašīnlasāmā formā: gadījumi, kas attēlo t-virknes
statisko struktūru uz msgid, un msgid plus kataloga rakstu uz renderētu virkni
vai noraidījumu.

Implementācija **atbilst spec. v1**, kad tā atveido katru gadījumu. Gadījumi
nosauc tikai to, ko specifikācija definē — atvasinātas msgid, pieņemtus un
noraidītus rakstus, renderētu izvadi — un nekad ne kļūdas ziņojumu vai izņēmuma
tipu, tāpēc implementācija citā valodā var tos palaist nemainītus.

Interpolācijas ir aprakstītas strukturāli, nekad kā Python pirmkods:

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

Atsauces implementācija palaiž komplektu kā daļu no savas testu kopas, tāpēc
proza un kods nevar klusējot aizvirzīties viens no otra.

## Versionēšana { #versioning }

Šī ir spec. v1. Atpakaļnesavietojama izmaiņa msgid atvasināšanā vai tulkojumu
validācijā palielina versiju un nāk ar jaunu `conformance/vN.json` blakus
esošajam. Papildinoši precizējumi, kas nemaina ne atvasinātās msgid, ne
pieņemtos rakstus, to nedara.
