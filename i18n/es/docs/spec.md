---
description: "La convención de t-string a msgid como un contrato pequeño y versionado, con una suite de conformidad legible por máquinas."
---

# Especificación

La convención que implementa esta biblioteca está documentada como un contrato
pequeño y estable para que otra implementación —un extractor, un IDE, un
comprobador de tipos o un futuro `pygettext`— pueda adoptarla e interoperar.

[Leer la especificación v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Las reglas en una pantalla

**Un msgid** es la concatenación, en el orden del código fuente, de los segmentos
literales y un token `{name}` por interpolación. Las llaves literales se escapan
(`{` pasa a ser `{{`). El nombre debe ser un marcador simple:
`str.isidentifier()` debe ser verdadero y no puede ser una palabra reservada de
Python. Las conversiones y las especificaciones de formato **no** forman parte
del msgid; permanecen bajo el control de la aplicación.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *rechazada: no es un nombre simple* |

**Una traducción** es válida si contiene únicamente marcadores `{name}` sin
modificadores, todos los nombres obligatorios aparecen al menos una vez y no
aparece ningún nombre fuera del conjunto permitido. El reordenamiento y la
repetición no se restringen deliberadamente: ambos pueden ser necesarios para la
gramática del idioma de destino.

Para los plurales, el conjunto *permitido* es la unión de los nombres de las
ramas y el conjunto *obligatorio* es su intersección. Así, `t"One file"` frente a
`t"{n} files"` permite usar `n` en cualquiera de las formas traducidas, pero no
lo exige en ninguna. Las reglas de plural del idioma de destino pueden ser
distintas de las del idioma de origen.

**Un msgid vacío** nunca se busca, porque gettext lo reserva para la cabecera de
metadatos del catálogo.

## Conformidad { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
es el mismo documento en formato legible por máquinas: contiene casos que
asocian la estructura estática de una t-string con un msgid, y un msgid más un
pattern de catálogo con una cadena renderizada o un rechazo.

Una implementación **cumple la especificación v1** si reproduce todos los casos.
Los casos nombran únicamente lo definido por la especificación —msgids
derivados, patterns aceptados y rechazados, y resultados renderizados—, nunca un
mensaje de error ni un tipo de excepción. Por eso una implementación en otro
lenguaje puede ejecutarlos sin cambios.

Las interpolaciones se describen estructuralmente, nunca como código fuente de
Python:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

La implementación de referencia ejecuta la suite como parte de sus propias
pruebas, por lo que la documentación y el código no pueden divergir en silencio.

## Versionado

Esta es la especificación v1. Un cambio incompatible en la derivación del msgid
o la validación de traducciones incrementa la versión y añade un nuevo
`conformance/vN.json` junto al existente. Las aclaraciones que no cambian los
msgids derivados ni los patterns aceptados no incrementan la versión.
