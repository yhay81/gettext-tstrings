---
description: "Trisdešimt metų gettext, du PEP'ai su dešimties metų tarpu ir standartinės bibliotekos diskusija, uždaryta kaip „not planned“ — kodėl ši biblioteka egzistuoja, su nuorodomis į šaltinius."
---

# Ištakos

Ši biblioteka stovi dviejų ilgų istorijų susitikimo taške — vienos apie tai,
kaip verčiama programinė įranga, kitos apie tai, kaip Python interpoliuoja
eilutes — kurios pagaliau susikirto 2025 m. ir tada sustojo lygiai toje
vietoje, kur reikėjo mažo, kruopštaus susitarimo. Šis puslapis pasakoja abi
istorijas su nuorodomis į šaltinius, nes šioje svetainėje priimtus sprendimus
lengviau vertinti, kai matai klausimus, į kuriuos jie atsako.

## Gettext ekosistema { #the-gettext-ecosystem }

[GNU gettext] nuo dešimtojo dešimtmečio vidurio yra būdas, kuriuo verčiama
laisvoji programinė įranga: pažymėk eilutes kode, ištrauk jas į šabloną,
duok vertėjams po vieną katalogo failą kiekvienai kalbai, sukompiliuok, įkelk
veikimo metu. Aplink tą ciklą išaugo visa ekosistema — PO redaktoriai,
peržiūros darbo eigos ir vertimo platformos, visos kalbančios tuo pačiu failų
formatu — o Python savo standartinėje bibliotekoje
[`gettext` modulį][stdlib-gettext] tiekia jau daugiau nei du dešimtmečius.
Vertimo vykdymo pusė niekada nebuvo problema.

Neišspręsta visada liko pusė, *kaip atrodo katalogo eilutė*. `%(name)s`
pranešimas paduoda vertėjams printf sintaksę, kurią viena ištrinta raidė
paverčia lūžiu produkcijoje; `.format()` pranešimas paduoda katalogui prieigą
prie gyvų objektų atributų. ([Kodėl t-eilutės](comparison.md) abu pereina, su
gedimais ant stalo.) O f-eilutės — sintaksė, kurią dabar labiausiai mėgsta
Python kodas — negali dalyvauti apskritai: kol jas pamato bet kuri biblioteka,
jos jau yra baigtos eilutės. Vis tiek bandoma — pakankamai dažnai, kad Babel
klaidų sekiklis kauptų tuos bandymus ([#594][babel-594], [#715][babel-715]);
gedimas yra struktūrinis, o ne trūkstama savybė.

## Du PEP'ai su dešimties metų tarpu { #two-peps-ten-years-apart }

2015 m. Alyssa Coghlan ir Nick Humrich parašė [PEP 501], siūlantį
interpoliacijos šablonus, kurių pirmoji nurodyta motyvacija buvo i18n —
„providing a cleaner syntax for i18n translation“, paties PEP'o žodžiais.
Pasiūlymas buvo atidėtas, iš dalies todėl, kad diskusija parodė, jog i18n
atvejis neša reikšmingų papildomų svarstymų, kurių paprastesni panaudojimo
atvejai neturi.

Po dešimtmečio [PEP 750] — Jim Baker, Guido van Rossum, Paul Everitt, Koudai
Aono, Lysandros Nikolaou ir Dave Peck — atgaivino idėją kaip t-eilutes, buvo
[priimtas 2025 m. balandį][sc-resolution] ir 2025 m. spalį pateko į
[Python 3.14]. PEP 501 tada buvo atsiimtas jo naudai. Vienas dalykas šiam
puslapiui svarbus: i18n *nėra* tarp PEP 750 nurodytų motyvacijų. PEP'as
apibendrino mechanizmą — šablono tipą, kurį gali vartoti bet kuri biblioteka —
ir paliko vertimo klausimą lygiai ten, kur PEP 501 jį buvo pastatęs dešimt metų
anksčiau: atvirą.

Taigi nuo Python 3.14 kalba turėjo būtent tokią duomenų struktūrą, kokios reikia
pranešimų katalogui, ir jokio susitarimo, kaip ja naudotis.

## Standartinės bibliotekos diskusija { #the-stdlib-discussion }

Likus dviem mėnesiams iki 3.14 išleidimo, Adrian Mönnich (ThiefMaster, Indico
projekto prižiūrėtojas) pasiūlė tą spragą užpildyti pačioje standartinėje
bibliotekoje: gija [Support t-strings in gettext][discuss-thread]
svetainėje discuss.python.org, atverta 2025 m. rugpjūtį, atėjo su veikiančiu
[pull request'u][cpython-pr], pridedančiu t-eilučių palaikymą tiek `gettext`,
tiek `pygettext`.

Giją verta perskaityti visą, nes joje iškyla visi sunkūs klausimai, į kuriuos
šiai bibliotekai vėliau teko atsakyti:

- **Kas gali būti interpoliacija?** Vien paprastas vardas, ar atributai ir
  iškvietimai su išvestiniu vietaženklio vardu? Kiekvienas atsakymas keičia
  patogumą į msgid stabilumą ir katalogo saugumą.
- **Ko reikalauja daugiskaitos formos,** kai tikslinės kalbos daugiskaitos
  sistema skiriasi nuo pirminės?
- **Ar gettext apskritai yra tinkamas taikinys?** Barry Warsaw — kuris PEP 750
  kūrimo metu buvo teigęs, kad t-eilutės i18n netinka — nurodė savo
  [`flufl.i18n`][flufl-i18n] ir jo `$` eilučių stilių kaip draugiškesnį
  įrankį; kiti siūlė gettext apskritai palikti ir pereiti prie naujesnių
  sistemų, tokių kaip [Fluent].
- **Ir metaklausimas:** ką bepatiektų standartinė biblioteka, to iš esmės
  niekada nebegalima pakeisti. Susitarimas su tiek atvirų pasirinkimų yra
  rizikingas dalykas užšaldyti iš pirmo karto.

Bendro sutarimo nesusidarė. CPython klausimas buvo
[uždarytas kaip „not planned“][cpython-issue], o pull request'as uždarytas
nesulietas 2025 m. spalį, kelios dienos po 3.14 išleidimo. Galimybė kalboje
egzistavo; susitarimas namų neturėjo.

## Kodėl pirmiau paketas { #why-a-package-first }

Būtent tą spragą šis projektas pasirinko užpildyti iš už standartinės
bibliotekos ribų, sąmoningai lažindamasis: susitarimas bręsta greičiau ten, kur
gali laisvai versijuotis ir pelnyti pritaikymą po vieną atvejį, o standartinė
biblioteka — kuri privalo būti teisi iš pirmo karto — yra ten, kur susitarimas
turėtų *atsidurti*, o ne ten, kur jis turėtų būti išrūšiuotas.

Konkrečiai: kiekvienas gijoje ginčytas klausimas čia turi surašytą atsakymą,
kiekvienas savo puslapyje:

- Interpoliacijos yra **tik paprasti vardai**, todėl msgid'ai išlieka stabilūs
  ir prasmingi — [vadovas](guide.md#safety-and-scope) parodo taisyklę,
  [Kaip tai veikia](internals.md#from-template-to-msgid) — priežastis.
- **Formatavimas visiškai lieka už katalogo ribų**
  ([Kodėl t-eilutės](comparison.md)).
- **Daugiskaita** paklūsta sąjungos/sankirtos taisyklei, leidžiančiai tikslinės
  kalbos daugiskaitos sistemai skirtis nuo pirminės ([spec §4](spec.md)).
- Sugadintas katalogas **grįžta atgal, o ne lūžta**, išlaikydamas paties
  gettext kontraktą ([vadovas](guide.md#what-happens-when-a-catalog-is-wrong)).
- O visas susitarimas yra [versijuota specifikacija](spec.md) su mašininiu būdu
  skaitomu atitikties rinkiniu — parašyta taip, kad kita realizacija, įskaitant
  būsimą standartinės bibliotekos, galėtų ją perimti nepakeistą ir sąveikauti.

Diskusija nesibaigė, o šis projektas yra jos dalyvis, o ne nuosprendis joje.
Jei turite produkcinės gettext patirties, susijusios su šiais pasirinkimais,
[ta pati gija][discuss-thread] ir šios saugyklos
[Discussions][gh-discussions] yra ten, kur apie tai ginčijamasi.

## Laiko juosta { #timeline }

| Kada | Kas nutiko |
| --- | --- |
| XX a. 10-ojo deš. vidurys | GNU gettext įtvirtina PO/POT/MO darbo eigą, kuria vertėjai ir platformos kalba iki šiol. |
| 2015 | [PEP 501] siūlo interpoliacijos šablonus, kurių pirmoji motyvacija — i18n; atidėtas. |
| 2016 | F-eilutės pasirodo Python 3.6 — interpoliacija gauna savo sintaksę, o vertimas ja pasinaudoti negali. |
| 2024 m. liepa | [PEP 750] siūlo t-eilutes. |
| 2025 m. balandis | PEP 750 [priimtas][sc-resolution]; PEP 501 atsiimtas jo naudai. |
| 2025 m. rugpjūtis | Atsiveria gija [Support t-strings in gettext][discuss-thread] su standartinės bibliotekos [pull request'u][cpython-pr]. |
| 2025 m. spalis | [Python 3.14] pateikia t-eilutes; standartinės bibliotekos klausimas uždaromas kaip [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` pasirodo kaip alfa su [spec v1](spec.md) ir jos atitikties rinkiniu. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
