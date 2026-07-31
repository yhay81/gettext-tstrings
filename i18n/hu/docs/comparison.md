---
description: "Ugyanaz a fordítható üzenet %-formázással, .format() hívással, flufl.i18n $-stringgel és t-stringgel megírva, a fordítói hibák, a katalógus hatalma és az integráció költsége szerint összehasonlítva."
---

# Miért t-string?

Négyféle módszer arra, hogy értéket tegyünk egy fordítható üzenetbe, ugyanazon
az üzeneten összehasonlítva. Mind a négy nevesíti a helyőrzőit, és mind a négy
engedi, hogy a fordító átrendezze őket; abban különböznek, hogy mi történik, ha
egy fordítás hibás, hogy a programodból mennyit érhet el a katalógus, és hogy
mibe kerül a bevezetésük.

A táblázatok jönnek elsőként, hogy megtaláld a téged érdeklő sort, és csak a
mögötte álló szakaszt kelljen elolvasnod.

!!! note "Minden lefordított üzenethez három fél nyúl hozzá"

    A **katalógus** a fordítások fájlja — `.po`, amíg emberek szerkesztik, és
    `.mo`-ra fordítva tölti be az alkalmazás (az [oktatóanyag](tutorial.md)
    mindkettőt végigjárja). Minden üzenethez három fél nyúl hozzá: a
    **fejlesztő** megírja a forrásszöveget, egy **fordító** szerkeszti a
    katalógust — gyakran külső platformon, minden kódfelülvizsgálattól távol
    —, az **alkalmazás** pedig futásidőben rendereli össze a kettőt. Az alábbi
    formázási stílusok mind ugyanarra a kérdésre válaszolnak másképp: *a
    formátumnyelvből mennyi fölött rendelkezhet a katalógus?* A példákban a
    `_` a fordítófüggvény szokásos neve, a `tr` pedig ennek a könyvtárnak a
    neve rá.

## Egymás mellett { #side-by-side }

**Amikor a fordító hibázik.** Egy katalógus sok kézen megy át, és a benne
elromló dolgok többsége véletlen:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| A fordítás *elhagy* egy helyőrzőt — mi jelenik meg? | az érték némán eltűnik | az érték némán eltűnik | az érték némán eltűnik | a forrásüzenet, figyelmeztetéssel ([alapértelmezésben](guide.md#what-happens-when-a-catalog-is-wrong)) |
| A fordítás *hozzáad* egy ismeretlen helyőrzőt — mi jelenik meg? | kivétel | kivétel | a helyőrző szövegként látható marad | a forrásüzenet, figyelmeztetéssel ([alapértelmezésben](guide.md#what-happens-when-a-catalog-is-wrong)) |
| A fordítás *átformázza* a helyőrzőt — mi jelenik meg? | amit a katalógus kért, vagy kivétel, ha a típusbetű már nem illik az értékhez | amit a katalógus kért | `$`-stringben nem is kifejezhető | a forrásüzenet, figyelmeztetéssel |
| Ellenőrzöttek-e a helyőrzők rendereléskor? | nem | nem | nem | igen (lásd alább) |

**Mekkora hatalma van a katalógusnak.** A fordítás a tárolódon kívülről
érkező adat, és mindegyik stílus más mennyiségű hatalmat ad a kezébe:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Honnan jönnek az értékek? | explicit leképezésből | explicit argumentumokból | a hívó lokális és globális változóiból, plusz opcionális `extras` | a t-stringen belül elkapott értékekből |
| Megváltoztathatja a katalógus egy érték formázását? | igen | igen | nem | nem |
| Belenyúlhat a katalógus az objektumokba (attribútum-hozzáférés)? | nem | igen | igen, pontozott nevekkel | nem |
| Hol él „az aktuális nyelv”? | ott, ahová az alkalmazás teszi | ott, ahová az alkalmazás teszi | nyelvkódok vermében a közös alkalmazásobjektumon | egy `ContextVar`-ban, feladatonként vagy kérésenként |

**Mibe kerül az integráció.** A fenti minden ingyen van, ha az eszközkészlet
illeszkedik; itt derül ki, ha mégsem:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Minimális Python | bármelyik | bármelyik | 3.10 | **3.14** |
| Érettség | standard könyvtár | standard könyvtár | stabil kiadás | **alfa** |
| Szokványos PO-/MO-katalógusokat használ? | igen | igen | igen | igen |
| Kell hozzá egyedi forráskinyerő? | nem | nem | nem | igen, jelenleg |
| Melyik PO-jelzőt vezeti le a Babel, hogy a meglévő eszközök validálhassanak? | `python-format` | `python-brace-format` | egyiket sem | `python-brace-format` |

A renderelésidejű ellenőrzésről: az egyes számú üzeneteknél pontos
helyőrző-egyezést várunk el. A többes számú üzeneteket is ellenőrizzük, az
[unió/metszet szabály](spec.md) szerint, amely megengedi, hogy a célnyelv
többesszám-alakjai eltérjenek a forrásnyelvéitől; a szigorúbb, alakonkénti
ellenőrzés a katalógusok bináris fordításakor fut le
([Kinyerés](extraction.md)).

A formátumjelzőről szóló sor a helyőrzőket ismerő validálásra vonatkozik, nem
a katalógus kompatibilitására. Az `egyiket sem` azt jelenti, hogy a szokásos
gettext-eszközök továbbra is olvassák és lefordítják az üzenetet, de a
`msgfmt --check-format` nem talál `$`-helyőrzőnyelvtant, amelyet alkalmazhatna.

## Kompatibilitás és érettség { #compatibility-and-maturity }

Az utolsó táblázat első két sora az, amelyik a bevezetésről dönt, ezért érdemes
kimondva is leírni, nem csak cellákban.

A `%`-formázás és a `.format()` be van építve a Pythonba, és semmilyen függőség
nem kell hozzájuk. A [`flufl.i18n`][flufl-i18n] érett csomag, kiadott és éles
használatban van, és Python 3.10-en és újabbon fut. A `gettext-tstrings`
**alfa**, és **Python 3.14-et vagy újabbat** igényel, mert a t-string a 3.14 új
szintaxisa — visszaportolás nincs, és nem is lehet. A
[specifikációja](spec.md) a stabil része; a Python API még mozoghat 1.0 előtt.

Amibe egyikük sem kerül, az a katalóguskompatibilitás. Mind a négy szokványos
POT-/PO-/MO-fájlokat állít elő, amelyeket minden PO-szerkesztő, fordítási
platform és GNU gettext-eszköz már most is olvas, így az alábbi választás
olyan értelemben visszafordítható, ahogy egy katalógus*formátum* váltása nem
lenne az. A [Migráció](migration.md) tárgyalja egy meglévő projekt átállítását.

Az alábbi szakaszok mindegyik kompromisszumot részletesen mutatják be,
egyszerre egy módszert.

## %-formázás { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Mi romolhat el: egy megrongált helyőrzőből futásidejű kivétel lesz, hacsak a
katalógus-ellenőrzés előbb el nem kapja.

A katalógus szövege printf-szintaxist visz magával, benne egy záró
típusbetűvel — az `s` a `%(name)s`-ben —, amelyet könnyű átnézni és könnyű
megrongálni:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Egy egykarakteres szerkesztés a PO-szerkesztőben futásidejű kivétellé válik,
hacsak a katalógusvalidálás előbb el nem kapja. A GNU `msgfmt --check-format`
ezt elkapja ugyan, de csak a `python-format` jelzővel ellátott üzeneteknél, és
csak akkor, ha a katalógus ténylegesen átmegy a msgfmten az alkalmazásod felé
vezető úton.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Ez megszünteti a záró típusbetűt, miközben megőrzi a nevesített, szabadon
átrendezhető helyőrzőt. A baj lehetősége átkerül a csere másik oldalára: a
fordítás hatalmat kap az objektumaid fölött.

A `str.format` egy kis kifejezésnyelv, és ha meghívod egy szövegen, azzal
odaadod annak a szövegnek a jogot, hogy használja:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Most cseréld ki ezeket a literális szövegeket arra, amit a `_()` visszaad. Ha
a `Hello {name}` fordítása `{conf.api_key}` alakban jön vissza, a renderelése
kiírja az API-kulcsodat — a katalógus döntötte el, mi olvasódik ki, nem a
kódod. A katalógus nem kód, de úgy utazik, mint az adat: ki egy fordítási
platformra, több kézen át, vissza `.po`-ként, `.mo`-ra fordítva, néha teljesen
a projekteden kívülről bevendorolva. A `.format()` ennek az útnak minden
állomásán attribútum-hozzáférést ad az általad átadott objektumokhoz.

## `$`-stringek és a flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

A standard könyvtár [`string.Template`][stdlib-template] osztálya adja a
`$name` interpolációs nyelvet, de maga nem fordítási API. A
[`flufl.i18n`][flufl-i18n] ezt a stílust kombinálja a gettext
katalóguskeresésével. Vedd észre, hogy az értéket sosem adjuk át: a
flufl.i18n a hívó globális és lokális változóiból építi fel a helyettesítési
névteret — az üzenet számára az összes olyan változó elérhető, amely a hívás
helyén létezik. Egy opcionális `extras` leképezés mindkettőnél előbbre való. A
fordítóknak szánt szintaxisában nincs záró típusbetű vagy formátumleíró, a
helyőrzők pedig szabadon átrendezhetők maradnak.

Egy elérhetetlen helyettesítés nem vált ki kivételt. Ha `name = "Ada"`, és a
hívó névterében nincs `nombre`, akkor a `Hello $nombre` katalógusbeli fordítása
`Hello $nombre` alakban jelenik meg: a feloldatlan helyőrző látható marad. Ez a
[dokumentált viselkedés] a hívás elbuktatása helyett megőrzi a lefordított
üzenet többi részét. Az attribútum feloldása vagy egy érték konvertálása
közben keletkező kivételek ettől még továbbterjedhetnek.

A `flufl.i18n` egy lényeges szempontból többet tud a puszta
`string.Template`-nél. A [saját Template]-je elfogad pontozott helyőrzőket,
például `$settings.api_key` alakban, a [fordítómodulja] pedig ezeket az
útvonalakat a hívó értékein oldja fel. Egy lefordított helyőrző bármelyik
elérhető lokális vagy globális változóra hivatkozhat a hívónál, a pontozott
szintaxissal pedig bejárhatja annak attribútumait is. Ez kényelmes, amikor egy
üzenetnek attribútumra van szüksége, egyúttal azonban a hívó veremkeretét is a
katalógus helyettesítési névterének részévé teszi. Az itteni összehasonlítás a
`flufl.i18n` 6.0.0 verziójára vonatkozik, nem a `string.Template` minden
lehetséges használatára.

Arra a kérdésre is választ ad, amelyet a másik két formázási stílus teljes
egészében az alkalmazásra hagy: *melyik* nyelv az aktuális, és hogyan lehet
váltani. Egy [alkalmazásobjektum][application object] nyelvekből álló vermet
tart, a `_.push(code)` és a `_.pop()` mozgatja, a `with _.using(code):`
egymásba ágyazható, egy [stratégia][strategy] pedig megkeresi a nyelvkódhoz
tartozó katalógust, így magának az alkalmazásnak sosem kell
katalógusobjektumokkal bajlódnia. Az az eset, amiért mindez létezik, az a
kiszolgáló, amelynek egyetlen munkaegységen belül egynél több nyelven kell
szöveget előállítania — egy oldalt az olvasónak, egy értesítést valakinek,
akinek a fiókja más nyelvre van állítva.

A verem azon az alkalmazásobjektumon él, amelyen az egész folyamat osztozik.
Két átfedő kérés így egyetlen vermen osztozik, és az *időben* nem szigorúan
egymásba ágyazott blokkok rossz nyelvet adnak át egymásnak:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Ez a könyvtár ugyanezt a képességet őrzi meg — a kötések ugyanúgy egymásba
ágyazódnak és bomlanak vissza —, csak közös verem helyett `ContextVar`
változóban, így a fenti átlapolódás feladatonként oldódik fel. A megfelelő
példák a [Több nyelv egyszerre](guide.md#several-languages-at-once) szakaszban
vannak. Amit nem ad, az a nyelvkódról katalógusra való feloldás: te adsz át egy
fordításobjektumot, ami a szokásos esetben egyetlen `gettext.translation()`
hívás, a standard könyvtár pedig gyorsítótárazza a beolvasott katalógust.

## t-stringek { #t-strings }

```python
tr(t"Hello {name}")
```

A katalógus továbbra is a `Hello {name}` üzenetet látja, és marad szokványos
PO-/MO-katalógus. A különbség az, hogy egy fordítás *mit mondhat*, és hogy ki
ellenőrzi ezt.

Ez a könyvtár renderelés előtt minden fordítást összevet a forrásüzenet
helyőrzőivel, és csak puszta neveket fogad el, semmi mást. A
`t"Hello {name}"` ellenében:

| Ha a fordítás ezt tartalmazza | ezzel utasítja el |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Az elutasítás nem összeomlás: alapértelmezésben a könyvtár figyelmeztetést
naplóz, és a forrásüzenetet rendereli, így egy rossz katalógus soha nem viszi
le az alkalmazást —
[ugyanaz a szerződés, amelyet maga a gettext is tart](guide.md#what-happens-when-a-catalog-is-wrong).

A formázás ott marad, ahol megírták: a kódban.

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

A `:,.2f` sosem jut el a katalógusig, így semmilyen fordítás nem
változtathatja meg, és egyetlen fordítónak sem kell ránéznie. Ez azonban
*rögzített* formátum, nem honosított: a számjegyek és az elválasztók
nyelvenkénti megválasztása [a Babel dolga, még a hívás
előtt](guide.md#locale-aware-values).

Egy további különbség az eszközkészlet: a t-string új szintaxis, ezért
`.pot`-ba kinyerésükhöz jelenleg t-stringet ismerő kinyerő kell, amilyet ez a
csomag is [ad a Babelhez](extraction.md).

## Mibe kerül a megszorítás { #the-cost-of-the-restriction }

A Python-követelményen túl mindennek egyetlen szabály az ára: egy
interpolációnak puszta névnek kell lennie.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Ez valódi korlát, és pontosan ugyanaz a korlát, amely a fenti garanciákat
megtermi. A forrásoldali értékkötéssel és a futásidejű helyőrző-ellenőrzéssel
együtt megakadályozza, hogy a katalógus szövegei kifejezéseket értékeljenek
ki, és értelmesen tartja a helyőrzők neveit annak számára, aki fordítja őket.

Az f-string egyáltalán nem használható így — mire bármelyik könyvtár meglátja,
már kész szöveg, tehát a fordítása töredék fordítását jelenti. A t-string
([PEP 750]) különtartja a statikus szöveget és az értékeket, miközben megőrzi
az f-stringszerű szintaxist és az explicit értékkötést.

Hogy a Python miként jutott el idáig — két PEP tíz év
különbséggel, és a stdlib-vita, amely válasz nélkül zárult —, azt forrásokkal
együtt a [Háttér](background.md) meséli el.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [dokumentált viselkedés]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [saját Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [fordítómodulja]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html