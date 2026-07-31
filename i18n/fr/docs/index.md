---
description: "Traduisez des messages t-string complets via gettext et Babel, en gardant les valeurs et le formatage hors du catalogue."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Traduisez des messages entiers,<br>pas des fragments de phrase.

`gettext-tstrings` relie les t-strings de Python 3.14+ aux catalogues gettext
standard et à l'outillage Babel. Les valeurs et le formatage restent dans le
code applicatif ; le catalogue détient un message complet avec de simples
marqueurs `{name}` :

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Commencer le tutoriel :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Comparer les alternatives](comparison.md){ .md-button }

Alpha · Python 3.14+ · catalogues PO/MO ordinaires · aucune dépendance à l'exécution
{ .home-facts }

Ce site pratique ce qu'il documente : chaque édition linguistique —
navigation, libellés et rapport de build avec pluriels — est rendue depuis
des catalogues PO par
[`gettext-tstrings` lui-même](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Est-ce fait pour vous ? { #is-this-for-you }

**Un bon choix dès aujourd'hui si** votre application tourne sur Python 3.14 ou
plus récent ; si vous utilisez déjà gettext et Babel, ou souhaitez adopter leur
workflow PO/MO ; et si vous voulez la syntaxe t-string avec des marqueurs
nommés vérifiés avant leur rendu.

**Pas encore un bon choix si** vous avez besoin de Python 3.13 ou antérieur ;
si vous exigez une API Python stable — ceci est une alpha, et la
[spécification](spec.md) en est la partie qui a pris forme ; ou si la quasi-
totalité de votre texte traduisible vit dans un langage de gabarits plutôt que
dans du source Python.

Vous avez déjà des catalogues ? Ils continuent de fonctionner.
`_("Hello {name}").format(name=name)` et `tr(t"Hello {name}")` produisent le
même msgid, si bien que les traductions existantes survivent au changement —
[Migration](migration.md) parcourt le déplacement entier.

## Ce que le catalogue a le droit de dire { #what-the-catalog-may-say }

Le catalogue reçoit le message complet `Hello {name}`. Une traduction peut
réordonner ou répéter `{name}`, et peut réécrire tous les autres mots autour de
lui. Elle ne peut ni supprimer le marqueur, ni en inventer un nouveau, ni
passer à travers lui pour atteindre vos objets, ni attacher son propre
formatage.

Voilà toute la promesse : **une traduction ne peut pas changer la structure du
message qu'elle traduit.** La bibliothèque le vérifie à l'entrée — quand les
catalogues sont compilés — puis à nouveau au moment du rendu ; une entrée cassée
qui atteindrait malgré tout la production journalise un avertissement et rend le
message source au lieu de planter.

!!! note "gettext est nouveau pour vous ? Tout le workflow en quatre phrases"

    **gettext** est la façon standard de traduire des logiciels, en Python et
    bien au-delà. Votre code marque les messages traduisibles ; un *extracteur*
    les collecte dans un fichier modèle (`.pot`) ; un traducteur — en général
    pas un programmeur — remplit un fichier catalogue (`.po`) par langue,
    compilé en un `.mo` binaire que votre application charge à l'exécution. Le
    nom conventionnel de la fonction de traduction est `_`, donc
    `_(t"Hello {name}")` se lit « traduis ce message ». Le
    **[tutoriel](tutorial.md)** parcourt tout le chemin — marquer, extraire,
    traduire, compiler, exécuter — en cinq minutes environ.

## Le problème résolu { #the-problem-it-solves }

Une f-string est déjà interpolée lorsqu'une bibliothèque la reçoit —
`f"Hello {name}"` est devenue `"Hello Ada"`, et traduire les fragments autour
d'une valeur casse la grammaire de la plupart des langues. Une t-string
([PEP 750]) conserve séparément le texte statique, les valeurs évaluées, les
expressions source, les conversions et les spécifications de format — c'est
exactement la séparation qu'attend un catalogue de messages.
[Ce que cela change](comparison.md), comparé à `%(name)s`, `.format()` et aux
chaînes `$`.

Ni gettext ni Babel ne disent cependant comment une t-string devient un
message. Cette bibliothèque fait ce choix, le consigne dans une
[spécification versionnée](spec.md) et livre la
[suite de conformité](spec.md#conformance) qui le vérifie.

## Les règles de conception { #the-design-rules }

- Traduire des messages complets, jamais des fragments de phrase.
- N'accepter que des noms de variables simples comme `{name}`.
- Garder `!r` et `:.2f` sous le contrôle de l'application, hors du catalogue.
- Autoriser les traductions à réordonner et répéter les marqueurs connus, tout
  en les empêchant d'atteindre des attributs ou d'ajouter du formatage.
- Réutiliser les fichiers POT, PO et MO ordinaires, et les outils qui les
  lisent déjà.

Et la liste symétrique de ce qu'elle laisse délibérément de côté : elle ne
localise ni les nombres, ni les devises, ni les dates —
[formatez-les d'abord](guide.md#locale-aware-values) avec Babel ; elle
n'échappe pas la sortie rendue pour du HTML, un shell ou un terminal ; et elle
ne peut pas juger si une traduction est *correcte*, seulement si ses marqueurs
sont intacts.

## Installation { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 ou plus récent. **Le rendu n'a aucune dépendance** : il utilise le
`gettext` de la bibliothèque standard et rien d'autre.

L'extraction et la validation des catalogues passent par [Babel]. Installez
donc cet extra là où `pybabel` s'exécute, c'est-à-dire en général un
environnement de développement ou de CI plutôt qu'une image de production :

```console
python -m pip install "gettext-tstrings[babel]"
```

## Pour continuer { #where-to-go-next }

**Commencer ici** — aucune expérience de gettext supposée :

<div class="grid cards" markdown>

- **[Tutoriel](tutorial.md)** — d'un répertoire vide à une traduction japonaise
  qui fonctionne, en cinq étapes, chaque commande montrée avec sa sortie.
- **[Pourquoi les t-strings](comparison.md)** — le même message écrit de quatre
  façons, et ce que `%(name)s`, `.format()` et les chaînes `$` confient chacun
  au catalogue.

</div>

**Passer à la pratique** — les références de travail :

<div class="grid cards" markdown>

- **[Guide](guide.md)** — l'API d'exécution : quel point d'entrée choisir, les
  pluriels, la langue par requête, les chaînes différées, et ce qui se passe
  quand un catalogue est incorrect.
- **[Extraction](extraction.md)** — la référence `pybabel` : configuration,
  noms de fonctions personnalisés, et comment les outils existants valident ces
  catalogues gratuitement.
- **[En production](workflow.md)** — la boucle telle qu'une équipe la fait
  tourner : le cycle de mise à jour, les entrées fuzzy, les barrières de CI,
  les plateformes de traduction et la livraison.
- **[Migration](migration.md)** — adopter tout cela dans un projet qui possède
  déjà des catalogues, un site d'appel à la fois.
- **[Pour les traducteurs](translators.md)** — une seule page à remettre à qui
  édite les fichiers `.po`.

</div>

**Comprendre le fond** — de l'histoire à l'implémentation :

<div class="grid cards" markdown>

- **[Contexte](background.md)** — pourquoi cette bibliothèque existe : trente
  ans de gettext, deux PEP et la discussion sur la bibliothèque standard close
  sans réponse.
- **[Pièges](pitfalls.md)** — ce que la traduction de ce site en trente-cinq
  langues a réellement cassé, et la moitié qu'un outil sait attraper.
- **[Fonctionnement](internals.md)** — de l'objet template de la PEP 750 à la
  chaîne rendue, et les caches qui rendent la vérification bon marché.

</div>

**Référence** — les contrats :

<div class="grid cards" markdown>

- **[API](api.md)** — tout ce que le paquet exporte, sur une seule page.
- **[Spécification](spec.md)** — la convention t-string ↔ msgid comme contrat
  stable et versionné, avec une suite de conformité lisible par machine.

</div>

## État { #status }

Une alpha. Le contrat reste volontairement réduit et la
[spécification](spec.md) en est la partie stable ; l'API Python peut encore
bouger. Avant une version stable, il faudra davantage de langues de test, un
suivi durable des performances, une revue d'API par des gens qui utilisent
sérieusement gettext et Babel, et des tests de compatibilité sur chaque version
prise en charge de Python et de Babel.

Les [issues et pull requests](https://github.com/yhay81/gettext-tstrings/issues)
sont bienvenues : une alpha est exactement le moment où l'interface vaut encore
la peine d'être discutée.

## Rejoindre la communauté { #join-the-community }

- Choisissez une
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  pour une contribution bien délimitée.
- Posez vos questions d'usage dans les
  [Discussions Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Apportez vos workflows gettext de production et vos idées d'API dans les
  [Discussions Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lisez le
  [guide de contribution](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  avant d'ouvrir une pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
