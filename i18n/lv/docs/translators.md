---
description: "Vietturu kontrakts tam, kurš rediģē .po failus: ko drīkstat mainīt, ko jāatstāj mierā un kā lasīt kļūdas."
---

# Tulkotājiem

Šī lapa ir domāta cilvēkam, kurš rediģē katalogu, nevis tam, kurš raksta kodu.
Tā ir apzināti īsa, un tā ir domāta, lai uz to saitētu vai to iekopētu projekta
paša norādēs tulkotājiem.

Nekas šeit neprasa lasīt Python. Viss šeit ir par vienu lietu: par ziņojuma
gabaliem figūriekavās.

## Kas ir vietturis { #what-a-placeholder-is }

Ziņojums katalogā drīkst saturēt nosaukumus figūriekavās:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` ir **vietturis**. Kad programma šo ziņojumu parāda, tā `{name}`
aizstāj ar vērtību, ko pati piegādā, — cilvēka vārdu, faila nosaukumu, skaitli.
Vietturis nav tulkojams vārds; tā ir vieta.

Jūsu tulkojums nonāk `msgstr`, un tam šī vieta jāsaglabā:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Ko drīkstat mainīt un ko ne { #what-you-may-change-and-what-you-may-not }

Jūs **drīkstat**:

- **Pārvietot vietturi** jebkur, kur to grib mērķa valodas gramatika, arī uz
  ziņojuma sākumu.
- **Atkārtot vietturi**, ja valodai vērtība vajadzīga divreiz.
- **Pārrakstīt katru citu vārdu**, arī pieturzīmes, atstarpes un teikuma
  secību.

Jūs **nedrīkstat**:

- **Tulkot nosaukumu figūriekavās.** `{name}` paliek `{name}` arī valodā, kas
  neko citu neraksta ar latīņu burtiem.
- **Noņemt figūriekavas** vai rakstīt nosaukumu bez tām.
- **Aizstāt ASCII figūriekavas `{` `}` ar pilnplatuma `｛` `｝`.** Daudzas
  ievades metodes rada pilnplatuma formas; tās izskatās gandrīz identiskas un
  nedarbojas.
- **Pievienot formatējumu**, tādu kā `{name!r}` vai `{amount:.2f}`. To, kā
  vērtība tiek attēlota, izlemj programmā, nevis katalogā.
- **Izdomāt vietturi**, kura nav `msgid`.

Ja ziņojumam vajadzīga vērtība, ko oriģināls nepiedāvā, tas ir ziņojums, kas
jāmaina izstrādātājam. Pasakiet to, nevis mēģiniet to apiet.

## Daudzskaitļa formas { #plural-forms }

Skaitāms ziņojums pienāk ar vienu `msgstr` vietu katrai jūsu valodas
daudzskaitļa formai, un cik to ir, izlemj jūsu valoda — viena japāņu, divas
vācu, trīs krievu, sešas arābu valodā. Aizpildiet katru vietu, ko katalogs jums
dod.

Divi noteikumi, kas cilvēkus pārsteidz:

- **Vietas nav “vienskaitlis, daudzskaitlis, vēl vairāk daudzskaitlis”.** Katrs
  indekss nozīmē to, ko saka jūsu valodas daudzskaitļa likums. Latviešu trešā
  forma ir domāta vienīgi nullei; slovēņu otrā — tieši diviem; velsiešu valodā
  vispārīgais gadījums ir indeksā 0, bet vienskaitlis — indeksā 1.
- **Divas vietas pamatoti drīkst saturēt vienu un to pašu tekstu.** Turku,
  ungāru, persiešu un bengāļu valodā lietvārds pēc skaitļa vārda paliek
  vienskaitlī, tāpēc abas skaitāma ziņojuma formas ir viena un tā pati virkne.
  Tas ir pareizi, nevis pārkopēšanas kļūda.

Augšminētie vietturu noteikumi attiecas uz katru formu atsevišķi.

## Fuzzy ieraksti { #fuzzy-entries }

Ieraksts, kas atzīmēts kā `fuzzy`, ir mašīnas minējums: izstrādātājs nomainīja
sākotnējo ziņojumu, un rīki sapāroja jauno tekstu ar jūsu veco tulkojumu, lai
jums būtu, no kā sākt.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Fuzzy ierakstu **programma nelieto** — tā vietā tā parāda neiztulkoto
oriģinālu —, līdz kāds tekstu pārstrādā un `fuzzy` marķieri noņem. Lielākajai
daļai PO redaktoru tieši tam ir poga.

## Kā lasīt kļūmes ziņojumu { #reading-a-failure-message }

Rīki pārbauda vietturus, kad katalogs tiek kompilēts, un ziņojums ir rakstīts
jums, nevis programmētājam. Ziņot tikai to, ka `{name}` trūkst, ir strupceļš,
ja jūs šīs rakstzīmes redzat sev priekšā, tāpēc tur, kur vietturis izskatās
klāt esošs, bet nav, ziņojums pasaka, kāpēc. Pret oriģinālu `Hello {name}`
katrs no šiem tiek ziņots zem
`translation does not match the source placeholders:`

| Jūsu tulkojumā rakstīts | Norādītais iemesls |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (figūriekavas ap to nav ASCII `{` un `}`) |
| `こんにちは {{name}}` | `{name}` is missing (tas rakstīts kā `{{name}}`, un tā tiek atsoļota literāla figūriekava) |
| `こんにちは name` | `{name}` is missing (nosaukums parādās, bet ne figūriekavās) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Rakstzīmes, kas nav redzamas, saņem savu apstrādi. Nedalāmā atstarpe
figūriekavās ir tas, ko rada ievades metode un ko neviens redaktors neparāda,
tāpēc ziņojums to izdrukā pēc koda punkta, nevis nosauc rakstzīmi, ko jūs nekad
nespētu atrast:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nosaukums, kura burti sajauc rakstības sistēmas — homoglifu gadījums, kad
kirilicas `а` nav atšķirama no latīņu burta —, tiek parādīts divreiz: vienreiz
lasāmi un vienreiz atsoļots, un tā ir vienīgā forma, kas abus izšķir:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Tā pati atšķiršana notiek, kad grieķu vai kirilicas nosaukums, kas pilnībā
rakstīts vienā rakstībā, konfliktē ar ASCII avota nosaukumu, arī viena burta
gadījumā ar latīņu `a` un kirilicas `а`.

Ja sastopat kādu no šiem un labojums nav acīmredzams, drošākais gājiens ir
nodzēst savu ierakstīto vietturi un pārkopēt to no `msgid`.

## Ko pārbaudes nespēj { #what-the-checks-cannot-do }

Rīki pārliecinās, ka jūsu vietturi ir neskarti. Tie nespēj pateikt, vai
tulkojums ir precīzs, dabisks vai kontekstam atbilstošs — tas pilnībā paliek
jūsu ziņā.

Divas lietas palīdz vairāk nekā jebkura pārbaude:

- **Izlasiet tulkotāja komentāru.** Rinda, kas sākas ar `#.` virs ziņojuma, ir
  izstrādātāja stāstījums par to, kur ziņojums parādās un ko tas nozīmē.
- **Pajautājiet par `msgctxt`.** Kad viens un tas pats vārds parādās divreiz ar
  dažādiem kontekstiem, tas ir tāpēc, ka abi jāiztulko atšķirīgi — piemēram,
  “Open” kā poga un “Open” kā stāvoklis.
