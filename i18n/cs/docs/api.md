---
description: "Každý název, který gettext_tstrings exportuje: funkce, Translator, vazba kontextu, líné řetězce a chyby."
---

# API

Vše níže je exportováno z `gettext_tstrings`. Nic jiného není veřejné.
Tato stránka je referencí signatur; propracované příklady každé funkce
najdete v [průvodci](guide.md).

## Překládání { #translating }

Každá funkce přijímá svůj t-string pozičně a akceptuje dva pojmenované
argumenty: `translations` (spadající zpět na kontextovou vazbu a poté na
globální funkce standardní knihovny) a `strict` (viz
[Průvodce](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funkce | Signatura |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias `gettext` |
| `ntr` | alias `ngettext` |

### `Translator`

Zmrazená dataclass vážící jeden objekt překladů, aby jej místa volání
neopakovala.

```python
Translator(translations, strict=False)
```

Je volatelná (`_(t"…")`) a nese `gettext`, `ngettext`, `pgettext`,
`npgettext` a aliasy `tr` / `ntr`.

## Vazba kontextu { #context-binding }

| Název | Účel |
| --- | --- |
| `use_translations(translations)` | Naváže po dobu bloku `with`, poté obnoví předchozí stav. |
| `set_translations(translations)` | Naváže bez bloku, pro životní cykly řízené frameworkem. |
| `get_translations()` | Přečte aktuální vazbu, nebo `None`. |

Vazba je `ContextVar`, takže platí na kontext a je bezpečná při
souběžnosti.

## Odložené řetězce { #deferred-strings }

| Název | Účel |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Odloží překlad do prvního použití. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Kontextová podoba. |
| `LazyString` | To, co obě vracejí. Vykresluje se přes `str()` a `format()`, je roven svému textu a je záměrně nehashovatelný. |

## Nižší úroveň { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Zkompiluje t-string s využitím jeho kešovaného statického plánu.

### `CompiledTemplate`

| Člen | Význam |
| --- | --- |
| `.msgid` | Stabilní identifikátor zprávy gettextu. |
| `.placeholders` | Jména zástupných symbolů v pořadí prvního výskytu. |
| `.render(pattern)` | Zvaliduje jeden vzor a vykreslí jej. Při neshodě **vždy vyhodí výjimku**. |

## Typy a chyby { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` pro čtyři standardní metody, všechny
výhradně poziční:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` i `Translations` z
Babelu jej všechny splňují.

### Výjimky { #exceptions }

| Třída | Vyhazována když |
| --- | --- |
| `TStringError` | Základní třída pro obě níže uvedené. |
| `InvalidTemplateError` | **Zdrojový** t-string porušuje konvenci — složitá interpolace, nebo opakované jméno s odlišným formátováním. |
| `InvalidTranslationError` | Porušuje ji **překlad**. Ve výchozím shovívavém režimu se to zaloguje a místo toho se vykreslí zdrojový text. |

## Vstupní body extrakce { #extraction-entry-points }

Registrují se automaticky při instalaci; odkazujete se na ně jménem, ne
importem.

| Skupina | Název | Používá |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` v `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automaticky. |

## Výkon { #performance }

Úplný rozbor — co se kešuje, podle čeho keše klíčují a naměřená čísla —
je [Horká cesta](internals.md#the-hot-path). Krátká verze: validace se
kešuje, nikdy nepřeskakuje, a celé vykreslení stojí zlomek mikrosekundy.
Spusťte benchmark na vlastním cíli:

```console
uv run python benchmarks/runtime.py
```
