---
description: "Vsa imena, ki jih gettext_tstrings izvaža: funkcije, Translator, vezava konteksta, leni nizi in napake."
---

# API

Vse spodaj našteto je izvoženo iz `gettext_tstrings`. Nič drugega ni javno.
Ta stran je referenca podpisov; za razdelane primere posamezne funkcije
glejte [vodnik](guide.md).

## Prevajanje { #translating }

Vsaka funkcija sprejme svoj t-niz pozicijsko in dva imenovana argumenta:
`translations` (če ni podan, se zateče k vezavi konteksta, nato h globalnim
funkcijam standardne knjižnice) in `strict` (glejte
[Vodnik](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funkcija | Podpis |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | vzdevek za `gettext` |
| `ntr` | vzdevek za `ngettext` |

### `Translator`

Zamrznjen razred podatkov (dataclass), ki veže en prevajalni objekt, da ga
klicnim mestom ni treba ponavljati.

```python
Translator(translations, strict=False)
```

Je klicljiv (`_(t"…")`) in nosi `gettext`, `ngettext`, `pgettext`,
`npgettext` ter vzdevka `tr` / `ntr`.

## Vezava konteksta { #context-binding }

| Ime | Namen |
| --- | --- |
| `use_translations(translations)` | Veže za čas trajanja bloka `with`, nato obnovi prejšnje stanje. |
| `set_translations(translations)` | Veže brez bloka, za življenjske cikle, ki jih upravlja ogrodje. |
| `get_translations()` | Prebere trenutno vezavo ali `None`. |

Vezava je `ContextVar`, zato je vezana na kontekst in varna pri sočasnosti.

## Odloženi nizi { #deferred-strings }

| Ime | Namen |
| --- | --- |
| `lazy_gettext(template, /)` | Odloži prevod do prve rabe. |
| `lazy_pgettext(context, template, /)` | Kontekstna oblika. |
| `LazyString` | Tisto, kar vrneta obe. Izriše se skozi `str()` in `format()`, je enak svojemu besedilu in namenoma ni zgoščljiv. |

## Nižja raven { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Prevede t-niz in pri tem znova uporabi njegov predpomnjeni statični načrt.

### `CompiledTemplate`

| Član | Pomen |
| --- | --- |
| `.msgid` | Stabilni gettextov identifikator sporočila. |
| `.placeholders` | Imena ograd v vrstnem redu prvega pojava. |
| `.render(pattern)` | Preveri en vzorec in ga izriše. Ob neujemanju **vedno sproži izjemo**. |

## Tipi in napake { #types-and-errors }

### `Translations`

Protokol (`runtime_checkable` `Protocol`) za štiri standardne metode, vse
izključno pozicijske:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

Zadoščajo mu `gettext.NullTranslations`, `gettext.GNUTranslations` in Babelov
`Translations`.

### Izjeme

| Razred | Sproži se, kadar |
| --- | --- |
| `TStringError` | Osnovni razred za oba spodnja. |
| `InvalidTemplateError` | **Izvorni** t-niz krši dogovor — zapletena interpolacija ali ponovljeno ime z različnim formatiranjem. |
| `InvalidTranslationError` | Ga krši **prevod**. V privzetem prizanesljivem načinu se to zabeleži v dnevnik, izriše pa se izvorno besedilo. |

## Vstopne točke za ekstrakcijo { #extraction-entry-points }

Ob namestitvi se registrirajo samodejno; nanje se sklicujete po imenu, ne z
uvozom.

| Skupina | Ime | Uporablja |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | Vrednost `method` v `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, samodejno. |

## Zmogljivost { #performance }

Celoten opis — kaj se predpomni, po čem se predpomnilniki ključijo in izmerjene
številke — je [Vroča pot](internals.md#the-hot-path). Na kratko: preverjanje je
predpomnjeno, nikoli preskočeno, celoten izris pa stane delček mikrosekunde.
Merilnik poženite na svojem cilju:

```console
uv run python benchmarks/runtime.py
```
