---
description: "El contrato de marcadores para quien edita los archivos .po: qué puedes cambiar, qué debes dejar intacto y cómo leer los errores."
---

# Para traductores

Esta página es para quien edita el catálogo, no para quien escribe el código.
Es breve a propósito, y está pensada para enlazarla o copiarla en las
instrucciones para traductores de cada proyecto.

Nada de lo que hay aquí exige saber Python. Todo trata de una sola cosa: los
fragmentos de un mensaje que van entre llaves.

## Qué es un marcador { #what-a-placeholder-is }

Un mensaje de un catálogo puede contener nombres entre llaves:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` es un **marcador**. Cuando el programa muestra este mensaje, sustituye
`{name}` por un valor que él mismo aporta: el nombre de una persona, el de un
archivo, una cantidad. El marcador no es una palabra que haya que traducir: es
un hueco.

Tu traducción va en el `msgstr`, y tiene que conservar ese hueco:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Qué puedes cambiar y qué no { #what-you-may-change-and-what-you-may-not }

**Puedes**:

- **Mover un marcador** allí donde lo pida la gramática del idioma de destino,
  incluso al principio del mensaje.
- **Repetir un marcador** si el idioma necesita el valor dos veces.
- **Reescribir todas las demás palabras**, incluidos la puntuación, los
  espacios y el orden de la frase.

**No puedes**:

- **Traducir el nombre que va entre las llaves.** `{name}` sigue siendo
  `{name}`, incluso en un idioma que no escriba nada más en letras latinas.
- **Quitar las llaves** ni escribir el nombre sin ellas.
- **Sustituir las llaves ASCII `{` `}` por las de ancho completo `｛` `｝`.**
  Muchos métodos de entrada producen las formas de ancho completo; se parecen
  muchísimo y no funcionan.
- **Añadir formato**, como `{name!r}` o `{amount:.2f}`. Cómo se muestra un valor
  se decide en el programa, no en el catálogo.
- **Inventar un marcador** que no esté en el `msgid`.

Si un mensaje necesita un valor que el original no ofrece, ese es un mensaje que
tiene que cambiar quien desarrolla. Dilo en lugar de buscar un rodeo.

## Formas plurales { #plural-forms }

Un mensaje con cantidad llega con un hueco `msgstr` por cada forma plural de tu
idioma, y es tu idioma el que decide cuántas son: una para el japonés, dos para
el alemán, tres para el ruso, seis para el árabe. Rellena todos los huecos que
te dé el catálogo.

Dos reglas con las que mucha gente tropieza:

- **Los huecos no son «singular, plural, más plural».** Cada índice significa
  lo que diga la regla de plurales de tu idioma. La tercera forma del letón es
  solo para el cero; la segunda del esloveno, para exactamente dos; el galés
  pone el caso general en el índice 0 y el singular en el índice 1.
- **Dos huecos pueden contener legítimamente el mismo texto.** En turco,
  húngaro, persa y bengalí un sustantivo se mantiene en singular tras un
  numeral, así que ambas formas de un mensaje con cantidad son la misma cadena.
  Eso es correcto, no un descuido al copiar y pegar.

Las reglas sobre marcadores de más arriba se aplican a cada forma por separado.

## Entradas fuzzy { #fuzzy-entries }

Una entrada marcada como `fuzzy` es la suposición de una máquina: quien
desarrolla cambió el mensaje original y la herramienta emparejó el texto nuevo
con tu traducción antigua para que tengas por dónde empezar.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Una entrada fuzzy **no la usa el programa** —muestra el original sin traducir—
hasta que alguien revisa el texto y quita la marca `fuzzy`. La mayoría de los
editores de PO tienen un botón para justamente eso.

## Leer un mensaje de error { #reading-a-failure-message }

La herramienta comprueba los marcadores cuando se compila el catálogo, y el
mensaje está escrito para ti y no para un programador. Indicar solo que falta
`{name}` no ayuda si ves esos caracteres delante. Por eso, cuando un marcador
parece estar presente pero no lo está, el mensaje explica el motivo. Frente al
original `Hello {name}`, cada ejemplo se informa bajo
`translation does not match the source placeholders:`:

| Tu traducción dice | Motivo indicado |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Los caracteres invisibles reciben un tratamiento específico. Un espacio de no
separación dentro de las llaves puede proceder de un método de entrada y ningún
editor lo muestra, así que el mensaje imprime su code point en vez de nombrar un
carácter que nunca podrías encontrar:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un nombre cuyas letras mezclan sistemas de escritura —el caso de homoglyph, en
el que una `а` cirílica es indistinguible de una latina— se muestra dos veces:
una de forma legible y otra escapada, que es la única que revela la diferencia.

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

La misma distinción se aplica cuando un nombre escrito por completo en griego o
cirílico entra en conflicto con un nombre ASCII, incluido el caso de una sola
letra `a` latina / `а` cirílica.

Si te encuentras con uno de estos casos y la solución no es evidente, lo seguro
es borrar el marcador que has escrito y copiar el del `msgid`.

## Qué no pueden hacer las comprobaciones { #what-the-checks-cannot-do }

La herramienta verifica que tus marcadores estén intactos. No puede saber si la
traducción es exacta, natural o adecuada para el contexto: eso queda
enteramente en tus manos.

Dos cosas ayudan más que cualquier comprobación:

- **Lee el comentario para traductores.** Una línea que empieza por `#.` encima
  del mensaje es quien desarrolla contándote dónde aparece y qué significa.
- **Pregunta por el `msgctxt`.** Cuando la misma palabra aparece dos veces con
  contextos distintos, es porque las dos necesitan traducirse de forma
  diferente: «Open» el botón y «Open» el estado, por ejemplo.
