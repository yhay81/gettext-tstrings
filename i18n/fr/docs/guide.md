---
description: "L'API d'exécution : quel point d'entrée choisir, la liaison d'un catalogue, la langue par requête, les chaînes différées, les valeurs dépendant de la locale et le signalement des traductions incorrectes."
---

# Guide

Cette page est la référence d'exécution : tout ce que fait votre *code
applicatif* avec cette bibliothèque une fois les catalogues en place. Si vous
n'avez pas encore vu la boucle complète — marquer, extraire, traduire,
compiler, exécuter — le [tutoriel](tutorial.md) la parcourt une fois en cinq
minutes ; la création et la validation des catalogues sont couvertes dans
[Extraction](extraction.md), et la façon dont une équipe fait tourner la
boucle — cycles de mise à jour, CI, plateformes de traduction — est
[En production](workflow.md).

## Quel point d'entrée choisir ? { #which-entry-point-should-i-use }

Le paquet exporte plusieurs façons de traduire un message parce que les
applications lient une langue de plusieurs façons différentes. Choisissez selon
la manière dont votre programme décide de la langue dans laquelle il se trouve :

| Votre situation | À utiliser |
| --- | --- |
| Une seule langue pour tout le processus — une CLI, une application de bureau, un script | `Translator`, appelé `_` |
| Une langue par requête ou par tâche asynchrone — une application web | `use_translations()` autour du travail, puis `tr()` |
| Un message défini à l'import — un libellé de formulaire, une enum, une constante | `lazy_gettext()` ou `lazy_pgettext()` |
| Un nombre décide de la formulation | `ngettext()` / `npgettext()`, sous l'une des formes ci-dessus |
| Rendre un pattern sans aucun catalogue | `compile_template()` |

Tout ce qui suit reprend ces cinq entrées, dans cet ordre.

## Lier un catalogue { #binding-a-catalog }

La forme recommandée reprend l'usage objet de gettext : liez une traduction
standard une fois et utilisez le processeur appelable comme `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Les fonctions de module suivent les noms et les arguments positionnels de la
bibliothèque standard :

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` et `ntr` sont les alias exacts de `gettext` et `ngettext`.

## Langue par requête { #per-request-language }

Un framework web choisit une langue par requête. Liez sa traduction au contexte
courant : chaque appel de module utilisera cette langue, y compris entre
requêtes concurrentes.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations()` lie sans bloc pour les frameworks qui gèrent eux-mêmes le
cycle de vie ; `get_translations()` lit la liaison. Un argument
`translations=` explicite est prioritaire. Sans liaison, les fonctions gettext
globales de la bibliothèque standard servent de fallback. Des exemples
complets pour Flask et un middleware ASGI figurent sur la page
[En production](workflow.md#binding-a-language-at-runtime).

## Traduction différée { #deferred-translation }

Une t-string capture immédiatement ses valeurs. Pour une étiquette, une enum ou
une constante définie à l'import mais rendue dans la langue active à
l'*utilisation*, employez une chaîne différée.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` se rend via `str()`, `format()` et les f-strings, et se compare à
son texte.

!!! note "Volontairement non hashable"

    Son texte dépend de la langue. Un hash qui change corromprait silencieusement
    un set ou un dict. Appelez d'abord `str()` pour obtenir une clé.

`strict` se décide là où le message est écrit, pas là où il est rendu :

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Une chaîne différée se rend là où elle finit par être utilisée — dans un
gabarit, un formulaire, une ligne de log — et cet endroit sait rarement s'il
s'agit d'une exécution de test ou de la production. Passer `strict=True` à la
définition est ce qui permet d'appliquer le même choix [bruyant en CI,
indulgent en production](#what-happens-when-a-catalog-is-wrong) à une chaîne
qui n'est pas rendue sur son site d'appel.

Les pluriels dépendent du nombre à l'exécution : rendez-les immédiatement avec
`ngettext`.

## Plusieurs langues à la fois { #several-languages-at-once }

Une même requête a souvent besoin de plusieurs langues : une page rendue pour
le lecteur qui met aussi en file une notification vers un compte réglé sur une
autre, ou un récapitulatif qui cite chaque participant dans la sienne. Les
liaisons s'imbriquent, et quitter le bloc intérieur restaure celui du dessus.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Sur une liste de destinataires, ce sont les chaînes différées qui font le
travail : le message est écrit une seule fois, à l'import, et se rend une fois
par langue.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

La liaison est une `ContextVar`, pas une pile portée par un objet partagé : des
requêtes qui se chevauchent ne peuvent donc pas récupérer la langue les unes
des autres — y compris dans le cas où elles *quittent* leurs blocs dans l'ordre
où elles y sont entrées, l'entrelacement qu'une pile à empilement prend à
revers. Charger un catalogue par langue coûte peu : `gettext.translation()`
analyse chaque `.mo` une seule fois et distribue des copies qui partagent le
catalogue analysé.

!!! warning "Qu'un thread de travail hérite de la liaison dépend du build"

    Un `threading.Thread` nu, ou `ThreadPoolExecutor.submit`, démarre soit depuis
    une copie du contexte de l'appelant, soit depuis un contexte vide, et ce qui
    en décide est `sys.flags.thread_inherit_context` — vrai par défaut sur les
    builds free-threaded, faux partout ailleurs. Le même code rend donc la langue
    liée sur 3.14t et le catalogue global au processus sur 3.14. Transmettez le
    contexte plutôt que de dépendre de la valeur par défaut :

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` le fait déjà pour vous.

## Valeurs dépendant de la locale { #locale-aware-values }

Cette bibliothèque décide *où* une valeur apparaît dans un message traduit.
Elle ne localise pas la valeur elle-même. `{amount:,.2f}` est une spécification
de format Python au comportement fixe — une virgule tous les trois chiffres et
un point avant les décimales — et elle produit les mêmes caractères quelle que
soit la langue du message :

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

L'allemand écrit ce nombre `1.234,50`, le français `1 234,50`, et le hindi
groupe `1234567` en `12,34,567` plutôt qu'en `1,234,567`. Les nombres, les
devises, les dates, les heures et les unités relèvent de
[Babel][babel-numbers]. Formatez la valeur d'abord, puis placez la chaîne
terminée :

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Dans un message avec compte, le nombre fait deux métiers — il sélectionne la
forme plurielle et il apparaît dans le texte — et seul le second est localisé.
Gardez le compte brut pour la sélection et passez la chaîne formatée pour
l'affichage :

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formater avant l'appel est aussi ce qui garde une spécification de format hors
du catalogue : ce qu'un traducteur voit est un morceau de texte terminé, pas un
nombre accompagné d'instructions de rendu.

## Si un catalogue est incorrect { #what-happens-when-a-catalog-is-wrong }

Si les marqueurs d'une traduction ne correspondent pas à la source — un champ
manquant, inconnu ou reformaté qui a échappé à la validation, venu d'un MO
édité à la main, d'un catalogue tiers ou d'une pipeline qui saute le contrôle —
le comportement par défaut rend le message source au lieu de lever. Cela suit
le contrat de gettext lui-même : un mauvais catalogue ne casse jamais
l'application.

Avec `Hello {name}` traduit en `こんにちは {nombre}`, le rendu réussit et un
avertissement est envoyé au logger `gettext_tstrings` :

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

L'avertissement n'est émis qu'une fois par message et pattern, pas à chaque
rendu : une entrée de catalogue cassée n'inonde pas le journal. En test et CI,
activez le mode strict :

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

La même recherche lève alors :

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Ces messages sont écrits pour qui peut agir dessus, c'est-à-dire, pour un
problème de catalogue, un traducteur plus souvent qu'un programmeur — donc
lorsqu'un marqueur *semble* présent sans l'être, le message explique pourquoi
au lieu de répéter qu'il manque. Accolades pleine chasse, `{{name}}` doublé,
espace insécable invisible, lettre cyrillique au milieu de lettres latines :
chaque cas a sa propre formulation, listée avec des exemples sur
[Pour les traducteurs](translators.md#reading-a-failure-message). Cette
page-là est écrite pour être remise à la personne qui édite le `.po`.

## Rendre un pattern sans catalogue { #rendering-a-pattern-without-a-catalog }

`compile_template` produit le msgid et les valeurs liées, puis rend un pattern :

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` valide avec les mêmes règles et **lève toujours** en cas d'écart. Il
n'existe pas de fallback sans recherche de catalogue.

## Sécurité et périmètre { #safety-and-scope }

Valide :

```python
tr(t"Hello {name}")
```

Rejeté volontairement :

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Calculez d'abord une valeur explicite :

```python
name = user.display_name()
tr(t"Hello {name}")
```

Une traduction n'est jamais évaluée et ne peut ajouter ni accès aux attributs,
ni appel, ni conversion, ni format. L'appelant reste responsable de
l'**échappement** pour la destination et de l'**intégrité du catalogue**, comme
avec gettext standard.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
