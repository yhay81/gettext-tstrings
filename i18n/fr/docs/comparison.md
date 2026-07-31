---
description: "Le même message traduisible écrit avec le format %, .format(), les chaînes $ de flufl.i18n et une t-string, y compris la manière dont chacun lie les valeurs et gère un catalogue endommagé."
---

# Pourquoi les t-strings

Quatre façons d'insérer une valeur dans un message traduisible, comparées sur
la même phrase. En résumé :

- Avec le **format %**, une lettre supprimée par un traducteur devient un
  plantage en production.
- Avec **str.format**, une traduction peut lire les attributs des objets que
  votre code lui passe — y compris des secrets.
- Avec les **chaînes `$`** (flufl.i18n), les valeurs sont tirées implicitement
  des variables de la fonction appelante, et les marqueurs à points atteignent
  aussi les attributs.
- Avec les **t-strings**, le formatage reste dans votre code, les traductions
  sont vérifiées à l'exécution et un catalogue cassé retombe sur le texte
  source au lieu de planter.

Le reste de cette page en apporte la preuve, une méthode à la fois.

!!! note "Trois parties touchent chaque message traduit"

    Un **catalogue** est le fichier des traductions — `.po` tant que des
    humains l'éditent, compilé en `.mo` pour que l'application le charge (le
    [tutoriel](tutorial.md) parcourt les deux). Trois parties touchent chaque
    message : le **développeur** écrit la chaîne source, un **traducteur**
    édite le catalogue — souvent sur une plateforme externe, loin de toute
    revue de code — et l'**application** rend les deux ensemble à l'exécution.
    Chaque style de formatage ci-dessous répond différemment à la même
    question : *quelle part du langage de formatage le catalogue
    contrôle-t-il ?* Dans les exemples, `_` est le nom conventionnel de la
    fonction de traduction, et `tr` celui de cette bibliothèque.

## Format % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Ce qui peut mal tourner : une seule lettre supprimée dans une traduction fait
planter le rendu.

La chaîne du catalogue contient la syntaxe printf, notamment une lettre de type
finale — le `s` de `%(name)s` — facile à ignorer et facile à endommager :

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Un caractère supprimé dans un éditeur PO devient une traceback en production.
GNU `msgfmt --check-format` le détecte, mais seulement si le message porte le
flag `python-format` et si le catalogue passe réellement par msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Il supprime la lettre de type finale tout en conservant un marqueur nommé et
librement réordonnable. Ce qui peut mal tourner passe de l'autre côté de
l'échange : la traduction gagne du pouvoir sur vos objets.

`str.format` est un petit langage d'expressions : l'appliquer à une chaîne
autorise cette chaîne à l'utiliser.

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Remplacez maintenant ces chaînes littérales par ce que renvoie `_()`. Si une
traduction de `Hello {name}` revient sous la forme `{conf.api_key}`, la rendre
imprime votre clé d'API — c'est le catalogue, pas votre code, qui a décidé de
ce qui était lu. Un catalogue n'est pas du code, mais il voyage comme donnée :
plateforme de traduction, plusieurs mains, retour en `.po`, compilation en
`.mo`, parfois import depuis un tiers extérieur au projet. `.format()` donne à
chaque étape de ce trajet la possibilité d'accéder aux attributs des objets
fournis.

## Chaînes `$` et flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Le module standard [`string.Template`][stdlib-template] fournit le langage d'interpolation
`$name`, mais ne constitue pas en lui-même une API de traduction.
[`flufl.i18n`][flufl-i18n] associe ce style à la recherche dans les catalogues gettext.
Remarquez que la valeur n'est jamais passée en argument : flufl.i18n construit
l'espace de noms de substitution à partir des variables globales et locales de
l'appelant — toutes les variables qui existent au point d'appel sont
disponibles pour le message. Un mapping `extras` facultatif prend le pas sur
les deux. La syntaxe destinée aux traducteurs ne comporte ni lettre de type
finale ni spécificateur de format, et les marqueurs restent librement
réordonnables.

Une substitution indisponible ne lève pas d'exception. Avec `name = "Ada"` et
sans `nombre` dans l'espace de noms de l'appelant, une traduction de catalogue
`Hello $nombre` donne `Hello $nombre` : le marqueur non résolu reste visible.
Ce [comportement documenté] préserve le reste du message traduit au lieu de
faire échouer l'appel. Les exceptions levées pendant la résolution d'un
attribut ou la conversion d'une valeur peuvent néanmoins se propager.

Sur un point pertinent, `flufl.i18n` est plus puissant qu'un
`string.Template` brut. Son [Template personnalisé] accepte des marqueurs avec
des points, comme `$settings.api_key`, et son [traducteur] résout ces chemins
sur les valeurs de l'appelant. Un marqueur traduit peut désigner toute variable
locale ou globale disponible de l'appelant et, avec la syntaxe à points,
parcourir ses attributs. C'est pratique lorsqu'un message a besoin d'un
attribut, tout en faisant du cadre de l'appelant une partie de l'espace de noms
de substitution du catalogue. La comparaison ci-dessous décrit
`flufl.i18n` 6.0.0, pas tous les usages possibles de `string.Template`.

Il répond aussi à une question que les deux autres styles de formatage
laissent entièrement à l'application : *quelle* langue est courante, et
comment en changer. Un [objet application][application object] conserve une
pile de langues, `_.push(code)` et `_.pop()` la déplacent, `with _.using(code):`
s'imbrique, et une [stratégie][strategy] trouve le catalogue correspondant à un
code de langue, si bien que l'application ne manipule jamais d'objets catalogue.
Un serveur qui doit produire du texte dans plusieurs langues au cours d'une même
unité de travail — une page pour le lecteur, une notification pour quelqu'un
dont le compte est réglé autrement — est précisément le cas pour lequel cela
existe.

La pile vit sur cet objet application, que tout le processus partage. Deux
requêtes qui se chevauchent partagent donc une seule pile, et des blocs qui ne
sont pas strictement imbriqués *dans le temps* se refilent la mauvaise langue :

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Cette bibliothèque conserve la même capacité — les liaisons s'imbriquent et se
dénouent de la même façon — dans une `ContextVar` plutôt que dans une pile
partagée, si bien que l'entrelacement ci-dessus se résout par tâche. Les
équivalents figurent sur
[Plusieurs langues à la fois](guide.md#several-languages-at-once). Ce qu'elle
ne fournit pas, c'est la recherche du catalogue à partir d'un code de langue :
vous passez un objet translations, qui dans le cas courant tient en un seul
appel à `gettext.translation()`, et la bibliothèque standard met en cache le
catalogue analysé.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

Le catalogue voit toujours `Hello {name}` et reste un catalogue PO/MO ordinaire.
La différence tient à ce qu'une traduction *a le droit de dire*, et à qui le
vérifie.

Cette bibliothèque valide chaque traduction par rapport aux marqueurs du
message source avant le rendu, et n'accepte que des noms simples, rien
d'autre. Face à `t"Hello {name}"` :

| Une traduction contenant | est rejetée avec |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Rejetée ne veut pas dire plantée : par défaut, la bibliothèque journalise un
avertissement et rend le texte source, si bien qu'un mauvais catalogue ne fait
jamais tomber l'application —
[le contrat que gettext lui-même respecte](guide.md#what-happens-when-a-catalog-is-wrong).

Le formatage reste là où il a été écrit, dans le code :

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` n'atteint jamais le catalogue : aucune traduction ne peut le modifier
et aucun traducteur n'a à le regarder.

Une dernière différence concerne l'outillage : les t-strings sont une syntaxe
nouvelle, donc les extraire vers un `.pot` demande aujourd'hui un extracteur
qui les comprend, comme celui que ce paquet
[fournit pour Babel](extraction.md).

## Comparaison { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Le marqueur est-il nommé ? | oui | oui | oui | oui |
| Un traducteur peut-il réordonner les marqueurs ? | oui | oui | oui | oui |
| D'où viennent les valeurs ? | un mapping explicite | des arguments explicites | les variables locales et globales de l'appelant, plus un `extras` facultatif | les valeurs capturées dans la t-string |
| Le catalogue peut-il changer le formatage d'une valeur ? | oui | oui | non | non |
| Le catalogue peut-il fouiller les objets (accès aux attributs) ? | non | oui | oui, avec des noms à points | non |
| Une traduction *supprime* un marqueur — que rend-on ? | la valeur disparaît silencieusement | la valeur disparaît silencieusement | la valeur disparaît silencieusement | le texte source, avec un avertissement ([par défaut](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Une traduction *ajoute* un marqueur inconnu — que rend-on ? | une exception | une exception | le marqueur reste visible comme texte | le texte source, avec un avertissement ([par défaut](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Les marqueurs sont-ils vérifiés au moment du rendu ? | non | non | non | oui (voir ci-dessous) |
| Quel flag PO Babel déduit-il, pour la validation par les outils existants ? | `python-format` | `python-brace-format` | aucun | `python-brace-format` |
| Utilise des catalogues PO/MO ordinaires ? | oui | oui | oui | oui |
| Nécessite un extracteur de code source personnalisé ? | non | non | non | oui, actuellement |
| Où vit « la langue courante » ? | là où l'application la met | là où l'application la met | une pile de codes de langue sur l'objet application partagé | une `ContextVar`, par tâche ou par requête |

Sur la vérification au rendu : les messages au singulier sont vérifiés pour une
correspondance exacte des marqueurs. Les messages au pluriel le sont aussi,
selon la [règle union/intersection](spec.md) qui permet aux formes plurielles
d'une langue cible de différer de celles de la source ; la vérification plus
stricte, forme par forme, s'exécute à la compilation des catalogues
([Extraction](extraction.md)).

La ligne sur l'indicateur de format concerne la validation qui tient compte des
marqueurs, pas la compatibilité du catalogue. `aucun` signifie que les outils
gettext standard peuvent toujours lire et compiler le message, mais que
`msgfmt --check-format` n'a pas de grammaire de marqueurs `$` à appliquer.

## Le coût { #what-it-costs }

Une f-string ne peut pas du tout être utilisée ainsi : lorsqu'une bibliothèque
la reçoit, c'est déjà une chaîne terminée, donc la traduire revient à traduire
un fragment. Les t-strings ([PEP 750]) gardent le texte statique et les valeurs
séparés, tout en conservant une syntaxe proche des f-strings et une liaison
explicite des valeurs. Les chaînes `$` offrent déjà une solution concise avec
un autre modèle de liaison et d'échec. `flufl.i18n` est un paquet mature qui
fonctionne sur Python 3.10 et suivants ; `gettext-tstrings` est actuellement en
phase alpha et, les t-strings étant une syntaxe nouvelle, il exige Python 3.14
ou plus récent.

L'autre coût est la restriction elle-même : une interpolation doit être un nom
simple.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

C'est une véritable contrainte. Avec la liaison des valeurs côté source et la
vérification des marqueurs à l'exécution, elle empêche les chaînes du catalogue
d'évaluer des expressions et conserve des noms de marqueurs explicites.

Comment Python est arrivé à cette croisée des chemins — deux PEP à dix ans
d'écart, et la discussion sur la bibliothèque standard close sans réponse —
est raconté, sources à l'appui, sur la page [Contexte](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [comportement documenté]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template personnalisé]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [traducteur]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
