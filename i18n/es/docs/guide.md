---
description: "La API de ejecución: qué punto de entrada usar, vincular un catálogo, idiomas por petición, cadenas diferidas, valores dependientes del locale y cómo se informa de una traducción incorrecta."
---

# Guía

Esta página es la referencia de tiempo de ejecución: todo lo que hace el
*código de tu aplicación* con esta biblioteca una vez que existen los
catálogos. Si aún no has visto el ciclo completo —marcar, extraer, traducir,
compilar, ejecutar—, el [tutorial](tutorial.md) lo recorre una vez en cinco
minutos; la creación y validación de catálogos se trata en
[Extracción](extraction.md), y cómo un equipo mantiene el ciclo en marcha
—ciclos de actualización, CI, plataformas de traducción— se explica en
[En producción](workflow.md).

## ¿Qué punto de entrada debo usar? { #which-entry-point-should-i-use }

El paquete exporta varias formas de traducir un mensaje porque las aplicaciones
vinculan un idioma de maneras muy distintas. Elige según cómo decide tu programa
en qué idioma está:

| Tu situación | Usa |
| --- | --- |
| Un solo idioma para todo el proceso: una CLI, una app de escritorio, un script | `Translator`, invocado como `_` |
| Un idioma por petición o por tarea asíncrona: una aplicación web | `use_translations()` alrededor del trabajo y después `tr()` |
| Un mensaje definido durante el import: una etiqueta de formulario, un enum, una constante | `lazy_gettext()` o `lazy_pgettext()` |
| Una cantidad decide la redacción | `ngettext()` / `npgettext()`, en cualquiera de las formas anteriores |
| Renderizar un pattern sin catálogo de por medio | `compile_template()` |

Todo lo que sigue son esos cinco casos, en ese orden.

## Vincular un catálogo { #binding-a-catalog }

La forma recomendada refleja el uso de gettext basado en clases: vincula una vez
un objeto de traducción estándar y utiliza el procesador invocable como `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Las funciones de módulo siguen los nombres y la convención de argumentos solo
posicionales de la biblioteca estándar:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` y `ntr` son alias exactos de `gettext` y `ngettext`.

## Idioma por petición { #per-request-language }

Un framework web elige un idioma para cada petición. Vincula las traducciones de
la petición al contexto actual y todas las llamadas de módulo se resolverán en
ese idioma, de forma segura incluso entre peticiones concurrentes:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` vincula sin bloque `with` para los frameworks
que administran el ciclo de vida por su cuenta; `get_translations()` lee la
vinculación actual. Un argumento `translations=` explícito siempre prevalece
sobre el contexto. Si no hay vinculación, se utilizan las funciones gettext
instaladas globalmente en la biblioteca estándar. Hay ejemplos completos para
Flask y middleware ASGI en la página
[En producción](workflow.md#binding-a-language-at-runtime).

## Traducción diferida { #deferred-translation }

Una t-string captura sus valores de inmediato. Eso no sirve para una cadena
definida durante el import —una etiqueta de formulario, un valor enum o una
constante de módulo— que debe renderizarse en el idioma activo cuando se *usa*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Un `LazyString` se renderiza mediante `str()`, `format()` y f-strings, y se
compara como igual a su texto renderizado.

!!! note "Deliberadamente sin hash"

    El texto de un `LazyString` depende del idioma activo. Si su hash cambiara al
    cambiar de idioma, corrompería silenciosamente cualquier set o dict que lo
    contuviera. Llama primero a `str()` si necesitas una clave.

`strict` se decide donde se escribe el mensaje, no donde se renderiza:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Una cadena diferida se renderiza allí donde acaba usándose —dentro de una
plantilla, un formulario o una línea de log— y ese lugar rara vez sabe si se
trata de una ejecución de pruebas o de producción. Pasar `strict=True` en la
definición es lo que permite aplicar la misma elección
[estricta en CI, permisiva en producción](#what-happens-when-a-catalog-is-wrong)
a una cadena que no se renderiza en su punto de llamada.

Las formas plurales dependen de una cantidad en tiempo de ejecución, así que se
renderizan inmediatamente con `ngettext` donde se conoce esa cantidad.

## Varios idiomas a la vez { #several-languages-at-once }

Una misma petición necesita a menudo más de un idioma: una página renderizada
para el lector que además encola una notificación a una cuenta configurada en
otro, o un resumen que cita a cada participante en el suyo. Las vinculaciones se
anidan, y al salir del bloque interior se restaura la del exterior.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Sobre una lista de destinatarios, el trabajo lo hacen las cadenas diferidas: el
mensaje se escribe una sola vez, en el import, y se renderiza una vez por idioma.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

La vinculación es un `ContextVar`, no una pila guardada en un objeto compartido,
así que las peticiones que se solapan no pueden tomar el idioma de otra
—incluido el caso en que *salen* de sus bloques en el mismo orden en que
entraron, que es el entrelazado que una pila LIFO resuelve mal—. Cargar un
catálogo por idioma es barato: `gettext.translation()` analiza cada `.mo` una
sola vez y entrega copias que comparten el catálogo ya analizado.

!!! warning "Que un hilo de trabajo herede la vinculación depende de la build"

    Un `threading.Thread` sin más, o `ThreadPoolExecutor.submit`, arranca o bien
    desde una copia del contexto de quien llama o bien desde uno vacío, y cuál de
    las dos cosas lo decide `sys.flags.thread_inherit_context` —verdadero por
    omisión en las builds free-threaded, falso en todo lo demás—. Por eso el
    mismo código renderiza el idioma vinculado en 3.14t y el catálogo global del
    proceso en 3.14. Pasa el contexto en lugar de depender del valor por omisión:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` ya lo hace por ti.

## Valores dependientes del locale { #locale-aware-values }

Esta biblioteca decide *dónde* aparece un valor dentro de un mensaje traducido.
No localiza el valor en sí. `{amount:,.2f}` es una especificación de formato de
Python con un comportamiento fijo —una coma cada tres dígitos y un punto antes
de los decimales— y produce los mismos caracteres sea cual sea el idioma del
mensaje:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

El alemán escribe ese número `1.234,50`; el francés, `1 234,50`; y el hindi
agrupa `1234567` como `12,34,567` en lugar de `1,234,567`. Los números, las
monedas, las fechas, las horas y las unidades son cosa de [Babel][babel-numbers].
Formatea primero el valor y coloca después la cadena ya terminada:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

En un mensaje con cantidad, el número hace dos trabajos —selecciona la forma
plural y aparece en el texto— y solo el segundo se localiza. Conserva la
cantidad en bruto para la selección y pasa la cadena formateada para mostrarla:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatear antes de la llamada es también lo que mantiene una especificación de
formato fuera del catálogo: lo que ve un traductor es un fragmento de texto ya
terminado, no un número acompañado de instrucciones para representarlo.

## Qué ocurre cuando un catálogo es incorrecto { #what-happens-when-a-catalog-is-wrong }

Si los marcadores de una traducción no coinciden con el origen —un campo
ausente, desconocido o reformateado que eludió la validación, procedente de un MO
editado a mano, un catálogo de un proveedor o un pipeline que omite el
checker—, el comportamiento predeterminado es renderizar el mensaje de origen en
vez de lanzar una excepción. Así se respeta el contrato de gettext: un catálogo
incorrecto nunca debe romper la aplicación.

Si `Hello {name}` se traduce como `こんにちは {nombre}`, el renderizado tiene
éxito y se envía una advertencia al logger `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

La advertencia se emite una vez por combinación de mensaje y pattern, no una
vez por renderizado, para que una entrada defectuosa no inunde el registro.

En pruebas y CI se puede optar por fallar de inmediato:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

La misma búsqueda lanza entonces una excepción con la misma frase, pero sin la
parte «using source text»:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Estos mensajes están escritos para quien pueda resolver el problema, que en un
catálogo suele ser un traductor más que un programador; por eso, cuando un
marcador parece estar presente pero no lo está, el mensaje explica el motivo en
lugar de repetir que falta. Llaves de ancho completo, un `{{name}}` duplicado,
un espacio de no separación invisible, una letra cirílica entre latinas: cada
caso tiene su propia redacción, y todos están enumerados con ejemplos en
[Para traductores](translators.md#reading-a-failure-message). Esa página está
escrita para entregársela a quien edita el `.po`.

## Renderizar un pattern sin catálogo { #rendering-a-pattern-without-a-catalog }

`compile_template` expone el mismo mecanismo un nivel más abajo: convierte una
t-string en su msgid y un conjunto vinculado de valores, y renderiza cualquier
pattern proporcionado.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` valida con las mismas reglas y **siempre lanza** si no coincide. Aquí no
existe modo lenient: se utiliza para que una búsqueda de *catálogo* pueda volver
al texto de origen, y un pattern proporcionado directamente no tiene origen al
que volver.

## Seguridad y alcance { #safety-and-scope }

Esto es válido:

```python
tr(t"Hello {name}")
```

Esto se rechaza deliberadamente:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Calcula primero un valor con significado:

```python
name = user.display_name()
tr(t"Hello {name}")
```

La restricción produce claves de catálogo estables, ofrece nombres útiles a los
traductores y evita que una cadena traducida se convierta en un lenguaje de
expresiones.

La garantía se limita a la *estructura y el formato*: una traducción nunca se
evalúa ni puede añadir accesos a atributos, llamadas, conversiones o
especificaciones de formato. Dos responsabilidades siguen correspondiendo al
llamador, igual que con gettext de la biblioteca estándar: **escapar** el
resultado para su destino (HTML, shell o terminal) y mantener la **integridad
del catálogo**. Un catálogo hostil puede repetir un marcador para amplificar el
tamaño de la salida, algo inherente a cualquier i18n basado en marcadores.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
