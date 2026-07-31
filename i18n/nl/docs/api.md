---
description: "Elke naam die gettext_tstrings exporteert: functies, de Translator, contextbinding, lazy strings en de fouten."
---

# API

Alles hieronder wordt geëxporteerd uit `gettext_tstrings`. Niets anders is
publiek. Deze pagina is de signatuurreferentie; voor uitgewerkte voorbeelden
van elke functie, zie de [handleiding](guide.md).

## Vertalen { #translating }

Elke functie neemt haar t-string positioneel en accepteert twee
keyword-argumenten: `translations` (met terugval op de contextbinding, dan
op de globale functies van de standaardbibliotheek) en `strict` (zie
[Handleiding](guide.md#what-happens-when-a-catalog-is-wrong)).

| Functie | Signatuur |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias van `gettext` |
| `ntr` | alias van `ngettext` |

### `Translator`

Een bevroren dataclass die één vertaalobject bindt, zodat aanroepplekken het
niet herhalen.

```python
Translator(translations, strict=False)
```

Hij is aanroepbaar (`_(t"…")`) en draagt `gettext`, `ngettext`, `pgettext`,
`npgettext` en de `tr`- / `ntr`-aliassen.

## Contextbinding { #context-binding }

| Naam | Doel |
| --- | --- |
| `use_translations(translations)` | Bind voor de duur van een `with`-blok, herstel daarna. |
| `set_translations(translations)` | Bind zonder blok, voor door frameworks beheerde levenscycli. |
| `get_translations()` | Lees de huidige binding, of `None`. |

De binding is een `ContextVar`, dus ze is per context en veilig onder
concurrency.

## Uitgestelde strings { #deferred-strings }

| Naam | Doel |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Stel een vertaling uit tot het eerste gebruik. |
| `lazy_pgettext(context, template, /, *, strict=False)` | De contextuele vorm. |
| `LazyString` | Wat beide teruggeven. Rendert via `str()` en `format()`, is gelijk aan zijn tekst, en is bewust unhashable. |

## Lager niveau { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compileer een t-string, met hergebruik van zijn gecachete statische plan.

### `CompiledTemplate`

| Lid | Betekenis |
| --- | --- |
| `.msgid` | De stabiele gettext-berichtidentifier. |
| `.placeholders` | Placeholdernamen in volgorde van eerste voorkomen. |
| `.render(pattern)` | Valideer één patroon en render het. **Raist altijd** bij een mismatch. |

## Typen en fouten { #types-and-errors }

### `Translations`

Een `runtime_checkable` `Protocol` voor de vier standaardmethoden, alle
positional-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` en Babels
`Translations` voldoen er alle drie aan.

### Excepties

| Klasse | Geraist wanneer |
| --- | --- |
| `TStringError` | Basisklasse voor de twee hieronder. |
| `InvalidTemplateError` | De **bron**-t-string breekt de conventie — een complexe interpolatie, of een herhaalde naam met andere opmaak. |
| `InvalidTranslationError` | De **vertaling** doet dat. In de standaard milde modus wordt dit gelogd en wordt de brontekst gerenderd. |

## Extractie-ingangen { #extraction-entry-points }

Automatisch geregistreerd bij installatie; je verwijst ernaar op naam, niet
via import.

| Groep | Naam | Gebruikt door |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | De `method` in `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatisch. |

## Performance { #performance }

Het volledige verhaal — wat er gecachet wordt, waarop de caches sleutelen,
en de gemeten cijfers — is [Het hete pad](internals.md#the-hot-path). De
korte versie: validatie wordt gecachet, nooit overgeslagen, en de hele
render kost een fractie van een microseconde. Draai de benchmark op je eigen
doel:

```console
uv run python benchmarks/runtime.py
```
