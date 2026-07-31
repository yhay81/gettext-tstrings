---
description: "Kiekvienas vardas, kurį eksportuoja gettext_tstrings: funkcijos, Translator, konteksto susiejimas, tingiosios eilutės ir klaidos."
---

# API

Viskas, kas žemiau, eksportuojama iš `gettext_tstrings`. Nieko daugiau nėra
viešo. Šis puslapis yra parašų žinynas; kiekvienos funkcijos išnagrinėtų
pavyzdžių ieškokite [vadove](guide.md).

## Vertimas { #translating }

Kiekviena funkcija savo t-eilutę priima poziciškai ir priima du raktažodinius
argumentus: `translations` (grįžtantį prie konteksto susiejimo, o tada prie
standartinės bibliotekos globalių funkcijų) ir `strict` (žr.
[Vadovas](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funkcija | Parašas |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` sinonimas |
| `ntr` | `ngettext` sinonimas |

### `Translator`

Užšaldyta duomenų klasė, susiejanti vieną vertimo objektą, kad iškvietimo
vietose jo nereikėtų kartoti.

```python
Translator(translations, strict=False)
```

Ji yra iškviečiama (`_(t"…")`) ir neša `gettext`, `ngettext`, `pgettext`,
`npgettext` bei `tr` / `ntr` sinonimus.

## Konteksto susiejimas { #context-binding }

| Vardas | Paskirtis |
| --- | --- |
| `use_translations(translations)` | Susieti `with` bloko trukmei, paskui atkurti. |
| `set_translations(translations)` | Susieti be bloko — karkaso valdomiems gyvavimo ciklams. |
| `get_translations()` | Nuskaityti dabartinį susiejimą arba `None`. |

Susiejimas yra `ContextVar`, todėl jis galioja kontekstui ir yra saugus
lygiagretumo sąlygomis.

## Atidėtos eilutės { #deferred-strings }

| Vardas | Paskirtis |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Atidėti vertimą iki pirmojo panaudojimo. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Kontekstinė forma. |
| `LazyString` | Tai, ką grąžina abi. Atvaizduojama per `str()` ir `format()`, lygybėje prilygsta savo tekstui ir tyčia neturi maišos. |

## Žemesnis lygmuo { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Sukompiliuoti t-eilutę, pakartotinai panaudojant jos podėlyje esantį statinį
planą.

### `CompiledTemplate`

| Narys | Reikšmė |
| --- | --- |
| `.msgid` | Stabilus gettext pranešimo identifikatorius. |
| `.placeholders` | Vietaženklių vardai pirmojo pasitaikymo tvarka. |
| `.render(pattern)` | Patikrinti vieną šabloną ir jį atvaizduoti. Neatitikus **visada kelia klaidą**. |

## Tipai ir klaidos { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` keturiems standartiniams metodams, visiems tik
su poziciniais argumentais:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` ir Babel `Translations` —
visi jį tenkina.

### Išimtys

| Klasė | Kada keliama |
| --- | --- |
| `TStringError` | Bazinė klasė abiem žemiau. |
| `InvalidTemplateError` | **Pirminė** t-eilutė laužo susitarimą — sudėtinga interpoliacija arba pasikartojantis vardas su skirtingu formatavimu. |
| `InvalidTranslationError` | Tą daro **vertimas**. Numatytuoju nuolaidžiu režimu tai užrašoma į žurnalą, o vietoj to atvaizduojamas pirminis tekstas. |

## Ištraukimo įėjimo taškai { #extraction-entry-points }

Užregistruojami automatiškai diegiant; į juos kreipiamasi vardu, o ne
importuojant.

| Grupė | Vardas | Kas naudoja |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` faile `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatiškai. |

## Našumas { #performance }

Pilna istorija — kas kešuojama, pagal ką podėliai raktuojami ir kokie išmatuoti
skaičiai — yra [Karštasis kelias](internals.md#the-hot-path). Trumpai:
tikrinimas kešuojamas, o ne praleidžiamas, ir visas atvaizdavimas kainuoja
mikrosekundės dalį. Paleiskite matavimą savo pačių aplinkoje:

```console
uv run python benchmarks/runtime.py
```
