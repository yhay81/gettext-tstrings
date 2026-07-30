---
description: "A mesma mensagem traduzível com %-format, .format() e t-string, mostrando o que cada opção permite ao catálogo controlar."
---

# Por que t-strings?

Todo modo de inserir valores em uma mensagem traduzível precisa responder:
*quanto da linguagem de formatação o catálogo pode controlar?*

## Formatação com %

```python
_("Hello %(name)s") % {"name": name}
```

O catálogo contém sintaxe printf. Remover um único caractere pode provocar um
erro em produção:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

`msgfmt --check-format` detecta o problema, mas somente em mensagens marcadas
como `python-format` e quando o catálogo realmente passa pelo msgfmt.

## str.format

```python
_("Hello {name}").format(name=name)
```

O marcador é nomeado e pode ser reordenado. Porém, `str.format` é uma pequena
linguagem de expressões:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

O catálogo viaja como dado por plataformas e pessoas. Mesmo assim, `.format()`
lhe dá acesso aos atributos dos objetos fornecidos.

## t-strings

```python
tr(t"Hello {name}")
```

O msgid continua sendo `Hello {name}`, mas a tradução não é executada como uma
string de formato. Ela é validada contra os marcadores da origem, aceitando
apenas nomes simples:

| A tradução contém | Motivo da rejeição |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

A formatação permanece na aplicação:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nunca chega ao catálogo.

## Lado a lado

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| Marcador nomeado | sim | sim | sim |
| Tradutor pode reordenar | sim | sim | sim |
| Um caractere removido quebra | **sim** | não | não |
| Catálogo controla formatação | sim | sim | **não** |
| Catálogo acessa atributos | não | **sim** | **não** |
| Catálogo inválido falha ao renderizar | **sim** | **sim** | [não por padrão](guide.md#what-happens-when-a-catalog-is-wrong) |
| Funciona com PO/MO e `msgfmt` | sim | sim | sim |

## O custo

Uma f-string já está pronta ao chegar à função. t-strings ([PEP 750]) exigem
Python 3.14 ou mais recente. Além disso, cada interpolação deve ser um nome
simples:

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Essa restrição fornece a garantia de segurança e dá a quem traduz nomes de
marcadores compreensíveis.

  [PEP 750]: https://peps.python.org/pep-0750/
