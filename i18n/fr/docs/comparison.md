---
description: "Le même message traduisible écrit avec le format %, .format(), les chaînes $ de flufl.i18n et une t-string, comparés sur les erreurs de traduction, l'autorité du catalogue et le coût d'intégration."
---

# Pourquoi les t-strings

Quatre façons d'insérer une valeur dans un message traduisible, comparées sur
la même phrase. Toutes les quatre nomment leurs marqueurs et laissent un
traducteur les réordonner ; elles diffèrent par ce qui arrive quand une
traduction est fausse, par la part de votre programme que le catalogue peut
atteindre, et par ce que leur adoption coûte.

Les tableaux viennent d'abord, pour que vous puissiez repérer la ligne qui vous
intéresse et ne lire que la section qui se trouve derrière.

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

## Comparaison { #side-by-side }

**Quand un traducteur se trompe.** Un catalogue passe entre beaucoup de mains,
et l'essentiel de ce qui y tourne mal est accidentel :

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Une traduction *supprime* un marqueur — que rend-on ? | la valeur disparaît silencieusement | la valeur disparaît silencieusement | la valeur disparaît silencieusement | le message source, avec un avertissement ([par défaut](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Une traduction *ajoute* un marqueur inconnu — que rend-on ? | une exception | une exception | le marqueur reste visible comme texte | le message source, avec un avertissement ([par défaut](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Une traduction *reformate* un marqueur — que rend-on ? | ce que le catalogue a demandé, ou une exception si la lettre de type ne convient plus à la valeur | ce que le catalogue a demandé | inexprimable dans les chaînes `$` | le message source, avec un avertissement |
| Les marqueurs sont-ils vérifiés au moment du rendu ? | non | non | non | oui (voir ci-dessous) |

**Quelle autorité détient le catalogue.** Une traduction est une donnée venue
de l'extérieur de votre dépôt, et chaque style lui confie une quantité de
pouvoir différente :

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| D'où viennent les valeurs ? | un mapping explicite | des arguments explicites | les variables locales et globales de l'appelant, plus un `extras` facultatif | les valeurs capturées dans la t-string |
| Le catalogue peut-il changer le formatage d'une valeur ? | oui | oui | non | non |
| Le catalogue peut-il fouiller les objets (accès aux attributs) ? | non | oui | oui, avec des noms à points | non |
| Où vit « la langue courante » ? | là où l'application la met | là où l'application la met | une pile de codes de langue sur l'objet application partagé | une `ContextVar`, par tâche ou par requête |

**Ce que coûte l'intégration.** Tout ce qui précède est gratuit si l'outillage
convient ; c'est ici qu'il pourrait ne pas convenir :

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python minimum | n'importe lequel | n'importe lequel | 3.10 | **3.14** |
| Maturité | bibliothèque standard | bibliothèque standard | version stable | **alpha** |
| Utilise des catalogues PO/MO ordinaires ? | oui | oui | oui | oui |
| Nécessite un extracteur de code source personnalisé ? | non | non | non | oui, actuellement |
| Quel flag PO Babel déduit-il, pour la validation par les outils existants ? | `python-format` | `python-brace-format` | aucun | `python-brace-format` |

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

## Compatibilité et maturité { #compatibility-and-maturity }

Les deux premières lignes du dernier tableau sont celles qui décident de
l'adoption : elles méritent d'être énoncées clairement plutôt que rangées dans
des cellules.

Le format `%` et `.format()` sont intégrés à Python et n'exigent aucune
dépendance. [`flufl.i18n`][flufl-i18n] est un paquet mature, publié et utilisé
en production, qui fonctionne sur Python 3.10 et suivants. `gettext-tstrings`
est en **alpha** et exige **Python 3.14 ou plus récent**, parce que les
t-strings sont une syntaxe nouvelle de la 3.14 — il n'en existe pas de
rétroportage et il ne peut pas en exister. Sa [spécification](spec.md) en est
la partie stable ; l'API Python peut encore bouger avant la 1.0.

Ce qu'aucune des quatre ne coûte, c'est la compatibilité des catalogues. Toutes
produisent des fichiers POT/PO/MO ordinaires que chaque éditeur PO, chaque
plateforme de traduction et chaque outil GNU gettext lit déjà, si bien que le
choix ci-dessous est réversible d'une façon qu'un changement de *format* de
catalogue ne serait pas. [Migration](migration.md) traite le déplacement d'un
projet existant.

Les sections qui suivent détaillent chaque compromis, une méthode à la fois.

## Format % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Ce qui peut mal tourner : un marqueur endommagé devient une exception à
l'exécution, à moins que la validation du catalogue ne l'attrape avant.

La chaîne du catalogue contient la syntaxe printf, notamment une lettre de type
finale — le `s` de `%(name)s` — facile à ignorer et facile à endommager :

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Un caractère supprimé dans un éditeur PO devient une exception à l'exécution, à
moins que la validation du catalogue ne l'attrape avant. GNU
`msgfmt --check-format` attrape bien celle-ci, mais seulement pour les messages
portant le flag `python-format`, et seulement si le catalogue passe réellement
par msgfmt en chemin vers votre application.

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

Le module standard [`string.Template`][stdlib-template] fournit le langage
d'interpolation `$name`, mais ne constitue pas en lui-même une API de
traduction. [`flufl.i18n`][flufl-i18n] associe ce style à la recherche dans les
catalogues gettext. Remarquez que la valeur n'est jamais passée en argument :
flufl.i18n construit l'espace de noms de substitution à partir des variables
globales et locales de l'appelant — toutes les variables qui existent au point
d'appel sont disponibles pour le message. Un mapping `extras` facultatif prend
le pas sur les deux. La syntaxe destinée aux traducteurs ne comporte ni lettre
de type finale ni spécificateur de format, et les marqueurs restent librement
réordonnables.

Une substitution indisponible ne lève pas d'exception. Avec `name = "Ada"` et
sans `nombre` dans l'espace de noms de l'appelant, une traduction de catalogue
`Hello $nombre` donne `Hello $nombre` : le marqueur non résolu reste visible.
Ce [comportement documenté][documented behavior] préserve le reste du message
traduit au lieu de faire échouer l'appel. Les exceptions levées pendant la
résolution d'un attribut ou la conversion d'une valeur peuvent néanmoins se
propager.

Sur un point pertinent, `flufl.i18n` est plus puissant qu'un
`string.Template` brut. Son [Template personnalisé][custom Template] accepte
des marqueurs avec des points, comme `$settings.api_key`, et son
[traducteur][translator] résout ces chemins sur les valeurs de l'appelant. Un
marqueur traduit peut désigner toute variable locale ou globale disponible de
l'appelant et, avec la syntaxe à points, parcourir ses attributs. C'est
pratique lorsqu'un message a besoin d'un attribut, tout en faisant du cadre de
l'appelant une partie de l'espace de noms de substitution du catalogue. La
comparaison faite ici décrit `flufl.i18n` 6.0.0, pas tous les usages possibles
de `string.Template`.

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
avertissement et rend le message source, si bien qu'un mauvais catalogue ne fait
jamais tomber l'application —
[le contrat que gettext lui-même respecte](guide.md#what-happens-when-a-catalog-is-wrong).

Le formatage reste là où il a été écrit, dans le code :

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` n'atteint jamais le catalogue : aucune traduction ne peut le modifier
et aucun traducteur n'a à le regarder. C'est cependant un format *fixe*, pas un
format localisé — choisir les chiffres et les séparateurs par langue est
[le travail de Babel, avant l'appel](guide.md#locale-aware-values).

Une dernière différence concerne l'outillage : les t-strings sont une syntaxe
nouvelle, donc les extraire vers un `.pot` demande aujourd'hui un extracteur
qui les comprend, comme celui que ce paquet
[fournit pour Babel](extraction.md).

## Le coût de la restriction { #the-cost-of-the-restriction }

Au-delà de l'exigence sur Python, le prix de tout cela tient en une règle : une
interpolation doit être un nom simple.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

C'est une véritable contrainte, et c'est la contrainte même qui produit les
garanties ci-dessus. Avec la liaison des valeurs côté source et la vérification
des marqueurs à l'exécution, elle empêche les chaînes du catalogue d'évaluer des
expressions et conserve aux noms de marqueurs un sens pour la personne qui les
traduit.

Une f-string ne peut pas du tout être utilisée ainsi : lorsqu'une bibliothèque
la reçoit, c'est déjà une chaîne terminée, donc la traduire revient à traduire
un fragment. Les t-strings ([PEP 750]) gardent le texte statique et les valeurs
séparés, tout en conservant une syntaxe proche des f-strings et une liaison
explicite des valeurs.

Comment Python en est arrivé là — deux PEP à dix ans
d'écart, et la discussion sur la bibliothèque standard close sans réponse —
est raconté, sources à l'appui, sur la page [Contexte](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
