---
description: "Le contrat des marqueurs pour qui édite les fichiers .po : ce que vous pouvez changer, ce que vous devez laisser tranquille, et comment lire les erreurs."
---

# Pour les traducteurs

Cette page s'adresse à la personne qui édite le catalogue, pas à celle qui
écrit le code. Elle est courte à dessein, et elle est faite pour être liée ou
recopiée dans les consignes de traduction d'un projet.

Rien ici n'exige de savoir lire Python. Tout ici porte sur une seule chose :
les morceaux d'un message placés entre accolades.

## Ce qu'est un marqueur { #what-a-placeholder-is }

Un message de catalogue peut contenir des noms entre accolades :

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` est un **marqueur**. Quand le programme affiche ce message, il
remplace `{name}` par une valeur qu'il fournit — un nom de personne, un nom de
fichier, un nombre. Le marqueur n'est pas un mot à traduire ; c'est un
emplacement.

Votre traduction va dans le `msgstr`, et elle doit conserver cet emplacement :

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Ce que vous pouvez changer, et ce que vous ne pouvez pas { #what-you-may-change-and-what-you-may-not }

Vous **pouvez** :

- **Déplacer un marqueur** partout où la grammaire de la langue cible le
  demande, y compris en tête du message.
- **Répéter un marqueur** si la langue a besoin de la valeur deux fois.
- **Réécrire tous les autres mots**, y compris la ponctuation, les espaces et
  l'ordre de la phrase.

Vous **ne devez pas** :

- **Traduire le nom entre les accolades.** `{name}` reste `{name}`, même dans
  une langue qui n'écrit rien d'autre en lettres latines.
- **Supprimer les accolades**, ni écrire le nom sans elles.
- **Remplacer les accolades ASCII `{` `}` par les pleine chasse `｛` `｝`.**
  Beaucoup de méthodes de saisie produisent les formes pleine chasse ; elles
  sont presque identiques à l'œil et ne fonctionnent pas.
- **Ajouter du formatage**, comme `{name!r}` ou `{amount:.2f}`. La façon dont
  une valeur s'affiche se décide dans le programme, pas dans le catalogue.
- **Inventer un marqueur** absent du `msgid`.

Si un message a besoin d'une valeur que l'original ne propose pas, c'est un
message que le développeur doit changer. Dites-le plutôt que de contourner.

## Formes plurielles { #plural-forms }

Un message compté arrive avec une case `msgstr` par forme plurielle de votre
langue, et c'est votre langue qui décide de leur nombre : une pour le japonais,
deux pour l'allemand, trois pour le russe, six pour l'arabe. Remplissez chaque
case que le catalogue vous donne.

Deux règles qui prennent les gens à revers :

- **Les cases ne sont pas « singulier, pluriel, encore plus pluriel ».** Chaque
  indice signifie ce que la règle de pluriel de votre langue dit qu'il
  signifie. La troisième forme du letton est pour le zéro seul ; la deuxième du
  slovène pour exactement deux ; le gallois met le cas général à l'indice 0 et
  le singulier à l'indice 1.
- **Deux cases peuvent légitimement contenir le même texte.** En turc, en
  hongrois, en persan et en bengali, un nom reste au singulier après un
  numéral : les deux formes d'un message compté sont donc la même chaîne. C'est
  correct, ce n'est pas une bévue de copier-coller.

Les règles sur les marqueurs ci-dessus s'appliquent à chaque forme
indépendamment.

## Entrées fuzzy { #fuzzy-entries }

Une entrée marquée `fuzzy` est la supposition d'une machine : le développeur a
changé le message d'origine, et l'outillage a apparié le nouveau texte avec
votre ancienne traduction pour vous donner un point de départ.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Une entrée fuzzy **n'est pas utilisée par le programme** — il affiche
l'original non traduit à la place — jusqu'à ce que quelqu'un en révise le texte
et retire la marque `fuzzy`. La plupart des éditeurs PO ont un bouton pour
exactement cela.

## Lire un message d'erreur { #reading-a-failure-message }

L'outillage vérifie les marqueurs à la compilation du catalogue, et le message
est écrit pour vous plutôt que pour un programmeur. Signaler seulement que
`{name}` manque est une impasse quand vous avez ces caractères sous les yeux :
là où un marqueur semble présent sans l'être, le message dit donc pourquoi.
Face à l'original `Hello {name}`, chacun des cas suivants est signalé sous
`translation does not match the source placeholders:`

| Votre traduction contient | La raison donnée |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Les caractères qu'on ne peut pas voir ont droit à leur propre traitement. Une
espace insécable à l'intérieur des accolades est produite par une méthode de
saisie et n'est affichée par aucun éditeur : le message l'imprime donc par
point de code plutôt que de nommer un caractère que vous ne trouveriez jamais :

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un nom dont les lettres mélangent les systèmes d'écriture — le cas de
l'homoglyphe, où un `а` cyrillique est indiscernable d'un latin — est affiché
deux fois, une fois lisiblement et une fois échappé, ce qui est la seule forme
qui distingue les deux :

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

La même levée d'ambiguïté s'applique quand un nom entièrement grec ou
cyrillique entre en conflit avec un nom source ASCII, y compris le cas d'une
seule lettre `a` latine contre `а` cyrillique.

Si vous rencontrez l'un de ces cas et que la correction ne saute pas aux yeux,
le geste sûr est de supprimer le marqueur que vous avez tapé et de recopier
celui du `msgid`.

## Ce que les contrôles ne peuvent pas faire { #what-the-checks-cannot-do }

L'outillage vérifie que vos marqueurs sont intacts. Il ne peut pas dire si la
traduction est exacte, naturelle ou juste pour le contexte — cela reste
entièrement entre vos mains.

Deux choses aident plus que n'importe quel contrôle :

- **Lisez le commentaire du traducteur.** Une ligne commençant par `#.`
  au-dessus du message, c'est le développeur qui vous dit où il apparaît et ce
  qu'il signifie.
- **Posez des questions sur `msgctxt`.** Quand le même mot apparaît deux fois
  avec des contextes différents, c'est parce que les deux doivent se traduire
  différemment — « Open » le bouton et « Open » l'état, par exemple.
