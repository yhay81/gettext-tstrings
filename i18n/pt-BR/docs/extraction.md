---
description: "Extraia mensagens t-string com pybabel e valide catálogos com msgfmt e o verificador Babel integrado."
---

# Extração

A extração é a etapa que coleta todas as mensagens marcadas do seu
código-fonte em um template `.pot` para quem traduz — o passo 3 do ciclo do
[tutorial](tutorial.md). Esta página é a referência dessa etapa: configuração,
nomes de função personalizados, modo estrito para CI e as verificações que
protegem seus catálogos depois disso.

A extração requer o extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Fluxo de trabalho { #the-workflow }

Crie `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Use então os comandos Babel habituais:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

O `init` roda uma única vez por idioma; depois disso, o `pybabel update`
incorpora cada template recém-extraído aos catálogos existentes. Esse ciclo
recorrente — e o que suas entradas `fuzzy` significam para um release — é
percorrido em [Em produção](workflow.md#the-cycle-after-the-first-translation).

O extrator também processa `_()`, `gettext()` e `ngettext()`. Um único
mapeamento cobre código misto, incluindo `tr()`, `ntr()`, `lazy_gettext()` e
`lazy_pgettext()`.

!!! warning "Ative os comentários para quem traduz com `-c`"

    O `pybabel extract` só coleta comentários dirigidos a quem traduz quando
    você passa `-c "Translators:"`, exatamente como faz com as chamadas gettext
    comuns. Sem essa opção a extração continua funcionando — os comentários
    simplesmente nunca chegam ao catálogo, onde são
    [a alavanca de qualidade mais barata](workflow.md#working-with-translators-and-platforms)
    de todo o fluxo.

## Nomes de função personalizados { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Em INI, o valor é uma string separada por espaços ou vírgulas; TOML aceita uma
lista. As opções cobrem as seis famílias de funções gettext.

!!! danger "`-k` não alcança uma t-string"

    Um helper como `mytr(t"…")` deve ser declarado nessas opções. O mecanismo
    `--keyword` do Babel não lê literais t-string:
    `pybabel extract -k mytr` os omite sem avisar.

    Somente a ordem padrão de argumentos é aceita.

## Tolerante localmente, estrito na CI { #lenient-locally-strict-in-ci }

Por padrão, um arquivo ruim não encerra a execução:

- Uma t-string que o extrator rejeita — acesso a atributo, uma expressão, um
  argumento errado — é reportada como aviso e ignorada.
- Um arquivo que não pode ser analisado de jeito nenhum é isolado do mesmo
  modo.
- E também um arquivo que só o `tokenize` recusa enquanto o `ast` aceita, no
  qual a passagem do próprio Babel abortaria.

Isso é conveniente enquanto você está editando e perigoso quando não está: uma
mensagem ignorada fica simplesmente **ausente do POT**, então ela nunca é
traduzida e nada avisa. Defina `strict = true` nas opções do mapeamento em todo
lugar em que a extração não esteja sendo observada por uma pessoa:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Cada aviso acima passa então a ser uma falha dura. Trate isto como a
configuração de produção e o padrão como a configuração local.

## Validação com as ferramentas existentes { #your-existing-toolchain-validates-these-catalogs }

Babel adiciona uma flag padrão:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Uma tradução `こんにちは {nombre}` é detectada sem configuração:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

O Weblate documenta essa verificação como
[Python brace format][weblate-checks], e as plataformas comerciais têm sua
própria QA de marcadores baseada na mesma flag. O comportamento de cada
plataforma é assunto dela; as duas ferramentas abaixo são as que foram
verificadas aqui.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

`pybabel compile` aplica o checker a cada mensagem marcada:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Para plurais, o erro identifica a forma:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` ainda grava o `.mo`"

    O erro acima é reportado, o status de saída é `1` — e o catálogo inválido é
    compilado mesmo assim. Só esse status de saída pode impedir um pipeline de
    publicá-lo; [O que o CI barra](workflow.md#what-ci-gates) mostra o passo de
    build que faz isso.

As duas verificações não são redundantes: o verificador do pacote é mais
estrito em pelo menos dois casos, validando chaves escapadas e cada forma de
plural separadamente, onde o msgfmt pode aceitar o arquivo. Nomes
ASCII permitem que todas as ferramentas participem; a biblioteca aceita
qualquer `str.isidentifier()`.

## Templates e outras ferramentas { #templates-and-other-tools }

t-strings são sintaxe Python. Jinja2 (`{% trans %}`), Django e outros templates
mantêm seus próprios extratores, alimentando o mesmo catálogo PO.

`pygettext` ainda não analisa t-strings. A [especificação](spec.md) permite que
outros extratores sigam a mesma convenção.
