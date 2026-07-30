---
description: "Alle öffentlichen Namen von gettext_tstrings: Funktionen, Translator, Kontextbindung, verzögerte Strings und Fehler."
---

# API

Alle folgenden Namen werden von `gettext_tstrings` exportiert. Andere Namen
sind nicht öffentlich.

## Übersetzung

Jede Funktion nimmt ihre t-string positionell sowie `translations` und `strict`
als Keyword-Argumente ([Anleitung](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funktion | Signatur |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | Alias für `gettext` |
| `ntr` | Alias für `ngettext` |

### `Translator`

Eine frozen Dataclass, die ein Übersetzungsobjekt bindet:

```python
Translator(translations, strict=False)
```

Sie ist aufrufbar (`_(t"…")`) und stellt `gettext`, `ngettext`, `pgettext`,
`npgettext`, `tr` und `ntr` bereit.

## Kontextbindung

| Name | Aufgabe |
| --- | --- |
| `use_translations(translations)` | Bindet für einen `with`-Block und stellt danach wieder her. |
| `set_translations(translations)` | Bindet ohne Block für frameworkverwaltete Lebenszyklen. |
| `get_translations()` | Liest die aktuelle Bindung oder liefert `None`. |

Die Bindung nutzt `ContextVar` und ist nebenläufigkeitssicher.

## Verzögerte Strings

| Name | Aufgabe |
| --- | --- |
| `lazy_gettext(template, /)` | Verschiebt die Übersetzung bis zur Nutzung. |
| `lazy_pgettext(context, template, /)` | Variante mit Kontext. |
| `LazyString` | Wird über `str()`, `format()` und f-strings gerendert, vergleicht sich mit Text und ist absichtlich nicht hashbar. |

## Low-Level-API

### `compile_template(template, /) -> CompiledTemplate`

Kompiliert eine t-string und verwendet ihren gecachten statischen Plan.

### `CompiledTemplate`

| Element | Bedeutung |
| --- | --- |
| `.msgid` | Stabiler gettext-Bezeichner. |
| `.placeholders` | Namen in der Reihenfolge ihres ersten Auftretens. |
| `.render(pattern)` | Prüft und rendert; **löst bei Abweichungen immer aus**. |

## Typen und Fehler

### `Translations`

Ein `runtime_checkable`-`Protocol` für die vier Standardmethoden:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` und Babels
`Translations` erfüllen dieses Protokoll.

### Exceptions

| Klasse | Wann |
| --- | --- |
| `TStringError` | Basisklasse. |
| `InvalidTemplateError` | Die Quell-t-string verletzt die Konvention. |
| `InvalidTranslationError` | Die Übersetzung verletzt sie; der weiche Modus protokolliert und rendert die Quelle. |

## Entry Points für Extraktion

| Gruppe | Name | Verwendung |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` in `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | automatisch durch `pybabel compile` |

## Performance

Eine Nachricht mit einem Feld benötigt auf Apple Silicon einschließlich
t-string-Erzeugung etwa 0,4 µs, ungefähr 2,5-mal so viel wie
`gettext(...).format(...)`. Caches sind begrenzt und halten nie interpolierte
Werte.

```console
uv run python benchmarks/runtime.py
```
