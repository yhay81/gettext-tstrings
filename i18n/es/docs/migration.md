---
description: "Adoptar las t-strings en un proyecto que ya tiene catálogos de gettext: qué sobrevive intacto, qué queda marcado como fuzzy y cómo mover un punto de llamada cada vez."
---

# Migración

Si tu proyecto ya usa gettext, las preguntas que deciden si esta biblioteca es
adoptable son muy concretas: ¿invalida los catálogos que ya tienes?, ¿puede
convivir con el código que todavía no quieres tocar?, ¿y cuánto de la mudanza
tiene que ocurrir de golpe? Las respuestas, de la más corta a la más larga:

| Pregunta | Respuesta |
| --- | --- |
| ¿Siguen funcionando los archivos `.po` y `.mo` que ya tengo? | Sí. Los mismos archivos, las mismas herramientas. |
| ¿Pueden convivir llamadas antiguas y nuevas en un mismo archivo? | Sí, y un solo mapping de extracción cubre ambas. |
| ¿Cambia el msgid? | Desde `.format()`, no. Desde `%`-format, sí. |
| ¿Tiene que migrar todo el proyecto a la vez? | No. Un solo punto de llamada es un cambio válido. |
| ¿Y Jinja, las plantillas de Django o JavaScript? | Intactos, con los mismos catálogos. |

El resto de esta página es el detalle de cada una de esas respuestas.

## Desde `.format()`: el msgid no cambia { #from-format-the-msgid-does-not-change }

Este es el caso en el que migrar no cuesta casi nada. Un mensaje con
`str.format` y un mensaje con t-string derivan la *misma* clave de catálogo,
porque en ambos casos la clave es el texto con `{name}` dentro:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Así que la traducción existente sigue enganchada. Partiendo de un catálogo que
contiene

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

cambia la llamada, vuelve a extraer y actualiza:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

La entrada que vuelve se diferencia en dos líneas de metadatos y en nada más: un
comentario marcador que la identifica como mensaje t-string y un número de línea
de origen:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Ni marca `fuzzy` ni retraducción, en ningún idioma. El mensaje se renderiza de
inmediato:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` dirá que los catálogos están desactualizados"

    Ese comentario marcador y los números de línea desplazados bastan para que
    `pybabel update --check` afirme que un catálogo necesita regenerarse, porque
    compara la entrada entera y no solo la traducción. Ejecuta el `pybabel
    update` de verdad en el mismo commit que el cambio de código y versiona los
    catálogos con él: es el mismo hábito que ya pide la
    [puerta de CI](workflow.md#what-ci-gates).

## Desde `%`-format: el msgid cambia, así que las traducciones quedan fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

La sintaxis printf vive *dentro* del mensaje, así que sustituirla reescribe la
clave del catálogo. No hay forma de evitarlo, y es el coste honesto de dejar
atrás `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` reconoce el mensaje nuevo como pariente cercano del eliminado y
arrastra la traducción antigua, marcada como fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Tres cosas que conviene saber sobre ese estado:

- **No se rompe nada en tiempo de ejecución.** Las entradas fuzzy quedan
  excluidas del `.mo` compilado, así que la aplicación renderiza el mensaje de
  origen hasta que una persona confirme la pareja: [la misma
  degradación](workflow.md#the-cycle-after-the-first-translation) por la que
  pasa cualquier mensaje reescrito.
- **`pybabel compile` informa de cada una**, porque el `%(name)s` arrastrado no
  es un marcador de llaves válido, y termina con estado distinto de cero. Esa
  lista es tu cola de trabajo, no una falsa alarma: las entradas que contiene
  necesitan edición de verdad.
- **El antiguo flag `python-format` viaja con ellas** y debe borrarse junto con
  el flag `fuzzy`, o `msgfmt --check-format` seguirá aplicando reglas de printf
  a un mensaje en formato de llaves.

Con marcadores printf con nombre la edición es mecánica —`%(name)s` pasa a ser
`{name}` y nada más se mueve—, así que un catálogo grande es una pasada
automatizada seguida de la revisión de un traductor, y no una retraducción. El
`%s` posicional no es mecánico: no tiene nombre que arrastrar, y elegir uno es
precisamente el sentido del cambio.

Por eso, el orden práctico es migrar los mensajes en `%`-format de forma
deliberada —un módulo, una versión o un idioma cada vez— en lugar de en una
única barrida que ponga todos los catálogos en rojo a la vez.

## Las llamadas antiguas y las nuevas conviven { #old-and-new-calls-coexist }

El extractor que lee t-strings lee también las llamadas gettext ordinarias, así
que un solo mapping cubre un archivo a medio migrar:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Ambos mensajes aterrizan en la misma plantilla, y solo el de la t-string lleva
el comentario marcador que activa las comprobaciones adicionales de esta
biblioteca:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Reconoce `_()`, los cuatro nombres estándar de gettext, los alias `tr()` /
`ntr()` y las funciones diferidas `lazy_gettext()` / `lazy_pgettext()`. Un
helper propio debe [nombrarse en el
mapping](extraction.md#registering-your-own-function-names).

En tiempo de ejecución los dos estilos son igual de independientes:
`gettext.translation()` devuelve un objeto de traducción y tanto `_` como los
puntos de entrada de esta biblioteca leen de él.

## Lo que no se mueve { #what-does-not-move }

- **Los lenguajes de plantillas.** El `{% trans %}` de Jinja2, las etiquetas de
  plantilla de Django y sus extractores de Babel siguen funcionando sin cambios
  y siguen alimentando los mismos catálogos PO. Las t-strings son sintaxis de
  Python; se aplican a código Python.
- **Tus archivos de catálogo.** Ni cambio de formato, ni archivo nuevo, ni paso
  de conversión.
- **Tu plataforma de traducción.** El intercambio en `.po` es idéntico, y el
  flag `python-brace-format` que lleva un mensaje t-string es el mismo que lleva
  un mensaje `.format()`, así que el QA de marcadores sigue funcionando.
- **El código que no es Python.** Un catálogo de JavaScript o de C en el mismo
  proyecto no se ve afectado.

## Una lista de comprobación para migrar { #a-migration-checklist }

1. Añade el extra `babel` allí donde se ejecute `pybabel` y cambia el mapping
   `python` de `babel.cfg` por el método `gettext_tstrings`: un solo mapping
   cubre entonces ambos estilos, y `-k` sigue funcionando para las llamadas
   ordinarias.
2. Convierte primero los puntos de llamada con `.format()`. Vuelve a extraer,
   ejecuta `pybabel update` y versiona los catálogos junto con el código; no
   esperes ninguna entrada fuzzy.
3. Convierte los puntos de llamada con `%`-format en lotes que puedas hacer
   revisar, reescribiendo los marcadores arrastrados y borrando los flags
   `fuzzy` y `python-format`.
4. Arregla lo que la restricción rechace: una interpolación tiene que ser un
   nombre simple, así que `t"Hello {user.name}"` pasa primero por una variable
   local. Esa es una edición del punto de llamada, no del catálogo.
5. Activa `strict = true` en el mapping del extractor cuando la barrida esté
   hecha, para que un mensaje que no se pueda extraer haga fallar
   [la build](extraction.md#lenient-locally-strict-in-ci) en lugar de
   desaparecer de la plantilla.
6. Añade la comprobación en tiempo de ejecución de [En
   producción](workflow.md#what-ci-gates): renderiza un mensaje por cada idioma
   distribuido a través de un `Translator` estricto.

Los pasos 2 y 3 son commits corrientes. Nada de esta lista necesita un día de
cambio total.
