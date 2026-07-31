---
description: "Teljes t-string üzenetek fordítása gettexten és Babelen keresztül, az értékeket és a formázást a katalóguson kívül tartva."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Teljes üzeneteket fordíts,<br>ne szövegtöredékeket.

A `gettext-tstrings` összeköti a Python 3.14+ t-stringjeit a szokásos
gettext-katalógusokkal és a Babel eszközkészletével. Az értékek és a formázás
az alkalmazáskódban maradnak; a katalógus egy teljes üzenetet kap, egyszerű
`{name}` helyőrzőkkel:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Irány az oktatóanyag :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Hasonlítsd össze az alternatívákat](comparison.md){ .md-button }

Alfa · Python 3.14+ · szokványos PO-/MO-katalógusok · nincs futásidejű függőség
{ .home-facts }

Ez a webhely maga is azt gyakorolja, amit dokumentál: minden nyelvi kiadását —
a navigációt, a feliratokat és a többes számot kezelő build-jelentést —
PO-katalógusokból rendereli maga a
[`gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Neked való ez? { #is-this-for-you }

**Ma illik hozzád, ha** az alkalmazásod Python 3.14-en vagy újabbon fut; már
használsz gettextet és Babelt, vagy szeretnéd bevezetni a PO-/MO-alapú
munkafolyamatukat; és olyan t-string-szintaxist szeretnél, amelynek nevesített
helyőrzőit renderelés előtt ellenőrzik.

**Még nem illik hozzád, ha** Python 3.13-ra vagy régebbire van szükséged; ha
stabil Python API-t követelsz meg — ez alfa, és a [specifikáció](spec.md) az a
része, amely megállapodott —; vagy ha a fordítandó szövegeid szinte mind egy
sablonnyelvben élnek, nem Python-forrásban.

Már vannak katalógusaid? Továbbra is működnek. A
`_("Hello {name}").format(name=name)` és a `tr(t"Hello {name}")` ugyanazt a
msgidet állítja elő, tehát a meglévő fordítások túlélik a váltást — a
[Migráció](migration.md) végigjárja az egész átállást.

## Mit mondhat a katalógus { #what-the-catalog-may-say }

A katalógus a teljes `Hello {name}` üzenetet kapja meg. Egy fordítás
átrendezheti vagy megismételheti a `{name}` helyőrzőt, és átírhat körülötte
minden más szót. Nem hagyhatja el a helyőrzőt, nem találhat ki újat, nem
nyúlhat rajta keresztül az objektumaidba, és nem aggathat rá saját formázást.

Ez az egész ígéret: **egy fordítás nem változtathatja meg annak az üzenetnek a
szerkezetét, amelyet fordít.** A könyvtár beérkezéskor ellenőrzi — a
katalógusok bináris fordításakor —, majd rendereléskor újra; az a hibás
bejegyzés, amely mégis eljut az éles üzembe, figyelmeztetést naplóz, és
összeomlás helyett a forrásüzenetet rendereli.

!!! note "Most ismerkedsz a gettexttel? Az egész munkafolyamat négy mondatban"

    A **gettext** a szoftverek fordításának bevett módja, Pythonban és jóval
    azon túl is. A kódod megjelöli a fordítandó üzeneteket; egy *kinyerő*
    összegyűjti őket egy sablonfájlba (`.pot`); egy fordító — aki rendszerint
    nem programozó — nyelvenként kitölt egy katalógusfájlt (`.po`), amelyből
    bináris `.mo` fordul, és ezt tölti be az alkalmazásod futás közben. A
    fordítófüggvény szokásos neve `_`, így a `_(t"Hello {name}")` úgy
    olvasható: „fordítsd le ezt az üzenetet”. Az **[oktatóanyag](tutorial.md)**
    végigjárja a teljes utat — megjelölés, kinyerés, fordítás, bináris
    fordítás, futtatás — nagyjából öt perc alatt.

## Milyen problémát old meg { #the-problem-it-solves }

Az f-string már interpolált, mire bármelyik könyvtár meglátja — az
`f"Hello {name}"` addigra `"Hello Ada"` lett, egy érték köré eső töredékek
fordítása pedig a legtöbb nyelv nyelvtanát tönkreteszi. A t-string
([PEP 750]) külön tartja a statikus szöveget, a kiértékelt értékeket, a
forráskifejezéseket, a konverziókat és a formátumleírókat — pontosan azt a
szétválasztást, amelyre egy üzenetkatalógusnak szüksége van.
[Mit változtat ez](comparison.md) a `%(name)s`, a `.format()` és a
`$`-stringek mellett?

Azt viszont sem a gettext, sem a Babel nem mondja meg, hogyan lesz egy
t-stringből üzenet. Ez a könyvtár meghozza ezt a döntést, leírja
[verziózott specifikációként](spec.md), és mellékeli az ellenőrzésére szolgáló
[konformitási készletet](spec.md#conformance).

## A tervezési szabályok { #the-design-rules }

- Teljes üzeneteket fordítunk, sosem mondattöredékeket.
- Csak egyszerű változóneveket fogadunk el, amilyen a `{name}`.
- A `!r` és a `:.2f` az alkalmazás kezében marad, a katalóguson kívül.
- Megengedjük, hogy a fordítások átrendezzék és megismételjék az ismert
  helyőrzőket, miközben megakadályozzuk, hogy attribútumokhoz nyúljanak vagy
  formázást adjanak hozzá.
- Újrahasznosítjuk a szokásos POT-, PO- és MO-fájlokat, és az őket már
  olvasó eszközöket.

És a hozzá tartozó lista arról, amihez szándékosan nem nyúl: nem honosítja a
számokat, a pénznemeket és a dátumokat — [azokat előbb formázd
meg](guide.md#locale-aware-values), Babellel; nem escape-eli a renderelt
kimenetet HTML-hez, shellhez vagy terminálhoz; és nem tudja megítélni, hogy
egy fordítás *helyes*-e, csak azt, hogy a helyőrzői épek-e.

## Telepítés { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 vagy újabb szükséges. **A renderelésnek nincsenek függőségei** —
csak a standard könyvtár `gettext` moduljára támaszkodik.

A kinyerés és a katalógus-ellenőrzés [Babel]en keresztül fut, ezért ezt az
extrát oda telepítsd, ahol a `pybabel` fut: ez rendszerint fejlesztői vagy
CI-környezet, nem pedig éles image:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Merre tovább { #where-to-go-next }

**Kezdd itt** — gettext-tapasztalat nélkül is:

<div class="grid cards" markdown>

- **[Oktatóanyag](tutorial.md)** — üres könyvtártól a működő japán fordításig
  öt lépésben, minden parancs a kimenetével együtt.
- **[Miért t-string?](comparison.md)** — ugyanaz az üzenet négyféleképpen
  megírva, és hogy a `%(name)s`, a `.format()` és a `$`-stringek külön-külön
  mit adnak a katalógus kezébe.

</div>

**Használd** — a munkareferenciák:

<div class="grid cards" markdown>

- **[Kézikönyv](guide.md)** — a futásidejű API: melyik belépési pontot
  használd, többes számok, kérésenkénti nyelvek, késleltetett szövegek, és mi
  történik, ha egy katalógus hibás.
- **[Kinyerés](extraction.md)** — a `pybabel`-referencia: konfiguráció, saját
  függvénynevek, és hogy a meglévő eszközök hogyan validálják ingyen ezeket a
  katalógusokat.
- **[Éles üzemben](workflow.md)** — a ciklus úgy, ahogy egy csapat működteti:
  a frissítési kör, a fuzzy bejegyzések, a CI-kapuk, a fordítási platformok és
  a kiszállítás.
- **[Migráció](migration.md)** — a bevezetés olyan projektben, amelynek már
  vannak katalógusai, egyszerre egy hívási hely.
- **[Fordítóknak](translators.md)** — egyetlen oldal annak, aki a `.po`
  fájlokat szerkeszti.

</div>

**Értsd meg** — a történettől a megvalósításig:

<div class="grid cards" markdown>

- **[Háttér](background.md)** — miért létezik ez a könyvtár: harminc év
  gettext, két PEP, és a stdlib-vita, amely válasz nélkül zárult.
- **[Buktatók](pitfalls.md)** — mi romlott el ténylegesen attól, hogy ezt a
  webhelyet harmincöt nyelvre fordítottuk, és melyik felét kapja el egy eszköz.
- **[Hogyan működik](internals.md)** — a PEP 750 sablonobjektumától a
  renderelt szövegig, és a gyorsítótárak, amelyek olcsóvá teszik az
  ellenőrzést.

</div>

**Referencia** — a szerződések:

<div class="grid cards" markdown>

- **[API](api.md)** — minden, amit a csomag exportál, egyetlen oldalon.
- **[Specifikáció](spec.md)** — a t-string ↔ msgid konvenció stabil,
  verziózott szerződésként, géppel olvasható konformitási készlettel.

</div>

## Állapot { #status }

Alfa. A szerződés szándékosan kicsi, és a [specifikáció](spec.md) a stabil
része; a Python API még mozoghat. Egy stabil kiadás előtt szükség van szélesebb
nyelvi fixtúrákra, folyamatos teljesítménykövetésre, olyanok API-átnézésére,
akik komolyan használják a gettextet és a Babelt, valamint kompatibilitási
tesztekre minden támogatott Python- és Babel-kiadáson.

A [hibajegyeket és pull requesteket](https://github.com/yhay81/gettext-tstrings/issues)
szívesen fogadjuk — az alfa épp az a szakasz, amikor még érdemes vitatkozni az
interfészről.

## Csatlakozz a közösséghez { #join-the-community }

- Válassz egy
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  címkéjűt egy jól körülhatárolt hozzájáruláshoz.
- Használati kérdéseidet tedd fel a
  [Q&A Discussionsban](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Az éles gettext-munkafolyamatokat és API-ötleteket hozd az
  [Ideas Discussionsba](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Pull request nyitása előtt olvasd el a
  [hozzájárulási útmutatót](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
