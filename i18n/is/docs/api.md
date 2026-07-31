---
description: "Öll nöfnin sem gettext_tstrings flytur út: föllin, Translator, samhengisbindingin, latir strengir og villurnar."
---

# API

Allt hér að neðan er flutt út frá `gettext_tstrings`. Ekkert annað er
opinbert. Þessi síða er uppflettirit yfir undirskriftir; fyrir útfærð dæmi um
hvert fall, sjá [handbókina](guide.md).

## Að þýða { #translating }

Hvert fall tekur t-streng sinn eftir stöðu og tekur við tveimur
lykilorðaviðfangi: `translations` (sem fellur aftur í samhengisbindinguna og
þaðan í altæku föllin í staðalsafninu) og `strict` (sjá
[Handbók](guide.md#what-happens-when-a-catalog-is-wrong)).

| Fall | Undirskrift |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | samheiti `gettext` |
| `ntr` | samheiti `ngettext` |

### `Translator`

Frosið gagnaklasi sem bindur eitt þýðingahlutfall, svo að kallstaðir þurfi
ekki að endurtaka það.

```python
Translator(translations, strict=False)
```

Það er kallanlegt (`_(t"…")`) og ber `gettext`, `ngettext`, `pgettext`,
`npgettext` og samheitin `tr` / `ntr`.

## Samhengisbinding { #context-binding }

| Nafn | Tilgangur |
| --- | --- |
| `use_translations(translations)` | Bindur á meðan `with`-blokk stendur, endurheimtir svo. |
| `set_translations(translations)` | Bindur án blokkar, fyrir líftíma sem umgjörð stýrir. |
| `get_translations()` | Les núverandi bindingu, eða `None`. |

Bindingin er `ContextVar`, svo hún er bundin samhengi og örugg í samhliða
keyrslu.

## Frestaðir strengir { #deferred-strings }

| Nafn | Tilgangur |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Frestar þýðingu fram að hverri birtingu. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Myndin með samhengi. |
| `LazyString` | Það sem bæði skila. Birtist gegnum `str()` og `format()` á því tungumáli sem bundið er á þeirri stundu, telst jafnt birtum texta sínum og er af ásettu ráði ekki tætanlegt. |

Unnin dæmi, þar á meðal hvers vegna `strict` á heima við skilgreininguna, eru
undir [Frestuð þýðing](guide.md#deferred-translation).

## Neðar í lögunum { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Vistþýðir t-streng og endurnýtir fasta áætlun hans úr skyndiminni.

### `CompiledTemplate`

| Meðlimur | Merking |
| --- | --- |
| `.msgid` | Stöðugt gettext-auðkenni skilaboðanna. |
| `.placeholders` | Nöfn staðgengla í röð fyrsta tilviks. |
| `.render(pattern)` | Athugar eitt mynstur og birtir það. **Varpar alltaf** ef ekki stemmir. |

## Tegundir og villur { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` fyrir stöðluðu aðferðirnar fjórar, allar
eingöngu eftir stöðu:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` og `Translations` úr
Babel uppfylla það öll.

### Frávörp

| Klasi | Varpað þegar |
| --- | --- |
| `TStringError` | Grunnklasi beggja hér að neðan. |
| `InvalidTemplateError` | **Frum**-t-strengurinn brýtur venjuna — flókin innskeyting, eða endurtekið nafn með ólíku sniði. |
| `InvalidTranslationError` | **Þýðingin** gerir það. Í sjálfgefna eftirláta hamnum er þetta skráð í atburðaskrá og frumtextinn birtur í staðinn. |

## Aðgangsstaðir útdráttar { #extraction-entry-points }

Skráðir sjálfkrafa við uppsetningu; þú vísar í þá með nafni, ekki með
innflutningi.

| Hópur | Nafn | Notað af |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method`-gildinu í `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, sjálfkrafa. |

## Afköst { #performance }

Öll frásögnin — hvað er geymt í skyndiminni, á hverju skyndiminnin lykla og
mældu tölurnar — er [Heita leiðin](internals.md#the-hot-path). Stutta
útgáfan: athugun er geymd í skyndiminni, aldrei sleppt, og öll birtingin
kostar brot úr míkrósekúndu. Keyrðu viðmiðunarmælinguna á þínu eigin
skotmarki:

```console
uv run python benchmarks/runtime.py
```
