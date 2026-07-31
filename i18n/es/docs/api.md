---
description: "Todos los nombres que exporta gettext_tstrings: funciones, Translator, vinculación de contexto, cadenas diferidas y errores."
---

# API

Todo lo siguiente se exporta desde `gettext_tstrings`. Nada más es público.
Esta página es la referencia de firmas; para ejemplos prácticos de cada
función, consulta la [guía](guide.md).

## Traducción { #translating }

Cada función recibe su t-string como argumento posicional y acepta dos
argumentos nombrados: `translations` (con fallback primero a la vinculación del
contexto y después a las funciones globales de la biblioteca estándar) y
`strict` (consulta la [Guía](guide.md#what-happens-when-a-catalog-is-wrong)).

| Función | Firma |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias de `gettext` |
| `ntr` | alias de `ngettext` |

### `Translator`

Un dataclass frozen que vincula un objeto de traducción para no repetirlo en
cada llamada.

```python
Translator(translations, strict=False)
```

Es invocable (`_(t"…")`) y ofrece `gettext`, `ngettext`, `pgettext`,
`npgettext` y los alias `tr` / `ntr`.

## Vinculación de contexto { #context-binding }

| Nombre | Finalidad |
| --- | --- |
| `use_translations(translations)` | Vincula durante un bloque `with` y restaura al terminar. |
| `set_translations(translations)` | Vincula sin bloque para ciclos de vida administrados por un framework. |
| `get_translations()` | Lee la vinculación actual o devuelve `None`. |

La vinculación es un `ContextVar`, por lo que pertenece a cada contexto y es
segura con concurrencia.

## Cadenas diferidas { #deferred-strings }

| Nombre | Finalidad |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Difiere una traducción hasta el primer uso. |
| `lazy_pgettext(context, template, /, *, strict=False)` | La forma con contexto. |
| `LazyString` | El tipo que devuelven ambas. Se renderiza mediante `str()`, `format()` y f-strings, se compara con su texto y deliberadamente no admite hash. |

## Bajo nivel { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compila una t-string reutilizando su plan estático en caché.

### `CompiledTemplate`

| Miembro | Significado |
| --- | --- |
| `.msgid` | El identificador estable del mensaje gettext. |
| `.placeholders` | Los nombres de marcador en el orden de su primera aparición. |
| `.render(pattern)` | Valida y renderiza un pattern. **Siempre lanza** si no coincide. |

## Tipos y errores { #types-and-errors }

### `Translations`

Un `Protocol` `runtime_checkable` para los cuatro métodos estándar, todos con
argumentos solo posicionales:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` y `Translations` de Babel
lo satisfacen.

### Excepciones

| Clase | Cuándo se lanza |
| --- | --- |
| `TStringError` | Clase base de las dos siguientes. |
| `InvalidTemplateError` | La t-string de **origen** rompe la convención: una interpolación compleja o un nombre repetido con distinto formato. |
| `InvalidTranslationError` | La **traducción** la rompe. En el modo lenient predeterminado se registra y se renderiza el texto de origen. |

## Entry points de extracción { #extraction-entry-points }

Se registran automáticamente al instalar; se utilizan por nombre, no mediante
import.

| Grupo | Nombre | Uso |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | El `method` de `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automáticamente |

## Rendimiento { #performance }

El relato completo —qué se cachea, con qué claves y las cifras medidas— está
en [La ruta caliente](internals.md#the-hot-path). La versión corta: la
validación se cachea, nunca se omite, y el renderizado completo cuesta una
fracción de microsegundo. Ejecuta el benchmark en tu propio destino:

```console
uv run python benchmarks/runtime.py
```
