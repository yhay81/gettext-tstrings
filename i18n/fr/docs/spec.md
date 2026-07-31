---
description: "La convention t-string vers msgid sous forme de contrat versionné, avec une suite de conformité lisible par machine."
---

# Spécification

Vous pouvez utiliser cette bibliothèque sans lire cette page — le
[tutoriel](tutorial.md) et le [guide](guide.md) couvrent l'usage quotidien.
Cette page s'adresse aux auteurs d'outils : la convention implémentée par la
bibliothèque est consignée sous forme de contrat petit et stable, afin qu'une
autre implémentation — un extracteur, un IDE, un vérificateur de types ou un
futur `pygettext` — puisse la cibler et interopérer. Pour les mêmes règles
expliquées avec leurs raisons, et la manière dont l'implémentation de
référence les applique, lisez d'abord [Fonctionnement](internals.md).

[Lire la spécification v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Les règles en un écran { #the-rules-in-one-screen }

**Un msgid** concatène les segments littéraux dans l'ordre source et un token
`{name}` par interpolation. Les accolades littérales sont échappées (`{`
devient `{{`). Un nom doit satisfaire `str.isidentifier()` et ne pas être un
mot-clé Python. Conversions et spécifications de format restent dans
l'application.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *rejetée — nom non simple* |

**Une traduction** est valide si elle ne contient que des marqueurs `{name}`
nus, si chaque nom requis apparaît et si aucun nom inconnu n'est ajouté.
Réordonnancement et répétition sont autorisés.

Pour les pluriels, l'ensemble autorisé est l'union des noms des branches et
l'ensemble requis leur intersection. Ainsi `t"One file"` et `t"{n} files"`
autorisent `n` dans chaque forme sans l'y imposer.

**Un msgid vide** n'est jamais recherché : gettext le réserve aux métadonnées.

## Conformité { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
décrit les mêmes règles sous forme de cas lisibles par machine. Une
implémentation **est conforme à la spec v1** si elle reproduit tous les cas.
Ils ne dépendent ni des messages d'erreur ni des types d'exception.

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Le champ `"spec"` n'est **pas** une version de spécification : tous les cas de
`v1.json` relèvent de la spec v1. Il nomme la section de `SPEC.md` que le cas
met à l'épreuve, si bien que `"2.2"` se lit § 2.2, la règle de dérivation d'un
jeton de marqueur.

L'implémentation de référence exécute cette suite dans ses propres tests.

## Versionnage { #versioning }

Une modification incompatible de la dérivation du msgid ou de la validation
crée une nouvelle version et un nouveau `conformance/vN.json`. Une clarification
additive qui ne change aucun résultat ne modifie pas la version.
