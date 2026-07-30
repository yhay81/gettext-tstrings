---
description: "Traduisez des messages t-string complets avec gettext et Babel, sans confier le formatage au catalogue."
---

# gettext-tstrings

Une intégration sûre de gettext et Babel pour les t-strings de Python 3.14+.

Écrivez la phrase une seule fois, dans votre langue source, avec la valeur en
place :

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Le catalogue reçoit la phrase complète `Hello {name}`. Une traduction peut
réordonner ou répéter `{name}` ; elle ne peut ni le supprimer, ni en inventer
un autre, ni ajouter son propre formatage — cette bibliothèque le vérifie, et
un catalogue cassé retombe sur le texte source au lieu de planter.

!!! note "gettext est nouveau pour vous ? Tout le workflow en quatre phrases"

    **gettext** est la façon standard de traduire des logiciels, en Python et
    bien au-delà. Votre code marque les chaînes traduisibles ; un *extracteur*
    les collecte dans un fichier modèle (`.pot`) ; un traducteur — en général
    pas un programmeur — remplit un fichier catalogue (`.po`) par langue,
    compilé en un `.mo` binaire que votre application charge à l'exécution. Le
    nom conventionnel de la fonction de traduction est `_`, donc
    `_(t"Hello {name}")` se lit « traduis cette phrase ». Le
    **[tutoriel](tutorial.md)** parcourt tout le chemin — marquer, extraire,
    traduire, compiler, exécuter — en cinq minutes environ.

## Le problème résolu

Une f-string est déjà interpolée lorsqu'une bibliothèque la reçoit —
`f"Hello {name}"` est devenue `"Hello Ada"`, et traduire les fragments autour
d'une valeur casse la grammaire de la plupart des langues. Une t-string
([PEP 750]) conserve séparément le texte statique, les valeurs évaluées, les
expressions source, les conversions et les spécifications de format. C'est
exactement la séparation qu'attend un catalogue. Découvrez
[ce que cela change](comparison.md) par rapport à `%(name)s`, `.format()` et
aux chaînes `$`.

Ni gettext ni Babel ne définissent cependant comment transformer une t-string
en message. Cette bibliothèque fixe cette convention, la documente dans une
[spécification versionnée](spec.md) et fournit une
[suite de conformité](spec.md#conformance).

## Les choix effectués

- Traduire des messages complets, jamais des fragments de phrase.
- N'accepter que des noms simples comme `{name}`.
- Garder `!r` et `:.2f` sous le contrôle de l'application.
- Autoriser le réordonnancement et la répétition de marqueurs connus, mais pas
  l'accès aux attributs ni l'ajout de formatage.
- Réutiliser les fichiers POT, PO et MO ainsi que leurs outils habituels.

## Installation

```console
python -m pip install gettext-tstrings
```

Python 3.14 ou plus récent est requis. **Le rendu n'a aucune dépendance** :
il utilise uniquement le `gettext` de la bibliothèque standard.

L'extraction et la validation passent par [Babel]. Installez l'extra dans
l'environnement qui exécute `pybabel`, généralement le développement ou la CI :

```console
python -m pip install "gettext-tstrings[babel]"
```

## Pour continuer

<div class="grid cards" markdown>

- **[Tutoriel](tutorial.md)** — commencez ici : d'un répertoire vide à une
  traduction japonaise qui fonctionne, en cinq étapes, chaque commande montrée
  avec sa sortie.
- **[Pourquoi les t-strings](comparison.md)** — le même message écrit de
  quatre façons et ce que `%(name)s`, `.format()` et les chaînes `$` confient
  chacun au catalogue.
- **[Guide](guide.md)** — l'API d'exécution : pluriels, langue par requête,
  chaînes différées et gestion d'un catalogue incorrect.
- **[Extraction](extraction.md)** — la référence `pybabel` : configuration,
  noms de fonctions personnalisés et comment les outils existants valident ces
  catalogues gratuitement.
- **[Spécification](spec.md)** — convention t-string ↔ msgid stable, versionnée
  et accompagnée d'une suite de conformité lisible par machine.
- **[API](api.md)** — tout ce que le paquet exporte, sur une seule page.

</div>

## Ce site l'utilise réellement

Cette documentation n'est pas une simple démonstration traduite. Sa navigation,
les libellés du thème, la ligne de copyright et le rapport de build avec
pluriels sont rendus depuis des catalogues PO par `gettext-tstrings`. Le
[builder multilingue](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
exerce les messages contextualisés, les marqueurs nommés et les règles de
pluriel des dix langues à chaque build strict.

## État

Le projet est en alpha. Le contrat reste volontairement réduit et la
[spécification](spec.md) en est la partie stable ; l'API Python peut encore
évoluer. Une version stable demandera davantage de langues de test, un suivi
durable des performances, l'avis d'utilisateurs de gettext et Babel et des
tests sur toutes les versions prises en charge.

Les [issues et pull requests](https://github.com/yhay81/gettext-tstrings/issues)
sont bienvenues : une alpha est le bon moment pour discuter de l'interface.

## Rejoindre la communauté

- Choisissez une
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
- Posez vos questions dans les
  [Discussions Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Proposez vos workflows et idées dans les
  [Discussions Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lisez le
  [guide de contribution](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  avant d'ouvrir une pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
