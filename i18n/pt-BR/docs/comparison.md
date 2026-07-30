---
description: "A mesma mensagem traduzível escrita com %-format, .format(), strings $ do flufl.i18n e uma t-string, incluindo como cada opção vincula valores e lida com um catálogo danificado."
---

# Por que t-strings?

Todo modo de inserir valores em uma mensagem traduzível precisa responder:
*quanto da linguagem de formatação o catálogo pode controlar?* As quatro
respostas abaixo também diferem quanto à origem dos valores e ao que acontece
quando um catálogo altera um marcador.

## Formatação com %

```python
_("Hello %(name)s") % {"name": name}
```

O catálogo contém sintaxe printf, incluindo uma letra de tipo ao final que é
fácil ignorar e pode ser danificada pela alteração de um único caractere:

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

Ele elimina a letra de tipo ao final, mantendo um marcador nomeado e livremente
reordenável.

O problema está do outro lado. `str.format` é uma pequena linguagem de
expressões:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

O catálogo viaja como dado por plataformas e pessoas. Mesmo assim, `.format()`
lhe dá acesso aos atributos dos objetos fornecidos.

## Strings `$` e flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

A biblioteca padrão fornece a linguagem de interpolação `$name` por meio de
[`string.Template`][stdlib-template], mas isso não é, por si só, uma API de tradução.
[`flufl.i18n`][flufl-i18n] combina esse estilo com a consulta de catálogos gettext. Ele
monta o namespace de substituição a partir das variáveis globais e locais de
quem chama; um mapeamento `extras` opcional tem precedência sobre ambos. Sua
sintaxe para quem traduz não tem letra de tipo ao final nem especificador de
formato, e os marcadores continuam livremente reordenáveis.

Uma substituição indisponível não gera exceção. Com `name = "Ada"` e sem
`nombre` no namespace de quem chama, uma tradução de catálogo `Hello $nombre`
é renderizada como `Hello $nombre`: o marcador não resolvido permanece visível.
Esse [comportamento documentado] preserva o restante da mensagem traduzida em
vez de fazer a chamada falhar. Exceções geradas ao resolver um atributo ou
converter um valor ainda podem se propagar.

Em um aspecto relevante, `flufl.i18n` tem mais recursos que um
`string.Template` puro. Seu [Template personalizado] aceita marcadores com
pontos, como `$settings.api_key`, e seu [tradutor] resolve esses caminhos com
base nos valores de quem chama. Um marcador traduzido pode nomear qualquer
variável local ou global disponível de quem chama e, com a sintaxe de pontos,
percorrer seus atributos. Isso é conveniente quando uma mensagem precisa de um
atributo, mas também torna o frame de quem chama parte do namespace de
substituição do catálogo. A comparação abaixo descreve o `flufl.i18n` 6.0.0,
e não todos os usos possíveis de `string.Template`.

## t-strings

```python
tr(t"Hello {name}")
```

O catálogo ainda vê `Hello {name}` e continua sendo um catálogo PO/MO comum.
A extração do código-fonte é diferente: as ferramentas atuais exigem um
extrator compatível com t-strings, como o fornecido por este pacote. Uma
tradução é validada contra os marcadores da mensagem de origem e renderizada
por esta biblioteca, que aceita somente nomes simples:

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

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Marcador nomeado | sim | sim | sim | sim |
| Quem traduz pode reordenar | sim | sim | sim | sim |
| Origem dos valores | mapeamento explícito | argumentos explícitos | variáveis globais e locais de quem chama, com `extras` opcional sobrescrevendo-as | interpolações capturadas pela t-string |
| Catálogo controla a conversão do valor ou o especificador de formato | sim | sim | não | não |
| Catálogo pode solicitar acesso a atributos | não | sim | sim, com nomes pontuados | não |
| Marcador da origem removido na renderização | omitido silenciosamente | omitido silenciosamente | omitido silenciosamente | padrão da origem totalmente renderizado [por padrão](guide.md#what-happens-when-a-catalog-is-wrong) |
| Marcador adicionado indisponível na renderização | gera exceção | gera exceção | permanece visível | padrão da origem totalmente renderizado [por padrão](guide.md#what-happens-when-a-catalog-is-wrong) |
| Conjunto de marcadores da origem verificado em tempo de execução (singular) | não | não | não | sim |
| Flag de formato PO inferida pelo Babel para o exemplo | `python-format` | `python-brace-format` | nenhuma | `python-brace-format` |
| Usa catálogos PO/MO comuns | sim | sim | sim | sim |
| Precisa de extrator de código-fonte personalizado | não | não | não | sim, atualmente |

A linha da flag de formato trata da validação ciente de marcadores, não da
compatibilidade do catálogo. `nenhuma` significa que as ferramentas gettext
padrão ainda leem e compilam a mensagem, mas `msgfmt --check-format` não tem
uma gramática de marcadores `$` para aplicar.

## O custo

Uma f-string não pode ser usada assim: quando qualquer biblioteca a vê, ela já
é uma string pronta, portanto traduzi-la significa traduzir um fragmento.
t-strings ([PEP 750]) permitem a separação, mantendo uma sintaxe semelhante à
de f-strings e vinculando valores explicitamente. Strings `$` já oferecem uma
alternativa concisa com modelos diferentes de vinculação e falha.
`flufl.i18n` é um pacote maduro cuja versão atual oferece suporte ao Python
3.10; `gettext-tstrings` está atualmente em fase alfa e as t-strings nativas
fazem do Python 3.14 sua versão mínima.

O outro custo é a própria restrição: uma interpolação deve ser um nome simples.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Essa é uma restrição real. Junto com a vinculação de valores no código-fonte e
a verificação de marcadores em tempo de execução, ela impede que strings de
catálogo avaliem expressões e mantém os nomes dos marcadores significativos.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [comportamento documentado]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [Template personalizado]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [tradutor]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
