---
description: "A futásidejű API: melyik belépési pontot használd, katalógus kötése, kérésenkénti nyelvek, késleltetett szövegek, honosított értékek, és hogyan jelenti a könyvtár a hibás fordítást."
---

# Kézikönyv

Ez az oldal a futásidejű referencia: mindaz, amit az *alkalmazáskódod* csinál
ezzel a könyvtárral, ha már vannak katalógusok. Ha még nem láttad a teljes
ciklust — megjelölés, kinyerés, fordítás, bináris fordítás, futtatás —, az
[oktatóanyag](tutorial.md) öt perc alatt végigjárja egyszer; a katalógusok
létrehozását és ellenőrzését a [Kinyerés](extraction.md) tárgyalja, azt pedig,
hogyan tartja egy csapat mozgásban a ciklust — frissítési körök, CI, fordítási
platformok —, az [Éles üzemben](workflow.md).

## Melyik belépési pontot használjam? { #which-entry-point-should-i-use }

A csomag több módot is exportál egy üzenet lefordítására, mert az alkalmazások
többféleképpen kötnek nyelvet. Aszerint válassz, ahogy a programod eldönti,
milyen nyelven van éppen:

| A helyzeted | Ezt használd |
| --- | --- |
| Egy nyelv az egész folyamatra — CLI, asztali alkalmazás, szkript | `Translator`, `_` néven hívva |
| Kérésenként vagy aszinkron feladatonként egy nyelv — webalkalmazás | `use_translations()` a munka köré, majd `tr()` |
| Importáláskor definiált üzenet — űrlapfelirat, enum, konstans | `lazy_gettext()` vagy `lazy_pgettext()` |
| A megfogalmazást egy darabszám dönti el | `ngettext()` / `npgettext()`, a fenti alakok bármelyikében |
| Minta renderelése katalógus közreműködése nélkül | `compile_template()` |

Minden, ami alább jön, ez az öt, ebben a sorrendben.

## Katalógus kötése { #binding-a-catalog }

Az ajánlott felépítés a gettext osztályalapú használatát tükrözi: köss be
egyszer egy szabványos fordításobjektumot, és használd a hívható feldolgozót
`_` néven.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

A modulszintű függvények a standard könyvtár neveit és pozicionális-only
hívási konvencióját követik:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

A `tr` és az `ntr` a `gettext`, illetve az `ngettext` pontos aliasa.

## Kérésenkénti nyelv { #per-request-language }

Egy webes keretrendszer kérésenként választ nyelvet. Köss be a kérés
fordításait az aktuális kontextusba, és minden modulszintű hívás arra a
nyelvre oldódik fel, biztonságosan a párhuzamos kérések között is:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

A `set_translations(translations)` `with` blokk nélkül köt be, azoknak a
keretrendszereknek, amelyek maguk kezelik a kérés életciklusát; a
`get_translations()` az aktuális kötést olvassa ki. Egy explicit
`translations=` argumentum mindig felülírja a kontextust, a kötetlen kontextus
pedig a standard könyvtár globálisan telepített gettext-függvényeire esik
vissza. Flaskhoz és ASGI-köztesréteghez kidolgozott példák az
[Éles üzemben](workflow.md#binding-a-language-at-runtime) oldalon vannak.

## Késleltetett fordítás { #deferred-translation }

A t-string mohón kapja el az értékeit, ami rossz egy importáláskor definiált
szöveg — űrlapfelirat, enum-érték, modulkonstans — esetében, amelynek abban a
nyelvben kell megjelennie, amely a *használatakor* aktív.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

A `LazyString` a `str()`, a `format()` és az f-stringek révén jelenik meg, és
egyenlőnek bizonyul a renderelt szövegével.

!!! note "Szándékosan nem hashelhető"

    Egy `LazyString` szövege az aktív nyelvtől függ, így a hasítóértéke
    nyelvváltáskor megváltozna, és csendben megrongálná az őt tartalmazó
    halmazokat és szótárakat. Hívd meg előbb a `str()` függvényt, ha kulcsra
    van szükséged.

A `strict` ott dől el, ahol az üzenetet megírják, nem ott, ahol megjelenik:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Egy késleltetett szöveg ott jelenik meg, ahol végül felhasználják — egy
sablonban, egy űrlapon, egy naplósorban —, és az a hely ritkán tudja, hogy
tesztfutásról vagy éles üzemről van-e szó. A `strict=True` átadása a
definíciónál teszi lehetővé, hogy ugyanaz a
[CI-ben hangos, éles üzemben elnéző](#what-happens-when-a-catalog-is-wrong)
döntés érvényesüljön egy olyan szövegre is, amely nem a hívási helyén jelenik
meg.

A többesszám-alakok futásidejű darabszámtól függnek, ezért azokat mohón
rendereld az `ngettext` segítségével, ott, ahol a darabszám ismert.

## Több nyelv egyszerre { #several-languages-at-once }

Egy kérésnek gyakran több nyelvre is szüksége van: egy oldal, amely az
olvasónak renderelődik, miközben értesítést tesz sorba egy másik nyelvre
állított fiókhoz, vagy egy összefoglaló, amely minden résztvevőt a saját
nyelvén idéz. A kötések egymásba ágyazódnak, és a belső blokkból kilépve
visszaáll a külső.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Címzettek listáján a késleltetett szövegek végzik a munkát: az üzenetet egyszer
írod meg, importáláskor, és nyelvenként egyszer renderelődik.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

A kötés `ContextVar`, nem közös objektumon tartott verem, így az egymást átfedő
kérések nem vehetik át egymás nyelvét — még abban az esetben sem, amikor abban
a sorrendben *lépnek ki* a blokkjaikból, ahogy beléptek; épp ezt az
átlapolódást rontja el a verem. Nyelvenként betölteni egy katalógust olcsó: a
`gettext.translation()` minden `.mo` fájlt egyszer olvas be, és olyan
másolatokat ad ki, amelyek osztoznak a beolvasott katalóguson.

!!! warning "Az, hogy a munkaszál örökli-e a kötést, a buildtől függ"

    Egy puszta `threading.Thread`, illetve a `ThreadPoolExecutor.submit` vagy
    a hívó kontextusának másolatával, vagy egy üres kontextussal indul, és
    hogy melyikkel, azt a `sys.flags.thread_inherit_context` mondja meg — a
    szabad szálú buildeken alapértelmezés szerint igaz, mindenhol máshol
    hamis. Ugyanaz a kód tehát 3.14t alatt a kötött nyelvet, 3.14 alatt a
    folyamatszintű globális katalógust rendereli. Add át a kontextust ahelyett, hogy az
    alapértelmezésre hagyatkoznál:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    Az `asyncio.to_thread` ezt már megteszi helyetted.

## Honosított értékek { #locale-aware-values }

Ez a könyvtár azt dönti el, *hová* kerül egy érték a lefordított üzenetben.
Magát az értéket nem honosítja. A `{amount:,.2f}` rögzített viselkedésű
Python-formátumleíró — vessző minden harmadik számjegynél, pont a tizedesek
előtt —, és ugyanazokat a karaktereket állítja elő, bármilyen nyelvű is az
üzenet:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

A német ezt a számot `1.234,50`, a francia `1 234,50` alakban írja, a hindi
pedig az `1234567` értéket `12,34,567` alakban csoportosítja, nem
`1,234,567` alakban. A számok, pénznemek, dátumok, időpontok és mértékegységek
a [Babelhez][babel-numbers] tartoznak. Előbb formázd meg az értéket, aztán
helyezd el a kész szöveget:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Számlált üzenetnél a szám két feladatot lát el — kiválasztja a
többesszám-alakot, és meg is jelenik a szövegben —, és csak a második
honosítandó. A kiválasztáshoz tartsd meg a nyers darabszámot, a
megjelenítéshez pedig a megformázott szöveget add át:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

A hívás előtti formázás egyben az is, ami a formátumleírót kívül tartja a
katalóguson: amit a fordító lát, az kész szövegdarab, nem pedig egy szám plusz
utasítások arra, hogyan kell renderelni.

## Mi történik, ha egy katalógus hibás { #what-happens-when-a-catalog-is-wrong }

Ha egy fordítás helyőrzői nem egyeznek a forráséival — hiányzó, ismeretlen
vagy átformázott mező, amely átcsúszott az ellenőrzésen kézzel szerkesztett
MO-ból, vendorolt katalógusból vagy az ellenőrzőt kihagyó folyamatból —, az
alapértelmezés a forrásüzenet renderelése kivétel helyett. Ez a gettext
saját szerződését tükrözi: rossz katalógus soha nem töri el az alkalmazást.

Ha a `Hello {name}` fordítása `こんにちは {nombre}`, a renderelés sikerül, és
egyetlen figyelmeztetés megy a `gettext_tstrings` naplózójába:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

A figyelmeztetés üzenetenként és mintánként egyszer szólal meg, nem
renderelésenként, így egy elromlott katalógusbejegyzés nem árasztja el a
naplót.

Teszteléshez és CI-hez választhatod a hangos hibázást:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Ugyanaz a keresés ekkor kivételt vált ki, ugyanazt a mondatot hozva, csak a
„using source text” fele nélkül:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Ezek az üzenetek annak szólnak, aki tehet ellenük, ami katalógusprobléma
esetén gyakrabban fordító, mint programozó — ezért ott, ahol egy helyőrző
jelen lévőnek *látszik*, de mégsem az, az üzenet megmagyarázza, miért, ahelyett
hogy megismételné, hogy hiányzik. Teljes szélességű kapcsos zárójelek,
megkettőzött `{{name}}`, láthatatlan nem törhető szóköz, cirill betű a latinok
között: mindegyiknek saját megfogalmazása van, példákkal együtt felsorolva a
[Fordítóknak](translators.md#reading-a-failure-message) oldalon. Azt az oldalt
úgy írtuk, hogy oda lehessen adni annak, aki a `.po` fájlt szerkeszti.

## Minta renderelése katalógus nélkül { #rendering-a-pattern-without-a-catalog }

A `compile_template` egy szinttel lejjebb teszi elérhetővé ugyanezt a
gépezetet: egy t-stringből előállítja a msgidjét és a hozzá kötött
értékkészletet, és bármilyen mintát rendereli, amit átadsz neki.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

A `render` ugyanazon szabályok szerint ellenőriz, és eltérés esetén **mindig
kivételt vált ki**. Itt nincs elnéző mód: az elnézés azért létezik, hogy egy
*katalógusbeli* keresés visszaeshessen a forrásszövegre, egy általad átadott
mintának viszont nincs mihez visszaesnie.

## Biztonság és hatókör { #safety-and-scope }

Ez érvényes:

```python
tr(t"Hello {name}")
```

Ezeket szándékosan elutasítjuk:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Számold ki előbb az értelmes értéket:

```python
name = user.display_name()
tr(t"Hello {name}")
```

A megszorítás stabil katalóguskulcsokat eredményez, használható neveket ad a
fordítóknak, és megakadályozza, hogy egy lefordított szövegből kifejezésnyelv
váljon.

A garancia a *szerkezetre és a formázásra* korlátozódik: egy fordítást soha
nem értékelünk ki, és soha nem adhat hozzá attribútum-hozzáférést, hívásokat,
konverziókat vagy formátumleírókat. Két dolog a hívó felelőssége marad,
pontosan úgy, mint a stdlib gettextnél — a renderelt kimenet **escape-elése**
a célja szerint (HTML, shell, terminál), valamint a **katalógus
sértetlensége**, hiszen egy ellenséges katalógus megismételhet egy helyőrzőt a
kimenet méretének felnagyítására, ami minden helyőrző-alapú i18n
sajátossága.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
