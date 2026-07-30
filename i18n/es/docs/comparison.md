---
description: "El mismo mensaje traducible escrito con formato %, .format(), cadenas $ de flufl.i18n y una t-string, incluida la forma en que cada opción vincula los valores y trata un catálogo dañado."
---

# Por qué usar t-strings

Toda forma de insertar un valor en un mensaje traducible debe responder a la
misma pregunta: *¿qué parte del lenguaje de formato puede controlar el catálogo?*
Las cuatro respuestas siguientes también se diferencian en el origen de los
valores y en lo que sucede cuando un catálogo cambia un marcador.

## Formato %

```python
_("Hello %(name)s") % {"name": name}
```

La cadena del catálogo contiene sintaxis de printf, incluida una letra de tipo
final fácil de pasar por alto y que puede dañarse al editar un solo carácter:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Editar un solo carácter en un editor PO se convierte en un traceback en
producción. GNU `msgfmt --check-format` puede detectarlo, pero solo en mensajes
marcados como `python-format` y si el catálogo pasa realmente por msgfmt antes
de llegar a la aplicación.

## str.format

```python
_("Hello {name}").format(name=name)
```

Elimina la letra de tipo final y conserva un marcador con nombre que puede
reordenarse libremente.

El problema está en el otro lado. `str.format` es un pequeño lenguaje de
expresiones, y llamarlo sobre una cadena significa concederle a esa cadena el
derecho a utilizarlo:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Un catálogo no es código, pero viaja como datos: sale hacia una plataforma de
traducción, pasa por varias manos, vuelve como `.po`, se compila como `.mo` y a
veces se incorpora desde un proyecto externo. `.format()` permite que cualquier
paso de ese recorrido acceda mediante la cadena a los atributos de los objetos
proporcionados.

## Cadenas `$` y flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

La biblioteca estándar proporciona el lenguaje de interpolación `$name` mediante
[`string.Template`][stdlib-template], pero este no es en sí mismo una API de traducción.
[`flufl.i18n`][flufl-i18n] combina ese estilo con la consulta de catálogos gettext. Construye
el espacio de nombres para las sustituciones a partir de las variables globales
y locales del llamador; un mapeo `extras` opcional tiene prioridad sobre ambas.
La sintaxis que ve el traductor no incluye una letra de tipo final ni un
especificador de formato, y los marcadores pueden reordenarse libremente.

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

## t-strings

```python
tr(t"Hello {name}")
```

El catálogo sigue viendo `Hello {name}` y continúa siendo un catálogo PO/MO
normal. La extracción del código fuente es distinta: las herramientas actuales
requieren un extractor compatible con t-strings, como el que proporciona este
paquete. La traducción se valida contra
los marcadores del mensaje de origen y esta biblioteca la renderiza aceptando
únicamente nombres simples. Para `t"Hello {name}"`:

| Si la traducción contiene | se rechaza con |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

El formato permanece donde se escribió:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nunca llega al catálogo, por lo que ninguna traducción puede cambiarlo y
ningún traductor tiene que interpretarlo.

## Comparación

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| El marcador tiene nombre | sí | sí | sí | sí |
| El traductor puede reordenarlo | sí | sí | sí | sí |
| Los valores proceden de | mapeo explícito | argumentos explícitos | variables globales y locales del llamador, con un `extras` opcional que las sobrescribe | interpolaciones capturadas por la t-string |
| El catálogo controla la conversión del valor o el especificador de formato | sí | sí | no | no |
| El catálogo puede solicitar acceso a atributos | no | sí | sí, con nombres separados por puntos | no |
| Marcador de origen eliminado al renderizar | se omite silenciosamente | se omite silenciosamente | se omite silenciosamente | patrón de origen renderizado por completo [por defecto](guide.md#what-happens-when-a-catalog-is-wrong) |
| Marcador añadido no disponible al renderizar | provoca una excepción | provoca una excepción | permanece visible | patrón de origen renderizado por completo [por defecto](guide.md#what-happens-when-a-catalog-is-wrong) |
| Conjunto de marcadores de origen comprobado en tiempo de ejecución (singular) | no | no | no | sí |
| Marca de formato PO que Babel infiere para el ejemplo | `python-format` | `python-brace-format` | ninguna | `python-brace-format` |
| Usa catálogos PO/MO normales | sí | sí | sí | sí |
| Necesita un extractor de código fuente personalizado | no | no | no | sí, actualmente |

La fila de la marca de formato se refiere a la validación que reconoce los
marcadores, no a la compatibilidad del catálogo. `ninguna` significa que las
herramientas gettext estándar aún pueden leer y compilar el mensaje, pero
`msgfmt --check-format` no dispone de una gramática de marcadores `$` que aplicar.

## El coste

Una f-string no puede utilizarse así: cuando cualquier biblioteca la recibe ya
es una cadena terminada, por lo que traducirla significa traducir un fragmento.
Las t-strings ([PEP 750]) permiten separar las partes conservando una sintaxis
similar a las f-strings y vinculando los valores explícitamente. Las cadenas `$`
ya ofrecen una alternativa concisa, con otro modelo de vinculación y de fallos.
`flufl.i18n` es un paquete maduro cuya versión actual admite Python 3.10;
`gettext-tstrings` se encuentra actualmente en fase alfa y las t-strings nativas
fijan su versión mínima en Python 3.14.

El otro coste es la propia restricción: una interpolación debe ser un nombre
simple.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Es una restricción real. Junto con la vinculación de valores en el código fuente
y la comprobación de marcadores en tiempo de ejecución, impide que las cadenas
del catálogo evalúen expresiones y mantiene significativos los nombres de los
marcadores.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [comportamiento documentado]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template personalizado]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [traductor]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
