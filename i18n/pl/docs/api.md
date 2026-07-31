---
description: "Każda nazwa eksportowana przez gettext_tstrings: funkcje, Translator, wiązanie kontekstu, leniwe łańcuchy i błędy."
---

# API

Wszystko poniżej jest eksportowane z `gettext_tstrings`. Nic innego nie jest
publiczne. Ta strona to spis sygnatur; opracowane przykłady każdej funkcji
znajdziesz w [przewodniku](guide.md).

## Tłumaczenie { #translating }

Każda funkcja przyjmuje swój t-string pozycyjnie i akceptuje dwa argumenty
nazwane: `translations` (wracający do wiązania kontekstowego, a potem do
globalnych funkcji biblioteki standardowej) i `strict` (patrz
[Przewodnik](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funkcja | Sygnatura |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias `gettext` |
| `ntr` | alias `ngettext` |

### `Translator`

Zamrożona dataclass wiążąca jeden obiekt tłumaczeń, żeby miejsca wywołań go
nie powtarzały.

```python
Translator(translations, strict=False)
```

Jest wywoływalna (`_(t"…")`) i niesie `gettext`, `ngettext`, `pgettext`,
`npgettext` oraz aliasy `tr` / `ntr`.

## Wiązanie kontekstu { #context-binding }

| Nazwa | Cel |
| --- | --- |
| `use_translations(translations)` | Zwiąż na czas bloku `with`, potem przywróć. |
| `set_translations(translations)` | Zwiąż bez bloku, dla cykli życia zarządzanych przez framework. |
| `get_translations()` | Odczytaj bieżące wiązanie albo `None`. |

Wiązanie jest `ContextVar`, więc jest per kontekst i bezpieczne przy
współbieżności.

## Łańcuchy odroczone { #deferred-strings }

| Nazwa | Cel |
| --- | --- |
| `lazy_gettext(template, /)` | Odrocz tłumaczenie do pierwszego użycia. |
| `lazy_pgettext(context, template, /)` | Forma z kontekstem. |
| `LazyString` | To, co obie zwracają. Renderuje się przez `str()` i `format()`, jest równy swojemu tekstowi i celowo niehashowalny. |

## Niższy poziom { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Skompiluj t-string, wykorzystując jego zbuforowany plan statyczny.

### `CompiledTemplate`

| Składnik | Znaczenie |
| --- | --- |
| `.msgid` | Stabilny identyfikator komunikatu gettext. |
| `.placeholders` | Nazwy symboli zastępczych w kolejności pierwszego wystąpienia. |
| `.render(pattern)` | Zwaliduj jeden wzorzec i wyrenderuj go. Przy niedopasowaniu **zawsze zgłasza wyjątek**. |

## Typy i błędy { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` dla czterech standardowych metod, wszystkich
wyłącznie pozycyjnych:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` i `Translations` z
Babel wszystkie go spełniają.

### Wyjątki { #exceptions }

| Klasa | Zgłaszana gdy |
| --- | --- |
| `TStringError` | Klasa bazowa dla obu poniższych. |
| `InvalidTemplateError` | **Źródłowy** t-string łamie konwencję — złożona interpolacja albo powtórzona nazwa z innym formatowaniem. |
| `InvalidTranslationError` | Robi to **tłumaczenie**. W domyślnym trybie łagodnym jest to logowane, a zamiast tego renderowany jest tekst źródłowy. |

## Punkty wejścia ekstrakcji { #extraction-entry-points }

Rejestrowane automatycznie przy instalacji; odwołujesz się do nich po
nazwie, nie przez import.

| Grupa | Nazwa | Używane przez |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` w `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatycznie. |

## Wydajność { #performance }

Pełny rachunek — co jest buforowane, po czym kluczują pamięci podręczne i
zmierzone liczby — to [Gorąca ścieżka](internals.md#the-hot-path). Wersja
skrócona: walidacja jest buforowana, nigdy pomijana, a całe renderowanie
kosztuje ułamek mikrosekundy. Uruchom benchmark na własnym celu:

```console
uv run python benchmarks/runtime.py
```
