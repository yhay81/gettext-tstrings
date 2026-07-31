---
description: "Ko patiesībā salauž vienas nelielas vietnes tulkošana trīsdesmit piecās valodās, ko no tā bibliotēka spēj noķert jūsu vietā un ko nespēj."
---

# Slazdi

Šī vietne ir iztulkota trīsdesmit piecās valodās, un katrs no izdevumiem tapis,
izpildot to pašu ciklu, ko māca šī dokumentācija. Nozares mērogā tas ir neliels
korpuss, un ar to tik un tā pietika, lai ietriektos gandrīz visos slazdos, kuru
dēļ i18n ir grūtāka, nekā izskatās.

Katra turpmākā sadaļa ir kaut kas, kas šeit tiešām nogāja greizi, tas, kā tas
toreiz izskatījās, un vieta, kur iet robeža starp to, ko bibliotēka pārbauda
jūsu vietā, un to, kas paliek jūsu spriedums.

## Mainīgā pārsaukšana pārtulko teikumu no jauna { #renaming-a-variable-retranslates-a-sentence }

msgid ir kataloga atslēga, un interpolētais nosaukums ir *tajā iekšā*. Vienas
konstantes pārcelšana uz moduļa līmeni un tās uzrakstīšana ar lielajiem
burtiem, kā prasa Python stils — `author` uz `AUTHOR` —, pārvērta
`Copyright © 2026 {author} · MIT License` par ziņojumu, kādu neviens katalogs
nekad nebija redzējis. Katrs šīs rindas tulkojums būtu devies atpakaļ caur
fuzzy ciklu, katrā valodā, pārsaukuma dēļ, kas nemainīja neko lasītājam
redzamu.

Bibliotēka jūs neapturēs: abas rakstības ir derīgi viettura nosaukumi. Ko tā
tiešām dara — tā padara nosaukumu *vērtu* sargāšanas: interpolācijai ir jābūt
[vienkāršam nosaukumam](internals.md#from-template-to-msgid), tāpēc tas, kas
nonāk kataloga atslēgā, ir vārds, ko tulkotājs var izlasīt, nevis izteiksme.

Spoguļgadījums ir drošs jau pēc uzbūves. Konversijas un formāta specifikācijas
nav msgid daļa, tāpēc `{amount:,.2f}` savilkšana līdz `{amount:,.0f}` nemaina
nevienu atslēgu un nepadara nederīgu nevienu tulkojumu nekur.

## `nplurals=2` nenozīmē divas dažādas virknes { #nplurals-2-does-not-mean-two-different-strings }

Turku, ungāru, persiešu un bengāļu valoda — visas deklarē divas daudzskaitļa
formas, un visās četrās skaitāma ziņojuma abas formas likumīgi ir *viena un tā
pati virkne*: lietvārds aiz skaitļa vārda paliek vienskaitlī, tāpēc
`{n} sayfa` der gan vienai lappusei, gan desmit. Recenzents, kurš “izlabo” šo
dublēšanos, salauž tulkojumu.

Pretējā kļūda ir tikpat viegla. Latviešu valodas trešā forma pastāv **vienīgi
nullei**; slovēņu valodas otrā ir **duālis**, tieši diviem; rumāņu valodas
pēdējai formai ir vajadzīgs vārds `de`, kura pirmajās divās nedrīkst būt. Šo
slotu aizpildīšana ar vienskaitli un daudzskaitli rada katalogu, kas ir
nepareizs tikai tiem skaitļiem, kurus neviens netestē.

Vēl ļaunāk — slotu *secība* nav semantiska. Velsiešu valoda savas piecas formas
indeksē tā, ka `msgstr[0]` ir vispārīgais gadījums un `msgstr[1]` —
vienskaitlis. To aizpildīšana acīmredzamajā secībā noliek vienskaitli tur, kur
to atradīs katrs neskaitāmais ziņojums.

Bibliotēka neko no tā neuzņemas uz sevi, un tieši tāda ir doma: mērķa valodas
daudzskaitļa likums mīt paša kataloga galvenē, un
[apvienojuma/šķēluma likums](spec.md) ļauj tulkojumam būt ar vairāk vai mazāk
formām nekā avotam. Tā pārbauda vienīgo, ko var pārbaudīt, valodu nezinot — ka
katra forma patur tai vajadzīgos vietturus.

## Divas formas var būt identiskas ar iemeslu { #two-forms-can-be-identical-for-a-reason }

Īru valodā ir piecas daudzskaitļa formas, un šīs vietnes būvējuma atskaitē
vairākas no tām ir uzrakstītas vienādi. Tā nav kopēšanas kļūda: *leathanach*
sākas ar `l`, un neviena no abām sākuma mutācijām, ko izraisa īru skaitļa
vārdi, uz `l` netiek rakstīta. Formas joprojām dara īstu darbu — celms mijas
starp *leathanach* un *leathanaigh*, un skaitļi virs desmit atgriežas pie
vienskaitļa —, bet neviens lietvārds ar nozīmi “lappuse” šo pretstatu
neparādītu.

Jebkura pārbaude, kas dublētas formas atzīmē kā aizdomīgas, atzīmēs pareizu īru
valodu. Vienīgais recenzents šim ir cilvēks, kurš valodu zina.

## Ziņojums var saskaņoties tikai ar vienu skaitu { #a-message-can-only-agree-with-one-count }

Šīs vietnes būvējuma atskaite pasaka, cik lappuses tika renderētas un cik ilgi
tas prasīja. Uzrakstīt to kā “Rendered {n} pages in {seconds} seconds” izskatās
nekaitīgi un nav iztulkojami: gettext izvēlas vienu formu pēc viena skaita, un
šis skaits ir `n`. Vārdam *seconds* būtu jāsaskaņojas ar skaitli, kuru
daudzskaitļa mehānisms nekad neierauga.

Risinājums ir padarīt otro lielumu par vienības simbolu, nevis vārdu, un
vienības simboli paši ir lokalizējami: šīs vietnes katalogi nes `s`, `с`, `ث`,
`שנ׳` un `mp`, un franču, spāņu un zviedru tipogrāfija grib atstarpi pirms
simbola tur, kur angļu valoda to negrib. Nekas no tā nav bibliotēkas darīšana —
bet pamanīt, ka ziņojumam vajadzīgas *divas* saskaņošanas, gan ir, un vienīgais
rīks tam ir uzrakstīt ziņojumu citādi.

## Angļu teikuma rediģēšana rediģē svešu gramatiku { #editing-an-english-sentence-edits-foreign-grammar }

Sākumlapā kādreiz bija rakstīts “all ten language editions”. Skaitļa
noņemšana — viena vārda rediģējums angļu valodā, izdarīts tāpēc, ka skaitlis
arvien novecoja — pārvērta daudzskaitļa teikuma priekšmetu vienskaitlīgā.
Spāņu, itāļu, portugāļu, krievu, ukraiņu, grieķu, nīderlandiešu un ebreju
valodā visās nācās no jauna saskaņot darbības vārdu; vairākās bija jāmaina arī
divdabis.

Avota rediģējums, kas angliski lasās kā nenozīmīgs, lejtecē nav nenozīmīgs. Tā
atzīmēšana par fuzzy — tieši to dara `pybabel update` — ir mehānisms, kas dod
katram tulkotājam iespēju to pamanīt.

## Neredzamas atšķirības pārdzīvo jebkuru kopēšanu { #invisible-differences-survive-every-copy-paste }

Ceļvedis citē diagnostiku, kurā ir `(nаme)` — apzināta atsoļošana, jo
rakstzīme, ko tā nosauc, ir kirilicas `а`, kuru neviens lasītājs neatšķirs no
latīņu burta. Šīs vietnes tulkotāji šo atsoļojumu pārvērta par īsto rakstzīmi
**piecas atsevišķas reizes**, piecās dažādās valodās, katru reizi radot lapu,
kas izskatījās pareiza un bija nepareiza.

Šo bibliotēka gan noķer, un tieši tāpēc diagnostikas ziņojumiem ir tāda forma,
kāda tiem ir: vietturis, kura burti sajauc rakstības sistēmas, tiek
[paziņots divreiz](internals.md#diagnostics-are-part-of-the-design) — vienreiz
lasāmi un vienreiz atsoļots —, jo atsoļotā forma ir vienīgais pieraksts, kas
tos izšķir. Nedalāmā atstarpe figūriekavās tiek izdrukāta pēc koda punkta tā
paša iemesla dēļ. Kataloga pārbaudītājs ziņojumu noraida, pirms tas paspēj
nonākt piegādē.

## Netukšs nav iztulkots { #non-empty-is-not-translated }

Katalogs, kas uzstatīts, tā msgid vērtības iekopējot msgstr laukos, iztur katru
naivu pārbaudi: nekas nav tukšs, nekas nav fuzzy, ziņojumu kopa sakrīt precīzi.
Viens šīs vietnes izdevums vairākas stundas bija piegādāts tieši tāds. Tāpat arī
astoņas cita izdevuma lapas, kas bija baitu pa baitam identiskas angļu avota
kopijas — kas iztur pārbaudi, kura salīdzina koda blokus starp tām, jo tas ir
viens un tas pats fails.

Neviena no tām nav kaut kas, ko tulkošanas bibliotēka spēj ieraudzīt. Abas ir
lēti pārbaudāmas, taču ne, pieprasot, lai katrs ieraksts atšķirtos no sava
avota: `OK`, produktu nosaukumi, personvārdi, akronīmi un koda identifikatori
visi tulkojas paši par sevi, un pārbaude, kas to aizliedz, mūžīgi ražo viltus
trauksmes.

Mēriet labāk *īpatsvaru* — pa visu katalogu vai pa visu lapu — un sūtiet
novirzes cilvēkam. Šīs vietnes paša tests dara tieši to: tas salīdzina katra
izdevuma prozas rindas ar angļu avotu un krīt virs 25% identisku. Viltotais
izdevums bija 87%; katrs īsts tulkojums ir starp 4% un 8%, kas ir tā nelielā
aste, kurā rindas sakrīt likumīgi, piemēram, URL un citēta programmas izvade.
Abas kopas ir pietiekami tālu viena no otras, lai slieksnim nebūtu jābūt
precīzam.

## Katalogs nav vienīgā iztulkotā lieta { #the-catalog-is-not-the-only-translated-thing }

Divām šejienes kļūmēm ar gettext nebija nekāda sakara.

Virsraksta iztulkošana maina no tā ģenerēto enkuru, tāpēc katra starplapu saite
uz šo sadaļu salūzt — klusējot un tikai šajā valodā. Šī vietne piesprauž angļu
enkuru katram virsrakstam, un tests atvasina gaidāmo sarakstu no angļu lapas.

Un vietnes ģenerators piegādā saskarnes tulkojumus sešdesmit astoņām valodām,
kuru vidū nav ne svahili, ne īru valodas. Bez tāda tulkojuma būvējums
neatkāpjas uz angļu valodu; šablona iekļāve neizdodas, un izdevumu vispār nav
iespējams uzbūvēt. Divi šī repozitorija paša faili pastāv, lai aizpildītu šo
robu.

## Arī jūsu rīkiem ir kļūdas { #your-tools-have-bugs-too }

CI solis, ko šī dokumentācija iesaka novecojušu katalogu noķeršanai,
`pybabel update --check`, šo darbu nespēj paveikt nevienam projektam, kas lieto
`pgettext` vai `npgettext`. Babel 2.18.0 versijā tas katrā izpildē ziņo, ka
katrs katalogs ar `msgctxt` ir novecojis. Salīdzināšana notiek caur
`Catalog.is_identical`, kas katru ziņojumu uzmeklē pēc atslēgas, ar kādu tas ir
saglabāts — un kontekstuālam ziņojumam šī atslēga ir pāris `(id, context)`, ko
`Catalog.get` nepieņem. Uzmeklēšana neatgriež neko, un katalogi nekad nav
vienādi:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Tā tika atrasta šeit, mēģinot to lietot, paziņota augšup, un aizstājošā
pārbaude ir [produkcijas lapā](workflow.md#what-ci-gates).

Vispārīgā mācība ir tā neērtā: vārti, kas vienmēr ir sarkani, ir sliktāki nekā
nekādi vārti, jo komanda tos izslēdz. Pārliecinieties, ka jūsu CI pārbaude
tiešām spēj iziet cauri, pirms uzticaties tam, ka tā kritīs.

## Kam bibliotēka ir domāta, vienā rindā { #what-the-library-is-for-in-one-line }

Lielākā daļa šīs lapas ir spriedums, ko neviens rīks nevar pārņemt. Ko rīks
*var*, ir garantēt, ka tulkojums nespēj mainīt tā teikuma struktūru, kuru tas
tulko — nespēj nomest vērtību, izdomāt jaunu, pārformatēt to vai ielīst jūsu
objektos —, un pateikt to teikumā, pēc kura cilvēks, kuram tas jālabo, var
rīkoties. Tas ir viss, ko šī bibliotēka sola, un pārējā vietne ir tas, kā tā to
tur.
