---
description: "Adotar t-strings em um projeto que já tem catálogos gettext: o que sobrevive intacto, o que vira fuzzy e como migrar um ponto de chamada por vez."
---

# Migração

Se o seu projeto já usa gettext, as perguntas que decidem se esta biblioteca é
adotável são poucas e específicas: ela invalida os catálogos que você já tem,
ela convive com o código que você ainda não está pronto para mudar, e quanto da
mudança precisa acontecer de uma vez só. As respostas, da mais curta para a
mais longa:

| Pergunta | Resposta |
| --- | --- |
| Os arquivos `.po` e `.mo` existentes continuam funcionando? | Sim. Mesmos arquivos, mesmas ferramentas. |
| Chamadas antigas e novas podem conviver em um arquivo? | Sim, e um único mapeamento de extrator cobre as duas. |
| O msgid muda? | Vindo de `.format()`, não. Vindo de `%`-format, sim. |
| O projeto inteiro precisa migrar de uma vez? | Não. Um ponto de chamada já é uma mudança válida. |
| E Jinja, templates do Django, JavaScript? | Intocados, mesmos catálogos. |

O restante desta página é o detalhe por trás de cada uma delas.

## Vindo de `.format()`: o msgid não muda { #from-format-the-msgid-does-not-change }

Este é o caso em que a migração quase não custa nada. Uma mensagem em
`str.format` e uma mensagem em t-string derivam a *mesma* chave de catálogo,
porque de um jeito ou de outro a chave é o texto com `{name}` dentro dele:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Assim, a tradução existente continua vinculada. Partindo de um catálogo que
contém

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

mude a chamada, extraia de novo e atualize:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

A entrada que volta difere em duas linhas de metadados e em mais nada — um
comentário marcador identificando-a como mensagem de t-string, e um número de
linha do código-fonte:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Nenhuma flag `fuzzy`, nenhuma retradução, em idioma nenhum. A mensagem é
renderizada imediatamente:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "O `update --check` vai relatar os catálogos como desatualizados"

    Aquele comentário marcador e os números de linha deslocados bastam para o
    `pybabel update --check` dizer que um catálogo precisa ser regenerado,
    porque ele compara a entrada inteira, e não só a tradução. Rode o
    `pybabel update` de verdade no mesmo commit da mudança de código e comite
    os catálogos junto — o mesmo hábito que o
    [portão de CI](workflow.md#what-ci-gates) já pede.

## Vindo de `%`-format: o msgid muda, então as traduções viram fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

A sintaxe printf vive *dentro* da mensagem, então substituí-la reescreve a
chave do catálogo. Não há como contornar isso, e esse é o custo honesto de
deixar `%(name)s` para trás:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

O `pybabel update` reconhece a nova mensagem como parente próxima da que foi
removida e transporta a tradução antiga, marcada como fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Três coisas a saber sobre esse estado:

- **Nada quebra em tempo de execução.** Entradas fuzzy ficam de fora do `.mo`
  compilado, então a aplicação renderiza a mensagem de origem até que alguém
  confirme o par — [a mesma degradação](workflow.md#the-cycle-after-the-first-translation)
  pela qual passa qualquer mensagem reescrita.
- **O `pybabel compile` reporta cada uma delas**, porque o `%(name)s`
  transportado não é um marcador de chaves válido, e sai com código diferente
  de zero. Essa lista é sua fila de trabalho, não um alarme falso; as entradas
  nela realmente precisam de edição.
- **A antiga flag `python-format` vem junto** e deve ser apagada com a flag
  `fuzzy`, ou o `msgfmt --check-format` vai continuar aplicando regras de
  printf a uma mensagem em formato de chaves.

Para marcadores printf nomeados a edição é mecânica — `%(name)s` vira `{name}`
e nada mais se move — de modo que um catálogo grande é uma passagem
programada seguida de revisão de quem traduz, e não uma retradução. Já o `%s`
posicional não é mecânico: ele não tem nome para transportar, e escolher um é
justamente o objetivo da mudança.

Por causa disso, a ordem prática é migrar as mensagens em `%`-format
deliberadamente — um módulo, uma versão, um idioma por vez — em vez de uma
varredura única que deixa todos os catálogos vermelhos de uma só vez.

## Chamadas antigas e novas convivem { #old-and-new-calls-coexist }

O extrator que lê t-strings também lê chamadas gettext comuns, então um único
mapeamento cobre um arquivo em plena migração:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

As duas mensagens caem no mesmo template, e só a de t-string carrega o
comentário marcador que liga a verificação extra desta biblioteca:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Ele reconhece `_()`, os quatro nomes gettext padrão, os apelidos `tr()` /
`ntr()` e as formas adiadas `lazy_gettext()` / `lazy_pgettext()`. Um auxiliar
seu precisa ser [nomeado no mapeamento](extraction.md#registering-your-own-function-names).

Em tempo de execução os dois estilos são igualmente independentes:
`gettext.translation()` devolve um objeto de traduções, e tanto `_` quanto os
pontos de entrada desta biblioteca leem dele.

## O que não se move { #what-does-not-move }

- **Linguagens de template.** O `{% trans %}` do Jinja2, as tags de template
  do Django e os extratores Babel correspondentes continuam funcionando sem
  mudança e continuam alimentando os mesmos catálogos PO. t-strings são
  sintaxe Python; elas valem para código-fonte Python.
- **Seus arquivos de catálogo.** Nenhuma mudança de formato, nenhum arquivo
  novo, nenhuma etapa de conversão.
- **Sua plataforma de tradução.** O intercâmbio via `.po` é idêntico, e a flag
  `python-brace-format` que uma mensagem de t-string carrega é a mesma flag que
  uma mensagem `.format()` carrega — então a QA de marcadores continua
  funcionando.
- **Código fora do Python.** Um catálogo JavaScript ou C no mesmo projeto não
  é afetado.

## Uma lista de verificação da migração { #a-migration-checklist }

1. Adicione o extra `babel` onde o `pybabel` roda e mude o mapeamento `python`
   do `babel.cfg` para o método `gettext_tstrings` — um único mapeamento passa
   então a cobrir os dois estilos, e o `-k` continua funcionando para as
   chamadas comuns.
2. Converta primeiro os pontos de chamada em `.format()`. Extraia de novo, rode
   o `pybabel update` e comite os catálogos junto com o código; não espere
   nenhuma entrada fuzzy.
3. Converta os pontos de chamada em `%`-format em lotes que você consiga levar
   à revisão, reescrevendo os marcadores transportados e limpando as flags
   `fuzzy` e `python-format`.
4. Corrija o que a restrição rejeita: uma interpolação precisa ser um nome
   simples, então `t"Hello {user.name}"` passa primeiro por uma variável local.
   Isso é uma edição no ponto de chamada, não no catálogo.
5. Ligue `strict = true` no mapeamento do extrator assim que a varredura
   terminar, para que uma mensagem que não pode ser extraída faça
   [o build falhar](extraction.md#lenient-locally-strict-in-ci) em vez de
   sumir do template.
6. Acrescente a verificação de execução descrita em
   [Em produção](workflow.md#what-ci-gates): renderize uma mensagem por idioma
   publicado através de um `Translator` estrito.

Os passos 2 e 3 são commits comuns. Nada nesta lista precisa de um dia de
virada.
