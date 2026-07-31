---
description: "API de execução: vínculo de catálogo, idioma por requisição, strings preguiçosas e tratamento de traduções inválidas."
---

# Guia

Esta página é a referência de execução: tudo o que o *código da sua aplicação*
faz com esta biblioteca quando os catálogos já existem. Se você ainda não viu o
ciclo completo — marcar, extrair, traduzir, compilar, executar — o
[tutorial](tutorial.md) o percorre uma vez em cinco minutos; a criação e a
validação de catálogos são tratadas em [Extração](extraction.md), e como uma
equipe mantém o ciclo girando — ciclos de atualização, CI, plataformas de
tradução — está em [Em produção](workflow.md).

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

!!! warning "Uma thread de trabalho começa sem vínculo"

    Uma `threading.Thread` pura, ou `ThreadPoolExecutor.submit`, começa com um
    contexto novo e não herda o vínculo — a chamada recai no catálogo gettext
    global do processo. Leve o contexto adiante explicitamente:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` já faz isso por você.

## Quando o catálogo está errado { #what-happens-when-a-catalog-is-wrong }

Se os marcadores da tradução não correspondem à origem, o comportamento padrão
renderiza o texto de origem em vez de lançar. Isso preserva o contrato do
gettext: um catálogo ruim não deve derrubar a aplicação.

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

## Como ler as mensagens de erro { #reading-a-failure-message }

As mensagens também explicam por que um marcador aparentemente correto é
inválido:

| A tradução contém | Motivo |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Um espaço inseparável invisível aparece por seu code point:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Um homoglyph de outro alfabeto aparece legível e escapado:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Isso também cobre conflitos entre nomes inteiramente gregos ou cirílicos e seus
equivalentes ASCII.

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
