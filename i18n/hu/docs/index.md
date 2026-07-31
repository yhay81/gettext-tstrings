---
description: "Teljes t-string üzenetek fordítása gettexten és Babelen keresztül, a formázást a katalóguson kívül tartva."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Írd meg egyszer a mondatot.<br>Fordítsd le egészben.

Biztonságos gettext- és Babel-integráció a Python 3.14+ t-stringjeihez — az
érték a helyén marad, a katalógus pedig a teljes üzenetet látja:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Irány az oktatóanyag :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Miért t-string?](comparison.md){ .md-button }

Ez a webhely maga is azt gyakorolja, amit dokumentál: minden nyelvi kiadását —
a navigációt, a feliratokat és a többes számot kezelő build-jelentést —
PO-katalógusokból rendereli maga a
[`gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

A katalógus a teljes `Hello {name}` mondatot kapja meg. Egy fordítás
átrendezheti vagy megismételheti a `{name}` helyőrzőt; de nem hagyhatja el,
nem találhat ki újat, és nem aggathat rá saját formázást — ezt a könyvtár
ellenőrzi, a hibás katalógus pedig összeomlás helyett a forrásszövegre esik
vissza.

!!! note "Most ismerkedsz a gettexttel? Az egész munkafolyamat négy mondatban"

    A **gettext** a szoftverek fordításának bevett módja, Pythonban és jóval
    azon túl is. A kódod megjelöli a fordítandó szövegeket; egy *kinyerő*
    összegyűjti őket egy sablonfájlba (`.pot`); egy fordító — aki rendszerint
    nem programozó — nyelvenként kitölt egy katalógusfájlt (`.po`), amelyből
    bináris `.mo` fordul, és ezt tölti be az alkalmazásod futás közben. A
    fordítófüggvény szokásos neve `_`, így a `_(t"Hello {name}")` úgy
    olvasható: „fordítsd le ezt a mondatot”. Az **[oktatóanyag](tutorial.md)**
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

## Milyen döntést hoz { #the-choice-it-makes }

- Teljes üzeneteket fordítunk, sosem mondattöredékeket.
- Csak egyszerű változóneveket fogadunk el, amilyen a `{name}`.
- A `!r` és a `:.2f` az alkalmazás kezében marad, a katalóguson kívül.
- A fordítók átrendezhetik és megismételhetik az ismert helyőrzőket — de nem
  hívhatnak attribútumokat, és nem adhatnak hozzá formázási viselkedést.
- Újrahasznosítjuk a szokásos POT-, PO- és MO-fájlokat, és az őket már
  olvasó eszközöket.

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

Háromféle olvasó érkezik ide: aki az első programját fordítja, aki egy valódi
projektbe köti be a fordítást, és aki pontosan tudni akarja, miért ilyen a
gépezet felépítése. Mindegyiknek van útja.

**Megtanulni** — gettext-tapasztalat nélkül is:

<div class="grid cards" markdown>

- **[Oktatóanyag](tutorial.md)** — kezdd itt: üres könyvtártól a működő
  japán fordításig öt lépésben, minden parancs a kimenetével együtt.
- **[Miért t-string?](comparison.md)** — ugyanaz az üzenet négyféleképpen
  megírva, és hogy a `%(name)s`, a `.format()` és a `$`-stringek külön-külön
  mit adnak a katalógus kezébe.
- **[Háttér](background.md)** — miért létezik ez a könyvtár: harminc év
  gettext, két PEP, és a stdlib-vita, amely válasz nélkül zárult.

</div>

**Komolyan használni** — a munkareferenciák:

<div class="grid cards" markdown>

- **[Kézikönyv](guide.md)** — a futásidejű API: többes számok, kérésenkénti
  nyelvek, késleltetett szövegek, és mi történik, ha egy katalógus hibás.
- **[Kinyerés](extraction.md)** — a `pybabel`-referencia: konfiguráció, saját
  függvénynevek, és hogy a meglévő eszközök hogyan validálják ingyen ezeket a
  katalógusokat.
- **[Éles üzemben](workflow.md)** — a ciklus úgy, ahogy egy csapat működteti:
  a frissítési kör, a fuzzy bejegyzések, a CI-kapuk, a fordítási platformok
  és a kérésenkénti nyelvek egy webalkalmazásban.
- **[API](api.md)** — minden, amit a csomag exportál, egyetlen oldalon.

</div>

**Megérteni** — az elvektől a megvalósításig:

<div class="grid cards" markdown>

- **[Hogyan működik](internals.md)** — a PEP 750 sablonobjektumától a
  renderelt szövegig, és a gyorsítótárak, amelyek olcsóvá teszik az
  ellenőrzést.
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
