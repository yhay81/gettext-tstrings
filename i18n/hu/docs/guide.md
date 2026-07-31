---
description: "A futásidejű API: katalógus kötése, kérésenkénti nyelvek, késleltetett szövegek, és hogyan jelenti a könyvtár a hibás fordítást."
---

# Kézikönyv

Ez az oldal a futásidejű referencia: mindaz, amit az *alkalmazáskódod* csinál
ezzel a könyvtárral, ha már vannak katalógusok. Ha még nem láttad a teljes
ciklust — megjelölés, kinyerés, fordítás, bináris fordítás, futtatás —, az
[oktatóanyag](tutorial.md) öt perc alatt végigjárja egyszer; a katalógusok
létrehozását és ellenőrzését a [Kinyerés](extraction.md) tárgyalja, azt pedig,
hogyan tartja egy csapat mozgásban a ciklust — frissítési körök, CI, fordítási
platformok —, az [Éles üzemben](workflow.md).

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

A többesszám-alakok futásidejű darabszámtól függnek, ezért azokat mohón
rendereld az `ngettext` segítségével, ott, ahol a darabszám ismert.

## Mi történik, ha egy katalógus hibás { #what-happens-when-a-catalog-is-wrong }

Ha egy fordítás helyőrzői nem egyeznek a forráséival — hiányzó, ismeretlen
vagy átformázott mező, amely átcsúszott az ellenőrzésen kézzel szerkesztett
MO-ból, vendorolt katalógusból vagy az ellenőrzőt kihagyó folyamatból —, az
alapértelmezés a forrásszöveg reprodukálása kivétel helyett. Ez a gettext
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

## Hibaüzenet olvasása { #reading-a-failure-message }

Ezek az üzenetek annak szólnak, aki tehet ellenük, ami katalógusprobléma
esetén gyakrabban fordító, mint programozó. Zsákutca csupán annyit jelenteni,
hogy a `{name}` hiányzik, amikor az olvasó pontosan ezeket a karaktereket
látja maga előtt, ezért ott, ahol egy helyőrző jelen lévőnek *látszik*, de
mégsem az, az üzenet megmondja, miért. A `Hello {name}` forrás ellenében az
alábbiak mindegyike a `translation does not match the source placeholders:`
alatt jelenik meg:

| Ezt mondja a fordítás | Ezt az okot adja |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (a körülötte lévő kapcsos zárójelek nem az ASCII `{` és `}`) |
| `こんにちは {{name}}` | `{name}` is missing (`{{name}}` alakban van írva, így kell escape-elni egy literális kapcsos zárójelet) |
| `こんにちは name` | `{name}` is missing (a név megjelenik, de nem kapcsos zárójelek között) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

A nem látható karakterek külön bánásmódot kapnak. A kapcsos zárójeleken belüli
nem törhető szóköz olyasmi, amit egy beviteli módszer állít elő, és amit
egyetlen szerkesztő sem mutat meg, ezért az üzenet kódponttal írja ki ahelyett,
hogy olyan karaktert nevezne meg, amelyet az olvasó nem talál:

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