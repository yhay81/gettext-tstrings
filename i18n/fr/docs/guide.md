---
description: "L'API d'exécution : liaison d'un catalogue, langue par requête, chaînes différées et signalement des traductions incorrectes."
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

## Si un catalogue est incorrect { #what-happens-when-a-catalog-is-wrong }

Si les marqueurs d'une traduction ne correspondent pas à la source, le
comportement par défaut rend le texte source au lieu de lever. Cela suit le
contrat de gettext : un mauvais catalogue ne doit pas casser l'application.

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

## Lire un message d'erreur { #reading-a-failure-message }

Les messages expliquent aussi pourquoi un marqueur visible n'est pas valide :

| La traduction contient | La raison |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Un espace insécable invisible est affiché par code point :

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un homoglyph mélangeant les alphabets est affiché lisiblement puis échappé :

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Cela couvre aussi les conflits entre noms entièrement grecs ou cyrilliques et
leurs équivalents ASCII.

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
