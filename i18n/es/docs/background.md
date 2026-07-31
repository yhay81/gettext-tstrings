---
description: "Treinta años de gettext, dos PEP con diez años de diferencia y la discusión sobre la biblioteca estándar que se cerró como «not planned»: por qué existe esta biblioteca, con enlaces a las fuentes."
---

# Trasfondo

Esta biblioteca se sitúa en el punto de encuentro de dos historias largas
—una sobre cómo se traduce el software y otra sobre cómo Python interpola
cadenas— que por fin se cruzaron en 2025 y se detuvieron exactamente en el
punto donde hacía falta una convención pequeña y cuidadosa. Esta página
cuenta ambas historias, con enlaces a las fuentes, porque las decisiones de
diseño de este sitio se juzgan mejor cuando se ven las preguntas a las que
responden.

## El ecosistema gettext { #the-gettext-ecosystem }

[GNU gettext] es la forma en que se traduce el software libre desde mediados
de los años noventa: marcar las cadenas en el código, extraerlas a una
plantilla, entregar a los traductores un archivo de catálogo por idioma,
compilar y cargar en tiempo de ejecución. Alrededor de ese ciclo creció todo
un ecosistema —editores de PO, flujos de revisión y plataformas de traducción
que hablan el mismo formato de archivo—, y Python incluye un
[módulo `gettext`][stdlib-gettext] en su biblioteca estándar desde hace más
de dos décadas. La mitad de la traducción que ocurre en tiempo de ejecución
nunca fue el problema.

La mitad sin resolver fue siempre *qué aspecto tiene la cadena del catálogo*.
Un mensaje `%(name)s` entrega a los traductores sintaxis de printf que una
sola letra borrada convierte en un fallo en producción; un mensaje
`.format()` concede al catálogo acceso a los atributos de objetos vivos.
([Por qué usar t-strings](comparison.md) recorre ambos casos, con los fallos
a la vista.) Y las f-strings —la sintaxis que hoy prefiere la mayoría del
código Python— no pueden participar en absoluto: cuando cualquier biblioteca
recibe una, ya es una cadena terminada. La gente lo intenta de todos modos,
con la frecuencia suficiente para que el gestor de incidencias de Babel
acumule los intentos ([#594][babel-594], [#715][babel-715]); el fallo es
estructural, no una funcionalidad pendiente.

## Dos PEP, con diez años de diferencia { #two-peps-ten-years-apart }

En 2015, Alyssa Coghlan y Nick Humrich escribieron el [PEP 501], que proponía
plantillas de interpolación cuya primera motivación declarada era la i18n:
«providing a cleaner syntax for i18n translation», en palabras del propio
PEP. La propuesta fue aplazada, en parte porque la discusión mostró que el
caso de la i18n arrastraba consideraciones adicionales significativas que los
casos de uso más simples no tenían.

Una década después, el [PEP 750] —de Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou y Dave Peck— retomó la idea como
t-strings, fue [aceptado en abril de 2025][sc-resolution] y se publicó en
[Python 3.14] en octubre de 2025. El PEP 501 se retiró entonces en su favor.
Un detalle importa para esta página: la i18n *no* figura entre las
motivaciones declaradas del PEP 750. El PEP generalizó el mecanismo —un tipo
de plantilla que cualquier biblioteca puede consumir— y dejó la cuestión de
la traducción exactamente donde el PEP 501 la había aparcado diez años antes:
abierta.

Así que, a partir de Python 3.14, el lenguaje tenía precisamente la
estructura de datos que necesita un catálogo de mensajes, y ninguna
convención para usarla como tal.

## La discusión sobre la biblioteca estándar { #the-stdlib-discussion }

Dos meses antes de que se publicara la 3.14, Adrian Mönnich (ThiefMaster,
mantenedor del proyecto Indico) propuso cerrar esa brecha en la propia
biblioteca estándar: el hilo [Support t-strings in gettext][discuss-thread]
en discuss.python.org, abierto en agosto de 2025, llegó con un
[pull request][cpython-pr] funcional que añadía soporte de t-strings tanto a
`gettext` como a `pygettext`.

Merece la pena leer el hilo completo, porque saca a la luz todas las
preguntas difíciles que esta biblioteca tuvo que responder después:

- **¿Qué puede ser una interpolación?** ¿Solo un nombre simple, o también
  atributos y llamadas con un nombre de marcador derivado? Cada respuesta
  intercambia comodidad por estabilidad de los msgid y seguridad del
  catálogo.
- **¿Qué exigen las formas plurales,** cuando el sistema de plurales del
  idioma de destino difiere del de origen?
- **¿Es gettext siquiera el objetivo correcto?** Barry Warsaw —que durante el
  desarrollo del PEP 750 había defendido que las t-strings no encajaban bien
  con la i18n— señaló su [`flufl.i18n`][flufl-i18n] y su estilo de cadenas
  `$` como la herramienta más amable; otros defendieron abandonar gettext por
  completo en favor de sistemas más nuevos como [Fluent].
- **Y la metapregunta:** lo que la biblioteca estándar publique, en la
  práctica ya no puede cambiar. Una convención con tantas decisiones abiertas
  es algo arriesgado de congelar al primer intento.

No se formó ningún consenso. La incidencia de CPython se
[cerró como «not planned»][cpython-issue] y el pull request se cerró sin
fusionar en octubre de 2025, días después de la publicación de la 3.14. La
capacidad existía en el lenguaje; la convención no tenía hogar.

## Por qué un paquete, primero { #why-a-package-first }

Esa es la brecha que este proyecto decidió cubrir desde fuera de la
biblioteca estándar, con una apuesta deliberada: una convención madura más
rápido donde puede versionarse con libertad y ganarse la adopción caso a
caso, y la biblioteca estándar —que debe acertar a la primera— es donde una
convención debería *terminar*, no donde debería elaborarse.

En concreto, cada cuestión disputada del hilo tiene aquí una respuesta por
escrito, cada una en su propia página:

- Las interpolaciones son **solo nombres simples**, de modo que los msgid se
  mantienen estables y significativos — [la guía](guide.md#safety-and-scope)
  muestra la regla y [Cómo funciona](internals.md#from-template-to-msgid),
  las razones.
- **El formato queda fuera del catálogo** por completo
  ([Por qué usar t-strings](comparison.md)).
- **Los plurales** siguen una regla de unión/intersección que permite que el
  sistema de plurales del idioma de destino difiera del de origen
  ([spec §4](spec.md)).
- Un catálogo dañado **recurre al texto de origen en lugar de fallar**,
  conservando el propio contrato de gettext
  ([la guía](guide.md#what-happens-when-a-catalog-is-wrong)).
- Y toda la convención es una [especificación versionada](spec.md) con una
  suite de conformidad legible por máquinas, escrita para que otra
  implementación —incluida una futura de la biblioteca estándar— pudiera
  adoptarla sin cambios e interoperar.

La discusión no ha terminado, y este proyecto es un participante en ella, no
un veredicto sobre ella. Si tienes experiencia con gettext en producción que
sea relevante para estas decisiones, el [mismo hilo][discuss-thread] y las
[Discussions][gh-discussions] de este repositorio son donde continúa la
discusión.

## Cronología { #timeline }

| Cuándo | Qué ocurrió |
| --- | --- |
| mediados de los 90 | GNU gettext establece el flujo PO/POT/MO que los traductores y las plataformas siguen usando hoy. |
| 2015 | El [PEP 501] propone plantillas de interpolación, con la i18n como primera motivación; aplazado. |
| 2016 | Las f-strings llegan con Python 3.6: la interpolación consigue su sintaxis, y la traducción no puede usarla. |
| jul 2024 | El [PEP 750] propone las t-strings. |
| abr 2025 | El PEP 750 es [aceptado][sc-resolution]; el PEP 501 se retira en su favor. |
| ago 2025 | Se abre el hilo [Support t-strings in gettext][discuss-thread], con un [pull request][cpython-pr] para la biblioteca estándar. |
| oct 2025 | [Python 3.14] publica las t-strings; la incidencia de la biblioteca estándar se cierra como [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` se publica como alpha, con la [spec v1](spec.md) y su suite de conformidad. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
