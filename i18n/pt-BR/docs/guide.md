---
description: "API de execução: qual ponto de entrada usar, vínculo de catálogo, idioma por requisição, strings preguiçosas, valores sensíveis à localidade e como uma tradução danificada é relatada."
---

# Guia

Esta página é a referência de execução: tudo o que o *código da sua aplicação*
faz com esta biblioteca quando os catálogos já existem. Se você ainda não viu o
ciclo completo — marcar, extrair, traduzir, compilar, executar — o
[tutorial](tutorial.md) o percorre uma vez em cinco minutos; a criação e a
validação de catálogos são tratadas em [Extração](extraction.md), e como uma
equipe mantém o ciclo girando — ciclos de atualização, CI, plataformas de
tradução — está em [Em produção](workflow.md).

## Qual ponto de entrada devo usar? { #which-entry-point-should-i-use }

O pacote exporta várias maneiras de traduzir uma mensagem porque as aplicações
vinculam um idioma de várias maneiras diferentes. Escolha pela forma como o seu
programa decide em que idioma ele está:

| Sua situação | Use |
| --- | --- |
| Um idioma para o processo inteiro — uma CLI, um app de desktop, um script | `Translator`, chamado como `_` |
| Um idioma por requisição ou por tarefa assíncrona — uma aplicação web | `use_translations()` em volta do trabalho, e depois `tr()` |
| Uma mensagem definida no import — um rótulo de formulário, um enum, uma constante | `lazy_gettext()` ou `lazy_pgettext()` |
| Uma contagem decide as palavras | `ngettext()` / `npgettext()`, em qualquer das formas acima |
| Renderizar um padrão sem catálogo nenhum envolvido | `compile_template()` |

Tudo o que vem abaixo são esses cinco, nessa ordem.

## Vincular um catálogo { #binding-a-catalog }

A forma recomendada segue o uso orientado a objetos do gettext: vincule uma
tradução padrão uma vez e use o processador chamável como `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

As funções do módulo seguem os nomes e argumentos posicionais da biblioteca
padrão:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` e `ntr` são aliases exatos de `gettext` e `ngettext`.

## Idioma por requisição { #per-request-language }

Um framework web escolhe um idioma por requisição. Vincule a tradução ao
contexto atual: todas as chamadas do módulo usarão esse idioma, inclusive entre
requisições concorrentes.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations()` vincula sem bloco para frameworks que gerenciam o ciclo de
vida; `get_translations()` lê o vínculo. Um `translations=` explícito tem
prioridade. Sem vínculo, as funções globais do gettext da biblioteca padrão são
o fallback. Exemplos completos para Flask e middleware ASGI estão na página
[Em produção](workflow.md#binding-a-language-at-runtime).

## Tradução preguiçosa { #deferred-translation }

Uma t-string captura seus valores imediatamente. Para um rótulo, enum ou
constante definido no import mas renderizado no idioma ativo apenas no *uso*,
utilize uma string preguiçosa.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` renderiza por `str()`, `format()` e f-strings e se compara ao texto.

!!! note "Não é hashable de propósito"

    O texto depende do idioma. Um hash mutável corromperia silenciosamente um
    set ou dict. Para obter uma chave, chame `str()` primeiro.

`strict` é decidido onde a mensagem é escrita, não onde ela é renderizada:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Uma string adiada é renderizada onde quer que ela acabe sendo usada — dentro de
um template, de um formulário, de uma linha de log — e esse lugar raramente sabe
se aquilo é uma execução de teste ou produção. Passar `strict=True` na definição
é o que permite aplicar a mesma escolha [rígida na CI, tolerante em
produção](#what-happens-when-a-catalog-is-wrong) a uma string que não é
renderizada no ponto em que é chamada.

Plurais dependem do número em tempo de execução; renderize-os imediatamente com
`ngettext`.

## Vários idiomas ao mesmo tempo { #several-languages-at-once }

Uma mesma requisição muitas vezes precisa de mais de um idioma: uma página
renderizada para quem lê que também enfileira uma notificação para uma conta
configurada em outro, ou um resumo que cita cada participante no idioma dele.
Os vínculos se aninham, e sair do bloco interno restaura o externo.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Ao percorrer uma lista de destinatários, as strings preguiçosas fazem o
trabalho: a mensagem é escrita uma única vez, no import, e renderizada uma vez
por idioma.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

O vínculo é um `ContextVar`, e não uma pilha mantida em um objeto
compartilhado, de modo que requisições sobrepostas não conseguem pegar o idioma
umas das outras — inclusive no caso em que elas *saem* de seus blocos na mesma
ordem em que entraram, que é o intercalamento que uma pilha erra. Carregar um
catálogo por idioma é barato: `gettext.translation()` analisa cada `.mo` uma vez
e entrega cópias que compartilham o catálogo já analisado.

!!! warning "Se uma thread de trabalho herda o vínculo depende do build"

    Uma `threading.Thread` pura, ou `ThreadPoolExecutor.submit`, começa ou de uma
    cópia do contexto de quem chamou ou de um contexto vazio, e quem decide isso
    é `sys.flags.thread_inherit_context` — verdadeiro por padrão em builds
    free-threaded, falso em todo o resto. O mesmo código, portanto, renderiza o
    idioma vinculado no 3.14t e o catálogo global do processo no 3.14. Passe o
    contexto em vez de depender do padrão:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` já faz isso por você.

## Valores sensíveis à localidade { #locale-aware-values }

Esta biblioteca decide *onde* um valor aparece em uma mensagem traduzida. Ela
não localiza o valor em si. `{amount:,.2f}` é uma especificação de formato do
Python com comportamento fixo — uma vírgula a cada três dígitos e um ponto
antes dos decimais — e produz os mesmos caracteres qualquer que seja o idioma
da mensagem:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

O alemão escreve esse número como `1.234,50`, o francês como `1 234,50`, e o
híndi agrupa `1234567` como `12,34,567` em vez de `1,234,567`. Números, moedas,
datas, horas e unidades são assunto do [Babel][babel-numbers]. Formate o valor
primeiro e depois posicione a string já pronta:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Em uma mensagem com contagem o número faz dois trabalhos — ele seleciona a
forma de plural e aparece no texto — e só o segundo é localizado. Guarde a
contagem bruta para a seleção e passe a string formatada para exibição:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatar antes da chamada também é o que mantém uma especificação de formato
fora do catálogo: o que quem traduz vê é um trecho de texto pronto, e não um
número acompanhado de instruções de renderização.

## Quando o catálogo está errado { #what-happens-when-a-catalog-is-wrong }

Se os marcadores de uma tradução não correspondem aos da origem — um campo
faltando, desconhecido ou reformatado que escapou da validação, vindo de um MO
editado à mão, de um catálogo de terceiros ou de um pipeline que pula o
verificador — o comportamento padrão é renderizar a mensagem de origem em vez
de lançar. Isso espelha o próprio contrato do gettext: um catálogo ruim nunca
derruba a aplicação.

Se `Hello {name}` for traduzido como `こんにちは {nombre}`, a renderização
continua e um aviso é enviado ao logger `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

O aviso ocorre uma única vez por mensagem e padrão, e não a cada renderização,
de modo que uma entrada de catálogo inválida não inunda o log. Em testes e CI,
ative o modo estrito:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

A mesma consulta então lança:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Essas mensagens são escritas para quem pode agir sobre elas, o que, num
problema de catálogo, é quem traduz com mais frequência do que quem programa —
então, onde um marcador parece presente mas não está, a mensagem explica por
quê, em vez de repetir que ele está faltando. Chaves de largura total, um
`{{name}}` duplicado, um espaço inseparável invisível, uma letra cirílica no
meio das latinas: cada caso tem sua própria redação, listada com exemplos em
[Para quem traduz](translators.md#reading-a-failure-message). Aquela página foi
escrita para ser entregue a quem edita o `.po`.

## Renderizar um padrão sem catálogo { #rendering-a-pattern-without-a-catalog }

`compile_template` produz o msgid e os valores vinculados e então renderiza um
padrão:

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` valida pelas mesmas regras e **sempre lança** em caso de diferença.
Sem consulta ao catálogo, não há fallback.

## Segurança e escopo { #safety-and-scope }

Válido:

```python
tr(t"Hello {name}")
```

Rejeitado de propósito:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Calcule o valor explícito antes:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Uma tradução nunca é avaliada e não pode acrescentar acesso a atributos,
chamadas, conversões nem formatos. Como no gettext padrão, a aplicação é
responsável pelo **escape no destino** e pela **integridade do catálogo**.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
