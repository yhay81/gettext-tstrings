---
description: "A mesma mensagem traduzível escrita com %-format, .format(), strings $ do flufl.i18n e uma t-string, comparadas quanto a erros de quem traduz, à autoridade do catálogo e ao custo de integração."
---

# Por que t-strings

Quatro formas de inserir um valor em uma mensagem traduzível, comparadas na
mesma mensagem. Todas as quatro nomeiam seus marcadores e deixam quem traduz
reordená-los; elas diferem no que acontece quando uma tradução está errada, em
quanto do seu programa o catálogo consegue alcançar e em quanto custa adotá-las.

As tabelas vêm primeiro, para você encontrar a linha que lhe interessa e ler
somente a seção por trás dela.

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

## Lado a lado { #side-by-side }

**Quando quem traduz comete um erro.** Um catálogo passa por muitas mãos, e a
maior parte do que dá errado nele é acidental:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Uma tradução *remove* um marcador — o que é renderizado? | o valor some silenciosamente | o valor some silenciosamente | o valor some silenciosamente | a mensagem de origem, com um aviso ([por padrão](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Uma tradução *acrescenta* um marcador desconhecido — o que é renderizado? | uma exceção | uma exceção | o marcador permanece visível como texto | a mensagem de origem, com um aviso ([por padrão](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Uma tradução *reformata* um marcador — o que é renderizado? | o que o catálogo pediu, ou uma exceção se a letra de tipo não servir mais ao valor | o que o catálogo pediu | não é expressável em strings `$` | a mensagem de origem, com um aviso |
| Os marcadores são verificados na renderização? | não | não | não | sim (veja abaixo) |

**Que autoridade o catálogo tem.** Uma tradução é um dado vindo de fora do seu
repositório, e cada estilo lhe entrega uma quantidade diferente de poder:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| De onde vêm os valores? | de um mapeamento explícito | de argumentos explícitos | das variáveis locais e globais de quem chama, mais um `extras` opcional | dos valores capturados dentro da t-string |
| O catálogo pode mudar como um valor é formatado? | sim | sim | não | não |
| O catálogo pode entrar nos objetos (acesso a atributos)? | não | sim | sim, com nomes pontuados | não |
| Onde vive "o idioma atual"? | onde a aplicação o colocar | onde a aplicação o colocar | uma pilha de códigos de idioma no objeto de aplicação compartilhado | um `ContextVar`, por tarefa ou requisição |

**Quanto custa integrar.** Tudo o que está acima sai de graça se o ferramental
servir; é aqui que ele pode não servir:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python mínimo | qualquer | qualquer | 3.10 | **3.14** |
| Maturidade | biblioteca padrão | biblioteca padrão | versão estável | **alfa** |
| Usa catálogos PO/MO comuns? | sim | sim | sim | sim |
| Precisa de extrator de código-fonte personalizado? | não | não | não | sim, atualmente |
| Qual flag PO o Babel infere, para as ferramentas existentes validarem? | `python-format` | `python-brace-format` | nenhuma | `python-brace-format` |

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

## Compatibilidade e maturidade { #compatibility-and-maturity }

As duas primeiras linhas da última tabela são as que decidem a adoção, então
vale enunciá-las com todas as letras, e não como células.

`%`-format e `.format()` são embutidos no Python e não exigem dependência
alguma. O [`flufl.i18n`][flufl-i18n] é um pacote maduro, lançado e em uso em
produção, que roda no Python 3.10 e posteriores. O `gettext-tstrings` está em
**alfa** e exige **Python 3.14 ou mais recente**, porque t-strings são sintaxe
nova na 3.14 — não existe back-port e não é possível haver um. A
[especificação](spec.md) é a parte estável dele; a API Python ainda pode mudar
antes da 1.0.

O que nenhuma delas custa é compatibilidade de catálogo. Todas as quatro
produzem arquivos POT/PO/MO comuns, que todo editor de PO, toda plataforma de
tradução e toda ferramenta GNU gettext já leem, de modo que a escolha abaixo é
reversível de um jeito que trocar o *formato* dos catálogos não seria. A
[Migração](migration.md) cobre a mudança de um projeto existente.

As seções abaixo mostram cada compromisso em detalhe, um método por vez.

## Formatação com % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

O que pode dar errado: uma única letra apagada em uma tradução trava a
renderização.

A string do catálogo carrega sintaxe printf, incluindo uma letra de tipo ao
final — o `s` de `%(name)s` — que é fácil ignorar e fácil danificar:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

A edição de um único caractere em um editor de PO vira uma exceção em tempo de
execução, a menos que a validação do catálogo a pegue antes. O GNU
`msgfmt --check-format` detecta este caso, mas somente em mensagens marcadas
como `python-format` e somente se o catálogo realmente passar pelo msgfmt a
caminho da sua aplicação.

## str.format { #strformat }

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

## Strings `$` e flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

A biblioteca padrão fornece a linguagem de interpolação `$name` por meio de
[`string.Template`][stdlib-template], mas isso não é, por si só, uma API de tradução.
O [`flufl.i18n`][flufl-i18n] combina esse estilo com a consulta de catálogos gettext.
Repare que o valor nunca é passado: flufl.i18n monta o namespace de
substituição a partir das variáveis globais e locais de quem chama — quaisquer
variáveis existentes no ponto da chamada ficam disponíveis para a mensagem. Um
mapeamento `extras` opcional tem precedência sobre ambos. Sua sintaxe para quem
traduz não tem letra de tipo ao final nem especificador de formato, e os
marcadores continuam livremente reordenáveis.

Uma substituição indisponível não gera exceção. Com `name = "Ada"` e sem
`nombre` no namespace de quem chama, uma tradução de catálogo `Hello $nombre`
é renderizada como `Hello $nombre`: o marcador não resolvido permanece visível.
Esse [comportamento documentado][documented behavior] preserva o restante da
mensagem traduzida em vez de fazer a chamada falhar. Exceções geradas ao
resolver um atributo ou converter um valor ainda podem se propagar.

Em um aspecto relevante, o `flufl.i18n` tem mais recursos que um
`string.Template` puro. Seu [Template personalizado][custom Template] aceita
marcadores com pontos, como `$settings.api_key`, e seu [tradutor][translator]
resolve esses caminhos com base nos valores de quem chama. Um marcador
traduzido pode nomear qualquer variável local ou global disponível de quem
chama e, com a sintaxe de pontos, percorrer seus atributos. Isso é conveniente
quando uma mensagem precisa de um atributo, mas também torna o frame de quem
chama parte do namespace de substituição do catálogo. A comparação aqui
descreve o `flufl.i18n` 6.0.0, e não todos os usos possíveis de
`string.Template`.

Ele também responde a uma pergunta que os outros dois estilos de formatação
deixam inteiramente para a aplicação: *qual* idioma está ativo e como trocá-lo.
Um [objeto de aplicação][application object] mantém uma pilha de idiomas,
`_.push(code)` e `_.pop()` a movimentam, `with _.using(code):` aninha, e uma
[estratégia][strategy] encontra o catálogo de um código de idioma, de modo que a
aplicação nunca manipula objetos de catálogo. Um servidor que precisa produzir
texto em mais de um idioma dentro de uma mesma unidade de trabalho — uma página
para quem lê, uma notificação para alguém cuja conta está configurada de outro
jeito — é o caso para o qual isso existe.

A pilha vive nesse objeto de aplicação, compartilhado por todo o processo. Duas
requisições sobrepostas, portanto, compartilham uma única pilha, e blocos que
não estão estritamente aninhados *no tempo* entregam uns aos outros o idioma
errado:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Esta biblioteca mantém a mesma capacidade — os vínculos se aninham e se desfazem
do mesmo jeito — em um `ContextVar`, e não em uma pilha compartilhada, de modo
que o intercalamento acima se resolve por tarefa. Os equivalentes estão em
[Vários idiomas ao mesmo tempo](guide.md#several-languages-at-once). O que ela
não fornece é a busca do catálogo a partir do código de idioma: você passa um
objeto de traduções, que no caso comum é uma única chamada a
`gettext.translation()`, e a biblioteca padrão mantém em cache o catálogo já
analisado.

## t-strings { #t-strings }

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
renderiza a mensagem de origem, então um catálogo ruim nunca derruba a
aplicação —
[o mesmo contrato que o próprio gettext mantém](guide.md#what-happens-when-a-catalog-is-wrong).

A formatação permanece onde foi escrita, no código:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nunca chega ao catálogo, então nenhuma tradução pode alterá-lo e
ninguém que traduz precisa olhar para ele. Ele é, porém, um formato *fixo*, não
um formato localizado — escolher dígitos e separadores por idioma é
[trabalho do Babel, antes da chamada](guide.md#locale-aware-values).

Mais uma diferença é o ferramental: t-strings são sintaxe nova, então extraí-las
para um `.pot` atualmente exige um extrator que entenda t-strings, como o que
este pacote [fornece para o Babel](extraction.md).

## O custo da restrição { #the-cost-of-the-restriction }

Além do requisito de versão do Python, o preço de tudo isso é uma única regra:
uma interpolação precisa ser um nome simples.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Essa é uma restrição real, e é a mesma restrição que produz as garantias acima.
Junto com a vinculação de valores no código-fonte e a verificação de marcadores
em tempo de execução, ela impede que strings de catálogo avaliem expressões e
mantém os nomes dos marcadores significativos para quem os traduz.

Uma f-string não pode ser usada assim de forma alguma: quando qualquer
biblioteca a vê, ela já é uma string pronta, portanto traduzi-la significa
traduzir um fragmento. t-strings ([PEP 750]) mantêm o texto estático e os
valores separados, preservando uma sintaxe semelhante à de f-strings e a
vinculação explícita de valores.

Como o Python chegou a essa encruzilhada — duas PEPs com dez anos de
intervalo, e a discussão na biblioteca padrão encerrada sem resposta — está
contado, com as fontes, em [Contexto](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
