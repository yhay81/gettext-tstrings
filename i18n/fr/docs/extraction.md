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

## Workflow { #the-workflow }

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

`init` ne s'exécute qu'une fois par langue ; ensuite, `pybabel update`
fusionne chaque modèle frais dans les catalogues existants. Ce cycle
récurrent — et ce que ses entrées `fuzzy` signifient pour une release — est
détaillé dans
[En production](workflow.md#the-cycle-after-the-first-translation).

L'extracteur traite aussi `_()`, `gettext()` et `ngettext()`. Un seul mapping
couvre donc un code mixte, y compris `tr()`, `ntr()`, `lazy_gettext()` et
`lazy_pgettext()`.

!!! warning "Activer les commentaires pour traducteurs avec `-c`"

    `pybabel extract` ne collecte les commentaires destinés aux traducteurs que
    si vous passez `-c "Translators:"`, exactement comme pour les appels gettext
    ordinaires. Sans cette option l'extraction fonctionne quand même — les
    commentaires n'atteignent simplement jamais le catalogue, où ils sont
    [le levier de qualité le moins cher](workflow.md#working-with-translators-and-platforms)
    de tout le workflow.

## Noms de fonctions personnalisés { #registering-your-own-function-names }

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

## Indulgent en local, strict en CI { #lenient-locally-strict-in-ci }

Par défaut, un seul fichier fautif n'interrompt pas l'exécution :

- Une t-string refusée par l'extracteur — accès à un attribut, expression,
  argument incorrect — est signalée en avertissement puis ignorée.
- Un fichier impossible à parser est ignoré de la même façon.
- De même pour un fichier que seul `tokenize` refuse alors qu'`ast` l'accepte,
  et sur lequel la passe propre à Babel s'arrêterait autrement.

C'est commode pendant que vous éditez, et dangereux le reste du temps : un
message ignoré est tout simplement **absent du POT**, il n'est donc jamais
traduit et rien ne le dit. Mettez `strict = true` dans les options du mapping
partout où l'extraction n'est pas surveillée par un humain :

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Chacun des avertissements ci-dessus devient alors une erreur fatale. Voyez ce
réglage comme celui de la production, et le défaut comme celui de votre poste.

## Validation par le toolchain existant { #your-existing-toolchain-validates-these-catalogs }

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

Weblate documente ce même contrôle sous le nom
[Python brace format][weblate-checks], et les plateformes commerciales ont leur
propre QA des marqueurs indexée sur ce flag. Le comportement de chaque
plateforme n'appartient qu'à elle ; les deux outils vérifiés ici sont msgfmt et
le checker Babel fourni.

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

    L'erreur ci-dessus est signalée, le statut de sortie est `1` — et le
    catalogue cassé est tout de même compilé. Seul ce statut de sortie peut
    empêcher une pipeline de le livrer ;
    [Ce que la CI verrouille](workflow.md#what-ci-gates) montre l'étape de
    build qui s'en charge.

Les deux contrôles ne sont pas redondants : le checker du paquet est plus
strict dans au moins deux cas. Un msgid dont les seules accolades sont
échappées (`Config {{raw}} only`) ne reçoit jamais le flag
`python-brace-format`, aucun outil externe ne le valide donc ; et les formes
plurielles sont vérifiées une par une, là où msgfmt peut accepter le fichier.
Des noms ASCII permettent à tous les outils de participer ; la bibliothèque
accepte tout `str.isidentifier()`.

## Templates et autres outils { #templates-and-other-tools }

Les t-strings sont de la syntaxe Python. Jinja2 (`{% trans %}`), Django et les
autres templates conservent leurs extracteurs, tout en alimentant le même
catalogue PO.

`pygettext` ne sait pas encore parser les t-strings. La
[spécification](spec.md) permet à un autre extracteur de suivre la même
convention.
