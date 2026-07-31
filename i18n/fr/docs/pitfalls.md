---
description: "Ce que traduire un petit site en trente-cinq langues casse réellement, ce que la bibliothèque peut détecter pour vous et ce qu'elle ne peut pas."
---

# Pièges

Ce site est traduit en trente-cinq langues, et chacune de ces éditions a été
produite en suivant la boucle que cette documentation enseigne. C'est un
corpus modeste à l'échelle de l'industrie, et il a pourtant suffi à rencontrer
la plupart des pièges qui rendent l'i18n plus difficile qu'il n'y paraît.

Chaque section ci-dessous décrit un incident réellement survenu ici, la forme
qu'il avait sur le moment, et où passe la frontière entre ce que la
bibliothèque vérifie pour vous et ce qui reste votre jugement.

## Renommer une variable retraduit une phrase { #renaming-a-variable-retranslates-a-sentence }

Le msgid est la clé du catalogue, et un nom interpolé se trouve *à
l'intérieur*. Déplacer une constante à la portée du module et la passer en
majuscules comme le demande le style Python — `author` en `AUTHOR` — a
transformé `Copyright © 2026 {author} · MIT License` en un message qu'aucun
catalogue n'avait jamais vu. Chaque traduction de cette ligne serait repassée
par le cycle fuzzy, dans toutes les langues, pour un renommage qui ne changeait
rien de visible pour un lecteur.

La bibliothèque ne vous en empêchera pas : les deux graphies sont des noms de
marqueur valides. Ce qu'elle fait, c'est rendre ce nom *digne* d'être protégé
— une interpolation doit être un [nom simple](internals.md#from-template-to-msgid),
de sorte que ce qui figure dans la clé du catalogue est un mot qu'un traducteur
peut lire, pas une expression.

Le cas symétrique est sûr par construction. Les conversions et les
spécifications de format ne font pas partie du msgid : resserrer
`{amount:,.2f}` en `{amount:,.0f}` ne change aucune clé et n'invalide aucune
traduction nulle part.

## `nplurals=2` ne veut pas dire deux chaînes différentes { #nplurals-2-does-not-mean-two-different-strings }

Le turc, le hongrois, le persan et le bengali déclarent tous deux formes
plurielles, et dans ces quatre langues les deux formes d'un message compté sont
légitimement la *même chaîne* — le nom reste au singulier après un numéral,
donc `{n} sayfa` convient pour une page comme pour dix. Un relecteur qui
« corrige » cette duplication casse la traduction.

L'erreur inverse est tout aussi facile. La troisième forme du letton existe
pour **le zéro seul** ; la deuxième du slovène est un **duel**, pour exactement
deux ; la dernière forme du roumain exige le mot `de` que ses deux premières ne
doivent pas porter. Remplir ces cases avec un singulier et un pluriel produit
un catalogue qui n'est faux que pour des nombres que personne ne teste.

Pire, l'*ordre* des cases n'est pas sémantique. Le gallois indexe ses cinq
formes de telle sorte que `msgstr[0]` est le cas général et `msgstr[1]` le
singulier. Les remplir dans l'ordre évident place le singulier là où tout
message non compté ira le chercher.

La bibliothèque ne prend rien de tout cela en charge, et c'est bien l'idée : la
règle de pluriel de la langue cible vit dans l'en-tête de son propre catalogue,
et la [règle union/intersection](spec.md) permet à une traduction d'avoir plus
de formes, ou moins, que la source. Ce qu'elle vérifie est la seule chose
vérifiable sans connaître la langue — que chaque forme conserve les marqueurs
dont elle a besoin.

## Deux formes peuvent être identiques à bon droit { #two-forms-can-be-identical-for-a-reason }

L'irlandais a cinq formes plurielles, et dans le rapport de build de ce site
plusieurs d'entre elles s'écrivent pareil. Ce n'est pas une bévue de
copier-coller : *leathanach* commence par `l`, et aucune des deux mutations
initiales que déclenchent les numéraux irlandais ne s'écrit sur `l`. Ces formes
font pourtant un vrai travail — le radical alterne entre *leathanach* et
*leathanaigh*, et au-delà de dix les nombres reviennent au singulier — mais
aucun nom signifiant « page » ne ferait apparaître le contraste.

Tout contrôle qui signale les formes dupliquées comme suspectes signalera de
l'irlandais correct. Un humain qui connaît la langue est ici le seul relecteur
possible.

## Un message ne peut s'accorder qu'avec un seul nombre { #a-message-can-only-agree-with-one-count }

Le rapport de build de ce site indique combien de pages ont été rendues et en
combien de temps. L'écrire « Rendered {n} pages in {seconds} seconds » paraît
inoffensif et n'est pas traduisible : gettext choisit une forme à partir d'un
seul nombre, et ce nombre est `n`. Le mot *seconds* devrait s'accorder avec un
nombre que la machinerie du pluriel ne voit jamais.

La correction consiste à faire de la seconde quantité un symbole d'unité plutôt
qu'un mot, et les symboles d'unité sont eux-mêmes localisés : les catalogues de
ce site portent `s`, `с`, `ث`, `שנ׳` et `mp`, et la typographie française,
espagnole et suédoise veut une espace avant le symbole là où l'anglais n'en met
pas. Rien de tout cela ne regarde la bibliothèque — mais remarquer qu'un
message demande *deux* accords, si, et le seul outil pour cela est d'écrire le
message autrement.

## Modifier une phrase anglaise modifie la grammaire étrangère { #editing-an-english-sentence-edits-foreign-grammar }

La page d'accueil disait autrefois « all ten language editions ». Retirer le
nombre — une modification d'un seul mot en anglais, faite parce que ce nombre
devenait sans cesse obsolète — a fait passer un sujet pluriel au singulier.
L'espagnol, l'italien, le portugais, le russe, l'ukrainien, le grec, le
néerlandais et l'hébreu ont tous dû réaccorder le verbe ; plusieurs ont dû
changer aussi le participe.

Une modification de la source qui se lit comme triviale en anglais ne l'est pas
en aval. La marquer fuzzy, ce que fait `pybabel update`, est le mécanisme qui
donne à chaque traducteur la chance de s'en apercevoir.

## Les différences invisibles survivent à tous les copier-coller { #invisible-differences-survive-every-copy-paste }

Le guide cite un diagnostic contenant `(nаme)` — un échappement délibéré, parce
que le caractère qu'il nomme est un `а` cyrillique qu'aucun lecteur ne peut
distinguer du latin. Les traducteurs de ce site ont converti cet échappement en
caractère réel **cinq fois distinctes**, dans cinq langues différentes,
produisant chaque fois une page qui avait l'air correcte et qui était fausse.

Celui-là, la bibliothèque le détecte, et c'est la raison pour laquelle les
diagnostics ont la forme qu'ils ont : un marqueur dont les lettres mélangent
des systèmes d'écriture est [signalé deux fois](internals.md#diagnostics-are-part-of-the-design),
une fois lisiblement et une fois échappé, parce que la forme échappée est la
seule graphie qui les distingue. Une espace insécable à l'intérieur des
accolades est imprimée par point de code pour la même raison. Le vérificateur
de catalogue refuse le message avant qu'il puisse être livré.

## Non vide ne veut pas dire traduit { #non-empty-is-not-translated }

Un catalogue échafaudé en copiant ses msgid dans les msgstr passe tous les
contrôles naïfs : rien n'est vide, rien n'est fuzzy, l'ensemble des messages
correspond exactement. Une édition de ce site a été livrée ainsi pendant
plusieurs heures. Huit pages d'une autre édition aussi, qui étaient des copies
octet pour octet de la source anglaise — ce qui passe un contrôle comparant les
blocs de code entre les deux, puisqu'il s'agit du même fichier.

Ni l'un ni l'autre n'est visible pour une bibliothèque de traduction. Les deux
sont faciles à tester, mais pas en exigeant que chaque entrée diffère de sa
source : `OK`, les noms de produits, les noms de personnes, les sigles et les
identifiants de code se traduisent tous par eux-mêmes, et un contrôle qui
l'interdit produit des faux positifs à perpétuité.

Mesurez plutôt le *taux*, sur tout un catalogue ou toute une page, et envoyez
les valeurs aberrantes à un humain. Le test de ce site fait exactement cela :
il compare les lignes de prose de chaque édition à la source anglaise et échoue
au-delà de 25 % d'identiques. L'édition contrefaite était à 87 % ; toutes les
traductions authentiques se situent entre 4 % et 8 %, ce qui correspond à la
petite queue de lignes qui coïncident légitimement, comme les URL et les
sorties de programme citées. Les deux populations sont assez éloignées pour que
le seuil n'ait pas besoin d'être précis.

## Le catalogue n'est pas la seule chose traduite { #the-catalog-is-not-the-only-translated-thing }

Deux échecs ici n'avaient rien à voir avec gettext.

Traduire un titre change l'ancre qui en est dérivée : tous les liens
inter-pages vers cette section se cassent — silencieusement, et dans cette
langue seulement. Ce site épingle l'ancre anglaise sur chaque titre, et un test
dérive la liste attendue de la page anglaise.

Et le générateur du site livre des traductions d'interface pour soixante-huit
langues, parmi lesquelles ne figurent ni le swahili ni l'irlandais. Sans elles,
le build ne se rabat pas sur l'anglais : l'inclusion du gabarit échoue et
l'édition ne peut pas être construite du tout. Deux fichiers propres à ce dépôt
existent pour combler ce manque.

## Vos outils aussi ont des bugs { #your-tools-have-bugs-too }

L'étape de CI que cette documentation recommande pour repérer les catalogues
obsolètes, `pybabel update --check`, ne peut pas faire ce travail pour un
projet qui utilise `pgettext` ou `npgettext`. Sur Babel 2.18.0, elle signale
comme périmé tout catalogue contenant un `msgctxt`, à chaque exécution. La
comparaison passe par `Catalog.is_identical`, qui recherche chaque message par
la clé sous laquelle il est stocké — et pour un message contextuel cette clé
est le couple `(id, context)`, que `Catalog.get` n'accepte pas. La recherche ne
renvoie rien, et les catalogues ne sont donc jamais jugés égaux :

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Le bug a été trouvé ici en essayant de s'en servir, remonté en amont, et le
contrôle de remplacement se trouve
[sur la page En production](workflow.md#what-ci-gates).

La leçon générale est la plus inconfortable : une barrière toujours au rouge
est pire que pas de barrière, parce qu'une équipe finit par la désactiver.
Vérifiez que votre contrôle de CI peut effectivement passer avant de lui faire
confiance pour échouer.

## À quoi sert la bibliothèque, en une phrase { #what-the-library-is-for-in-one-line }

L'essentiel de cette page relève d'un jugement qu'aucun outil ne peut reprendre
à son compte. Ce qu'un outil *peut* faire, c'est garantir qu'une traduction ne
puisse pas changer la structure de la phrase qu'elle traduit — ni supprimer une
valeur, ni en inventer une, ni en reformater une, ni aller fouiller dans vos
objets — et le dire dans une phrase sur laquelle la personne chargée de
corriger peut agir. C'est là toute la promesse de cette bibliothèque, et le
reste de ce site est la manière dont elle la tient.
