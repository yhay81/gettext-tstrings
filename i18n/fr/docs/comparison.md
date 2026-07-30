---
description: "Le même message avec le format %, .format() et une t-string, et la part du format contrôlée par le catalogue."
---

# Pourquoi les t-strings

Toute méthode qui insère une valeur dans un message traduisible doit répondre à
la même question : *quelle part du langage de formatage le catalogue
contrôle-t-il ?*

## Format %

```python
_("Hello %(name)s") % {"name": name}
```

La chaîne du catalogue contient la syntaxe printf. La partie la plus facile à
abîmer est aussi la moins parlante : la lettre finale qui choisit le rendu.

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

Le marqueur est nommé, sans caractère final fragile, et peut être réordonné.
Mais `str.format` est un petit langage d'expressions : l'appliquer à une chaîne
autorise cette chaîne à l'utiliser.

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

## t-strings

```python
tr(t"Hello {name}")
```

Le msgid reste `Hello {name}`. La traduction n'est toutefois plus une chaîne de
format : elle est validée contre les marqueurs source puis rendue par la
bibliothèque, qui n'accepte que des noms simples.

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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| Marqueur nommé | oui | oui | oui |
| Réordonnable | oui | oui | oui |
| Un caractère perdu casse le rendu | **oui** | non | non |
| Le catalogue contrôle le format | oui | oui | **non** |
| Le catalogue accède aux attributs | non | **oui** | **non** |
| Un catalogue incorrect lève au rendu | **oui** | **oui** | non, [par défaut](guide.md#what-happens-when-a-catalog-is-wrong) |
| Compatible PO/MO et `msgfmt` | oui | oui | oui |

## Le coût

Une f-string est déjà terminée quand la bibliothèque la reçoit. Les t-strings
([PEP 750]) rendent cette séparation possible, d'où Python 3.14 minimum.

L'interpolation doit en contrepartie être un nom simple :

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Cette contrainte apporte toutes les garanties précédentes et donne aux
traducteurs un nom compréhensible plutôt qu'une expression.

  [PEP 750]: https://peps.python.org/pep-0750/
