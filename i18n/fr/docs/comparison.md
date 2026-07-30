---
description: "Le même message traduisible écrit avec le format %, .format(), les chaînes $ de flufl.i18n et une t-string, y compris la manière dont chacun lie les valeurs et gère un catalogue endommagé."
---

# Pourquoi les t-strings

Toute méthode qui insère une valeur dans un message traduisible doit répondre à
la même question : *quelle part du langage de formatage le catalogue
contrôle-t-il ?* Les quatre réponses ci-dessous diffèrent aussi par l'origine
des valeurs et par ce qui arrive lorsqu'un catalogue modifie un marqueur.

## Format %

```python
_("Hello %(name)s") % {"name": name}
```

La chaîne du catalogue contient la syntaxe printf, notamment une lettre de type
finale facile à ignorer et qu'une modification d'un caractère peut endommager :

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Un caractère supprimé dans un éditeur PO devient une traceback en production.
GNU `msgfmt --check-format` le détecte, mais seulement si le message porte le
flag `python-format` et si le catalogue passe réellement par msgfmt.

## str.format

```python
_("Hello {name}").format(name=name)
```

Il supprime la lettre de type finale tout en conservant un marqueur nommé et
librement réordonnable.

Le problème se trouve de l'autre côté. `str.format` est un petit langage
d'expressions : l'appliquer à une chaîne autorise cette chaîne à l'utiliser.

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Un catalogue voyage comme donnée : plateforme de traduction, plusieurs mains,
retour en `.po`, compilation en `.mo`, parfois import depuis un tiers.
`.format()` donne à chaque étape la possibilité d'accéder aux attributs des
objets fournis.

## Chaînes `$` et flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

Le module standard [`string.Template`][stdlib-template] fournit le langage d'interpolation
`$name`, mais ne constitue pas en lui-même une API de traduction.
[`flufl.i18n`][flufl-i18n] associe ce style à la recherche dans les catalogues gettext. Il
construit l'espace de noms de substitution à partir des variables globales et
locales de l'appelant ; un mapping `extras` facultatif prend le pas sur les deux.
La syntaxe destinée aux traducteurs ne comporte ni lettre de type finale ni
spécificateur de format, et les marqueurs restent librement réordonnables.

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

## t-strings

```python
tr(t"Hello {name}")
```

Le catalogue voit toujours `Hello {name}` et reste un catalogue PO/MO ordinaire.
L'extraction du code source diffère : les outils actuels nécessitent un
extracteur compatible avec les t-strings, comme celui fourni par ce paquet. Une
traduction est validée par rapport aux marqueurs du message source puis rendue
par cette bibliothèque, qui n'accepte que des noms simples.

| Une traduction contenant | est rejetée avec |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Le formatage reste dans le code :

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` n'atteint jamais le catalogue.

## Comparaison

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Marqueur nommé | oui | oui | oui | oui |
| Réordonnable par le traducteur | oui | oui | oui | oui |
| Origine des valeurs | mapping explicite | arguments explicites | variables globales et locales de l'appelant, avec un `extras` facultatif prioritaire | interpolations capturées par la t-string |
| Le catalogue contrôle la conversion de valeur ou le spécificateur de format | oui | oui | non | non |
| Le catalogue peut demander l'accès à un attribut | non | oui | oui, avec des noms à points | non |
| Marqueur source supprimé au rendu | omis silencieusement | omis silencieusement | omis silencieusement | motif source entièrement rendu [par défaut](guide.md#what-happens-when-a-catalog-is-wrong) |
| Marqueur ajouté indisponible au rendu | lève une exception | lève une exception | reste visible | motif source entièrement rendu [par défaut](guide.md#what-happens-when-a-catalog-is-wrong) |
| Ensemble des marqueurs source vérifié à l'exécution (singulier) | non | non | non | oui |
| Indicateur de format PO déduit par Babel pour l'exemple | `python-format` | `python-brace-format` | aucun | `python-brace-format` |
| Utilise des catalogues PO/MO ordinaires | oui | oui | oui | oui |
| Nécessite un extracteur de code source personnalisé | non | non | non | oui, actuellement |

La ligne sur l'indicateur de format concerne la validation qui tient compte des
marqueurs, pas la compatibilité du catalogue. `aucun` signifie que les outils
gettext standard peuvent toujours lire et compiler le message, mais que
`msgfmt --check-format` n'a pas de grammaire de marqueurs `$` à appliquer.

## Le coût

Une f-string ne peut pas du tout être utilisée ainsi : lorsqu'une bibliothèque
la reçoit, c'est déjà une chaîne terminée, donc la traduire revient à traduire
un fragment. Les t-strings ([PEP 750]) permettent cette séparation en gardant
une syntaxe proche des f-strings et en liant explicitement les valeurs. Les
chaînes `$` offrent déjà une solution concise avec un autre modèle de liaison
et d'échec. `flufl.i18n` est un paquet mature dont la version actuelle prend en
charge Python 3.10 ; `gettext-tstrings` est actuellement en phase alpha et les
t-strings natives lui imposent Python 3.14 comme version minimale.

L'autre coût est la restriction elle-même : une interpolation doit être un nom
simple.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

C'est une véritable contrainte. Avec la liaison des valeurs côté source et la
vérification des marqueurs à l'exécution, elle empêche les chaînes du catalogue
d'évaluer des expressions et conserve des noms de marqueurs explicites.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [comportement documenté]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template personnalisé]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [traducteur]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
