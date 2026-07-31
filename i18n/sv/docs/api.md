---
description: "Varje namn gettext_tstrings exporterar: funktionerna, Translator, kontextbindning, lata strängar och felen."
---

# API

Allt nedan exporteras från `gettext_tstrings`. Ingenting annat är publikt.
Den här sidan är signaturreferensen; för utarbetade exempel på varje
funktion, se [guiden](guide.md).

## Översätta { #translating }

Varje funktion tar sin t-string som positionsargument och accepterar två
nyckelordsargument: `translations` (som faller tillbaka till
kontextbindningen, sedan till standardbibliotekets globala funktioner) och
`strict` (se [Guide](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funktion | Signatur |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias för `gettext` |
| `ntr` | alias för `ngettext` |

### `Translator`

En frusen dataklass som binder ett översättningsobjekt, så att
anropsplatserna inte upprepar det.

```python
Translator(translations, strict=False)
```

Den är anropbar (`_(t"…")`) och bär `gettext`, `ngettext`, `pgettext`,
`npgettext` samt aliasen `tr` / `ntr`.

## Kontextbindning { #context-binding }

| Namn | Syfte |
| --- | --- |
| `use_translations(translations)` | Bind under ett `with`-blocks varaktighet, återställ sedan. |
| `set_translations(translations)` | Bind utan block, för ramverksstyrda livscykler. |
| `get_translations()` | Läs den aktuella bindningen, eller `None`. |

Bindningen är en `ContextVar`, så den är per kontext och säker under
samtidighet.

## Uppskjutna strängar { #deferred-strings }

| Namn | Syfte |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Skjut upp en översättning till första användning. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Den kontextuella formen. |
| `LazyString` | Vad båda returnerar. Renderar genom `str()` och `format()`, jämförs lika med sin text, och är avsiktligt ohashbar. |

## Lägre nivå { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Kompilera en t-string, med återanvändning av dess cachade statiska plan.

### `CompiledTemplate`

| Medlem | Betydelse |
| --- | --- |
| `.msgid` | Den stabila gettext-meddelandeidentifieraren. |
| `.placeholders` | Platshållarnamnen i första förekomstens ordning. |
| `.render(pattern)` | Validera ett mönster och rendera det. **Kastar alltid** vid en missmatchning. |

## Typer och fel { #types-and-errors }

### `Translations`

Ett `runtime_checkable` `Protocol` för de fyra standardmetoderna, alla med
enbart positionsargument:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` och Babels
`Translations` uppfyller det alla.

### Undantag

| Klass | Kastas när |
| --- | --- |
| `TStringError` | Basklass för de två nedan. |
| `InvalidTemplateError` | **Käll**-t-strängen bryter konventionen — en komplex interpolation, eller ett upprepat namn med olika formatering. |
| `InvalidTranslationError` | **Översättningen** gör det. Under det överseende standardläget loggas detta och källtexten renderas i stället. |

## Ingångspunkter för extrahering { #extraction-entry-points }

Registreras automatiskt vid installation; du hänvisar till dem med namn,
inte genom import.

| Grupp | Namn | Används av |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` i `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatiskt. |

## Prestanda { #performance }

Hela redogörelsen — vad som cachas, vad cacharna nycklas på, och de uppmätta
siffrorna — är [Den heta vägen](internals.md#the-hot-path). Den korta
versionen: valideringen cachas, hoppas aldrig över, och hela renderingen
kostar en bråkdel av en mikrosekund. Kör mätningen på ditt eget mål:

```console
uv run python benchmarks/runtime.py
```
