---
description: "Kila jina ambalo gettext_tstrings hulitoa nje: vitendakazi, Translator, ufungaji wa muktadha, mifuatano ya uvivu, na hitilafu."
---

# API

Kila kitu kilicho hapa chini hutolewa nje kutoka `gettext_tstrings`. Hakuna
kingine kilicho cha umma. Ukurasa huu ni marejeo ya sahihi za vitendakazi; kwa
mifano iliyofanyiwa kazi ya kila kitendakazi, ona [mwongozo](guide.md).

## Kutafsiri { #translating }

Kila kitendakazi huchukua t-string yake kwa nafasi na hukubali hoja mbili za
maneno muhimu: `translations` (ikirejea kwenye ufungaji wa muktadha, kisha
kwenye vitendakazi vya jumla vya maktaba sanifu) na `strict` (ona
[Mwongozo](guide.md#what-happens-when-a-catalog-is-wrong)).

| Kitendakazi | Sahihi |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | kisawe cha `gettext` |
| `ntr` | kisawe cha `ngettext` |

### `Translator`

Dataclass iliyogandishwa inayofunga kitu kimoja cha tafsiri, ili mahali pa wito
pasirudie kukiandika.

```python
Translator(translations, strict=False)
```

Inaitika (`_(t"…")`) nayo hubeba `gettext`, `ngettext`, `pgettext`,
`npgettext`, pamoja na visawe vya `tr` / `ntr`.

## Ufungaji wa muktadha { #context-binding }

| Jina | Kusudi |
| --- | --- |
| `use_translations(translations)` | Funga kwa muda wa kizuizi cha `with`, kisha rejesha. |
| `set_translations(translations)` | Funga bila kizuizi, kwa mizunguko ya maisha inayosimamiwa na mfumo. |
| `get_translations()` | Soma ufungaji wa sasa, au `None`. |

Ufungaji ni `ContextVar`, hivyo ni wa kila muktadha na salama chini ya
utendaji sambamba.

## Mifuatano iliyoahirishwa { #deferred-strings }

| Jina | Kusudi |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Ahirisha tafsiri hadi kila uonyeshaji. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Umbo lenye muktadha. |
| `LazyString` | Kile ambacho zote mbili hurudisha. Huonyeshwa kupitia `str()` na `format()` katika lugha yoyote iliyofungwa wakati huo, hulingana sawa na maandishi yake yaliyoonyeshwa, nayo haihifadhiki kwa makusudi. |

Mifano iliyofanyiwa kazi, pamoja na sababu ya `strict` kuwekwa mahali pa
kufafanua, imo chini ya [Tafsiri iliyoahirishwa](guide.md#deferred-translation).

## Ngazi ya chini { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Kusanya t-string, ukitumia tena mpango wake tuli uliohifadhiwa akibani.

### `CompiledTemplate`

| Kiungo | Maana |
| --- | --- |
| `.msgid` | Kitambulisho thabiti cha ujumbe cha gettext. |
| `.placeholders` | Majina ya vishika nafasi kwa mpangilio wa kutokea kwa mara ya kwanza. |
| `.render(pattern)` | Thibitisha muundo mmoja na uuonyeshe. **Daima huinua hitilafu** zinapotofautiana. |

## Aina na hitilafu { #types-and-errors }

### `Translations`

`Protocol` yenye `runtime_checkable` kwa mbinu nne sanifu, zote za nafasi
pekee:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations`, na `Translations` ya
Babel zote huitosheleza.

### Hitilafu

| Klasi | Huinuliwa wakati |
| --- | --- |
| `TStringError` | Klasi msingi ya zote mbili zilizo hapa chini. |
| `InvalidTemplateError` | t-string **chanzo** huvunja makubaliano — kiingizio changamano, au jina linalorudiwa lenye uumbizaji tofauti. |
| `InvalidTranslationError` | **Tafsiri** ndiyo huvunja. Chini ya hali ya kuvumilia ya chaguo-msingi hii huandikwa kumbukumbuni na maandishi chanzo huonyeshwa badala yake. |

## Vituo vya kuingilia vya utoaji { #extraction-entry-points }

Husajiliwa kiotomatiki wakati wa usakinishaji; unavirejelea kwa jina, si kwa
kuviingiza.

| Kundi | Jina | Hutumiwa na |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` iliyo ndani ya `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, kiotomatiki. |

## Utendaji { #performance }

Maelezo kamili — kinachohifadhiwa akibani, akiba hutegemea nini, na nambari
zilizopimwa — yako katika [Njia yenye joto](internals.md#the-hot-path). Kwa
ufupi: uthibitishaji huhifadhiwa akibani, hauruki kamwe, na uonyeshaji mzima
hugharimu sehemu ndogo ya mikrosekunde. Endesha kipimo kwenye lengo lako
mwenyewe:

```console
uv run python benchmarks/runtime.py
```
