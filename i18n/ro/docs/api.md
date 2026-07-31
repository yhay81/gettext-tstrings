---
description: "Fiecare nume exportat de gettext_tstrings: funcțiile, Translator, legarea de context, șirurile amânate și erorile."
---

# API

Tot ce urmează este exportat din `gettext_tstrings`. Nimic altceva nu este
public. Această pagină este referința semnăturilor; pentru exemple lucrate ale
fiecărei funcții, vezi [ghidul](guide.md).

## Traducerea { #translating }

Fiecare funcție își primește t-stringul pozițional și acceptă două argumente
cu cuvânt-cheie: `translations` (care revine la legarea de context, apoi la
funcțiile globale ale bibliotecii standard) și `strict`
(vezi [Ghidul](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funcție | Semnătură |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias pentru `gettext` |
| `ntr` | alias pentru `ngettext` |

### `Translator`

Un dataclass înghețat care leagă un singur obiect de traducere, astfel încât
punctele de apel să nu îl repete.

```python
Translator(translations, strict=False)
```

Este apelabil (`_(t"…")`) și poartă cu sine `gettext`, `ngettext`, `pgettext`,
`npgettext` și aliasurile `tr` / `ntr`.

## Legarea de context { #context-binding }

| Nume | Scop |
| --- | --- |
| `use_translations(translations)` | Leagă pe durata unui bloc `with`, apoi restaurează. |
| `set_translations(translations)` | Leagă fără un bloc, pentru cicluri de viață gestionate de framework. |
| `get_translations()` | Citește legarea curentă, sau `None`. |

Legarea este o `ContextVar`, deci este per context și sigură sub concurență.

## Șiruri amânate { #deferred-strings }

| Nume | Scop |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Amână traducerea până la fiecare randare. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Forma cu context. |
| `LazyString` | Ce returnează amândouă. Se randează prin `str()` și `format()` în oricare limbă este legată în acel moment, se compară egal cu textul său randat și este intenționat nehashabil. |

Exemple lucrate, inclusiv de ce `strict` își are locul la definiție, se află sub
[Traducere amânată](guide.md#deferred-translation).

## Nivel mai jos { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compilează un t-string, reutilizându-i planul static din cache.

### `CompiledTemplate`

| Membru | Semnificație |
| --- | --- |
| `.msgid` | Identificatorul stabil de mesaj gettext. |
| `.placeholders` | Numele substituenților în ordinea primei apariții. |
| `.render(pattern)` | Validează un tipar și îl randează. **Ridică întotdeauna** o excepție la nepotrivire. |

## Tipuri și erori { #types-and-errors }

### `Translations`

Un `Protocol` `runtime_checkable` pentru cele patru metode standard, toate
strict pozițional:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` și `Translations` de la
Babel îl satisfac toate.

### Excepții

| Clasă | Ridicată când |
| --- | --- |
| `TStringError` | Clasa de bază pentru amândouă cele de mai jos. |
| `InvalidTemplateError` | T-stringul **sursă** încalcă convenția — o interpolare complexă, sau un nume repetat cu formatare diferită. |
| `InvalidTranslationError` | O încalcă **traducerea**. În modul permisiv implicit acest lucru este consemnat în jurnal, iar în loc se randează textul sursă. |

## Puncte de intrare pentru extragere { #extraction-entry-points }

Înregistrate automat la instalare; te referi la ele după nume, nu prin import.

| Grup | Nume | Folosit de |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method`-ul din `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automat. |

## Performanță { #performance }

Relatarea completă — ce anume se pune în cache, pe ce fac cache-urile cheie și
cifrele măsurate — este [Calea fierbinte](internals.md#the-hot-path). Versiunea
scurtă: validarea este pusă în cache, niciodată sărită, iar randarea întreagă
costă o fracțiune de microsecundă. Rulează benchmarkul pe ținta ta:

```console
uv run python benchmarks/runtime.py
```
