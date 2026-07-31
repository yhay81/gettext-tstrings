---
description: "Tous les noms exportés par gettext_tstrings : fonctions, Translator, contexte, chaînes différées et erreurs."
---

# API

Tout ce qui suit est exporté par `gettext_tstrings`. Rien d'autre n'est public.
Cette page est la référence des signatures ; pour des exemples commentés de
chaque fonction, voir le [guide](guide.md).

## Traduction { #translating }

Chaque fonction prend sa t-string positionnellement et accepte `translations`
(contexte, puis fonctions globales de la bibliothèque standard) et `strict`
([voir le guide](guide.md#what-happens-when-a-catalog-is-wrong)).

| Fonction | Signature |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias de `gettext` |
| `ntr` | alias de `ngettext` |

### `Translator`

Dataclass frozen qui lie un objet de traduction.

```python
Translator(translations, strict=False)
```

Il est appelable (`_(t"…")`) et fournit `gettext`, `ngettext`, `pgettext`,
`npgettext`, `tr` et `ntr`.

## Liaison de contexte { #context-binding }

| Nom | Rôle |
| --- | --- |
| `use_translations(translations)` | Lie pendant un bloc `with`, puis restaure. |
| `set_translations(translations)` | Lie sans bloc pour un cycle géré par un framework. |
| `get_translations()` | Lit la liaison courante ou renvoie `None`. |

La liaison utilise un `ContextVar` et reste sûre en concurrence.

## Chaînes différées { #deferred-strings }

| Nom | Rôle |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Diffère la traduction jusqu'à chaque rendu. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Variante avec contexte. |
| `LazyString` | Type renvoyé. Se rend via `str()` et `format()` dans la langue liée à cet instant précis, se compare à son texte rendu et n'est volontairement pas hashable. |

Des exemples travaillés, dont la raison pour laquelle `strict` se décide à la
définition, figurent sous
[Traduction différée](guide.md#deferred-translation).

## Bas niveau { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Compile une t-string en réutilisant son plan statique mis en cache.

### `CompiledTemplate`

| Membre | Signification |
| --- | --- |
| `.msgid` | Identifiant gettext stable. |
| `.placeholders` | Noms dans l'ordre de première apparition. |
| `.render(pattern)` | Valide et rend un pattern ; **lève toujours** en cas d'écart. |

## Types et erreurs { #types-and-errors }

### `Translations`

Un `Protocol` `runtime_checkable` pour les quatre méthodes standard :

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` et `Translations` de
Babel le satisfont.

### Exceptions

| Classe | Quand |
| --- | --- |
| `TStringError` | Classe de base. |
| `InvalidTemplateError` | La t-string **source** enfreint la convention. |
| `InvalidTranslationError` | La **traduction** l'enfreint ; le mode souple journalise et rend le texte source. |

## Entry points d'extraction { #extraction-entry-points }

| Groupe | Nom | Utilisé par |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | Le `method` de `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automatiquement |

## Performances { #performance }

Le récit complet — ce qui est mis en cache, sur quoi les caches sont indexés
et les chiffres mesurés — se trouve dans
[Le chemin chaud](internals.md#the-hot-path). En bref : la validation est
mise en cache, jamais sautée, et le rendu entier coûte une fraction de
microseconde. Exécutez le benchmark sur votre propre machine :

```console
uv run python benchmarks/runtime.py
```
