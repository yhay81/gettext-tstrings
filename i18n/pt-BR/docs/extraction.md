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

## Fluxo de trabalho

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

O extrator também processa `_()`, `gettext()` e `ngettext()`. Um único
mapeamento cobre código misto, incluindo `tr()`, `ntr()`, `lazy_gettext()` e
`lazy_pgettext()`.

!!! warning "`-c` não é opcional"

    Use `-c "Translators:"` para coletar comentários dirigidos a quem traduz,
    como no gettext comum.

## Nomes de função personalizados

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

## Robusto por padrão

- Uma t-string rejeitada é avisada e ignorada.
- Um arquivo impossível de analisar é isolado da mesma forma.
- Um arquivo recusado apenas por `tokenize` também é isolado.

Defina `strict = true` para transformar esses avisos em erros na CI.

## Validação com as ferramentas existentes

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
[Python brace format][weblate-checks]. As ferramentas verificadas aqui são
msgfmt e o checker Babel incluído.

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

    O status é `1`, mas o catálogo inválido é compilado. O pipeline deve tratar
    esse status como uma barreira.

    ```yaml
    - run: pybabel compile -d locales   # non-zero exit is the gate
    ```

As verificações não são redundantes: o checker incluído valida chaves escapadas
e cada forma plural separadamente, onde msgfmt pode aceitar o arquivo. Nomes
ASCII permitem que todas as ferramentas participem; a biblioteca aceita
qualquer `str.isidentifier()`.

## Templates e outras ferramentas

t-strings são sintaxe Python. Jinja2 (`{% trans %}`), Django e outros templates
mantêm seus próprios extratores, alimentando o mesmo catálogo PO.

`pygettext` ainda não analisa t-strings. A [especificação](spec.md) permite que
outros extratores sigam a mesma convenção.
