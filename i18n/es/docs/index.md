---
description: "Traduce mensajes t-string completos con gettext y Babel, manteniendo los valores y el formato fuera del catálogo."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Escribe la frase una vez.<br>Tradúcela entera.

`gettext-tstrings` conecta las t-strings de Python 3.14+ con los catálogos
gettext estándar y las herramientas de Babel. Los valores y el formato se
quedan en el código de la aplicación; el catálogo guarda un mensaje completo
con marcadores `{name}` sencillos:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Empieza el tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Compara las alternativas](comparison.md){ .md-button }

Alpha · Python 3.14+ · catálogos PO/MO normales · sin dependencias en tiempo de ejecución
{ .home-facts }

Este sitio practica lo que documenta: cada edición lingüística
—navegación, etiquetas y el informe de compilación con plurales— se renderiza
desde catálogos PO mediante
[el propio `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## ¿Es para ti? { #is-this-for-you }

**Encaja hoy si** tu aplicación se ejecuta en Python 3.14 o posterior; ya
utilizas gettext y Babel, o quieres adoptar su flujo de trabajo PO/MO; y
quieres la sintaxis de las t-strings con marcadores con nombre que se
comprueban antes de renderizarse.

**Todavía no encaja si** necesitas Python 3.13 o anterior; requieres una API de
Python estable —esto es una versión alpha, y la [especificación](spec.md) es la
parte que ya se ha asentado—; o casi todo tu texto traducible vive en un
lenguaje de plantillas y no en código Python.

¿Ya tienes catálogos? Siguen funcionando. `_("Hello {name}").format(name=name)`
y `tr(t"Hello {name}")` producen el mismo msgid, así que las traducciones
existentes sobreviven al cambio: [Migración](migration.md) recorre el traslado
completo.

## Qué puede decir el catálogo { #what-the-catalog-may-say }

El catálogo recibe el mensaje completo `Hello {name}`. Una traducción puede
reordenar o repetir `{name}`, y puede reescribir todas las demás palabras que
lo rodean. No puede omitir el marcador, inventar uno nuevo, atravesarlo para
llegar a tus objetos ni añadir formato por su cuenta.

Esa es toda la promesa: **una traducción no puede cambiar la estructura del
mensaje que traduce.** La biblioteca lo comprueba a la entrada —cuando se
compilan los catálogos— y de nuevo al renderizar; una entrada dañada que aun
así llegue a producción registra una advertencia y renderiza el texto de origen
en lugar de provocar un fallo.

!!! note "¿Nuevo en gettext? Todo el flujo de trabajo en cuatro frases"

    **gettext** es la forma estándar de traducir software, en Python y mucho
    más allá. Tu código marca las cadenas traducibles; un *extractor* las
    recopila en un archivo de plantilla (`.pot`); un traductor —normalmente no
    un programador— rellena un archivo de catálogo (`.po`) por idioma, que se
    compila a un `.mo` binario que tu aplicación carga en tiempo de ejecución.
    El nombre convencional de la función de traducción es `_`, así que
    `_(t"Hello {name}")` se lee como «traduce esta frase». El
    **[tutorial](tutorial.md)** recorre el camino completo —marcar, extraer,
    traducir, compilar, ejecutar— en unos cinco minutos.

## El problema que resuelve { #the-problem-it-solves }

Una f-string ya está interpolada cuando cualquier biblioteca la recibe:
`f"Hello {name}"` se ha convertido en `"Hello Ada"`, y traducir los fragmentos
que rodean un valor rompe la gramática de la mayoría de los idiomas. Una
t-string ([PEP 750]) mantiene separados el texto estático, los valores
evaluados, las expresiones de origen, las conversiones y las especificaciones
de formato: exactamente la separación que necesita un catálogo de mensajes.
Consulta [qué cambia](comparison.md) respecto a `%(name)s`, `.format()` y las
cadenas `$`.

Sin embargo, ni gettext ni Babel definen cómo convertir una t-string en un
mensaje. Esta biblioteca toma esa decisión, la documenta como una
[especificación versionada](spec.md) e incluye una
[suite de conformidad](spec.md#conformance) para comprobarla.

## Las reglas de diseño { #the-design-rules }

- Traduce mensajes completos, nunca fragmentos de frases.
- Acepta solo nombres de variable sencillos como `{name}`.
- Mantiene `!r` y `:.2f` bajo el control de la aplicación, fuera del catálogo.
- Permite que las traducciones reordenen y repitan marcadores conocidos, pero
  les impide acceder a atributos o añadir formato.
- Reutiliza los archivos POT, PO y MO habituales y las herramientas que ya los
  leen.

Y la lista correspondiente de lo que deja deliberadamente en paz: no localiza
números, monedas ni fechas —[formatéalos antes](guide.md#locale-aware-values),
con Babel—; no escapa la salida renderizada para HTML, un intérprete de
comandos o un terminal; y no puede juzgar si una traducción es *correcta*, solo
si sus marcadores están intactos.

## Instalación { #install }

```console
python -m pip install gettext-tstrings
```

Requiere Python 3.14 o posterior. **El renderizado no tiene dependencias**:
utiliza únicamente el `gettext` de la biblioteca estándar.

La extracción y la validación de catálogos se ejecutan mediante [Babel]. Instala
el extra donde se ejecute `pybabel`, normalmente en desarrollo o CI y no en una
imagen de producción:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Próximos pasos { #where-to-go-next }

**Empieza aquí** — sin experiencia previa con gettext:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — de un directorio vacío a una traducción japonesa
  en funcionamiento en cinco pasos, con la salida de cada comando.
- **[Por qué usar t-strings](comparison.md)** — el mismo mensaje escrito de
  cuatro formas y qué entregan al catálogo `%(name)s`, `.format()` y las
  cadenas `$`.

</div>

**Úsalo** — las referencias de trabajo:

<div class="grid cards" markdown>

- **[Guía](guide.md)** — la API de ejecución: qué punto de entrada utilizar,
  plurales, idiomas por petición, cadenas diferidas y qué ocurre cuando un
  catálogo es incorrecto.
- **[Extracción](extraction.md)** — la referencia de `pybabel`: configuración,
  nombres de función propios y cómo las herramientas existentes validan estos
  catálogos sin coste añadido.
- **[En producción](workflow.md)** — el ciclo tal como lo ejecuta un equipo:
  el ciclo de actualización, las entradas fuzzy, las puertas de CI, las
  plataformas de traducción y la publicación.
- **[Migración](migration.md)** — adoptarlo en un proyecto que ya tiene
  catálogos, un punto de llamada cada vez.
- **[Para traductores](translators.md)** — una única página para entregar a
  quien edita los archivos `.po`.

</div>

**Entiéndelo** — de la historia a la implementación:

<div class="grid cards" markdown>

- **[Trasfondo](background.md)** — por qué existe esta biblioteca: treinta
  años de gettext, dos PEP y la discusión sobre la biblioteca estándar que
  se cerró sin una respuesta.
- **[Escollos](pitfalls.md)** — qué rompió realmente traducir este sitio a
  treinta y cinco idiomas, y qué mitad puede detectar una herramienta.
- **[Cómo funciona](internals.md)** — del objeto plantilla del PEP 750 a la
  cadena renderizada, y las cachés que abaratan las comprobaciones.

</div>

**Referencia** — los contratos:

<div class="grid cards" markdown>

- **[API](api.md)** — todo lo que exporta el paquete, en una sola página.
- **[Especificación](spec.md)** — la convención t-string ↔ msgid como contrato
  estable y versionado, con una suite de conformidad legible por máquinas.

</div>

## Estado { #status }

| | |
| --- | --- |
| Versión del paquete | 0.1.0a7 |
| Estabilidad de la API | alpha — la API de Python todavía puede cambiar |
| [Especificación](spec.md) | v1, con una [suite de conformidad](spec.md#conformance) |
| Python | 3.14 y posteriores; probado en 3.14, 3.14t (free-threaded) y 3.15 |
| Babel | 2.18 o posterior, y solo donde se ejecute `pybabel` |
| Dependencias en tiempo de ejecución | ninguna — el `gettext` de la biblioteca estándar |
| Formato de catálogo | POT, PO y MO corrientes |
| Cambios | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Es una versión alpha. El contrato es pequeño a propósito y la
[especificación](spec.md) es su parte estable; la API de Python todavía puede
cambiar. Antes de una versión estable se necesitan fixtures en más idiomas,
seguimiento continuo del rendimiento, revisión de la API por personas que
utilizan gettext y Babel de forma habitual, y pruebas de compatibilidad con cada
versión compatible de Python y Babel.

Se agradecen los
[Issues y Pull Requests](https://github.com/yhay81/gettext-tstrings/issues):
una versión alpha es precisamente el momento en el que aún merece la pena
debatir la interfaz.

## Únete a la comunidad { #join-the-community }

- Elige un
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  para una contribución de alcance acotado.
- Haz preguntas de uso en
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Comparte flujos de gettext en producción e ideas para la API en
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lee la
  [guía de contribución](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  antes de abrir un Pull Request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
