---
description: "Todos os nomes públicos de gettext_tstrings: funções, Translator, contexto, strings preguiçosas e erros."
---

# API

Todos os nomes abaixo são exportados por `gettext_tstrings`. Nenhum outro nome
é público. Esta página é a referência de assinaturas; para exemplos práticos de
cada função, consulte o [guia](guide.md).

## Tradução

Cada função recebe sua t-string de forma posicional e aceita `translations` e
`strict` como argumentos nomeados
([veja o guia](guide.md#what-happens-when-a-catalog-is-wrong)).

| Função | Assinatura |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias de `gettext` |
| `ntr` | alias de `ngettext` |

### `Translator`

Dataclass frozen que vincula um objeto de tradução:

```python
Translator(translations, strict=False)
```

É chamável (`_(t"…")`) e fornece `gettext`, `ngettext`, `pgettext`,
`npgettext`, `tr` e `ntr`.

## Vínculo de contexto

| Nome | Função |
| --- | --- |
| `use_translations(translations)` | Vincula durante um bloco `with` e restaura ao final. |
| `set_translations(translations)` | Vincula sem bloco em ciclos gerenciados pelo framework. |
| `get_translations()` | Lê o vínculo atual ou devolve `None`. |

O vínculo usa `ContextVar` e é seguro em concorrência.

## Strings preguiçosas

| Nome | Função |
| --- | --- |
| `lazy_gettext(template, /)` | Adia a tradução até o uso. |
| `lazy_pgettext(context, template, /)` | Variante com contexto. |
| `LazyString` | Renderiza por `str()`, `format()` e f-strings, compara-se ao texto e não é hashable de propósito. |

## Baixo nível

### `compile_template(template, /) -> CompiledTemplate`

Compila uma t-string reutilizando seu plano estático em cache.

### `CompiledTemplate`

| Membro | Significado |
| --- | --- |
| `.msgid` | Identificador gettext estável. |
| `.placeholders` | Nomes na ordem da primeira ocorrência. |
| `.render(pattern)` | Valida e renderiza; **sempre lança** em caso de diferença. |

## Tipos e erros

### `Translations`

Um `Protocol` `runtime_checkable` para os quatro métodos padrão:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` e `Translations` do
Babel atendem ao protocolo.

### Exceções

| Classe | Quando |
| --- | --- |
| `TStringError` | Classe base. |
| `InvalidTemplateError` | A t-string de origem viola a convenção. |
| `InvalidTranslationError` | A tradução viola a convenção; o modo flexível registra e renderiza a origem. |

## Entry points de extração

| Grupo | Nome | Usado por |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` no `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | automaticamente por `pybabel compile` |

## Desempenho

Uma mensagem com um campo leva cerca de 0,4 µs em Apple Silicon, incluindo a
criação da t-string: aproximadamente 2,5 vezes `gettext(...).format(...)`. Os
caches são limitados e nunca retêm os valores interpolados.

```console
uv run python benchmarks/runtime.py
```
