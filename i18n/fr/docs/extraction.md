---
description: "Extraire les messages t-string avec pybabel et valider les catalogues avec msgfmt et le checker Babel intégré."
---

# Extraction

L'extraction est l'étape qui collecte chaque message marqué dans votre code
source vers un modèle `.pot` destiné aux traducteurs — l'étape 3 de la boucle
du [tutoriel](tutorial.md). Cette page est la référence de cette étape :
configuration, noms de fonctions personnalisés, mode strict pour la CI et les
contrôles qui protègent ensuite vos catalogues.

L'extraction nécessite l'extra `babel` :

```console
python -m pip install "gettext-tstrings[babel]"
```

## Workflow

Créez `babel.cfg` :

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Puis utilisez les commandes Babel habituelles :

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

L'extracteur traite aussi `_()`, `gettext()` et `ngettext()`. Un seul mapping
couvre donc un code mixte, y compris `tr()`, `ntr()`, `lazy_gettext()` et
`lazy_pgettext()`.

!!! warning "`-c` n'est pas facultatif"

    Passez `-c "Translators:"` pour collecter les commentaires destinés aux
    traducteurs, comme avec gettext ordinaire.

## Noms de fonctions personnalisés

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Une valeur ini est une chaîne séparée par espaces ou virgules ; TOML accepte une
liste. Les options couvrent les six familles de fonctions gettext.

!!! danger "`-k` n'atteint pas une t-string"

    Un helper comme `mytr(t"…")` doit être déclaré dans ces options. Le mécanisme
    `--keyword` de Babel ne lit pas les littéraux t-string :
    `pybabel extract -k mytr` les omet sans avertissement.

    Seul l'ordre d'arguments standard est pris en charge.

## Robuste par défaut

- Une t-string refusée est signalée puis ignorée.
- Un fichier impossible à parser est ignoré de la même façon.
- Un fichier refusé seulement par `tokenize` est aussi isolé.

Utilisez `strict = true` pour transformer ces avertissements en erreurs dans la
CI.

## Validation par le toolchain existant

Babel ajoute un flag standard :

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Une traduction `こんにちは {nombre}` est détectée sans configuration :

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documente ce contrôle sous le nom
[Python brace format][weblate-checks]. Les deux outils vérifiés ici sont msgfmt
et le checker Babel fourni.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

`pybabel compile` applique le checker à chaque message marqué :

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Pour un pluriel, l'erreur nomme la forme :

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` écrit quand même le `.mo`"

    Le statut est `1`, mais le catalogue incorrect est tout de même compilé.
    Une pipeline doit traiter ce statut comme une barrière.

    ```yaml
    - run: pybabel compile -d locales   # non-zero exit is the gate
    ```

Les contrôles ne sont pas redondants : le checker fourni valide les accolades
échappées et chaque forme plurielle séparément, là où msgfmt peut accepter le
fichier. Des noms ASCII permettent à tous les outils de participer ; la
bibliothèque accepte tout `str.isidentifier()`.

## Templates et autres outils

Les t-strings sont de la syntaxe Python. Jinja2 (`{% trans %}`), Django et les
autres templates conservent leurs extracteurs, tout en alimentant le même
catalogue PO.

`pygettext` ne sait pas encore parser les t-strings. La
[spécification](spec.md) permet à un autre extracteur de suivre la même
convention.
