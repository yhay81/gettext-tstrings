---
description: "Trente ans de gettext, deux PEP à dix ans d'écart et la discussion sur la bibliothèque standard close en « not planned » : pourquoi cette bibliothèque existe, avec les liens vers les sources."
---

# Contexte

Cette bibliothèque se situe au point de rencontre de deux longues histoires —
l'une sur la façon dont les logiciels sont traduits, l'autre sur la façon dont
Python interpole les chaînes — qui se sont enfin croisées en 2025, puis se
sont arrêtées exactement là où une convention petite et soignée devenait
nécessaire. Cette page raconte les deux histoires, avec des liens vers les
sources, parce que les décisions de conception de ce site se jugent plus
facilement quand on voit les questions auxquelles elles répondent.

## L'écosystème gettext { #the-gettext-ecosystem }

[GNU gettext] est la manière dont le logiciel libre se traduit depuis le
milieu des années 1990 : marquer les chaînes dans le code, les extraire dans
un fichier modèle, donner aux traducteurs un fichier catalogue par langue,
compiler, charger à l'exécution. Autour de cette boucle a grandi tout un
écosystème — éditeurs PO, workflows de relecture et plateformes de traduction
qui parlent tous le même format de fichier — et Python embarque un
[module `gettext`][stdlib-gettext] dans sa bibliothèque standard depuis plus
de deux décennies. La moitié « exécution » de la traduction n'a jamais été le
problème.

La moitié restée en suspens a toujours été *l'allure de la chaîne dans le
catalogue*. Un message `%(name)s` confie aux traducteurs une syntaxe printf
qu'une seule lettre supprimée transforme en plantage en production ; un
message `.format()` confie au catalogue l'accès aux attributs d'objets
vivants. ([Pourquoi les t-strings](comparison.md) parcourt les deux, avec les
défaillances à l'appui.) Et les f-strings — la syntaxe que préfère désormais
la plupart du code Python — ne peuvent pas du tout participer : lorsqu'une
bibliothèque en voit une, c'est déjà une chaîne terminée. On essaie quand
même, assez souvent pour que le gestionnaire d'issues de Babel collectionne
les tentatives ([#594][babel-594], [#715][babel-715]) ; l'échec est
structurel, pas une fonctionnalité manquante.

## Deux PEP, à dix ans d'écart { #two-peps-ten-years-apart }

En 2015, Alyssa Coghlan et Nick Humrich écrivent la [PEP 501], qui propose des
modèles d'interpolation dont la première motivation déclarée était l'i18n —
« providing a cleaner syntax for i18n translation », selon les propres mots de
la PEP. La proposition fut différée, en partie parce que la discussion
montrait que le cas de l'i18n soulevait des considérations supplémentaires
importantes que des usages plus simples n'avaient pas.

Une décennie plus tard, la [PEP 750] — de Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou et Dave Peck — reprend l'idée sous la
forme des t-strings, est [acceptée en avril 2025][sc-resolution] et arrive
dans [Python 3.14] en octobre 2025. La PEP 501 est alors retirée en sa
faveur. Un détail compte pour cette page : l'i18n ne figure *pas* parmi les
motivations déclarées de la PEP 750. La PEP a généralisé le mécanisme — un
type de template que n'importe quelle bibliothèque peut consommer — et a
laissé la question de la traduction exactement là où la PEP 501 l'avait garée
dix ans plus tôt : ouverte.

Ainsi, à partir de Python 3.14, le langage disposait précisément de la
structure de données dont un catalogue de messages a besoin, et d'aucune
convention pour l'utiliser comme telle.

## La discussion sur la bibliothèque standard { #the-stdlib-discussion }

Deux mois avant la sortie de 3.14, Adrian Mönnich (ThiefMaster, mainteneur du
projet Indico) propose de combler ce manque dans la bibliothèque standard
elle-même : le fil [Support t-strings in gettext][discuss-thread] sur
discuss.python.org, ouvert en août 2025, s'accompagnait d'une
[pull request][cpython-pr] fonctionnelle ajoutant la prise en charge des
t-strings à `gettext` et à `pygettext`.

Le fil mérite d'être lu en entier, parce qu'il fait apparaître chaque question
difficile à laquelle cette bibliothèque a ensuite dû répondre :

- **Que peut être une interpolation ?** Un nom simple seulement, ou des
  attributs et des appels avec un nom de marqueur dérivé ? Chaque réponse
  échange de la commodité contre la stabilité des msgid et la sûreté du
  catalogue.
- **Qu'exigent les formes plurielles,** lorsque le système de pluriels de la
  langue cible diffère de celui de la source ?
- **gettext est-il seulement la bonne cible ?** Barry Warsaw — qui avait
  soutenu, pendant l'élaboration de la PEP 750, que les t-strings ne
  convenaient pas à l'i18n — renvoyait à son [`flufl.i18n`][flufl-i18n] et à
  son style de chaînes `$` comme outil plus accueillant ; d'autres plaidaient
  pour abandonner gettext au profit de systèmes plus récents tels que
  [Fluent].
- **Et la méta-question :** quoi que la bibliothèque standard publie, elle ne
  peut pour ainsi dire plus jamais le changer. Une convention comportant
  autant de choix ouverts est une chose risquée à figer du premier coup.

Aucun consensus ne s'est formé. L'issue CPython a été
[close en « not planned »][cpython-issue] et la pull request fermée sans être
fusionnée en octobre 2025, quelques jours après la sortie de 3.14. La
capacité existait dans le langage ; la convention n'avait pas de foyer.

## Pourquoi un paquet, d'abord { #why-a-package-first }

C'est ce manque que ce projet a choisi de combler depuis l'extérieur de la
bibliothèque standard, sur un pari délibéré : une convention mûrit plus vite
là où elle peut évoluer librement de version en version et gagner l'adoption
cas par cas, et la bibliothèque standard — qui doit être juste du premier
coup — est l'endroit où une convention devrait *aboutir*, pas celui où elle
devrait s'élaborer.

Concrètement, chaque question contestée du fil a ici une réponse écrite,
chacune sur sa propre page :

- Les interpolations sont **des noms simples uniquement**, si bien que les
  msgid restent stables et parlants — [le guide](guide.md#safety-and-scope)
  montre la règle, [Fonctionnement](internals.md#from-template-to-msgid) en
  donne les raisons.
- **Le formatage reste entièrement hors du catalogue**
  ([Pourquoi les t-strings](comparison.md)).
- **Les pluriels** suivent une règle union/intersection qui permet au système
  de pluriels d'une langue cible de différer de celui de la source
  ([spec §4](spec.md)).
- Un catalogue cassé **retombe sur le texte source au lieu de planter**, en
  gardant le contrat de gettext lui-même
  ([le guide](guide.md#what-happens-when-a-catalog-is-wrong)).
- Et la convention tout entière est une [spécification versionnée](spec.md)
  accompagnée d'une suite de conformité lisible par machine — écrite pour
  qu'une autre implémentation, y compris une future implémentation dans la
  bibliothèque standard, puisse l'adopter telle quelle et interopérer.

La discussion n'est pas terminée, et ce projet y participe ; il n'en est pas
le verdict. Si vous avez une expérience de gettext en production qui éclaire
ces choix, le [même fil][discuss-thread] et les [Discussions][gh-discussions]
de ce dépôt sont les lieux où elle se débat.

## Chronologie { #timeline }

| Quand | Ce qui s'est passé |
| --- | --- |
| milieu des années 1990 | GNU gettext établit le workflow PO/POT/MO que traducteurs et plateformes parlent encore. |
| 2015 | La [PEP 501] propose des modèles d'interpolation, avec l'i18n comme première motivation ; différée. |
| 2016 | Les f-strings arrivent dans Python 3.6 — l'interpolation obtient sa syntaxe, et la traduction ne peut pas s'en servir. |
| juil. 2024 | La [PEP 750] propose les t-strings. |
| avr. 2025 | La PEP 750 est [acceptée][sc-resolution] ; la PEP 501 est retirée en sa faveur. |
| août 2025 | Le fil [Support t-strings in gettext][discuss-thread] s'ouvre, avec une [pull request][cpython-pr] pour la bibliothèque standard. |
| oct. 2025 | [Python 3.14] embarque les t-strings ; l'issue stdlib est close en [« not planned »][cpython-issue]. |
| 2026 | `gettext-tstrings` sort en alpha, avec la [spec v1](spec.md) et sa suite de conformité. |

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
