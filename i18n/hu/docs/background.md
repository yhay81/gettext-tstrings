---
description: "Harminc év gettext, két PEP tíz év különbséggel, és a stdlib-vita, amely „not planned” jelzéssel zárult: miért létezik ez a könyvtár, forrásokkal."
---

# Háttér

Ez a könyvtár két hosszú történet találkozási pontján ül — az egyik arról
szól, hogyan fordítják le a szoftvereket, a másik arról, hogyan interpolál a
Python szövegeket —, amelyek 2025-ben végre metszették egymást, majd pontosan
ott akadtak el, ahol egy kicsi, gondos konvencióra lett volna szükség. Ez az
oldal mindkét történetet elmeséli, forráshivatkozásokkal, mert a webhelyen
szereplő tervezési döntéseket könnyebb megítélni, ha látod a kérdéseket,
amelyekre válaszolnak.

## A gettext ökoszisztémája { #the-gettext-ecosystem }

A [GNU gettext] az 1990-es évek közepe óta a szabad szoftverek fordításának
módja: jelöld meg a szövegeket a kódban, nyerd ki őket egy sablonba, adj a
fordítóknak nyelvenként egy katalógusfájlt, fordítsd binárisra, töltsd be
futásidőben. E ciklus köré egész ökoszisztéma nőtt — PO-szerkesztők,
felülvizsgálati munkafolyamatok és fordítási platformok, amelyek mind ugyanazt
a fájlformátumot beszélik —, a Python pedig több mint két évtizede szállít
[`gettext` modult][stdlib-gettext] a standard könyvtárában. A fordítás
futásidejű fele soha nem volt gond.

A megoldatlan fele mindig az volt, hogy *hogyan néz ki a katalógus szövege*.
Egy `%(name)s` üzenet olyan printf-szintaxist ad a fordítók kezébe, amelyet
egyetlen törölt betű éles összeomlássá változtat; egy `.format()` üzenet
attribútum-hozzáférést ad a katalógusnak élő objektumokhoz. (A
[Miért t-string?](comparison.md) mindkettőt végigjárja, a hibákat kirakatba
téve.) Az f-stringek pedig — az a szintaxis, amelyet ma a legtöbb Python-kód
előnyben részesít — egyáltalán nem tudnak részt venni: mire bármelyik könyvtár
meglátja őket, már kész szövegek. Az emberek mégis próbálkoznak, elég gyakran
ahhoz, hogy a Babel hibajegyzéke gyűjtse a kísérleteket
([#594][babel-594], [#715][babel-715]); a kudarc szerkezeti, nem hiányzó
funkció kérdése.

## Két PEP, tíz év különbséggel { #two-peps-ten-years-apart }

2015-ben Alyssa Coghlan és Nick Humrich megírta a [PEP 501]-et, amely
interpolációs sablonokat javasolt, és amelynek kimondott első motivációja az
i18n volt — „tisztább szintaxis biztosítása az i18n-fordításhoz”, a PEP saját
szavaival. A javaslatot elnapolták, részben azért, mert a vita megmutatta:
az i18n-eset olyan jelentős többletszempontokat hordoz, amilyeneket az
egyszerűbb felhasználási módok nem.

Egy évtizeddel később a [PEP 750] — Jim Baker, Guido van Rossum, Paul Everitt,
Koudai Aono, Lysandros Nikolaou és Dave Peck tollából — t-stringek néven
élesztette újra az ötletet, [2025 áprilisában elfogadták][sc-resolution], és
2025 októberében megjelent a [Python 3.14]-ben. A PEP 501-et ezután annak
javára visszavonták. Egy részlet fontos ezen az oldalon: az i18n *nem*
szerepel a PEP 750 kimondott motivációi között. A PEP általánosította a
mechanizmust — egy sablontípust, amelyet bármely könyvtár feldolgozhat —, és
pontosan ott hagyta a fordítás kérdését, ahol a PEP 501 tíz évvel korábban
letette: nyitva.

Így hát a Python 3.14 idejére a nyelvnek pontosan megvolt az az
adatszerkezete, amelyre egy üzenetkatalógusnak szüksége van, és nem volt
konvenciója arra, hogyan használja ilyenként.

## A stdlib-vita { #the-stdlib-discussion }

Két hónappal a 3.14 megjelenése előtt Adrian Mönnich (ThiefMaster, az Indico
projekt egyik karbantartója) azt javasolta, hogy magában a standard
könyvtárban zárják be ezt a rést: a discuss.python.orgon 2025 augusztusában
nyitott [Support t-strings in gettext][discuss-thread] szál egy működő
[pull requesttel][cpython-pr] érkezett, amely mind a `gettext`, mind a
`pygettext` számára t-string-támogatást adott hozzá.

A szálat érdemes teljes egészében elolvasni, mert felszínre hozza mindazokat a
nehéz kérdéseket, amelyekre ennek a könyvtárnak később válaszolnia kellett:

- **Mi lehet egy interpoláció?** Csak egyszerű név, vagy attribútumok és
  hívások is, származtatott helyőrzőnévvel? Minden válasz a kényelmet cseréli
  el a msgid stabilitására és a katalógus biztonságára.
- **Mit követelnek meg a többesszám-alakok,** amikor a célnyelv
  többesszám-rendszere eltér a forrásnyelvétől?
- **Egyáltalán a gettext a jó célpont?** Barry Warsaw — aki a PEP 750
  kidolgozása során amellett érvelt, hogy a t-string nem jó választás az
  i18n-hez — a saját [`flufl.i18n`][flufl-i18n] csomagjára és annak
  `$`-string stílusára mutatott mint barátságosabb eszközre; mások azt
  javasolták, hogy hagyják el egészen a gettextet olyan újabb rendszerek
  javára, mint a [Fluent].
- **És a metakérdés:** bármit szállítson is a standard könyvtár, azon
  gyakorlatilag soha többé nem lehet változtatni. Egy ennyi nyitott döntést
  hordozó konvenciót kockázatos elsőre befagyasztani.

Nem alakult ki konszenzus. A CPython hibajegyét
[„not planned” jelzéssel lezárták][cpython-issue], a pull requestet pedig
egyesítés nélkül zárták le 2025 októberében, néhány nappal a 3.14 megjelenése
után. A képesség megvolt a nyelvben; a konvenciónak nem lett otthona.

## Miért előbb egy csomag { #why-a-package-first }

Ezt a rést választotta ez a projekt betöltendőnek, a standard könyvtáron
kívülről, egy tudatos fogadás alapján: egy konvenció ott érik meg gyorsabban,
ahol szabadon verziózhat és esetről esetre nyerheti el az elfogadottságot, a
standard könyvtár pedig — amelynek elsőre kell eltalálnia — az a hely, ahová
egy konvenciónak *meg kell érkeznie*, nem az, ahol ki kell dolgozni.

Konkrétan a szál minden vitatott kérdésére van leírt válasz itt, mindegyikre a
maga oldalán:

- Az interpolációk **csak egyszerű nevek** lehetnek, hogy a msgidek stabilak
  és értelmesek maradjanak — [a kézikönyv](guide.md#safety-and-scope) mutatja
  a szabályt, a [Hogyan működik](internals.md#from-template-to-msgid) az
  okokat.
- A **formázás teljesen kimarad a katalógusból**
  ([Miért t-string?](comparison.md)).
- A **többes számok** unió/metszet szabályt követnek, amely megengedi, hogy a
  célnyelv többesszám-rendszere eltérjen a forrásnyelvétől
  ([spec 4. §](spec.md)).
- A hibás katalógus **összeomlás helyett visszaesik**, megtartva a gettext
  saját szerződését
  ([a kézikönyv](guide.md#what-happens-when-a-catalog-is-wrong)).
- Az egész konvenció pedig [verziózott specifikáció](spec.md) géppel olvasható
  konformitási készlettel — úgy megírva, hogy egy másik megvalósítás, akár egy
  jövőbeli standard könyvtárbeli is, változtatás nélkül átvehesse, és
  együttműködhessen vele.

A vita nem ért véget, és ez a projekt résztvevője annak, nem ítélete fölötte.
Ha van olyan éles üzemi gettext-tapasztalatod, amely érinti ezeket a
döntéseket, [ugyanaz a szál][discuss-thread] és ennek a tárolónak a
[Discussions][gh-discussions] felülete az a hely, ahol a beszélgetés
folytatódik.

## Idővonal { #timeline }

| Mikor | Mi történt |
| --- | --- |
| 1990-es évek közepe | A GNU gettext megteremti azt a PO/POT/MO munkafolyamatot, amelyet a fordítók és a platformok máig beszélnek. |
| 2015 | A [PEP 501] interpolációs sablonokat javasol, első motivációjaként az i18n-nel; elnapolják. |
| 2016 | Megjelennek az f-stringek a Python 3.6-ban — az interpoláció megkapja a szintaxisát, a fordítás pedig nem tudja használni. |
| 2024. júl. | A [PEP 750] javaslatot tesz a t-stringekre. |
| 2025. ápr. | A PEP 750-et [elfogadják][sc-resolution]; a PEP 501-et annak javára visszavonják. |
| 2025. aug. | Megnyílik a [Support t-strings in gettext][discuss-thread] szál, stdlib-beli [pull requesttel][cpython-pr]. |
| 2025. okt. | A [Python 3.14] szállítja a t-stringeket; a stdlib-hibajegy [„not planned”][cpython-issue] jelzéssel lezárul. |
| 2026 | A `gettext-tstrings` alfaként megjelenik, [v1-es speckel](spec.md) és annak konformitási készletével. |

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