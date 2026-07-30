---
description: "A convenção de t-string para msgid como contrato versionado, com uma suíte de conformidade legível por máquinas."
---

# Especificação

O contrato é pequeno e estável para que extratores, IDEs, verificadores de tipo
e um futuro `pygettext` possam implementá-lo.

[Leia a especificação v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Regras em uma tela

Um **msgid** concatena segmentos literais na ordem da origem e um token `{name}`
para cada interpolação. Chaves literais são escapadas (`{` vira `{{`). O nome
deve satisfazer `str.isidentifier()` e não pode ser uma palavra reservada do
Python. Conversões e especificações de formato ficam na aplicação.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *rejeitada — não é um nome simples* |

Uma **tradução** é válida se contém apenas marcadores `{name}` simples, inclui
todos os nomes obrigatórios e não acrescenta nomes desconhecidos. Reordenar e
repetir é permitido.

Nos plurais, o conjunto permitido é a união dos nomes dos dois ramos e o
conjunto obrigatório é sua interseção. Portanto, `t"One file"` e
`t"{n} files"` permitem `n` em qualquer forma sem obrigá-lo.

Um **msgid vazio** nunca é consultado: gettext o reserva para metadados.

## Conformidade { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
descreve as mesmas regras como casos legíveis por máquinas. Uma implementação
está em conformidade com a spec v1 quando reproduz todos os casos, sem depender
das mensagens de erro ou dos tipos de exceção.

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

A implementação de referência executa essa suíte em seus próprios testes.

## Versionamento

Uma alteração incompatível na geração do msgid ou na validação cria uma nova
versão e um novo `conformance/vN.json`. Um esclarecimento aditivo que não muda
resultados não altera a versão.
