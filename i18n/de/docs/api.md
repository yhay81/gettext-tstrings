---
description: "Alle öffentlichen Namen von gettext_tstrings: Funktionen, Translator, Kontextbindung, verzögerte Strings und Fehler."
---

# API

Alle folgenden Namen werden von `gettext_tstrings` exportiert. Andere Namen
sind nicht öffentlich. Diese Seite ist die Signaturreferenz; ausgearbeitete
Beispiele zu jeder Funktion stehen in der [Anleitung](guide.md).

## Übersetzung { #translating }

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

## Kontextbindung { #context-binding }

| Name | Aufgabe |
| --- | --- |
| `use_translations(translations)` | Bindet für einen `with`-Block und stellt danach wieder her. |
| `set_translations(translations)` | Bindet ohne Block für frameworkverwaltete Lebenszyklen. |
| `get_translations()` | Liest die aktuelle Bindung oder liefert `None`. |

Die Bindung nutzt `ContextVar` und ist nebenläufigkeitssicher.

## Verzögerte Strings { #deferred-strings }

| Name | Aufgabe |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Verschiebt die Übersetzung bis zum jeweiligen Rendern. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Variante mit Kontext. |
| `LazyString` | Was beide zurückgeben. Wird über `str()` und `format()` in der Sprache gerendert, die in diesem Moment gebunden ist, vergleicht sich gleich mit seinem gerenderten Text und ist absichtlich nicht hashbar. |

Ausgearbeitete Beispiele, darunter warum `strict` an die Definition gehört,
stehen unter [Verzögerte Übersetzung](guide.md#deferred-translation).

## Low-Level-API { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Kompiliert eine t-string und verwendet ihren gecachten statischen Plan.

### `CompiledTemplate`

| Element | Bedeutung |
| --- | --- |
| `.msgid` | Stabiler gettext-Bezeichner. |
| `.placeholders` | Namen in der Reihenfolge ihres ersten Auftretens. |
| `.render(pattern)` | Prüft und rendert; **löst bei Abweichungen immer aus**. |

## Typen und Fehler { #types-and-errors }

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

## Entry Points für Extraktion { #extraction-entry-points }

| Gruppe | Name | Verwendung |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` in `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | automatisch durch `pybabel compile` |

## Performance { #performance }

Die vollständige Darstellung — was gecacht wird, worauf die Caches schlüsseln
und die gemessenen Zahlen — steht in
[Der Hot Path](internals.md#the-hot-path). Die Kurzfassung: Die Validierung
wird gecacht, nie übersprungen, und das gesamte Rendern kostet einen Bruchteil
einer Mikrosekunde. Führe den Benchmark auf deinem eigenen Zielsystem aus:

```console
uv run python benchmarks/runtime.py
```
