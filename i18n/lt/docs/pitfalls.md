---
description: "Ką iš tikrųjų sulaužo vienos nedidelės svetainės vertimas į trisdešimt penkias kalbas, ką iš to biblioteka gali pagauti už jus, o ko — ne."
---

# Spąstai

Ši svetainė išversta į trisdešimt penkias kalbas, ir kiekvienas jos leidimas
gimė sukant tą patį ciklą, kurio moko ši dokumentacija. Pagal pramonės
mastelius tai nedidelis rinkinys, ir vis tiek jo pakako, kad įkliūtume į
daugumą spąstų, dėl kurių i18n yra sunkiau, nei atrodo.

Kiekvienas žemiau esantis skyrius — tai kažkas, kas čia iš tikrųjų nepavyko:
kaip tai atrodė tuo metu ir kur eina riba tarp to, ką biblioteka patikrina už
jus, ir to, kas lieka jūsų nuožiūrai.

## Kintamojo pervadinimas iš naujo verčia sakinį { #renaming-a-variable-retranslates-a-sentence }

msgid yra katalogo raktas, o interpoliuotas vardas yra *jo viduje*. Perkėlus
vieną konstantą į modulio lygmenį ir užrašius ją didžiosiomis, kaip prašo
Python stilius — `author` į `AUTHOR` — `Copyright © 2026 {author} · MIT License`
virto pranešimu, kurio nė vienas katalogas nebuvo matęs. Kiekvienas tos
eilutės vertimas būtų grįžęs per fuzzy ciklą, visomis kalbomis, dėl
pervadinimo, kuris skaitytojui nepakeitė nieko.

Biblioteka jūsų nesustabdys: abi rašybos yra galiojantys vietaženklių vardai.
Ką ji padaro — tai paverčia vardą *vertu* saugojimo: interpoliacija privalo
būti [paprastas vardas](internals.md#from-template-to-msgid), tad katalogo
rakte glūdi žodis, kurį vertėjas gali perskaityti, o ne išraiška.

Veidrodinis atvejis saugus jau pagal sandarą. Konversijos ir formato aprašai į
msgid nepatenka, todėl `{amount:,.2f}` sugriežtinimas iki `{amount:,.0f}`
nekeičia jokio rakto ir niekur nepanaikina jokio vertimo.

## `nplurals=2` nereiškia dviejų skirtingų eilučių { #nplurals-2-does-not-mean-two-different-strings }

Turkų, vengrų, persų ir bengalų kalbos skelbia po dvi daugiskaitos formas, ir
visose keturiose abi skaičiuojamo pranešimo formos teisėtai yra *ta pati
eilutė* — daiktavardis po skaitvardžio lieka vienaskaitos, tad `{n} sayfa`
tinka ir vienam puslapiui, ir dešimčiai. Peržiūrėtojas, „ištaisantis“ tą
dvigubinimą, sulaužo vertimą.

Priešinga klaida ne mažiau lengva. Latvių trečioji forma skirta **vien tik
nuliui**; slovėnų antroji yra **dviskaita**, lygiai dviem; rumunų paskutinei
formai būtinas žodis `de`, kurio pirmosios dvi neturi turėti. Užpildžius tas
vietas vienaskaita ir daugiskaita gaunamas katalogas, klaidingas tik tiems
skaičiams, kurių niekas netikrina.

Blogiau — vietų *tvarka* nėra prasminė. Valų kalba savo penkias formas
indeksuoja taip, kad `msgstr[0]` yra bendrasis atvejis, o `msgstr[1]` —
vienaskaita. Užpildžius jas akivaizdžia seka, vienaskaita atsiduria ten, kur ją
ras kiekvienas neskaičiuojamas pranešimas.

Biblioteka nieko iš viso to neprisiima, ir tai yra esmė: tikslinės kalbos
daugiskaitos taisyklė gyvena jos pačios katalogo antraštėje, o
[sąjungos ir sankirtos taisyklė](spec.md) leidžia vertimui turėti daugiau
formų nei pirminis tekstas arba mažiau. Ji tikrina vienintelį dalyką, kurį
galima patikrinti nemokant kalbos — kad kiekviena forma išlaikytų jai
reikalingus vietaženklius.

## Dvi formos gali sutapti neatsitiktinai { #two-forms-can-be-identical-for-a-reason }

Airių kalba turi penkias daugiskaitos formas, ir šios svetainės kūrimo
ataskaitoje kelios jų rašomos vienodai. Tai ne kopijavimo apsirikimas:
*leathanach* prasideda `l`, o nė viena iš pradinių mutacijų, kurias sukelia
airiški skaitvardžiai, ties `l` nerašoma. Formos vis tiek dirba tikrą darbą —
kamienas kaitaliojasi tarp *leathanach* ir *leathanaigh*, o skaičiai virš
dešimties grįžta prie vienaskaitos — bet joks „puslapį“ reiškiantis
daiktavardis to skirtumo neparodytų.

Bet kuri patikra, laikanti pasikartojančias formas įtartinomis, pažymės
teisingą airių kalbą. Vienintelis šio dalyko recenzentas — žmogus, mokantis tą
kalbą.

## Pranešimas gali derėti tik su vienu skaičiumi { #a-message-can-only-agree-with-one-count }

Šios svetainės kūrimo ataskaita nurodo, kiek puslapių atvaizduota ir kiek tai
truko. Užrašius ją kaip „Rendered {n} pages in {seconds} seconds“, atrodo
nekaltai, o išversti neįmanoma: gettext parenka vieną formą pagal vieną
skaičių, ir tas skaičius yra `n`. Žodis *seconds* turėtų derėti su skaičiumi,
kurio daugiskaitos mechanizmas niekada nemato.

Sprendimas — antrąjį dydį pateikti ne žodžiu, o mato vieneto simboliu; patys
vienetų simboliai irgi lokalizuojami: šios svetainės kataloguose yra `s`, `с`,
`ث`, `שנ׳` ir `mp`, o prancūzų, ispanų ir švedų tipografija prieš simbolį nori
tarpo, kurio anglų kalba nededa. Nieko iš to biblioteka netvarko — bet
pastebėti, kad pranešimui reikia *dviejų* derinimų, jau taip, o vienintelis
įrankis tam yra parašyti pranešimą kitaip.

## Angliško sakinio taisymas taiso svetimą gramatiką { #editing-an-english-sentence-edits-foreign-grammar }

Pradiniame puslapyje anksčiau buvo parašyta „all ten language editions“.
Pašalinus skaičių — vieno žodžio angliška pataisa, padaryta todėl, kad skaičius
vis pasensdavo — daugiskaitinis veiksnys tapo vienaskaitinis. Ispanų, italų,
portugalų, rusų, ukrainiečių, graikų, olandų ir hebrajų leidimams teko iš naujo
derinti veiksmažodį; keliuose reikėjo pakeisti ir dalyvį.

Pirminio teksto pataisa, angliškai atrodanti menkutė, tolesnėje grandinėje
menkutė nėra. Pažymėjimas fuzzy, kurį atlieka `pybabel update`, yra tas
mechanizmas, kuris kiekvienam vertėjui suteikia progą tai pastebėti.

## Nematomi skirtumai išgyvena bet kokį kopijavimą { #invisible-differences-survive-every-copy-paste }

Vadove cituojama diagnostika, kurioje yra `(nаme)` — sąmoninga kaitos seka, nes
joje įvardytas rašmuo yra kirilicos `а`, kurios joks skaitytojas neatskirs nuo
lotyniškos. Šios svetainės vertėjai tą seką pavertė tikruoju rašmeniu **penkis
atskirus kartus**, penkiomis skirtingomis kalbomis, kaskart pagamindami
puslapį, kuris atrodė teisingas ir buvo klaidingas.

Šitą biblioteka pagauna, ir būtent dėl to diagnostikos yra tokios formos,
kokios yra: vietaženklis, kurio raidės maišo rašto sistemas,
[pranešamas dukart](internals.md#diagnostics-are-part-of-the-design) — kartą
skaitomai, kartą ekranuotai — nes ekranuota forma yra vienintelis užrašymas,
kuris juos atskiria. Nedalus tarpas riestiniuose skliaustuose dėl tos pačios
priežasties spausdinamas kodo pozicija. Katalogo tikrintuvas pranešimą atmeta
dar prieš jam išplaukiant pas naudotoją.

## Netuščia nereiškia išversta { #non-empty-is-not-translated }

Katalogas, kurio karkasas sudarytas nukopijavus msgid į msgstr, praeina
kiekvieną naivią patikrą: niekas nėra tuščia, niekas nepažymėta fuzzy,
pranešimų aibė sutampa tiksliai. Vienas šios svetainės leidimas taip gyveno
kelias valandas. Taip pat ir aštuoni kito leidimo puslapiai, buvę baitas į
baitą tapačios angliško šaltinio kopijos — o tokie praeina ir patikrą,
lyginančią jų kodo blokus, nes tai tas pats failas.

Nė vieno iš šių dalykų vertimo biblioteka matyti negali. Abu pigu patikrinti,
kai tik apie tai pagalvoji: palygink su pirminiu tekstu ir reikalauk skirtumo.

## Katalogas — ne vienintelis verčiamas dalykas { #the-catalog-is-not-the-only-translated-thing }

Dvi čia įvykusios nesėkmės su gettext neturėjo nieko bendra.

Išvertus antraštę, pasikeičia iš jos sugeneruotas inkaras, tad kiekviena
nuoroda iš kito puslapio į tą skyrių nutrūksta — tyliai ir tik toje kalboje.
Ši svetainė kiekvienoje antraštėje prisega anglišką inkarą, o testas laukiamą
sąrašą išveda iš angliško puslapio.

O svetainės generatorius pateikia sąsajos vertimus šešiasdešimt aštuoniomis
kalbomis, tarp kurių nėra nei suahilių, nei airių. Jo neturint, kūrimas
nenusileidžia iki anglų kalbos: šablono įtraukimas nepavyksta ir leidimo
apskritai sukurti neįmanoma. Būtent tai spragai užpildyti egzistuoja du šios
saugyklos failai.

## Jūsų įrankiai irgi turi klaidų { #your-tools-have-bugs-too }

CI žingsnis, kurį ši dokumentacija rekomenduoja pasenusiems katalogams gaudyti,
`pybabel update --check`, to darbo negali atlikti jokiam projektui,
naudojančiam `pgettext` ar `npgettext` — kiekvieną katalogą su `msgctxt` jis
kiekvieną kartą praneša kaip pasenusį dėl klaidos tame, kaip palyginimas ieško
pranešimų. Ji rasta būtent čia, bandant tuo pasinaudoti, pranešta autoriams ir
[aprašyta išsamiai kartu su apėjimu](workflow.md#what-ci-gates).

Bendra pamoka nemaloni: visada raudoni vartai yra blogiau nei jokių vartų, nes
komanda juos išjungia. Įsitikinkite, kad jūsų CI patikra iš tikrųjų gali būti
praeita, prieš pasikliaudami tuo, kad ji jus sustabdys.

## Kam skirta biblioteka, vienu sakiniu { #what-the-library-is-for-in-one-line }

Didžioji šio puslapio dalis yra nuožiūra, kurios joks įrankis neperims. Ką
įrankis *gali* — tai užtikrinti, kad vertimas negalėtų pakeisti verčiamo
sakinio sandaros: negalėtų numesti reikšmės, jos išgalvoti, performatuoti ar
siekti į jūsų objektus — ir pasakyti tai sakiniu, pagal kurį taisyti turintis
žmogus gali imtis veiksmų. Tai ir yra viskas, ką ši biblioteka žada, o visa
likusi svetainė — kaip ji tą pažadą laiko.
