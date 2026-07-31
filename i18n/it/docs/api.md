---
description: "Ogni nome che gettext_tstrings esporta: le funzioni, il Translator, il binding di contesto, le stringhe lazy e gli errori."
---

# API

Tutto ciò che segue è esportato da `gettext_tstrings`. Nient'altro è
pubblico. Questa pagina è il riferimento delle firme; per esempi svolti di
ogni funzione, vedi la [guida](guide.md).

## Tradurre { #translating }

Ogni funzione prende la sua t-string in modo posizionale e accetta due
argomenti a parola chiave: `translations` (che ripiega sul binding di
contesto, poi sulle funzioni globali della libreria standard) e `strict`
(vedi la [Guida](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funzione | Firma |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias di `gettext` |
| `ntr` | alias di `ngettext` |

### `Translator`

Una dataclass congelata che lega un oggetto di traduzione, così i punti di
chiamata non lo ripetono.

```python
Translator(translations, strict=False)
```

È chiamabile (`_(t"…")`) e porta con sé `gettext`, `ngettext`, `pgettext`,
`npgettext` e gli alias `tr` / `ntr`.

## Binding di contesto { #context-binding }

| Nome | Scopo |
| --- | --- |
| `use_translations(translations)` | Lega per la durata di un blocco `with`, poi ripristina. |
| `set_translations(translations)` | Lega senza un blocco, per cicli di vita gestiti dal framework. |
| `get_translations()` | Legge il binding corrente, oppure `None`. |

Il binding è una `ContextVar`, quindi è per contesto e sicuro sotto
concorrenza.

## Stringhe differite { #deferred-strings }

| Nome | Scopo |
| --- | --- |
| `lazy_gettext(template, /)` | Rinvia una traduzione al primo uso. |
| `lazy_pgettext(context, template, /)` | La forma con contesto. |
| `LazyString` | Ciò che entrambe restituiscono. Si rende attraverso `str()` e `format()`, risulta uguale al suo testo nei confronti ed è deliberatamente non hashabile. |

## Livello più basso { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compila una t-string, riutilizzando il suo piano statico in cache.

### `CompiledTemplate`

| Membro | Significato |
| --- | --- |
| `.msgid` | L'identificatore di messaggio gettext stabile. |
| `.placeholders` | I nomi dei segnaposto in ordine di prima occorrenza. |
| `.render(pattern)` | Valida un pattern e lo rende. **Solleva sempre** su una mancata corrispondenza. |

## Tipi ed errori { #types-and-errors }

### `Translations`

Un `Protocol` `runtime_checkable` per i quattro metodi standard, tutti con
soli argomenti posizionali:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` e le `Translations` di
Babel lo soddisfano tutte.

### Eccezioni

| Classe | Sollevata quando |
| --- | --- |
| `TStringError` | Classe base di entrambe le seguenti. |
| `InvalidTemplateError` | La t-string **sorgente** rompe la convenzione — un'interpolazione complessa, o un nome ripetuto con formattazione diversa. |
| `InvalidTranslationError` | Lo fa la **traduzione**. Nella modalità permissiva predefinita viene registrata nel log e al suo posto si rende il testo sorgente. |

## Entry point di estrazione { #extraction-entry-points }

Registrati automaticamente all'installazione; ci si riferisce a loro per
nome, non per import.

| Gruppo | Nome | Usato da |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | Il `method` in `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automaticamente. |

## Prestazioni { #performance }

Il resoconto completo — che cosa viene messo in cache, su che cosa le cache
fanno da chiave e i numeri misurati — è
[Il percorso caldo](internals.md#the-hot-path). La versione breve: la
validazione è in cache, mai saltata, e l'intero rendering costa una frazione
di microsecondo. Esegui il benchmark sul tuo bersaglio:

```console
uv run python benchmarks/runtime.py
```
