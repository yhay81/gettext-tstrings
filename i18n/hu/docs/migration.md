---
description: "T-stringek bevezetése olyan projektben, amelynek már vannak gettext-katalógusai: mi marad érintetlenül, mi lesz fuzzy, és hogyan lehet egyszerre egy hívási helyet átállítani."
---

# Migráció

Ha a projekted már használ gettextet, szűk kérdések döntik el, bevezethető-e ez
a könyvtár: érvényteleníti-e a meglévő katalógusaidat, megfér-e azzal a
kóddal, amelyet még nem állsz készen megváltoztatni, és mennyinek kell az
átállásból egyszerre megtörténnie. A válaszok, a legrövidebbel kezdve:

| Kérdés | Válasz |
| --- | --- |
| Működnek még a meglévő `.po` és `.mo` fájlok? | Igen. Ugyanazok a fájlok, ugyanazok az eszközök. |
| Megfér egy fájlban a régi és az új hívás? | Igen, és egyetlen kinyerő-leképezés lefedi mindkettőt. |
| Változik a msgid? | A `.format()` felől nem. A `%`-formázás felől igen. |
| Az egész projektnek egyszerre kell átállnia? | Nem. Egyetlen hívási hely is érvényes változtatás. |
| Mi lesz a Jinjával, a Django-sablonokkal, a JavaScripttel? | Érintetlenek, ugyanazok a katalógusok. |

Az oldal többi része a fentiek mindegyikének a részlete.

## A `.format()` felől: a msgid nem változik { #from-format-the-msgid-does-not-change }

Ez az az eset, amelyben a migráció szinte semmibe nem kerül. Egy `str.format`
üzenet és egy t-string üzenet *ugyanazt* a katalóguskulcsot vezeti le, mert a
kulcs mindkét esetben az a szöveg, amelyben a `{name}` benne maradt:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Így a meglévő fordítás a helyén marad. Indulj egy katalógusból, amely ezt
tartalmazza:

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

módosítsd a hívást, nyerd ki újra, és frissíts:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

A visszakapott bejegyzés két metaadatsorban tér el, semmi másban — egy jelölő
megjegyzésben, amely t-string üzenetként azonosítja, és egy forrássor
számában:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Semmilyen `fuzzy` jelző, semmilyen újrafordítás, egyetlen nyelven sem. Az
üzenet azonnal megjelenik:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "Az `update --check` elavultként fogja jelenteni a katalógusokat"

    Az a jelölő megjegyzés és az elmozdult sorszámok elegendők ahhoz, hogy a
    `pybabel update --check` szerint egy katalógust újra kell generálni, mert
    az egész bejegyzést hasonlítja össze, nem csak a fordítást. Futtasd le a
    valódi `pybabel update` parancsot ugyanabban a commitban, amelyben a
    kódváltozás van, és a katalógusokat is vele együtt commitold — ugyanaz a
    szokás, amelyet a [CI-kapu](workflow.md#what-ci-gates) már amúgy is kér.

## A `%`-formázás felől: a msgid változik, így a fordítások fuzzyk lesznek { #from--format-the-msgid-changes-so-translations-go-fuzzy }

A printf-szintaxis magán az üzeneten *belül* él, ezért a lecserélése átírja a
katalóguskulcsot. Ezt nem lehet megkerülni, és ez a `%(name)s` elhagyásának
őszinte ára:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

A `pybabel update` felismeri, hogy az új üzenet közeli rokona az
eltávolítottnak, és átviszi a régi fordítást, fuzzyként megjelölve:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Három dolgot érdemes tudni erről az állapotról:

- **Futásidőben semmi nem romlik el.** A fuzzy bejegyzések kimaradnak a
  lefordított `.mo` fájlból, így az alkalmazás a forrásüzenetet rendereli,
  amíg egy ember meg nem erősíti a párosítást —
  [ugyanaz a degradáció](workflow.md#the-cycle-after-the-first-translation),
  amelyen minden átfogalmazott üzenet átmegy.
- **A CI zöld marad, amíg fuzzyk.** A helyőrző-ellenőrző kihagyja a fuzzy
  bejegyzéseket, pontosan úgy, ahogy a `msgfmt --check-format` teszi, mert az
  a bejegyzés, amely el sem juthat a futásidőig, ne buktasson el egy buildet.
  Abban a pillanatban, amikor egy fordító leveszi a jelzőt, a bejegyzést a
  többivel egyformán ellenőrizzük — így a megerősített fordításban hagyott
  `%(name)s` akkor akad fenn, vagyis pontosan akkor, amikor egyébként
  megjelenni kezdene.
- **A régi `python-format` jelző is átjön**, és a `fuzzy` jelzővel együtt
  törölni kell, különben a `msgfmt --check-format` továbbra is printf-szabályokat
  alkalmaz egy brace-formátumú üzenetre.

A nevesített printf-helyőrzőknél a szerkesztés gépies — a `%(name)s` helyére
`{name}` kerül, és semmi más nem mozdul —, tehát egy nagy katalógus
szkriptelt átfutás plusz egy fordítói átnézés, nem pedig újrafordítás. A
pozicionális `%s` viszont nem gépies: nincs neve, amit át lehetne vinni, a név
megválasztása pedig épp a változtatás lényege.

A migráció tehát abban a tempóban haladhat, amelyet az átnézés megenged: egy
át nem alakított fuzzy bejegyzés látható munkadarab a katalógusban, nem pedig
elromlott build.

## A régi és az új hívások megférnek egymással { #old-and-new-calls-coexist }

Az a kinyerő, amely a t-stringeket olvassa, a szokásos gettext-hívásokat is
olvassa, így egyetlen leképezés lefed egy migráció közepén lévő fájlt:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Mindkét üzenet ugyanabba a sablonba kerül, és csak a t-stringes viseli azt a
jelölő megjegyzést, amely bekapcsolja ennek a könyvtárnak a többletellenőrzését:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Felismeri a `_()` hívást, a négy szabványos gettext-nevet, a `tr()` / `ntr()`
aliasokat, valamint a késleltetett `lazy_gettext()` / `lazy_pgettext()`
hívásokat. A saját segédfüggvényedet
[meg kell nevezni a leképezésben](extraction.md#registering-your-own-function-names).

Futásidőben a két stílus ugyanennyire független egymástól: a
`gettext.translation()` egyetlen fordításobjektumot ad vissza, és a `_`
éppúgy, mint ennek a könyvtárnak a belépési pontjai, abból olvasnak.

## Ami nem mozdul { #what-does-not-move }

- **Sablonnyelvek.** A Jinja2 `{% trans %}` szerkezete, a Django sabloncímkéi
  és a hozzájuk tartozó Babel-kinyerők változtatás nélkül működnek tovább, és
  ugyanazokat a PO-katalógusokat táplálják. A t-string Python-szintaxis;
  Python-forrásra vonatkozik.
- **A katalógusfájljaid.** Nincs formátumváltás, nincs új fájl, nincs
  konverziós lépés.
- **A fordítási platformod.** A `.po` csereformátum azonos, és az a
  `python-brace-format` jelző, amelyet egy t-string üzenet visel, ugyanaz a
  jelző, amelyet egy `.format()` üzenet visel — így a helyőrző-QA tovább
  működik.
- **A nem Python kód.** Egy ugyanabban a projektben lévő JavaScript- vagy
  C-katalógust ez nem érint.

## Migrációs ellenőrzőlista { #a-migration-checklist }

1. Add hozzá a `babel` extrát ott, ahol a `pybabel` fut, és állítsd át a
   `babel.cfg` `python` leképezését a `gettext_tstrings` metódusra — egyetlen
   leképezés ekkor mindkét stílust lefedi, a `-k` pedig továbbra is működik a
   szokásos hívásokra.
2. Először a `.format()` hívási helyeket alakítsd át. Nyerd ki újra, futtasd a
   `pybabel update` parancsot, és a katalógusokat a kóddal együtt commitold;
   fuzzy bejegyzésre nem kell számítani.
3. A `%`-formázású hívási helyeket olyan adagokban alakítsd át, amelyeket át
   tudsz nézetni: írd át az átvitt helyőrzőket, és töröld a `fuzzy` és a
   `python-format` jelzőt.
4. Javítsd ki, amit a megszorítás elutasít: egy interpolációnak puszta névnek
   kell lennie, tehát a `t"Hello {user.name}"` előbb lokális változó lesz. Ez
   hívási helyi szerkesztés, nem katalógusbeli.
5. Kapcsold be a `strict = true` beállítást a kinyerő-leképezésben, amint a
   átfutás kész, hogy a ki nem nyerhető üzenet inkább
   [a buildet buktassa el](extraction.md#lenient-locally-strict-in-ci),
   mintsem eltűnjön a sablonból.
6. Vedd fel az [Éles üzemben](workflow.md#what-ci-gates) oldalról a futásidejű
   ellenőrzést: rendereld le nyelvenként egy üzenetet egy szigorú
   `Translator`-on keresztül.

A 2. és a 3. lépés szokványos commit. Ebben a listában semmihez nem kell
egyetlen nagy átállási nap.
