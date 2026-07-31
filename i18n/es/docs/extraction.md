---
description: "Extracción de mensajes t-string con pybabel y validación de catálogos mediante msgfmt y el checker de Babel incluido."
---

# Extracción

La extracción es el paso que recopila todos los mensajes marcados en tu código
fuente en una plantilla `.pot` para los traductores: el paso 3 del ciclo del
[tutorial](tutorial.md). Esta página es la referencia de ese paso: la
configuración, los nombres de función propios, el modo estricto para CI y las
comprobaciones que después protegen tus catálogos.

La extracción necesita el extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## El flujo de trabajo { #the-workflow }

Crea `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Después utiliza los comandos habituales de Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` se ejecuta una sola vez por idioma; a partir de ahí, `pybabel update`
incorpora cada plantilla nueva a los catálogos existentes. Ese ciclo
recurrente —y qué significan sus entradas `fuzzy` para una versión— se recorre
en [En producción](workflow.md#the-cycle-after-the-first-translation).

El extractor `gettext_tstrings` también procesa llamadas ordinarias a `_()`,
`gettext()` y `ngettext()`, de modo que un solo mapping cubre una base de código
mixta. Reconoce `_()`, los cuatro nombres estándar de gettext, los alias `tr()` /
`ntr()` y las funciones diferidas `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Activa los comentarios para traductores con `-c`"

    `pybabel extract` solo recoge los comentarios para traductores si se pasa
    `-c "Translators:"`, exactamente igual que con las llamadas gettext
    ordinarias. Si lo omites, la extracción sigue funcionando: lo que pasa es
    que los comentarios nunca llegan al catálogo, donde son [la palanca de
    calidad más barata](workflow.md#working-with-translators-and-platforms) de
    todo el flujo de trabajo.

## Registrar nombres de función propios { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Un archivo ini proporciona una cadena y un mapping TOML proporciona una lista;
dentro de una cadena, tanto los espacios como las comas separan los nombres.
Las cuatro variantes funcionan.

Las opciones son `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` y `npgettext_functions`.

!!! danger "`-k` no llega a una t-string"

    Un helper propio como `mytr(t"…")` debe registrarse en una de las opciones
    anteriores. El mecanismo `--keyword` de Babel no puede leer un literal
    t-string, por lo que `pybabel extract -k mytr` no encuentra nada ni muestra
    ningún aviso: los mensajes simplemente no aparecen en el POT. `-k` sigue
    funcionando para las llamadas gettext ordinarias extraídas al mismo tiempo.

    Solo se admite el orden de argumentos estándar: primero el mensaje; en
    `pgettext`, contexto y mensaje; en `npgettext`, contexto, singular y plural.

## Permisivo en local, estricto en CI { #lenient-locally-strict-in-ci }

Por defecto, un archivo incorrecto no detiene la ejecución:

- Una t-string rechazada por el extractor —acceso a atributos, una expresión o
  un argumento incorrecto— se notifica como advertencia y se omite.
- Un archivo que no puede analizarse se omite de la misma forma.
- También se omite un archivo que solo rechaza `tokenize` aunque `ast` lo acepte,
  ya que de otro modo el propio paso de Babel se detendría.

Eso resulta cómodo mientras estás editando y peligroso cuando no lo estás: un
mensaje omitido está sencillamente **ausente del POT**, así que nunca se traduce
y nada lo advierte. Establece `strict = true` en las opciones del mapping allí
donde ninguna persona esté vigilando la extracción:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Con ello, todas las advertencias anteriores pasan a ser errores. Considera esta
la configuración de producción y la anterior la de trabajo local.

## El toolchain existente valida estos catálogos { #your-existing-toolchain-validates-these-catalogs }

Babel marca cada mensaje extraído con un flag estándar. Esa línea activa la
validación de marcadores en las herramientas que ya utilizas:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Si se traduce como `こんにちは {nombre}`, el error se detecta sin configuración:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documenta la misma comprobación como
[Python brace format][weblate-checks], y las plataformas comerciales tienen su
propio QA de marcadores basado en el mismo flag. El comportamiento de cada
plataforma es cosa suya; las dos herramientas siguientes son las verificadas
aquí.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Además, el paquete registra un **checker** de Babel, por lo que
`pybabel compile` aplica las reglas de la especificación a cada mensaje con el
comentario marcador `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

En un mensaje plural el indicador nombra la forma, porque el número de línea que
informa Babel es el del msgid y un bloque ruso tiene tres `msgstr` debajo:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` escribe el `.mo` de todos modos"

    El error anterior se informa, el estado de salida es `1`, y aun así el
    catálogo incorrecto se compila. Solo ese estado de salida puede impedir que
    un pipeline lo publique; [Qué controla la CI](workflow.md#what-ci-gates)
    muestra el paso de compilación que lo permite.

Las dos comprobaciones no son redundantes. El checker del paquete es más
estricto al menos en dos casos:

- Un msgid cuyas únicas llaves están escapadas (`Config {{raw}} only`) nunca
  recibe el flag `python-brace-format`, así que ninguna herramienta externa lo
  valida.
- Las formas plurales se comprueban una a una. `msgfmt --check-format` lee el
  archivo anterior y devuelve `0`; acepta una forma que omite un marcador
  presente en sus formas hermanas, mientras que este checker la rechaza.

`msgfmt` solo comprueba nombres que puede interpretar como formato de llaves de
Python. Los nombres ASCII permiten que todas las herramientas de la cadena
validen el mensaje. La propia biblioteca acepta cualquier nombre para el que
`str.isidentifier()` sea verdadero.

## Templates y otras herramientas { #templates-and-other-tools }

Las t-strings son sintaxis de Python, por lo que esta biblioteca cubre código
Python. Los lenguajes de template siguen usando su propia i18n —`{% trans %}` de
Jinja2, las etiquetas de Django— y sus extractores de Babel. Todo alimenta el
mismo catálogo PO, de modo que una sola traducción sigue cubriendo una base de
código mixta.

`pygettext` no puede analizar t-strings actualmente, por eso la extracción se
realiza mediante Babel. La convención se documenta en la
[especificación](spec.md) para que otro extractor, o un futuro `pygettext`,
pueda implementarla.
