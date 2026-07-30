---
description: "El mismo mensaje traducible escrito con formato %, .format() y una t-string, y qué permite controlar al catálogo cada opción."
---

# Por qué usar t-strings

Toda forma de insertar un valor en un mensaje traducible debe responder a la
misma pregunta: *¿qué parte del lenguaje de formato puede controlar el catálogo?*
Las tres respuestas siguientes se diferencian sobre todo en este aspecto.

## Formato %

```python
_("Hello %(name)s") % {"name": name}
```

La cadena del catálogo contiene sintaxis de printf, y la parte que un traductor
puede dañar con mayor facilidad es la menos comprensible: la letra final que
indica cómo renderizar el valor.

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

Es mejor en todo lo que importa a un traductor: el marcador tiene nombre, no hay
un carácter final que pueda perderse y reordenarlo es sencillo.

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

## t-strings

```python
tr(t"Hello {name}")
```

El msgid sigue siendo `Hello {name}`, por lo que el catálogo y las herramientas
no cambian. Lo que cambia es que la traducción deja de ser una cadena de formato.
Esta biblioteca la valida contra los marcadores del mensaje de origen y la
renderiza aceptando únicamente nombres simples. Para `t"Hello {name}"`:

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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| El marcador tiene nombre | sí | sí | sí |
| El traductor puede reordenarlo | sí | sí | sí |
| Perder un carácter lo rompe | **sí** | no | no |
| El catálogo controla el formato | sí | sí | **no** |
| El catálogo puede acceder a atributos | no | **sí** | **no** |
| Un catálogo incorrecto falla al renderizar | **sí** | **sí** | no, [por defecto](guide.md#what-happens-when-a-catalog-is-wrong) |
| Funciona con PO/MO y `msgfmt` | sí | sí | sí |

## El coste

Una f-string no puede utilizarse así: cuando cualquier biblioteca la recibe ya
es una cadena terminada, por lo que traducirla significa traducir un fragmento.
Las t-strings ([PEP 750]) permiten esta separación y por eso Python 3.14 es la
versión mínima.

El otro coste es la propia restricción: una interpolación debe ser un nombre
simple.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Es una restricción real y es lo que permite obtener todo lo anterior. Además,
ofrece a los traductores un nombre con significado en lugar de una expresión que
no pueden interpretar.

  [PEP 750]: https://peps.python.org/pep-0750/
