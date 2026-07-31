---
description: "A helyőrző-szerződés annak, aki a .po fájlokat szerkeszti: mit változtathatsz meg, mihez nem szabad hozzányúlni, és hogyan kell olvasni a hibaüzeneteket."
---

# Fordítóknak

Ez az oldal annak szól, aki a katalógust szerkeszti, nem annak, aki a kódot
írja. Szándékosan rövid, és arra való, hogy egy projekt a saját fordítói
útmutatójába belinkelje vagy bemásolja.

Semmi nem kívánja meg itt, hogy Pythonul olvass. Minden egyetlen dologról
szól: az üzenet kapcsos zárójelek közé zárt darabjairól.

## Mi a helyőrző { #what-a-placeholder-is }

Egy katalógusbeli üzenet tartalmazhat kapcsos zárójelek közé írt neveket:

```po
msgid "Hello {name}"
msgstr ""
```

A `{name}` egy **helyőrző**. Amikor a program megjeleníti ezt az üzenetet, a
`{name}` helyére egy általa adott értéket tesz — egy személy nevét, egy
fájlnevet, egy számot. A helyőrző nem lefordítandó szó, hanem hely.

A fordításod a `msgstr` mezőbe kerül, és meg kell tartania ezt a helyet:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Mit változtathatsz meg, és mit nem { #what-you-may-change-and-what-you-may-not }

**Szabad**:

- **Áthelyezni egy helyőrzőt** oda, ahová a célnyelv nyelvtana kívánja, akár az
  üzenet elejére is.
- **Megismételni egy helyőrzőt**, ha a nyelvnek kétszer kell az érték.
- **Átírni minden más szót**, beleértve az írásjeleket, a szóközöket és a
  mondat sorrendjét.

**Nem szabad**:

- **Lefordítani a kapcsos zárójelek közötti nevet.** A `{name}` marad `{name}`,
  még olyan nyelvben is, amely semmi mást nem ír latin betűkkel.
- **Eltávolítani a kapcsos zárójeleket**, vagy nélkülük leírni a nevet.
- **Az ASCII `{` `}` zárójeleket teljes szélességű `｛` `｝` zárójelekre
  cserélni.** Sok beviteli módszer a teljes szélességű alakokat állítja elő;
  szinte azonosan néznek ki, és nem működnek.
- **Formázást hozzáadni**, például `{name!r}` vagy `{amount:.2f}` alakban. Azt,
  hogy egy érték hogyan jelenik meg, a program dönti el, nem a katalógus.
- **Kitalálni egy helyőrzőt**, amely nincs benne a `msgid` mezőben.

Ha egy üzenetnek olyan értékre van szüksége, amelyet az eredeti nem kínál,
akkor azt az üzenetet a fejlesztőnek kell megváltoztatnia. Szólj érte, ne
kerüld meg.

## Többesszám-alakok { #plural-forms }

A számlált üzenet a nyelved minden többesszám-alakjához egy-egy `msgstr`
hellyel érkezik, és a nyelved dönti el, hányan vannak — a japánban egy, a
németben kettő, az oroszban három, az arabban hat. Töltsd ki mindegyik helyet,
amelyet a katalógus ad.

Két szabály, amelyen sokan elcsúsznak:

- **A helyek nem „egyes szám, többes szám, még többes szám”.** Minden index
  azt jelenti, amit a nyelved többesszám-szabálya mond. A lett harmadik alak
  egyedül a nullára való; a szlovén második pontosan a kettőre; a walesi a
  0. indexre teszi az általános esetet, az 1.-re az egyes számot.
- **Két hely jogosan tartalmazhatja ugyanazt a szöveget.** A törökben, a
  magyarban, a perzsában és a bengáliban a főnév számnév után egyes számban
  marad, tehát egy számlált üzenet mindkét alakja ugyanaz a szöveg. Ez így
  helyes, nem másolás-beillesztési baki.

A fenti helyőrzőszabályok minden alakra külön-külön vonatkoznak.

## Fuzzy bejegyzések { #fuzzy-entries }

A `fuzzy` jelzővel ellátott bejegyzés egy gép tippje: a fejlesztő
megváltoztatta az eredeti üzenetet, az eszközkészlet pedig a régi fordításodhoz
párosította az új szöveget, hogy legyen honnan indulnod.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

A fuzzy bejegyzést **a program nem használja** — helyette a lefordítatlan
eredetit mutatja —, amíg valaki át nem dolgozza a szöveget, és le nem veszi a
`fuzzy` jelölést. A legtöbb PO-szerkesztőben van erre egy gomb.

## Hibaüzenet olvasása { #reading-a-failure-message }

Az eszközkészlet a katalógus bináris fordításakor ellenőrzi a helyőrzőket, és
az üzenet neked szól, nem egy programozónak. Zsákutca csupán annyit jelenteni,
hogy a `{name}` hiányzik, amikor pontosan ezeket a karaktereket látod magad
előtt, ezért ott, ahol egy helyőrző jelen lévőnek látszik, de mégsem az, az
üzenet megmondja, miért. Az eredeti `Hello {name}` ellenében az alábbiak
mindegyike a `translation does not match the source placeholders:` alatt
jelenik meg:

| Ezt mondja a fordításod | Ezt az okot adja |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (a körülötte lévő kapcsos zárójelek nem az ASCII `{` és `}`) |
| `こんにちは {{name}}` | `{name}` is missing (`{{name}}` alakban van írva, így kell escape-elni egy literális kapcsos zárójelet) |
| `こんにちは name` | `{name}` is missing (a név megjelenik, de nem kapcsos zárójelek között) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

A nem látható karakterek külön bánásmódot kapnak. A kapcsos zárójeleken belüli
nem törhető szóköz olyasmi, amit egy beviteli módszer állít elő, és amit
egyetlen szerkesztő sem mutat meg, ezért az üzenet kódponttal írja ki ahelyett,
hogy olyan karaktert nevezne meg, amelyet sosem találnál meg:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Az olyan nevet, amelynek betűi írásrendszereket kevernek — a homoglifa-eset,
amikor a cirill `а` megkülönböztethetetlen a latintól —, kétszer mutatjuk meg:
egyszer olvashatóan, egyszer escape-elve, mert csak ez az alak árulja el a
kettő közti különbséget:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Ugyanez az egyértelműsítés érvényes akkor is, amikor egy teljes egészében
egyetlen írásrendszerrel írt görög vagy cirill név ütközik egy ASCII
forrásnévvel, beleértve az egybetűs latin `a` és cirill `а` esetét.

Ha ezek egyikébe belefutsz, és a javítás nem magától értetődő, a biztonságos
lépés az, hogy törlöd az általad beírt helyőrzőt, és bemásolod a `msgid`
mezőben lévőt.

## Amit az ellenőrzések nem tudnak { #what-the-checks-cannot-do }

Az eszközkészlet azt igazolja, hogy a helyőrzőid épek. Azt nem tudja
megmondani, hogy a fordítás pontos-e, természetes-e, vagy megfelel-e a
szövegkörnyezetnek — az teljes egészében rád marad.

Két dolog többet segít minden ellenőrzésnél:

- **Olvasd el a fordítói megjegyzést.** Az üzenet fölött `#.` jellel kezdődő
  sor a fejlesztő üzenete arról, hol jelenik meg a szöveg, és mit jelent.
- **Kérdezz rá a `msgctxt` mezőre.** Amikor ugyanaz a szó kétszer jelenik meg,
  eltérő kontextusokkal, az azért van, mert a kettőt máshogy kell fordítani —
  például a „Megnyitás” gomb és a „Nyitva” állapot.
