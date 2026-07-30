---
description: "A mesma mensagem traduzível escrita com %-format, .format(), strings $ do flufl.i18n e uma t-string, incluindo como cada opção vincula valores e lida com um catálogo danificado."
---

# Por que t-strings?

Quatro formas de inserir um valor em uma mensagem traduzível, comparadas na
mesma frase. A versão curta:

- Com **%-format**, uma letra apagada por quem traduz vira um travamento em
  produção.
- Com **str.format**, uma tradução pode ler atributos dos objetos que seu
  código passa — inclusive segredos.
- Com **strings $** (flufl.i18n), os valores são obtidos implicitamente das
  variáveis da função chamadora, e marcadores com pontos também alcançam
  atributos.
- Com **t-strings**, a formatação fica no seu código, as traduções são
  verificadas em tempo de execução e um catálogo danificado recai no texto de
  origem em vez de travar.

O restante desta página é a evidência, um método por vez.

!!! note "Três partes tocam cada mensagem traduzida"

    Um **catálogo** é o arquivo de traduções — `.po` enquanto pessoas o
    editam, compilado em `.mo` para a aplicação carregar (o
    [tutorial](tutorial.md) percorre os dois). Três partes tocam cada
    mensagem: quem **desenvolve** escreve a string de origem, quem **traduz**
    edita o catálogo — muitas vezes em uma plataforma externa, longe de
    qualquer revisão de código — e a **aplicação** renderiza os dois juntos em
    tempo de execução. Cada estilo de formatação abaixo responde de forma
    diferente à mesma pergunta: *quanto da linguagem de formatação o catálogo
    pode controlar?* Nos exemplos, `_` é o nome convencional da função de
    tradução, e `tr` é o desta biblioteca.

## Formatação com %

```python
_("Hello %(name)s") % {"name": name}
```

O que pode dar errado: uma única letra apagada em uma tradução trava a
renderização.

O catálogo contém sintaxe printf, incluindo uma letra de tipo ao final — o `s`
de `%(name)s` — que é fácil ignorar e fácil danificar:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

A edição de um único caractere em um editor de PO vira um traceback em
produção. O GNU `msgfmt --check-format` detecta o problema, mas somente em
mensagens marcadas como `python-format` e somente se o catálogo realmente
passar pelo msgfmt a caminho da sua aplicação.

## str.format

```python
_("Hello {name}").format(name=name)
```

Ele elimina a letra de tipo ao final, mantendo um marcador nomeado e livremente
reordenável. O que pode dar errado passa para o outro lado da troca: a tradução
ganha poder sobre os seus objetos.

`str.format` é uma pequena linguagem de expressões, e chamá-lo em uma string
significa entregar a essa string o direito de usá-la:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Agora substitua essas strings literais pelo que `_()` retornar. Se uma tradução
de `Hello {name}` voltar como `{conf.api_key}`, renderizá-la imprime sua chave
de API — quem decidiu o que seria lido foi o catálogo, não o seu código. Um
catálogo não é código, mas viaja como dado: sai para uma plataforma de
tradução, passa por várias mãos, volta como `.po`, é compilado em `.mo`, às
vezes é até incorporado de fora do seu projeto. `.format()` dá a cada etapa
dessa viagem acesso aos atributos dos objetos que você fornece.

## Strings `$` e flufl.i18n

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

A biblioteca padrão fornece a linguagem de interpolação `$name` por meio de
[`string.Template`][stdlib-template], mas isso não é, por si só, uma API de tradução.
[`flufl.i18n`][flufl-i18n] combina esse estilo com a consulta de catálogos gettext.
Repare que o valor nunca é passado: flufl.i18n monta o namespace de
substituição a partir das variáveis globais e locais de quem chama — quaisquer
variáveis existentes no ponto da chamada ficam disponíveis para a mensagem. Um
mapeamento `extras` opcional tem precedência sobre ambos. Sua sintaxe para quem
traduz não tem letra de tipo ao final nem especificador de formato, e os
marcadores continuam livremente reordenáveis.

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
A diferença está no que uma tradução *tem permissão para dizer*, e em quem
verifica isso.

Esta biblioteca valida cada tradução contra os marcadores da mensagem de origem
antes de renderizar, e aceita nomes simples e nada mais. Contra
`t"Hello {name}"`:

| A tradução contém | Motivo da rejeição |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Rejeitada não significa travada: por padrão, a biblioteca registra um aviso e
renderiza o texto de origem, então um catálogo ruim nunca derruba a aplicação —
[o mesmo contrato que o próprio gettext mantém](guide.md#what-happens-when-a-catalog-is-wrong).

A formatação permanece onde foi escrita, no código:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nunca chega ao catálogo, então nenhuma tradução pode alterá-lo e
ninguém que traduz precisa olhar para ele.

Mais uma diferença é o ferramental: t-strings são sintaxe nova, então extraí-las
para um `.pot` atualmente exige um extrator que entenda t-strings, como o que
este pacote [fornece para o Babel](extraction.md).

## Lado a lado

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| O marcador é nomeado? | sim | sim | sim | sim |
| Quem traduz pode reordenar marcadores? | sim | sim | sim | sim |
| De onde vêm os valores? | de um mapeamento explícito | de argumentos explícitos | das variáveis locais e globais de quem chama, mais um `extras` opcional | dos valores capturados dentro da t-string |
| O catálogo pode mudar como um valor é formatado? | sim | sim | não | não |
| O catálogo pode entrar nos objetos (acesso a atributos)? | não | sim | sim, com nomes pontuados | não |
| Uma tradução *remove* um marcador — o que é renderizado? | o valor some silenciosamente | o valor some silenciosamente | o valor some silenciosamente | o texto de origem, com um aviso ([por padrão](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Uma tradução *acrescenta* um marcador desconhecido — o que é renderizado? | uma exceção | uma exceção | o marcador permanece visível como texto | o texto de origem, com um aviso ([por padrão](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Os marcadores são verificados na renderização? | não | não | não | sim (veja abaixo) |
| Qual flag PO o Babel infere, para as ferramentas existentes validarem? | `python-format` | `python-brace-format` | nenhuma | `python-brace-format` |
| Usa catálogos PO/MO comuns? | sim | sim | sim | sim |
| Precisa de extrator de código-fonte personalizado? | não | não | não | sim, atualmente |

Sobre a verificação na renderização: mensagens no singular são verificadas por
correspondência exata de marcadores. Mensagens no plural também são
verificadas, contra a [regra de união/interseção](spec.md) que permite que as
formas de plural do idioma de destino sejam diferentes das da origem; a
verificação mais estrita, forma por forma, é executada quando os catálogos são
compilados ([Extração](extraction.md)).

A linha da flag de formato trata da validação ciente de marcadores, não da
compatibilidade do catálogo. `nenhuma` significa que as ferramentas gettext
padrão ainda leem e compilam a mensagem, mas `msgfmt --check-format` não tem
uma gramática de marcadores `$` para aplicar.

## O custo

Uma f-string não pode ser usada assim de forma alguma: quando qualquer
biblioteca a vê, ela já é uma string pronta, portanto traduzi-la significa
traduzir um fragmento. t-strings ([PEP 750]) mantêm o texto estático e os
valores separados, preservando uma sintaxe semelhante à de f-strings e a
vinculação explícita de valores. Strings `$` já oferecem uma alternativa
concisa com modelos diferentes de vinculação e falha. `flufl.i18n` é um pacote
maduro que roda no Python 3.10 e posteriores; `gettext-tstrings` está
atualmente em fase alfa e, como t-strings são sintaxe nova, requer Python 3.14
ou mais recente.

O outro custo é a própria restrição: uma interpolação deve ser um nome simples.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
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
