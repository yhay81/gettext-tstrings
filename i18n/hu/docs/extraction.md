---
description: "T-string üzenetek kinyerése pybabellel, és hogyan validálja a katalógusokat a msgfmt és a mellékelt Babel-ellenőrző."
---

# Kinyerés

A kinyerés az a lépés, amely a forráskódodból minden megjelölt üzenetet
összegyűjt egy `.pot` sablonba a fordítók számára — az
[oktatóanyag](tutorial.md) ciklusának 3. lépése. Ez az oldal ennek a lépésnek
a referenciája: konfiguráció, saját függvénynevek, szigorú CI-mód, és az
ellenőrzések, amelyek utána a katalógusaidat őrzik.

A kinyeréshez kell a `babel` extra:

```console
python -m pip install "gettext-tstrings[babel]"
```

## A munkafolyamat { #the-workflow }

Hozd létre a `babel.cfg` fájlt:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Ezután használd a szokásos Babel-parancsokat:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

Az `init` nyelvenként egyszer fut le; ezután a `pybabel update` gyúrja bele a
friss sablont a meglévő katalógusokba. Ezt a visszatérő kört — és azt, hogy a
`fuzzy` bejegyzései mit jelentenek egy kiadás szempontjából — az
[Éles üzemben](workflow.md#the-cycle-after-the-first-translation) járja végig.

A `gettext_tstrings` kinyerő a szokásos `_()`, `gettext()` és `ngettext()`
hívásokat is kezeli, így egyetlen leképezés lefed egy vegyes kódbázist.
Felismeri a `_()` hívást, a négy szabványos gettext-nevet, a `tr()` / `ntr()`
aliasokat, valamint a késleltetett `lazy_gettext()` / `lazy_pgettext()`
hívásokat.

!!! warning "Kapcsold be a fordítói megjegyzéseket a `-c` kapcsolóval"

    A `pybabel extract` csak akkor gyűjti be a fordítóknak szóló
    megjegyzéseket, ha megadod a `-c "Translators:"` kapcsolót — pontosan úgy,
    ahogy a szokásos gettext-hívásoknál is teszi. Ha elhagyod, a kinyerés
    továbbra is működik — a megjegyzések egyszerűen soha nem jutnak el a
    katalógusba, ahol pedig az egész folyamat [legolcsóbb
    minőségi eszköze](workflow.md#working-with-translators-and-platforms).

## Saját függvénynevek regisztrálása { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Egy ini-fájl egyetlen szöveget ad, egy TOML-leképezés listát, és egy szövegen
belül szóköz vagy vessző is elválasztja a neveket. Mind a négy írásmód
működik.

A beállítások: `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` és `npgettext_functions`.

!!! danger "A `-k` nem ér el egy t-stringig"

    Egy egyedi segédfüggvényt, például a `mytr(t"…")` hívást, meg kell nevezni
    a fenti beállítások valamelyikében. A Babel `--keyword` gépezete nem tud
    beleolvasni egy t-string literálba, így a `pybabel extract -k mytr` semmit
    nem talál, és semmit nem mond — az üzenetek egyszerűen hiányoznak a
    POT-ból. A `-k` továbbra is működik a mellettük kinyert szokásos
    gettext-hívásokra.

    Csak a szabványos argumentumsorrend támogatott: előbb az üzenet;
    `pgettext` esetén kontextus, majd üzenet; `npgettext` esetén kontextus,
    majd egyes szám, majd többes szám.

## Helyben elnéző, CI-ben szigorú { #lenient-locally-strict-in-ci }

Alapértelmezés szerint egyetlen rossz fájl nem vet véget a futásnak:

- Az olyan t-stringet, amelyet a kinyerő elutasít — attribútum-hozzáférés,
  kifejezés, hibás argumentum —, figyelmeztetésként jelenti és kihagyja.
- A nem elemezhető fájlt ugyanígy kihagyja.
- És ugyanígy azt is, amelyet csak a `tokenize` utasít el, míg az `ast`
  elfogadja — ezen a Babel saját menete egyébként megszakadna.

Ez kényelmes, amíg szerkesztesz, és veszélyes, amikor nem: a kihagyott üzenet
egyszerűen **hiányzik a POT-ból**, tehát soha nem fordítják le, és semmi nem
szól róla. Állítsd a leképezés beállításai közé a `strict = true` értéket
mindenütt, ahol a kinyerést nem figyeli ember:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Ekkor a fenti figyelmeztetések mindegyike kemény hibává válik. Tekintsd ezt az
éles beállításnak, az alapértelmezést pedig a helyinek.

## A meglévő eszközláncod validálja ezeket a katalógusokat { #your-existing-toolchain-validates-these-catalogs }

A Babel minden kinyert üzenetet szabványos jelzővel lát el, és épp ez az
egyetlen sor kapcsolja be a helyőrző-ellenőrzést azokban az eszközökben,
amelyeket már futtatsz:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Fordítsd `こんにちは {nombre}` alakban, és a hiba mindenféle konfiguráció
nélkül fennakad:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

A Weblate ugyanezt az ellenőrzést [Python brace format][weblate-checks] néven
dokumentálja, a kereskedelmi platformoknak pedig saját helyőrző-QA-juk van,
ugyanerre a jelzőre kötve. Minden platform viselkedése a sajátja; az alábbi
két eszköz az, amelyet itt ellenőriztünk.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Ezen felül a csomag regisztrál egy Babel-**ellenőrzőt**, így a
`pybabel compile` a specifikáció szabályait alkalmazza minden olyan üzenetre,
amely a `gettext-tstrings` jelölőmegjegyzést viseli:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Többes számú üzenetnél a mutató megnevezi az alakot, mert a Babel által
jelentett sorszám a msgidé, egy orosz blokk alatt pedig három `msgstr` áll:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "A `pybabel compile` akkor is megírja a `.mo` fájlt"

    A fenti hibát jelenti, a kilépési státusz `1` — a hibás katalógus mégis
    lefordul. Csak ez a kilépési státusz akadályozhatja meg, hogy egy folyamat
    kiszállítsa; a [Mit kapuz a CI](workflow.md#what-ci-gates) mutatja azt a
    build-lépést, amely ezt lehetővé teszi.

A két ellenőrzés nem redundáns. A csomag ellenőrzője legalább két esetben
szigorúbb:

- Az a msgid, amelyben csak escape-elt kapcsos zárójelek vannak
  (`Config {{raw}} only`), soha nem kapja meg a `python-brace-format` jelzőt,
  így semmilyen külső eszköz nem validálja.
- A többesszám-alakokat egyenként ellenőrizzük. A `msgfmt --check-format`
  ugyanezt a fájlt olvassa, és `0` státusszal lép ki; azt az alakot, amely
  elhagy egy helyőrzőt, amelyet a testvérei megtartanak, ott elfogadja, itt
  viszont elutasítjuk.

A `msgfmt` csak azokat a helyőrzőneveket ellenőrzi, amelyeket Python brace
formátumként tud értelmezni, ezért az ASCII nevekkel a lánc minden eszköze
képes marad az üzenet validálására. Maga a könyvtár bármilyen
`str.isidentifier()` nevet elfogad.

## Sablonok és más eszközök { #templates-and-other-tools }

A t-string Python-szintaxis, így ez a könyvtár a Python-forrásokat fedi le. A
sablonnyelvek továbbra is a saját i18n-jüket használják — a Jinja2
`{% trans %}` szerkezetét, a Django sabloncímkéit — és a Babel hozzájuk való
kinyerőit. Minden ugyanabba a PO-katalógusba táplál be, így egyetlen fordítási
munkafolyamat továbbra is lefed egy vegyes kódbázist.

A `pygettext` ma nem tudja elemezni a t-stringeket, ezért megy a kinyerés a
Babelen keresztül. A konvenciót leírtuk a [specifikációban](spec.md), hogy egy
másik kinyerő vagy egy jövőbeli `pygettext` is megcélozhassa.