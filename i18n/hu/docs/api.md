---
description: "Minden név, amelyet a gettext_tstrings exportál: függvények, a Translator, kontextuskötés, lusta szövegek és a hibák."
---

# API

Az alábbi mindegyike a `gettext_tstrings` csomagból van exportálva. Semmi más
nem publikus. Ez az oldal a szignatúrareferencia; az egyes függvények
kidolgozott példáiért lásd a [kézikönyvet](guide.md).

## Fordítás { #translating }

Minden függvény pozicionálisan veszi át a t-stringjét, és két kulcsszavas
argumentumot fogad el: `translations` (amely a kontextuskötésre, majd a
standard könyvtár globális függvényeire esik vissza) és `strict` (lásd
[Kézikönyv](guide.md#what-happens-when-a-catalog-is-wrong)).

| Függvény | Szignatúra |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | a `gettext` aliasa |
| `ntr` | az `ngettext` aliasa |

### `Translator`

Fagyasztott dataclass, amely egyetlen fordításobjektumot köt be, hogy a hívási
helyeknek ne kelljen megismételniük.

```python
Translator(translations, strict=False)
```

Hívható (`_(t"…")`), és hordozza a `gettext`, `ngettext`, `pgettext`,
`npgettext` metódusokat, valamint a `tr` / `ntr` aliasokat.

## Kontextuskötés { #context-binding }

| Név | Mire való |
| --- | --- |
| `use_translations(translations)` | Bekötés egy `with` blokk idejére, majd visszaállítás. |
| `set_translations(translations)` | Bekötés blokk nélkül, keretrendszer által kezelt életciklushoz. |
| `get_translations()` | Az aktuális kötés kiolvasása, vagy `None`. |

A kötés `ContextVar`, tehát kontextusonkénti és biztonságos párhuzamosság
mellett.

## Késleltetett szövegek { #deferred-strings }

| Név | Mire való |
| --- | --- |
| `lazy_gettext(template, /)` | Egy fordítás elhalasztása az első használatig. |
| `lazy_pgettext(context, template, /)` | A kontextusos alak. |
| `LazyString` | Amit mindkettő visszaad. A `str()` és a `format()` révén jelenik meg, egyenlőnek bizonyul a szövegével, és szándékosan nem hashelhető. |

## Alacsonyabb szint { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Lefordít egy t-stringet, újrahasznosítva a gyorsítótárazott statikus tervét.

### `CompiledTemplate`

| Tag | Jelentése |
| --- | --- |
| `.msgid` | A stabil gettext-üzenetazonosító. |
| `.placeholders` | A helyőrzők nevei az első előfordulásuk sorrendjében. |
| `.render(pattern)` | Egyetlen minta validálása és renderelése. Eltérés esetén **mindig kivételt vált ki**. |

## Típusok és hibák { #types-and-errors }

### `Translations`

Egy `runtime_checkable` `Protocol` a négy szabványos metódusra, mind
pozicionális-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

A `gettext.NullTranslations`, a `gettext.GNUTranslations` és a Babel
`Translations` osztálya egyaránt kielégíti.

### Kivételek

| Osztály | Mikor váltódik ki |
| --- | --- |
| `TStringError` | Az alatta lévő kettő ősosztálya. |
| `InvalidTemplateError` | A **forrás** t-string sérti a konvenciót — összetett interpoláció, vagy eltérő formázással ismételt név. |
| `InvalidTranslationError` | A **fordítás** sérti. Az alapértelmezett elnéző módban ezt naplózzuk, és helyette a forrásszöveg jelenik meg. |

## Kinyerési belépési pontok { #extraction-entry-points }

Telepítéskor automatikusan regisztrálódnak; név szerint hivatkozol rájuk, nem
importtal.

| Csoport | Név | Mi használja |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | A `method` a `babel.cfg` fájlban. |
| `babel.checkers` | `gettext_tstrings` | A `pybabel compile`, automatikusan. |

## Teljesítmény { #performance }

A teljes beszámoló — mit gyorsítótárazunk, mire kulcsolnak a gyorsítótárak, és
mik a mért számok — [A forró útvonal](internals.md#the-hot-path) oldalon
olvasható. Röviden: a validálás gyorsítótárazódik, sosem marad ki, és az egész
renderelés a mikroszekundum töredékébe kerül. Futtasd a benchmarkot a saját
célkörnyezeteden:

```console
uv run python benchmarks/runtime.py
```