---
description: "El mismo mensaje traducible escrito con formato %, .format(), cadenas $ de flufl.i18n y una t-string, incluida la forma en que cada opción vincula los valores y trata un catálogo dañado."
---

# Por qué usar t-strings

Cuatro formas de insertar un valor en un mensaje traducible, comparadas sobre
la misma frase. La versión corta:

- Con el **formato %**, una sola letra borrada por un traductor se convierte en
  un fallo en producción.
- Con **str.format**, una traducción puede leer atributos de los objetos que
  pasa tu código, incluidos secretos.
- Con las **cadenas $** (flufl.i18n), los valores se obtienen implícitamente de
  las variables de la función llamadora, y los marcadores con puntos también
  alcanzan atributos.
- Con las **t-strings**, el formato permanece en tu código, las traducciones se
  comprueban en tiempo de ejecución y un catálogo dañado recurre al texto de
  origen en lugar de provocar un fallo.

El resto de esta página es la evidencia, método a método.

!!! note "Tres partes tocan cada mensaje traducido"

    Un **catálogo** es el archivo de traducciones: `.po` mientras lo editan
    personas, compilado a `.mo` para que la aplicación lo cargue (el
    [tutorial](tutorial.md) recorre ambos). Tres partes tocan cada mensaje: el
    **desarrollador** escribe la cadena de origen, un **traductor** edita el
    catálogo —a menudo en una plataforma externa, lejos de cualquier revisión
    de código— y la **aplicación** renderiza ambos juntos en tiempo de
    ejecución. Cada estilo de formato responde de manera distinta a la misma
    pregunta: *¿qué parte del lenguaje de formato puede controlar el
    catálogo?* En los ejemplos, `_` es el nombre convencional de la función de
    traducción y `tr` es la de esta biblioteca.

## Formato % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Qué puede salir mal: una letra borrada en una traducción hace fallar el
renderizado.

La cadena del catálogo contiene sintaxis de printf, incluida una letra de tipo
final —la `s` de `%(name)s`— fácil de pasar por alto y fácil de dañar:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Editar un solo carácter en un editor PO se convierte en un traceback en
producción. GNU `msgfmt --check-format` puede detectarlo, pero solo en mensajes
marcados como `python-format` y si el catálogo pasa realmente por msgfmt antes
de llegar a la aplicación.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Elimina la letra de tipo final y conserva un marcador con nombre que puede
reordenarse libremente. Lo que puede salir mal pasa al otro lado del
intercambio: la traducción gana poder sobre tus objetos.

`str.format` es un pequeño lenguaje de expresiones, y llamarlo sobre una cadena
significa concederle a esa cadena el derecho a utilizarlo:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ahora sustituye esas cadenas literales por lo que devuelva `_()`. Si una
traducción de `Hello {name}` vuelve como `{conf.api_key}`, renderizarla imprime
tu clave de API: fue el catálogo, no tu código, quien decidió qué se leía. Un
catálogo no es código, pero viaja como datos: sale hacia una plataforma de
traducción, pasa por varias manos, vuelve como `.po`, se compila como `.mo` y a
veces se incorpora desde un proyecto externo. `.format()` permite que cualquier
paso de ese recorrido acceda a los atributos de los objetos proporcionados.

## Cadenas `$` y flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

La biblioteca estándar proporciona el lenguaje de interpolación `$name`
mediante [`string.Template`][stdlib-template], pero este no es en sí mismo una
API de traducción. [`flufl.i18n`][flufl-i18n] combina ese estilo con la
consulta de catálogos gettext. Fíjate en que el valor nunca se pasa como
argumento: flufl.i18n construye el espacio de nombres para las sustituciones a
partir de las variables globales y locales del llamador —cualquier variable que
exista en el punto de llamada queda disponible para el mensaje—. Un mapeo
`extras` opcional tiene prioridad sobre ambas. La sintaxis que ve el traductor
no incluye una letra de tipo final ni un especificador de formato, y los
marcadores pueden reordenarse libremente.

Una sustitución no disponible no provoca una excepción. Con `name = "Ada"` y sin
`nombre` en el espacio de nombres del llamador, una traducción de catálogo
`Hello $nombre` se renderiza como `Hello $nombre`: el marcador sin resolver
permanece visible. Este [comportamiento documentado] conserva el resto del
mensaje traducido en vez de hacer fallar la llamada. Las excepciones que surjan
al resolver un atributo o convertir un valor sí pueden propagarse.

En un aspecto relevante, `flufl.i18n` tiene más capacidad que un
`string.Template` sin modificar. Su [Template personalizado] acepta marcadores
con puntos, como `$settings.api_key`, y su [traductor] resuelve esas rutas en los
valores del llamador. Un marcador traducido puede nombrar cualquier variable
local o global disponible del llamador y, con la sintaxis de puntos, recorrer
sus atributos. Esto resulta práctico cuando un mensaje necesita un atributo,
pero también convierte el marco del llamador en parte del espacio de nombres de
sustitución del catálogo. La comparación siguiente describe `flufl.i18n` 6.0.0,
no todos los usos posibles de `string.Template`.

También responde a una pregunta que los otros dos estilos de formato dejan por
completo en manos de la aplicación: *cuál* es el idioma actual y cómo cambiarlo.
Un [objeto de aplicación][application object] mantiene una pila de idiomas,
`_.push(code)` y `_.pop()` la desplazan, `with _.using(code):` la anida, y una
[estrategia][strategy] encuentra el catálogo correspondiente a un código de
idioma, de modo que la aplicación nunca manipula objetos de catálogo. El caso
para el que existe todo esto es un servidor que debe producir texto en más de un
idioma dentro de una misma unidad de trabajo —una página para el lector, una
notificación para alguien cuya cuenta está configurada de otra manera—.

La pila reside en ese objeto de aplicación, que comparte todo el proceso. Por
eso dos peticiones que se solapan comparten una única pila, y los bloques que no
están estrictamente anidados *en el tiempo* se pasan entre sí el idioma
equivocado:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Esta biblioteca conserva la misma capacidad —las vinculaciones se anidan y se
deshacen igual— pero en un `ContextVar` en lugar de una pila compartida, así que
el entrelazado anterior se resuelve por tarea. Los equivalentes están en
[Varios idiomas a la vez](guide.md#several-languages-at-once). Lo que no
proporciona es la búsqueda que va del código de idioma al catálogo: tú pasas un
objeto de traducciones, que en el caso habitual es una sola llamada a
`gettext.translation()`, y la biblioteca estándar cachea el catálogo ya
analizado.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

El catálogo sigue viendo `Hello {name}` y continúa siendo un catálogo PO/MO
normal. La diferencia está en lo que una traducción tiene *permitido decir* y
en quién lo comprueba.

Esta biblioteca valida cada traducción contra los marcadores del mensaje de
origen antes de renderizarla, y acepta nombres simples y nada más. Para
`t"Hello {name}"`:

| Si la traducción contiene | se rechaza con |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Rechazada no significa fallo: por defecto, la biblioteca registra una
advertencia y renderiza el texto de origen, de modo que un catálogo dañado
nunca derriba la aplicación —
[el mismo contrato que mantiene el propio gettext](guide.md#what-happens-when-a-catalog-is-wrong).

El formato permanece donde se escribió, en el código:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nunca llega al catálogo, por lo que ninguna traducción puede cambiarlo y
ningún traductor tiene que interpretarlo.

Una diferencia más son las herramientas: las t-strings son sintaxis nueva, así
que extraerlas a un `.pot` requiere actualmente un extractor que las entienda,
como el que este paquete [proporciona para Babel](extraction.md).

## Comparación { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| ¿El marcador tiene nombre? | sí | sí | sí | sí |
| ¿Un traductor puede reordenar los marcadores? | sí | sí | sí | sí |
| ¿De dónde proceden los valores? | de un mapeo explícito | de argumentos explícitos | de las variables locales y globales del llamador, más un `extras` opcional | de los valores capturados dentro de la t-string |
| ¿El catálogo puede cambiar cómo se formatea un valor? | sí | sí | no | no |
| ¿El catálogo puede entrar en los objetos (acceso a atributos)? | no | sí | sí, con nombres separados por puntos | no |
| Una traducción *elimina* un marcador: ¿qué se renderiza? | el valor desaparece silenciosamente | el valor desaparece silenciosamente | el valor desaparece silenciosamente | el texto de origen, con una advertencia ([por defecto](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Una traducción *añade* un marcador desconocido: ¿qué se renderiza? | una excepción | una excepción | el marcador permanece visible como texto | el texto de origen, con una advertencia ([por defecto](guide.md#what-happens-when-a-catalog-is-wrong)) |
| ¿Los marcadores se comprueban al renderizar? | no | no | no | sí (véase más abajo) |
| ¿Qué flag PO infiere Babel, para que lo validen las herramientas existentes? | `python-format` | `python-brace-format` | ninguna | `python-brace-format` |
| ¿Usa catálogos PO/MO normales? | sí | sí | sí | sí |
| ¿Necesita un extractor de código fuente personalizado? | no | no | no | sí, actualmente |
| ¿Dónde reside «el idioma actual»? | donde lo ponga la aplicación | donde lo ponga la aplicación | una pila de códigos de idioma en el objeto de aplicación compartido | un `ContextVar`, por tarea o por petición |

Sobre la comprobación al renderizar: en los mensajes singulares se exige una
coincidencia exacta de marcadores. Los mensajes plurales también se comprueban,
según la [regla de unión/intersección](spec.md) que permite que las formas
plurales del idioma de destino difieran de las del origen; la comprobación más
estricta, forma por forma, se ejecuta al compilar los catálogos
([Extracción](extraction.md)).

La fila de la marca de formato se refiere a la validación que reconoce los
marcadores, no a la compatibilidad del catálogo. `ninguna` significa que las
herramientas gettext estándar aún pueden leer y compilar el mensaje, pero
`msgfmt --check-format` no dispone de una gramática de marcadores `$` que aplicar.

## El coste { #what-it-costs }

Una f-string no puede utilizarse así: cuando cualquier biblioteca la recibe ya
es una cadena terminada, por lo que traducirla significa traducir un fragmento.
Las t-strings ([PEP 750]) mantienen separados el texto estático y los valores,
conservando una sintaxis similar a las f-strings y la vinculación explícita de
los valores. Las cadenas `$` ya ofrecen una alternativa concisa, con otro
modelo de vinculación y de fallos. `flufl.i18n` es un paquete maduro que
funciona en Python 3.10 y posteriores; `gettext-tstrings` se encuentra
actualmente en fase alfa y, como las t-strings son sintaxis nueva, requiere
Python 3.14 o posterior.

El otro coste es la propia restricción: una interpolación debe ser un nombre
simple.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Es una restricción real. Junto con la vinculación de valores en el código fuente
y la comprobación de marcadores en tiempo de ejecución, impide que las cadenas
del catálogo evalúen expresiones y mantiene significativos los nombres de los
marcadores.

Cómo llegó Python a esta encrucijada —dos PEP con diez años de diferencia y
la discusión sobre la biblioteca estándar que se cerró sin una respuesta— se
cuenta con sus fuentes en [Trasfondo](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [comportamiento documentado]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template personalizado]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [traductor]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
