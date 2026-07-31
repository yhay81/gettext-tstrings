---
description: "Adopter les t-strings dans un projet qui possède déjà des catalogues gettext : ce qui reste intact, ce qui passe en fuzzy, et comment déplacer un site d'appel à la fois."
---

# Migration

Si votre projet utilise déjà gettext, les questions qui décident de
l'adoptabilité de cette bibliothèque sont étroites : invalide-t-elle les
catalogues que vous avez, peut-elle cohabiter avec le code que vous n'êtes pas
prêt à changer, et quelle part du déplacement doit se faire d'un coup. Les
réponses, de la plus courte à la plus longue :

| Question | Réponse |
| --- | --- |
| Les fichiers `.po` et `.mo` existants fonctionnent-ils toujours ? | Oui. Mêmes fichiers, mêmes outils. |
| Anciens et nouveaux appels peuvent-ils vivre dans un même fichier ? | Oui, et un seul mapping d'extraction couvre les deux. |
| Le msgid change-t-il ? | Pas depuis `.format()`. Oui depuis le format `%`. |
| Tout le projet doit-il bouger d'un coup ? | Non. Un seul site d'appel est un changement valide. |
| Et Jinja, les gabarits Django, JavaScript ? | Intacts, mêmes catalogues. |

Le reste de cette page est le détail derrière chacune de ces réponses.

## Depuis `.format()` : le msgid ne change pas { #from-format-the-msgid-does-not-change }

C'est le cas où la migration ne coûte presque rien. Un message `str.format` et
un message t-string dérivent la *même* clé de catalogue, parce que la clé est
dans les deux cas le texte où `{name}` est resté :

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

La traduction existante reste donc attachée. En partant d'un catalogue qui
contient

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

changez l'appel, réextrayez, puis mettez à jour :

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

L'entrée qui revient diffère par deux lignes de métadonnées et rien d'autre —
un commentaire marqueur qui l'identifie comme message t-string, et un numéro de
ligne source :

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Aucun flag `fuzzy`, aucune retraduction, dans aucune langue. Le message se rend
immédiatement :

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` signalera les catalogues comme périmés"

    Ce commentaire marqueur et les numéros de ligne déplacés suffisent à faire
    dire à `pybabel update --check` qu'un catalogue doit être régénéré, parce
    qu'il compare l'entrée entière et pas seulement la traduction. Lancez le
    vrai `pybabel update` dans le même commit que le changement de code, et
    committez les catalogues avec lui — l'habitude même que
    [la barrière de CI](workflow.md#what-ci-gates) réclame déjà.

## Depuis le format `%` : le msgid change, donc les traductions passent en fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

La syntaxe printf vit *à l'intérieur* du message : la remplacer réécrit donc la
clé du catalogue. Il n'y a pas moyen de l'éviter, et c'est le coût honnête d'un
abandon de `%(name)s` :

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` reconnaît dans le nouveau message un proche parent de celui
qui a disparu et reporte l'ancienne traduction, marquée fuzzy :

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Trois choses à savoir sur cet état :

- **Rien ne casse à l'exécution.** Les entrées fuzzy sont exclues du `.mo`
  compilé, si bien que l'application rend le message source jusqu'à ce qu'un
  humain confirme la paire —
  [la même dégradation](workflow.md#the-cycle-after-the-first-translation) que
  traverse tout message reformulé.
- **`pybabel compile` signale chacune d'elles**, parce que le `%(name)s`
  reporté n'est pas un marqueur à accolades valide, et sort avec un statut non
  nul. Cette liste est votre file de travail, pas une fausse alerte : les
  entrées qu'elle contient ont réellement besoin d'être éditées.
- **L'ancien flag `python-format` fait le voyage** et doit être supprimé en
  même temps que le flag `fuzzy`, sinon `msgfmt --check-format` continuera
  d'appliquer les règles printf à un message au format à accolades.

Pour des marqueurs printf nommés, l'édition est mécanique — `%(name)s` devient
`{name}` et rien d'autre ne bouge — si bien qu'un gros catalogue est une passe
scriptée suivie d'une relecture par un traducteur, et non une retraduction. Le
`%s` positionnel, lui, n'est pas mécanique : il n'a aucun nom à reporter, et
choisir ce nom est justement l'objet du changement.

Pour cette raison, l'ordre pratique consiste à migrer les messages au format
`%` délibérément — un module, une release, une langue à la fois — plutôt qu'en
un seul balayage qui fait virer tous les catalogues au rouge d'un coup.

## Anciens et nouveaux appels cohabitent { #old-and-new-calls-coexist }

L'extracteur qui lit les t-strings lit aussi les appels gettext ordinaires : un
seul mapping couvre donc un fichier en pleine migration.

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Les deux messages atterrissent dans le même modèle, et seul celui issu d'une
t-string porte le commentaire marqueur qui active les vérifications
supplémentaires de cette bibliothèque :

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Il reconnaît `_()`, les quatre noms gettext standard, les alias `tr()` / `ntr()`
et les formes différées `lazy_gettext()` / `lazy_pgettext()`. Un helper à vous
doit être [déclaré dans le mapping](extraction.md#registering-your-own-function-names).

À l'exécution, les deux styles sont tout aussi indépendants :
`gettext.translation()` renvoie un objet translations, et `_` comme les points
d'entrée de cette bibliothèque y puisent.

## Ce qui ne bouge pas { #what-does-not-move }

- **Les langages de gabarits.** Le `{% trans %}` de Jinja2, les balises de
  gabarit de Django et leurs extracteurs Babel continuent de fonctionner sans
  changement et d'alimenter les mêmes catalogues PO. Les t-strings sont de la
  syntaxe Python ; elles s'appliquent au source Python.
- **Vos fichiers catalogues.** Aucun changement de format, aucun nouveau
  fichier, aucune étape de conversion.
- **Votre plateforme de traduction.** L'échange en `.po` est identique, et le
  flag `python-brace-format` que porte un message t-string est le même que
  porte un message `.format()` — la QA des marqueurs continue donc de
  fonctionner.
- **Le code non-Python.** Un catalogue JavaScript ou C dans le même projet
  n'est pas affecté.

## Une checklist de migration { #a-migration-checklist }

1. Ajoutez l'extra `babel` là où `pybabel` s'exécute, et faites passer le
   mapping `python` de `babel.cfg` à la méthode `gettext_tstrings` — un seul
   mapping couvre alors les deux styles, et `-k` continue de fonctionner pour
   les appels ordinaires.
2. Convertissez d'abord les sites d'appel `.format()`. Réextrayez, lancez
   `pybabel update` et committez les catalogues avec le code ; n'attendez
   aucune entrée fuzzy.
3. Convertissez les sites d'appel au format `%` par lots que vous pouvez faire
   relire, en réécrivant les marqueurs reportés et en effaçant les flags
   `fuzzy` et `python-format`.
4. Corrigez ce que la restriction refuse : une interpolation doit être un nom
   simple, donc `t"Hello {user.name}"` passe d'abord par une variable locale.
   C'est une édition de site d'appel, pas de catalogue.
5. Activez `strict = true` dans les options du mapping une fois le balayage
   terminé, pour qu'un message impossible à extraire fasse échouer
   [le build](extraction.md#lenient-locally-strict-in-ci) au lieu de
   disparaître du modèle.
6. Ajoutez le contrôle d'exécution décrit dans
   [En production](workflow.md#what-ci-gates) : rendre un message par langue
   livrée à travers un `Translator` strict.

Les étapes 2 et 3 sont des commits ordinaires. Rien dans cette liste n'exige
un jour de bascule.
