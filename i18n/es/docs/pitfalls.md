---
description: "Qué se rompe de verdad al traducir un sitio pequeño a treinta y cinco idiomas, qué parte de eso puede detectar la biblioteca por ti y qué parte no."
---

# Escollos

Este sitio está traducido a treinta y cinco idiomas, y todos ellos se
produjeron ejecutando el ciclo que enseña esta documentación. Es un corpus
pequeño para los estándares del sector y aun así bastó para caer en casi todas
las trampas que hacen que la i18n sea más difícil de lo que parece.

Cada sección de abajo es algo que salió mal aquí de verdad, qué aspecto tenía
en su momento y dónde está la línea entre lo que la biblioteca comprueba por ti
y lo que sigue siendo criterio tuyo.

## Renombrar una variable retraduce una frase { #renaming-a-variable-retranslates-a-sentence }

El msgid es la clave del catálogo, y un nombre interpolado está *dentro* de
ella. Mover una constante al ámbito de módulo y ponerla en mayúsculas como pide
el estilo de Python —de `author` a `AUTHOR`— convirtió
`Copyright © 2026 {author} · MIT License` en un mensaje que ningún catálogo
había visto nunca. Todas las traducciones de esa línea habrían vuelto a pasar
por el ciclo fuzzy, en todos los idiomas, por un renombrado que no cambiaba
nada que un lector pudiera ver.

La biblioteca no te lo impedirá: ambas grafías son nombres de marcador válidos.
Lo que sí hace es que el nombre *merezca* protegerse: una interpolación tiene
que ser un [nombre simple](internals.md#from-template-to-msgid), así que lo que
queda en la clave del catálogo es una palabra que un traductor puede leer, no
una expresión.

El caso simétrico es seguro por construcción. Las conversiones y los
especificadores de formato no forman parte del msgid, así que ajustar
`{amount:,.2f}` a `{amount:,.0f}` no cambia ninguna clave ni invalida ninguna
traducción en ningún idioma.

## `nplurals=2` no significa dos cadenas distintas { #nplurals-2-does-not-mean-two-different-strings }

El turco, el húngaro, el persa y el bengalí declaran los cuatro dos formas
plurales, y en los cuatro las dos formas de un mensaje con cantidad son
legítimamente *la misma cadena*: el sustantivo permanece en singular tras un
numeral, así que `{n} sayfa` vale igual para una página que para diez. Quien
revise el texto y «corrija» esa duplicación rompe la traducción.

El error contrario es igual de fácil. La tercera forma del letón existe **solo
para el cero**; la segunda del esloveno es un **dual**, para exactamente dos;
la última del rumano exige la palabra `de` que las dos primeras no pueden
llevar. Rellenar esos huecos con un singular y un plural produce un catálogo
que es incorrecto solo para las cantidades que nadie prueba.

Peor aún: el *orden* de los huecos no es semántico. El galés indexa sus cinco
formas de modo que `msgstr[0]` es el caso general y `msgstr[1]` es el singular.
Rellenarlas en la secuencia obvia coloca el singular justo donde lo encontrará
todo mensaje sin cantidad.

La biblioteca no asume nada de esto, y esa es precisamente la idea: la regla de
plural del idioma de destino vive en la cabecera de su propio catálogo, y la
[regla de unión/intersección](spec.md) permite que una traducción tenga más
formas, o menos, que el origen. Lo que sí comprueba es lo único que puede
comprobarse sin conocer el idioma: que cada forma conserve los marcadores que
necesita.

## Dos formas pueden ser idénticas por un motivo { #two-forms-can-be-identical-for-a-reason }

El irlandés tiene cinco formas plurales y, en el informe de compilación de este
sitio, varias se escriben igual. No es un desliz de copiar y pegar:
*leathanach* empieza por `l`, y ninguna de las dos mutaciones iniciales que
provocan los numerales irlandeses se escribe sobre la `l`. Las formas siguen
haciendo un trabajo real —la raíz alterna entre *leathanach* y *leathanaigh*, y
las cantidades superiores a diez vuelven al singular—, pero ningún sustantivo
que signifique «página» mostraría el contraste.

Cualquier comprobación que marque como sospechosas las formas duplicadas
marcará irlandés correcto. Aquí el único revisor posible es una persona que
conozca el idioma.

## Un mensaje solo puede concordar con una cantidad { #a-message-can-only-agree-with-one-count }

El informe de compilación de este sitio dice cuántas páginas se renderizaron y
cuánto tardó. Escribirlo como «Renderizadas {n} páginas en {seconds} segundos»
parece inofensivo y no es traducible: gettext selecciona una forma a partir de
una cantidad, y esa cantidad es `n`. La palabra *segundos* tendría que
concordar con un número que el mecanismo de plurales nunca llega a ver.

La solución es que la segunda magnitud sea un símbolo de unidad en lugar de una
palabra, y los símbolos de unidad también se localizan: los catálogos de este
sitio llevan `s`, `с`, `ث`, `שנ׳` y `mp`, y la tipografía francesa, española y
sueca quiere un espacio antes del símbolo donde el inglés no lo pone. Nada de
eso es asunto de la biblioteca; pero darse cuenta de que un mensaje necesita
*dos* concordancias sí lo es, y la única herramienta para ello es escribir el
mensaje de otra manera.

## Editar una frase en inglés edita gramática ajena { #editing-an-english-sentence-edits-foreign-grammar }

La página de inicio decía «all ten language editions». Quitar el número —una
edición de una sola palabra en inglés, hecha porque el número se quedaba
obsoleto una y otra vez— convirtió un sujeto plural en singular. El español, el
italiano, el portugués, el ruso, el ucraniano, el griego, el neerlandés y el
hebreo tuvieron todos que volver a concordar el verbo; varios necesitaron
cambiar también el participio.

Una edición del origen que en inglés parece trivial no lo es aguas abajo.
Marcarla como fuzzy, que es lo que hace `pybabel update`, es el mecanismo que
da a cada traductor la oportunidad de darse cuenta.

## Las diferencias invisibles sobreviven a cualquier copiar y pegar { #invisible-differences-survive-every-copy-paste }

La guía cita un diagnóstico que contiene `(nаme)` —un escape deliberado, porque
el carácter que nombra es una `а` cirílica que ningún lector distingue de la
latina—. Quienes tradujeron este sitio convirtieron ese escape en el carácter
real **cinco veces distintas**, en cinco idiomas diferentes, y cada una de ellas
produjo una página que parecía correcta y estaba mal.

Esto sí lo detecta la biblioteca, y es la razón de que los diagnósticos tengan
la forma que tienen: un marcador cuyas letras mezclan sistemas de escritura se
[informa dos veces](internals.md#diagnostics-are-part-of-the-design), una de
forma legible y otra escapada, porque la forma escapada es la única grafía que
las distingue. Un espacio de no separación dentro de las llaves se imprime por
punto de código por la misma razón. El comprobador de catálogos rechaza el
mensaje antes de que pueda publicarse.

## No vacío no es traducido { #non-empty-is-not-translated }

Un catálogo generado con sus msgids copiados en los msgstr pasa todas las
comprobaciones ingenuas: nada está vacío, nada es fuzzy, el conjunto de
mensajes coincide exactamente. Una edición de este sitio se publicó así durante
varias horas. Y también ocho páginas de otra edición que eran copias byte a
byte del origen en inglés, cosa que supera una comprobación que compare los
bloques de código entre ambas, porque son el mismo archivo.

Ninguna de las dos cosas puede verlas una biblioteca de traducción. Ambas son
baratas de comprobar una vez que sabes que hay que hacerlo: compara con el
origen y exige que haya una diferencia.

## El catálogo no es lo único traducido { #the-catalog-is-not-the-only-translated-thing }

Dos de los fallos de aquí no tuvieron nada que ver con gettext.

Traducir un encabezado cambia el ancla que se genera a partir de él, así que
todos los enlaces entre páginas que apuntan a esa sección se rompen —en
silencio y solo en ese idioma—. Este sitio fija el ancla inglesa en todos los
encabezados, y una prueba deriva la lista esperada de la página en inglés.

Y el generador del sitio incluye traducciones de interfaz para sesenta y ocho
idiomas, entre los que no están ni el suajili ni el irlandés. Sin ellas la
compilación no degrada a inglés: el include de la plantilla falla y la edición
no puede construirse en absoluto. Dos archivos propios de este repositorio
existen para llenar ese hueco.

## Tus herramientas también tienen errores { #your-tools-have-bugs-too }

El paso de CI que recomienda esta documentación para detectar catálogos
obsoletos, `pybabel update --check`, no puede hacer ese trabajo en ningún
proyecto que use `pgettext` o `npgettext`: informa de que todos los catálogos
con un `msgctxt` están desactualizados, en cada ejecución, por un error en cómo
la comparación busca los mensajes. Se descubrió aquí al intentar usarlo, se
comunicó aguas arriba y está
[descrito por completo junto con su solución alternativa](workflow.md#what-ci-gates).

La lección general es la incómoda: una puerta que siempre está en rojo es peor
que no tener puerta, porque el equipo acaba desactivándola. Verifica que tu
comprobación de CI puede pasar de verdad antes de confiar en que falle.

## Para qué sirve la biblioteca, en una línea { #what-the-library-is-for-in-one-line }

Casi toda esta página es criterio que ninguna herramienta puede asumir por ti.
Lo que una herramienta *sí* puede hacer es garantizar que una traducción no
pueda cambiar la estructura de la frase que traduce —no pueda eliminar un
valor, inventarse uno, reformatearlo ni acceder a tus objetos— y decirlo en una
frase sobre la que pueda actuar quien tenga que arreglarlo. Eso es todo lo que
promete esta biblioteca, y el resto de este sitio es cómo lo cumple.
