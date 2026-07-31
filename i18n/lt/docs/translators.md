---
description: "Vietaženklių susitarimas tam, kas redaguoja .po failus: ką galite keisti, ką privalote palikti ramybėje ir kaip skaityti klaidas."
---

# Vertėjams

Šis puslapis skirtas tam, kas redaguoja katalogą, o ne tam, kas rašo kodą. Jis
tyčia trumpas ir skirtas būti pridedamas nuoroda arba nukopijuojamas į projekto
paties vertėjų instrukcijas.

Niekas čia nereikalauja mokėti skaityti Python. Visa čia yra apie vieną dalyką:
pranešimo gabalus riestiniuose skliaustuose.

## Kas yra vietaženklis { #what-a-placeholder-is }

Katalogo pranešime gali būti vardų riestiniuose skliaustuose:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` yra **vietaženklis**. Rodydama šį pranešimą programa pakeičia `{name}`
savo pateikiama reikšme — žmogaus vardu, failo vardu, skaičiumi. Vietaženklis
nėra verstinas žodis; tai lizdas.

Jūsų vertimas rašomas į `msgstr` ir privalo tą lizdą išlaikyti:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Ką galite keisti, o ko ne { #what-you-may-change-and-what-you-may-not }

**Galite**:

- **Perkelti vietaženklį** ten, kur jo nori tikslinės kalbos gramatika —
  įskaitant pranešimo pradžią.
- **Pakartoti vietaženklį**, jei kalbai reikšmės reikia du kartus.
- **Perrašyti kiekvieną kitą žodį**, taip pat skyrybą, tarpus ir sakinio tvarką.

**Negalite**:

- **Versti vardo skliaustų viduje.** `{name}` lieka `{name}` net ir kalboje,
  kuri daugiau nieko nerašo lotyniškomis raidėmis.
- **Šalinti skliaustų** ar rašyti vardą be jų.
- **Keisti ASCII skliaustų `{` `}` viso pločio `｛` `｝`.** Daugelis įvesties
  metodų pagamina viso pločio formas; jos atrodo beveik vienodai ir neveikia.
- **Pridėti formatavimo**, tokio kaip `{name!r}` ar `{amount:.2f}`. Kaip
  reikšmė rodoma, sprendžiama programoje, o ne kataloge.
- **Sugalvoti vietaženklio**, kurio nėra `msgid`.

Jei pranešimui reikia reikšmės, kurios originalas nesiūlo, tai pranešimas, kurį
turi pakeisti programuotojas. Pasakykite tai, o ne ieškokite apėjimo.

## Daugiskaitos formos { #plural-forms }

Skaičiuojamas pranešimas ateina su po vieną `msgstr` lizdu kiekvienai jūsų
kalbos daugiskaitos formai, o kiek jų yra, sprendžia jūsų kalba — vienas
japonų, du vokiečių, trys rusų, šeši arabų. Užpildykite kiekvieną katalogo
duodamą lizdą.

Dvi taisyklės, ant kurių žmonės klumpa:

- **Lizdai nėra „vienaskaita, daugiskaita, dar daugiau“.** Kiekvienas indeksas
  reiškia tai, ką sako jūsų kalbos daugiskaitos taisyklė. Latvių trečioji forma
  skirta vien nuliui; slovėnų antroji — lygiai dviem; valų kalba bendrąjį atvejį
  deda į 0 indeksą, o vienaskaitą į 1.
- **Du lizdai visiškai teisėtai gali turėti tą patį tekstą.** Turkų, vengrų,
  persų ir bengalų kalbose daiktavardis po skaitvardžio lieka vienaskaitos,
  todėl abi skaičiuojamo pranešimo formos yra ta pati eilutė. Tai teisinga, o ne
  kopijavimo klaida.

Aukščiau esančios vietaženklių taisyklės kiekvienai formai taikomos atskirai.

## Fuzzy įrašai { #fuzzy-entries }

Žyma `fuzzy` pažymėtas įrašas yra mašinos spėjimas: programuotojas pakeitė
pirminį pranešimą, o įrankiai suporavo naują tekstą su jūsų senu vertimu, kad
turėtumėte nuo ko pradėti.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Fuzzy įrašo **programa nenaudoja** — vietoj jo ji rodo neišverstą originalą —
tol, kol kas nors teksto neperžiūri ir nenuima `fuzzy` žymos. Dauguma PO
redaktorių tam turi mygtuką.

## Kaip skaityti klaidos pranešimą { #reading-a-failure-message }

Įrankiai vietaženklius patikrina, kai katalogas kompiliuojamas, o pranešimas
parašytas jums, o ne programuotojui. Pranešti vien, kad `{name}` trūksta, yra
aklavietė, kai matote tuos simbolius prieš save, todėl ten, kur vietaženklis
atrodo esantis, bet jo nėra, pranešimas pasako kodėl. Prieš originalą
`Hello {name}` kiekvienas iš šių atvejų pranešamas po antrašte
`translation does not match the source placeholders:`

| Jūsų vertime parašyta | Nurodoma priežastis |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (skliaustai aplink jį nėra ASCII `{` ir `}`) |
| `こんにちは {{name}}` | `{name}` is missing (parašyta `{{name}}`, o taip užrašomas literalus riestinis skliaustas) |
| `こんにちは name` | `{name}` is missing (vardas yra, bet ne skliaustuose) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Simboliai, kurių pamatyti neįmanoma, sulaukia atskiro elgesio. Nedalus tarpas
skliaustų viduje yra tai, ką pagamina įvesties metodas ir ko neparodo joks
redaktorius, todėl pranešimas jį išspausdina kodo pozicija, užuot įvardijęs
simbolį, kurio niekaip nerastumėte:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Vardas, kurio raidės maišo skirtingas rašto sistemas — homoglifų atvejis, kai
kirilicos `а` neatskiriama nuo lotyniškos — parodomas dukart: kartą skaitomai,
kartą su kaitos sekomis, nes tik ši forma leidžia jas atskirti:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Tas pats atskyrimas taikomas, kai graikiškas ar kirilinis vardas, parašytas
ištisai viena rašto sistema, konfliktuoja su ASCII pirminiu vardu — įskaitant
vienos raidės atvejį: lotyniška `a` prieš kirilinę `а`.

Jei susidūrėte su vienu iš šių atvejų ir taisymas nėra akivaizdus, saugiausia
ištrinti savo įvestą vietaženklį ir nukopijuoti tą, kuris yra `msgid`.

## Ko patikros negali { #what-the-checks-cannot-do }

Įrankiai patikrina, ar jūsų vietaženkliai nepažeisti. Jie negali pasakyti, ar
vertimas tikslus, natūralus ar tinkamas kontekstui — tai lieka vien jums.

Du dalykai padeda labiau nei bet kuri patikra:

- **Perskaitykite vertėjo komentarą.** Eilutė, prasidedanti `#.` virš
  pranešimo, yra programuotojo žinutė jums, kur pranešimas pasirodo ir ką jis
  reiškia.
- **Klauskite apie `msgctxt`.** Kai tas pats žodis pasitaiko dukart su
  skirtingais kontekstais, taip yra todėl, kad juos reikia išversti skirtingai —
  pavyzdžiui, „Open“ mygtukas ir „Open“ būsena.
