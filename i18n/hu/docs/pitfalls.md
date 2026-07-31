---
description: "Mi törik el valójában, ha egy kis webhelyet harmincöt nyelvre fordítanak, ezek közül mit tud elkapni helyetted a könyvtár, és mit nem."
---

# Buktatók

Ez a webhely harmincöt nyelvre van lefordítva, és mindegyik kiadása annak a
ciklusnak a lefuttatásával készült, amelyet ez a dokumentáció tanít. Iparági
mércével ez kicsi korpusz, mégis elég volt ahhoz, hogy a legtöbb csapdába
belefussunk, amelyektől az i18n nehezebb, mint amilyennek látszik.

Az alábbi szakaszok mindegyike valami olyasmi, ami itt tényleg elromlott: hogy
nézett ki akkoriban, és hol húzódik a határ aközött, amit a könyvtár ellenőriz
helyetted, és ami a te megítélésed marad.

## Egy változó átnevezése újrafordíttat egy mondatot { #renaming-a-variable-retranslates-a-sentence }

A msgid a katalógus kulcsa, és egy interpolált név *benne van*. Ha egyetlen
konstanst modulszintre emelünk, és a Python stílusa szerint nagybetűssé
teszünk — `author` helyett `AUTHOR` —, a `Copyright © 2026 {author} · MIT
License` olyan üzenetté válik, amelyet még egyetlen katalógus sem látott.
Ennek a sornak minden fordítása visszament volna a fuzzy körbe, minden nyelven,
egy olyan átnevezés miatt, amely semmit nem változtatott abból, amit az olvasó
lát.

A könyvtár nem állít meg: mindkét írásmód érvényes helyőrzőnév. Amit viszont
tesz, az az, hogy a nevet *érdemessé* teszi a védelemre — egy interpolációnak
[egyszerű névnek](internals.md#from-template-to-msgid) kell lennie, így a
katalóguskulcsban álló dolog olyan szó, amelyet a fordító el tud olvasni, nem
pedig kifejezés.

A tükörhelyzet konstrukciójánál fogva biztonságos. A konverziók és a
formátumspecifikációk nem részei a msgidnek, így ha a `{amount:,.2f}` helyett
`{amount:,.0f}` lesz, az egyetlen kulcsot sem változtat meg, és sehol nem
érvénytelenít fordítást.

## Az `nplurals=2` nem jelent két különböző szöveget { #nplurals-2-does-not-mean-two-different-strings }

A török, a magyar, a perzsa és a bengáli mind két többesszám-alakot deklarál,
és mind a négyben egy megszámlált üzenet két alakja jogosan *ugyanaz a szöveg*
— a főnév számnév után egyes számban marad, így a `{n} sayfa` helyes egy
oldalra és tízre is. Az az átnéző, aki „kijavítja” a duplikációt, elrontja a
fordítást.

Az ellenkező hiba ugyanilyen könnyen jön. A lett harmadik alak **kizárólag a
nullára** való; a szlovén második egy **kettes szám**, pontosan kettőre; a
román utolsó alak megköveteli a `de` szót, amelynek az első kettőben nem szabad
szerepelnie. Ha ezeket a helyeket egy egyes és egy többes számú alakkal töltöd
ki, olyan katalógust kapsz, amely csak azoknál a darabszámoknál hibás,
amelyeket senki sem tesztel.

Ami rosszabb: a helyek *sorrendje* nem jelentéshordozó. A walesi úgy indexeli
az öt alakját, hogy a `msgstr[0]` az általános eset, a `msgstr[1]` pedig az
egyes szám. Ha a kézenfekvő sorrendben töltöd ki őket, az egyes számú alak épp
oda kerül, ahol minden meg nem számlált üzenet megtalálja.

A könyvtár ebből semmit nem vállal magára, és éppen ez a lényeg: a célnyelv
többesszám-szabálya a saját katalógusfejlécében lakik, az [unió/metszet
szabály](spec.md) pedig megengedi, hogy egy fordításnak több vagy kevesebb
alakja legyen, mint a forrásnak. Amit ellenőriz, az az egyetlen dolog, amit a
nyelv ismerete nélkül ellenőrizni tud — hogy minden alak megtartja azokat a
helyőrzőket, amelyekre szüksége van.

## Két alak okkal lehet azonos { #two-forms-can-be-identical-for-a-reason }

Az írnek öt többesszám-alakja van, és ennek a webhelynek a build-jelentésében
több közülük ugyanúgy van írva. Ez nem másolás-beillesztési baklövés: a
*leathanach* `l`-lel kezdődik, és az ír számnevek kiváltotta szókezdő mutációk
egyikét sem írjuk ki `l` előtt. Az alakok ettől még valódi munkát végeznek — a
szótő a *leathanach* és a *leathanaigh* között váltakozik, a tíz feletti
darabszámok pedig visszatérnek az egyes számhoz —, de egyetlen „oldal”
jelentésű főnéven sem látszana a különbség.

Minden olyan ellenőrzés, amely gyanúsnak jelöli az azonos alakokat, a helyes
írt is megjelöli. Erre egyedül a nyelvet ismerő ember lehet az átnéző.

## Egy üzenet csak egyetlen darabszámmal tud egyeztetni { #a-message-can-only-agree-with-one-count }

Ennek a webhelynek a build-jelentése megmondja, hány oldal renderelődött, és
mennyi ideig tartott. Ha „Rendered {n} pages in {seconds} seconds” alakban
írjuk meg, ártalmatlannak látszik, és nem lefordítható: a gettext egyetlen
darabszámból választ egyetlen alakot, ez a darabszám pedig az `n`. A *seconds*
szónak olyan számmal kellene egyeztetnie, amelyet a többesszám-gépezet soha nem
lát.

A javítás az, hogy a második mennyiség szó helyett mértékegységjel legyen — a
mértékegységjelek pedig maguk is honosítottak: ennek a webhelynek a
katalógusaiban `s`, `с`, `ث`, `שנ׳` és `mp` szerepel, a francia, a spanyol és a
svéd tipográfia pedig szóközt kíván a jel elé, ahol az angol nem. Ebből semmi
nem a könyvtár dolga — de az igen, hogy észreveszed: egy üzenetnek *két*
egyeztetésre volna szüksége, és erre az egyetlen eszköz az, hogy másképp írod
meg az üzenetet.

## Egy angol mondat szerkesztése idegen nyelvtant szerkeszt { #editing-an-english-sentence-edits-foreign-grammar }

A kezdőlapon korábban „mind a tíz nyelvi kiadás” állt. A szám eltávolítása —
egyetlen szavas angol szerkesztés, azért, mert a szám folyton elavult — a
többes számú alanyt egyes számúvá tette. A spanyolban, az olaszban, a
portugálban, az oroszban, az ukránban, a görögben, a hollandban és a héberben
mind újra kellett egyeztetni az igét; többükben a melléknévi igenevet is
módosítani kellett.

Egy forrásszerkesztés, amely angolul triviálisnak olvasódik, a lánc további
részén nem triviális. A fuzzyként való megjelölés — ezt teszi a `pybabel
update` — az a mechanizmus, amely minden fordítónak esélyt ad arra, hogy
észrevegye.

## A láthatatlan különbségek minden másolás-beillesztést túlélnek { #invisible-differences-survive-every-copy-paste }

A kézikönyv idéz egy diagnosztikát, amely `(nаme)` alakot tartalmaz — ez
szándékos escape, mert a benne megnevezett karakter egy cirill `а`, amelyet
egyetlen olvasó sem tud megkülönböztetni a latin betűtől. Ennek a webhelynek a
fordítói **öt külön alkalommal**, öt különböző nyelven alakították át ezt az
escape-et a tényleges karakterré, és minden alkalommal olyan oldal született,
amely helyesnek látszott, és hibás volt.

Ezt a könyvtár elkapja, és épp ez az oka annak, hogy a diagnosztikák olyan
alakúak, amilyenek: az olyan helyőrzőt, amelynek a betűi írásrendszereket
kevernek, [kétszer jelenti](internals.md#diagnostics-are-part-of-the-design) —
egyszer olvashatóan, egyszer escape-elve —, mert az escape-elt alak az egyetlen
írásmód, amely megkülönbözteti őket. A kapcsos zárójelek közé került nem
törhető szóköz ugyanezért íródik ki kódponttal. A katalógus-ellenőrző
visszautasítja az üzenetet, mielőtt kiszállítható lenne.

## A nem üres nem jelent lefordítottat { #non-empty-is-not-translated }

Az a katalógus, amelynek a vázát úgy készítik, hogy a msgideket a msgstrekbe
másolják, minden naiv ellenőrzésen átmegy: semmi nem üres, semmi nem fuzzy, az
üzenethalmaz pontosan egyezik. Ennek a webhelynek az egyik kiadása több órán át
így volt kiszállítva. Ahogy egy másik kiadás nyolc oldala is, amelyek az angol
forrás bájtra azonos másolatai voltak — és ez átmegy azon az ellenőrzésen,
amely a kettő kódblokkjait hasonlítja össze, mert ugyanarról a fájlról van szó.

Egyiket sem látja egy fordítókönyvtár. Mindkettőt olcsó tesztelni, ha egyszer
tudod, hogy kell: hasonlítsd össze a forrással, és követeld meg az eltérést.

## Nem a katalógus az egyetlen lefordított dolog { #the-catalog-is-not-the-only-translated-thing }

Két itteni hibának semmi köze nem volt a gettexthez.

Egy címsor lefordítása megváltoztatja a belőle generált horgonyt, így minden
oldalak közötti hivatkozás, amely arra a szakaszra mutat, eltörik — csendben,
csak abban az egy nyelvben. Ez a webhely minden címsoron rögzíti az angol
horgonyt, és egy teszt az angol oldalból vezeti le az elvárt listát.

A webhelygenerátor pedig hatvannyolc nyelvhez szállít felületi fordítást, és
ebben nincs benne a szuahéli és az ír. Ilyen nélkül a build nem esik vissza
angolra; a sablon include-ja elhasal, és a kiadás egyáltalán nem építhető meg.
Ennek a tárolónak két saját fájlja azért létezik, hogy betöltse ezt a hézagot.

## Az eszközeidben is vannak hibák { #your-tools-have-bugs-too }

Az a CI-lépés, amelyet ez a dokumentáció az elavult katalógusok elkapására
ajánl, a `pybabel update --check`, egyetlen olyan projektben sem tudja
elvégezni ezt a munkát, amely `pgettext`et vagy `npgettext`et használ. A Babel
2.18.0 verzióján minden `msgctxt`-tel rendelkező katalógust elavultnak jelent,
minden futáskor. Az összehasonlítás a `Catalog.is_identical` metóduson át
megy, amely minden üzenetet azon a kulcson keres ki, amely alatt tárolva van —
egy kontextusos üzenetnél pedig ez a kulcs az `(id, context)` pár, amelyet a
`Catalog.get` nem fogad el. A keresés semmit sem ad vissza, és a katalógusok
soha nem bizonyulnak egyenlőnek:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Itt derült ki, azzal, hogy megpróbáltuk használni; jelentettük az upstreamnek,
a helyettesítő ellenőrzés pedig [az üzemeltetési oldalon
található](workflow.md#what-ci-gates).

Az általános tanulság a kellemetlen: a mindig piros kapu rosszabb, mint a kapu
hiánya, mert a csapat kikapcsolja. Győződj meg róla, hogy a CI-ellenőrzésed
valóban át tud menni, mielőtt rábíznád, hogy elbuktasson.

## Mire való a könyvtár, egy sorban { #what-the-library-is-for-in-one-line }

Ennek az oldalnak a nagyobb része olyan megítélés, amelyet semmilyen eszköz nem
vehet át. Amit egy eszköz *meg tud* tenni, az az, hogy garantálja: egy fordítás
nem változtathatja meg annak a mondatnak a szerkezetét, amelyet lefordít — nem
ejthet el értéket, nem találhat ki újat, nem formázhatja át, és nem nyúlhat
bele az objektumaidba —, és ezt olyan mondatban tudja megmondani, amellyel az
kezdhet valamit, akinek javítania kell. Ennyi az egész, amit ez a könyvtár
ígér, és a webhely többi része arról szól, hogyan tartja meg.
